"""
Viral Demand Model — Training Pipeline
========================================
End-to-end pipeline to train and evaluate the Viral Demand Model.

Pipeline stages:
  1. Data loading and validation
  2. Feature engineering (novelty, SAF, TDF, AIM)
  3. Batch preprocessing
  4. Model training (gradient boosted + citation-curve calibration)
  5. Evaluation with multiple metrics
  6. FastAPI service scaffold

Usage:
    # Full pipeline
    python training_pipeline.py

    # Or run in Jupyter Notebook (recommended):
    # Each stage is a standalone function that can be called in cells
"""

import csv
import math
import random
import json
import os
from collections import defaultdict

random.seed(42)

# ─── Stage 0: Configuration ────────────────────────────────────────────────────

CONFIG = {
    "data_path": "temp/datasets/viral_demand_dataset.csv",
    "author_path": "temp/datasets/author_cognitive_snapshot.csv",
    "output_dir": "temp/model_output",
    "target_column": "virality_composite_score",
    "train_split": 0.7,
    "val_split": 0.15,
    "test_split": 0.15,
    "n_estimators": 100,       # For gradient boosted trees
    "learning_rate": 0.05,
    "max_depth": 6,
    "batch_size": 16,
    "n_epochs": 50,
    "viral_threshold": 0.6,    # Score above this → predicted viral
}

FEATURE_GROUPS = {
    "academic":    ["citation_count", "novelty_score", "aim_score"],
    "micro_viral": ["k_factor", "aha_conversion_24h", "invite_initiation_rate",
                    "social_proof_multiplier", "share_to_value_ratio",
                    "friction_coefficient", "viral_cycle_time_days"],
    "network":     ["retention_d1", "retention_d7", "retention_d30",
                    "stickiness_dau_mau", "network_density_growth"],
    "macro":       ["global_demand_score", "cultural_resonance_score",
                    "infrastructure_readiness", "capital_alignment_score",
                    "timing_window_score", "emotional_trigger_index"],
    "structural":  ["shock_amplification_factor", "temporal_decay_factor",
                    "geopolitical_tension", "regulatory_disruption",
                    "capital_acceleration"],
}

GROUP_WEIGHTS = {
    "academic":    0.25,
    "micro_viral": 0.20,
    "network":     0.15,
    "macro":       0.25,
    "structural":  0.15,
}


# ─── Stage 1: Data Loading ─────────────────────────────────────────────────────

def load_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cast_row(row: dict) -> dict:
    """Convert CSV strings to appropriate Python types."""
    float_keys = {
        "k_factor", "invite_rate", "conversion_rate", "viral_cycle_time_days",
        "aha_conversion_24h", "invite_initiation_rate", "social_proof_multiplier",
        "share_to_value_ratio", "friction_coefficient", "complexity_score",
        "retention_d1", "retention_d7", "retention_d30", "stickiness_dau_mau",
        "network_density_growth", "global_demand_score", "cultural_resonance_score",
        "infrastructure_readiness", "capital_alignment_score", "timing_window_score",
        "emotional_trigger_index", "geopolitical_tension", "regulatory_disruption",
        "capital_acceleration", "shock_amplification_factor", "virality_horizon_years",
        "temporal_decay_factor", "novelty_score", "aim_score",
        "q1_universal_pain", "q2_emotion_trigger", "q3_low_friction",
        "q4_network_effect", "q5_scalable_economics", "q6_cultural_resonance",
        "q7_structural_readiness", "q8_capital_alignment", "q9_timing_window",
        "q10_author_credibility", "virality_composite_score",
    }
    int_keys = {"row_id", "citation_count", "patent_count", "publication_year"}

    casted = {}
    for k, v in row.items():
        if k in float_keys:
            try:
                casted[k] = float(v)
            except (ValueError, TypeError):
                casted[k] = 0.0
        elif k in int_keys:
            try:
                casted[k] = int(v)
            except (ValueError, TypeError):
                casted[k] = 0
        else:
            casted[k] = v
    return casted


def validate_dataset(rows: list[dict]) -> dict:
    """Basic data quality checks."""
    issues = defaultdict(int)
    target = CONFIG["target_column"]

    for r in rows:
        if target not in r:
            issues["missing_target"] += 1
        else:
            try:
                val = float(r[target])
                if not (0 <= val <= 1):
                    issues["target_out_of_range"] += 1
            except (ValueError, TypeError):
                issues["target_not_numeric"] += 1

        if float(r.get("k_factor", 0)) < 0:
            issues["negative_k_factor"] += 1

    report = {
        "total_rows": len(rows),
        "issues": dict(issues),
        "valid": all(v == 0 for v in issues.values()),
    }
    return report


# ─── Stage 2: Feature Engineering ─────────────────────────────────────────────

def engineer_features(row: dict) -> dict:
    """Derive additional features from raw data."""
    # Log-transform skewed features
    row["log_citations"] = math.log1p(row.get("citation_count", 0))
    row["log_patents"]   = math.log1p(row.get("patent_count", 0))

    # K-factor category
    k = row.get("k_factor", 0)
    if k > 1:
        row["k_category"] = 2   # viral
    elif k > 0.5:
        row["k_category"] = 1   # sub-viral
    else:
        row["k_category"] = 0   # dying

    # Retention health index (harmonic mean of D1, D7, D30)
    d1  = row.get("retention_d1",  0.01)
    d7  = row.get("retention_d7",  0.01)
    d30 = row.get("retention_d30", 0.01)
    row["retention_health"] = round(
        3 / (1/max(d1, 1e-9) + 1/max(d7, 1e-9) + 1/max(d30, 1e-9)), 4
    )

    # Macro virality index (weighted average of macro group)
    macro_features = ["global_demand_score", "cultural_resonance_score",
                      "infrastructure_readiness", "capital_alignment_score",
                      "timing_window_score", "emotional_trigger_index"]
    macro_values = [row.get(f, 0) for f in macro_features]
    row["macro_virality_index"] = round(sum(macro_values) / len(macro_values), 4)

    # Structural risk (high SAF + low TDF = volatile)
    row["structural_volatility"] = round(
        row.get("shock_amplification_factor", 0) *
        (1 - row.get("temporal_decay_factor", 0)), 4
    )

    return row


def get_feature_vector(row: dict) -> list[float]:
    """Flatten all feature groups into a single vector."""
    features = []
    for group, cols in FEATURE_GROUPS.items():
        weight = GROUP_WEIGHTS[group]
        for col in cols:
            val = row.get(col, 0.0)
            features.append(float(val) * weight)  # Apply group weight

    # Add engineered features
    features.append(row.get("log_citations", 0.0))
    features.append(row.get("log_patents", 0.0))
    features.append(float(row.get("k_category", 0)))
    features.append(row.get("retention_health", 0.0))
    features.append(row.get("macro_virality_index", 0.0))
    features.append(row.get("structural_volatility", 0.0))
    return features


# ─── Stage 3: Batch Processing ────────────────────────────────────────────────

def make_batches(rows: list, batch_size: int) -> list[list]:
    return [rows[i:i+batch_size] for i in range(0, len(rows), batch_size)]


def process_batch(batch: list[dict]) -> list[dict]:
    return [engineer_features(cast_row(row)) for row in batch]


def train_val_test_split(rows: list) -> tuple[list, list, list]:
    rows = list(rows)
    random.shuffle(rows)
    n = len(rows)
    n_train = int(n * CONFIG["train_split"])
    n_val   = int(n * CONFIG["val_split"])
    train = rows[:n_train]
    val   = rows[n_train:n_train+n_val]
    test  = rows[n_train+n_val:]
    return train, val, test


# ─── Stage 4: Model Training (Gradient Boosted Ensemble - pure Python MVP) ────

class ViralityGradientBooster:
    """
    Simplified gradient boosted regressor (for demonstration / MVP).
    In production: replace with XGBoost, LightGBM, or scikit-learn GBR.
    """

    def __init__(self, n_estimators: int = 50, learning_rate: float = 0.1,
                 max_depth: int = 4):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.trees: list[dict] = []
        self.base_score = 0.5

    def _mse(self, y_true: list[float], y_pred: list[float]) -> float:
        return sum((a - b)**2 for a, b in zip(y_true, y_pred)) / len(y_true)

    def _mean(self, vals: list[float]) -> float:
        return sum(vals) / len(vals) if vals else 0.0

    def _build_stump(self, X: list[list[float]], residuals: list[float]) -> dict:
        """Build a depth-1 regression stump on the best feature split."""
        best = {"mse": float("inf"), "feat": 0, "threshold": 0.0,
                "left_val": 0.0, "right_val": 0.0}
        n_features = len(X[0])

        for feat_idx in range(min(n_features, 15)):  # sample features for speed
            values = sorted(set(row[feat_idx] for row in X))
            thresholds = [(a + b) / 2 for a, b in zip(values[:-1], values[1:])]

            for thr in thresholds[:20]:  # limit splits for speed
                left_res  = [r for x, r in zip(X, residuals) if x[feat_idx] <= thr]
                right_res = [r for x, r in zip(X, residuals) if x[feat_idx] >  thr]

                if not left_res or not right_res:
                    continue

                left_val  = self._mean(left_res)
                right_val = self._mean(right_res)

                preds = [left_val if x[feat_idx] <= thr else right_val for x in X]
                mse = self._mse(residuals, preds)

                if mse < best["mse"]:
                    best = {"mse": mse, "feat": feat_idx, "threshold": thr,
                            "left_val": left_val, "right_val": right_val}
        return best

    def _stump_predict(self, stump: dict, X: list[list[float]]) -> list[float]:
        return [
            stump["left_val"] if x[stump["feat"]] <= stump["threshold"]
            else stump["right_val"]
            for x in X
        ]

    def fit(self, X: list[list[float]], y: list[float]) -> "ViralityGradientBooster":
        self.base_score = self._mean(y)
        predictions = [self.base_score] * len(y)

        for i in range(self.n_estimators):
            residuals = [yt - yp for yt, yp in zip(y, predictions)]
            stump = self._build_stump(X, residuals)
            stump_preds = self._stump_predict(stump, X)
            self.trees.append(stump)

            predictions = [
                p + self.learning_rate * s
                for p, s in zip(predictions, stump_preds)
            ]

            if (i + 1) % 10 == 0:
                mse = self._mse(y, predictions)
                print(f"  Epoch {i+1:3d}/{self.n_estimators} — Train MSE: {mse:.4f}")

        return self

    def predict(self, X: list[list[float]]) -> list[float]:
        preds = [self.base_score] * len(X)
        for stump in self.trees:
            stump_preds = self._stump_predict(stump, X)
            preds = [p + self.learning_rate * s for p, s in zip(preds, stump_preds)]
        return [max(0.0, min(1.0, p)) for p in preds]


# ─── Stage 5: Evaluation ──────────────────────────────────────────────────────

def evaluate(y_true: list[float], y_pred: list[float]) -> dict:
    n = len(y_true)
    mse  = sum((a-b)**2 for a,b in zip(y_true, y_pred)) / n
    mae  = sum(abs(a-b) for a,b in zip(y_true, y_pred)) / n
    rmse = math.sqrt(mse)

    # Pearson correlation
    mean_t = sum(y_true) / n
    mean_p = sum(y_pred) / n
    num  = sum((t - mean_t) * (p - mean_p) for t, p in zip(y_true, y_pred))
    den  = math.sqrt(
        sum((t - mean_t)**2 for t in y_true) *
        sum((p - mean_p)**2 for p in y_pred)
    )
    pearson = num / den if den > 0 else 0.0

    # Classification metrics (viral vs not-viral)
    thr = CONFIG["viral_threshold"]
    tp = sum(1 for t, p in zip(y_true, y_pred) if t >= thr and p >= thr)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t <  thr and p >= thr)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t >= thr and p <  thr)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t <  thr and p <  thr)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy  = (tp + tn) / n

    return {
        "mse": round(mse, 5), "rmse": round(rmse, 5), "mae": round(mae, 5),
        "pearson_r": round(pearson, 4),
        "precision": round(precision, 4), "recall": round(recall, 4),
        "f1_score": round(f1, 4), "accuracy": round(accuracy, 4),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
    }


def calibrate_temporal(y_true: list[float], y_pred: list[float],
                        horizons: list[float]) -> dict:
    """
    Temporal calibration: evaluate accuracy at different time horizons.
    Mimics isotonic regression behaviour for MVP.
    """
    bins = {"<1yr": [], "1-10yr": [], "10-50yr": [], "50+yr": []}
    for t, p, h in zip(y_true, y_pred, horizons):
        if   h < 1:   bins["<1yr"].append((t, p))
        elif h < 10:  bins["1-10yr"].append((t, p))
        elif h < 50:  bins["10-50yr"].append((t, p))
        else:         bins["50+yr"].append((t, p))

    results = {}
    for label, pairs in bins.items():
        if pairs:
            mae = sum(abs(t-p) for t,p in pairs) / len(pairs)
            results[label] = {"n": len(pairs), "mae": round(mae, 4)}
        else:
            results[label] = {"n": 0, "mae": None}
    return results


# ─── Stage 6: FastAPI Service (scaffold) ─────────────────────────────────────

FASTAPI_SCAFFOLD = '''"""
Viral Demand Model — FastAPI Service
======================================
Run with:
    uvicorn fastapi_service:app --reload --port 8000

API Endpoints:
    POST /predict          → Predict virality score for an idea
    GET  /health           → Health check
    GET  /criteria         → Return the 10 virality criteria
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Viral Demand Model API",
    description="Predict future virality of ideas across time horizons (0.1 – ∞ years)",
    version="0.1.0",
)

class IdeaRequest(BaseModel):
    title: str
    domain: str
    description: str
    author_profession: Optional[str] = "unknown"
    author_city: Optional[str] = "unknown"
    virality_horizon_years: Optional[float] = 10.0
    # Optional raw metrics (if available from parser)
    citation_count: Optional[int] = 0
    patent_count: Optional[int] = 0
    publication_year: Optional[int] = 2025

class VirtualityResponse(BaseModel):
    virality_composite_score: float
    virality_label: str          # "viral" | "promising" | "niche" | "declining"
    k_factor_estimate: float
    temporal_decay_factor: float
    shock_amplification_factor: float
    virality_horizon_years: float
    criteria_scores: dict        # Q1–Q10
    idea_chain: list[str]        # Causal chain of virality factors
    confidence: float

@app.post("/predict", response_model=VirtualityResponse)
async def predict_virality(request: IdeaRequest):
    """
    Predict virality score for an idea.
    In production: loads the trained model and runs inference.
    For MVP: returns a mock response.
    """
    # TODO: load actual trained model here
    mock_score = 0.72
    return VirtualityResponse(
        virality_composite_score=mock_score,
        virality_label="promising" if mock_score > 0.5 else "niche",
        k_factor_estimate=1.3,
        temporal_decay_factor=0.85,
        shock_amplification_factor=0.6,
        virality_horizon_years=request.virality_horizon_years,
        criteria_scores={
            "q1_universal_pain": 0.8, "q2_emotion_trigger": 0.7,
            "q3_low_friction": 0.6, "q4_network_effect": 0.75,
            "q5_scalable_economics": 0.65, "q6_cultural_resonance": 0.7,
            "q7_structural_readiness": 0.8, "q8_capital_alignment": 0.7,
            "q9_timing_window": 0.75, "q10_author_credibility": 0.8,
        },
        idea_chain=[
            "Universal Pain Point → High Global Demand",
            "High Emotional Trigger → Social Sharing Intent",
            "Low Friction → Fast Viral Cycle Time",
            "Network Effects → Exponential K-Factor",
            "Capital Alignment → Structural Readiness",
            "SAF = 0.6 → Horizon compressed to ~8 years",
        ],
        confidence=0.78,
    )

@app.get("/health")
async def health():
    return {"status": "ok", "model_version": "0.1.0"}

@app.get("/criteria")
async def get_criteria():
    return {
        "criteria": [
            {"id": "Q1", "name": "Universal Pain", "description": "Solves a globally felt problem"},
            {"id": "Q2", "name": "Emotion Trigger", "description": "Evokes awe, fear, or belonging"},
            {"id": "Q3", "name": "Low Friction", "description": "First value felt in under 60 seconds"},
            {"id": "Q4", "name": "Network Effect", "description": "Value grows with each new user"},
            {"id": "Q5", "name": "Scalable Economics", "description": "Near-zero marginal cost growth"},
            {"id": "Q6", "name": "Cultural Resonance", "description": "Aligns with emerging cultural megatrend"},
            {"id": "Q7", "name": "Structural Readiness", "description": "Infrastructure available now"},
            {"id": "Q8", "name": "Capital Alignment", "description": "VCs and governments fund this category"},
            {"id": "Q9", "name": "Timing Window", "description": "Regulatory or tech unlock in horizon"},
            {"id": "Q10", "name": "Author Credibility", "description": "Originator is a recognized expert"},
        ]
    }
'''


# ─── Main pipeline ─────────────────────────────────────────────────────────────

def run_pipeline():
    print("=" * 60)
    print("  Viral Demand Model — Training Pipeline")
    print("=" * 60)

    os.makedirs(CONFIG["output_dir"], exist_ok=True)

    # Stage 1: Load data
    print("\n[1/5] Loading data...")
    raw_rows = load_csv(CONFIG["data_path"])
    print(f"  Loaded {len(raw_rows)} rows from {CONFIG['data_path']}")

    validation = validate_dataset(raw_rows)
    print(f"  Validation: {validation}")
    if not validation["valid"]:
        print("  ⚠ Data issues found, proceeding anyway for MVP")

    # Stage 2 & 3: Feature engineering + batch processing
    print("\n[2/5] Feature engineering (batch processing)...")
    batches = make_batches(raw_rows, CONFIG["batch_size"])
    processed = []
    for i, batch in enumerate(batches):
        processed.extend(process_batch(batch))
    print(f"  Processed {len(processed)} rows in {len(batches)} batches")

    # Stage 3: Split
    print("\n[3/5] Train/Val/Test split...")
    train, val, test = train_val_test_split(processed)
    print(f"  Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

    # Build feature vectors
    target = CONFIG["target_column"]
    X_train = [get_feature_vector(r) for r in train]
    y_train = [r[target] for r in train]
    X_val   = [get_feature_vector(r) for r in val]
    y_val   = [r[target] for r in val]
    X_test  = [get_feature_vector(r) for r in test]
    y_test  = [r[target] for r in test]

    # Stage 4: Train model
    print(f"\n[4/5] Training ViralityGradientBooster "
          f"({CONFIG['n_estimators']} estimators)...")
    model = ViralityGradientBooster(
        n_estimators=CONFIG["n_estimators"],
        learning_rate=CONFIG["learning_rate"],
        max_depth=CONFIG["max_depth"],
    )
    model.fit(X_train, y_train)

    # Stage 5: Evaluate
    print("\n[5/5] Evaluation...")
    val_preds  = model.predict(X_val)
    test_preds = model.predict(X_test)

    val_metrics  = evaluate(y_val,  val_preds)
    test_metrics = evaluate(y_test, test_preds)

    print(f"\n  Validation Metrics:")
    for k, v in val_metrics.items():
        print(f"    {k}: {v}")

    print(f"\n  Test Metrics:")
    for k, v in test_metrics.items():
        print(f"    {k}: {v}")

    # Temporal calibration
    test_horizons = [r.get("virality_horizon_years", 10) for r in test]
    temporal_cal = calibrate_temporal(y_test, test_preds, test_horizons)
    print(f"\n  Temporal Calibration (MAE by time horizon):")
    for label, stats in temporal_cal.items():
        print(f"    {label}: {stats}")

    # Save results
    results_path = os.path.join(CONFIG["output_dir"], "pipeline_results.json")
    with open(results_path, "w") as f:
        json.dump({
            "config": CONFIG,
            "validation_metrics": val_metrics,
            "test_metrics": test_metrics,
            "temporal_calibration": temporal_cal,
        }, f, indent=2)
    print(f"\n  Results saved to {results_path}")

    # Write FastAPI scaffold
    api_path = os.path.join(CONFIG["output_dir"], "fastapi_service.py")
    with open(api_path, "w") as f:
        f.write(FASTAPI_SCAFFOLD)
    print(f"  FastAPI scaffold saved to {api_path}")
    print(f"\n  To run the API: uvicorn {api_path.replace('/', '.')}:app --reload")

    print("\n✓ Pipeline complete!")
    return model, test_metrics


if __name__ == "__main__":
    run_pipeline()
