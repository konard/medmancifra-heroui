"""
Viral Demand Model - Dataset Generator
========================================
Generates a synthetic dataset for training a viral demand prediction model.

Dataset captures multi-level virality signals (Levels 1-5):
  - Product Virality (K-factor)
  - Network Virality (Graph density)
  - Market Virality (Adoption curve)
  - Structural Virality (Capital + Law + Infrastructure)
  - Civilizational Virality (Demography + Culture)

Also captures Author Cognitive Snapshot (AIM - Author Intelligence Model)
for building expert avatar profiles.

Usage:
    python dataset_generator.py
    # Outputs: datasets/viral_demand_dataset.csv, datasets/author_cognitive_snapshot.csv
"""

import csv
import random
import math
import os
from datetime import datetime, timedelta

random.seed(42)

# ── Lookup tables ──────────────────────────────────────────────────────────────

PROFESSIONS = [
    "physician", "data_scientist", "entrepreneur", "lawyer", "engineer",
    "sociologist", "economist", "biologist", "educator", "journalist",
    "policy_analyst", "urban_planner", "biotech_researcher", "investor",
    "cultural_anthropologist",
]

CITIES = [
    "New York", "Tokyo", "London", "Lagos", "Mumbai", "São Paulo",
    "Berlin", "Singapore", "Cairo", "Toronto", "Seoul", "Sydney",
    "Stockholm", "Dubai", "Nairobi",
]

RELIGIONS = [
    "secular", "christian", "muslim", "hindu", "buddhist",
    "jewish", "sikh", "agnostic", "atheist", "syncretic",
]

DOMAINS = [
    "biotech", "fintech", "edtech", "healthtech", "cleantech",
    "agritech", "spacetech", "govtech", "mediatech", "socialtech",
]

SOURCE_TYPES = [
    "academic_paper", "patent", "startup_pitch", "news_article",
    "policy_document", "social_post", "conference_talk", "market_report",
    "legislation_draft", "startup_post_mortem",
]

OPEN_SOURCES = [
    "openalex.org", "semanticscholar.org", "scholar.google.com",
    "patents.google.com", "producthunt.com", "legislation.gov",
    "crunchbase.com", "arxiv.org", "biorxiv.org", "ssrn.com",
]

IDEA_TITLES = [
    "AI-Powered Diagnostic Companion for Rural Physicians",
    "Decentralized Carbon Credit Exchange on Blockchain",
    "Predictive Mental Health Coach via Wearable Biometrics",
    "Vertical Farming Mesh Network for Urban Food Security",
    "Universal Coding Tutor for Non-English Speaking Youth",
    "Bio-Mimetic Water Purification Nano-Filter",
    "Legal AI Copilot for Unrepresented Litigants",
    "Emotional Support Robot for Elderly in Care Facilities",
    "Peer-to-Peer Renewable Energy Trading Platform",
    "Genomic Risk Map for Pandemic Early Warning",
    "Smart City Traffic AI Reducing Commute by 40%",
    "Affordable Exoskeleton for Mobility-Impaired Workers",
    "NLP-Based Financial Literacy Bot for Developing Markets",
    "On-Chain Scientific Research Funding DAO",
    "Micro-Drone Pollination Network for Failing Ecosystems",
    "Real-Time Disinformation Detection Browser Extension",
    "Longevity Drug Discovery via Protein Folding AI",
    "Cross-Border Micro-Loan Network using DeFi",
    "3D-Printed Custom Prosthetics via Mobile Clinic",
    "Wildfire Prediction System using Satellite ML",
]


# ── Helper functions ───────────────────────────────────────────────────────────

def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, val))


def noise(scale: float = 0.05) -> float:
    return random.gauss(0, scale)


def compute_k_factor(invite_rate: float, conversion: float) -> float:
    """K = i × c  (Viral Coefficient)"""
    return round(invite_rate * conversion, 4)


def compute_viral_cycle_time(complexity: float, friction: float) -> float:
    """VCT in days; lower friction and complexity → faster cycle."""
    base = 3 + complexity * 30
    return round(base * (1 + friction), 2)


def compute_novelty_score(
    citation_count: int,
    patent_count: int,
    publication_year: int,
    current_year: int = 2025,
) -> float:
    """
    Novelty = recency weight × (1 / (1 + saturation))
    Saturation grows with citations + patents.
    """
    age = current_year - publication_year
    recency_weight = math.exp(-0.1 * age)
    saturation = math.log1p(citation_count + patent_count * 3)
    novelty = clamp(recency_weight / (1 + saturation * 0.2))
    return round(novelty, 4)


def compute_shock_amplification(
    geopolitical_tension: float,
    regulatory_disruption: float,
    capital_acceleration: float,
) -> float:
    """
    SAF captures sudden external forces that compress/expand virality horizon.
    Formula: SAF = (GT + RD + CA) / 3 + cross-term bonus
    """
    cross_term = geopolitical_tension * regulatory_disruption * 0.3
    saf = (geopolitical_tension + regulatory_disruption + capital_acceleration) / 3 + cross_term
    return round(clamp(saf, 0, 2.0), 4)


def compute_temporal_decay(
    virality_horizon_years: float,
    saf: float,
) -> float:
    """
    Temporal Decay Factor: ideas far in the future decay unless amplified by SAF.
    TDF = exp(-λ × T / SAF)  where λ=0.05
    """
    if saf < 0.01:
        saf = 0.01
    tdf = math.exp(-0.05 * virality_horizon_years / saf)
    return round(clamp(tdf), 4)


def compute_aim_score(
    h_index: int,
    publication_count: int,
    domain_diversity: float,
    social_influence_score: float,
) -> float:
    """
    Author Intelligence Model (AIM) composite score.
    Used to weight idea virality by author credibility.
    """
    h_norm = clamp(h_index / 100)
    pub_norm = clamp(publication_count / 500)
    aim = (h_norm * 0.35 + pub_norm * 0.25 +
           domain_diversity * 0.2 + social_influence_score * 0.2)
    return round(clamp(aim), 4)


# ── Virality 10-criteria scoring ───────────────────────────────────────────────

def score_10_criteria(row: dict) -> dict:
    """
    Q1  Universal pain — does it solve a problem felt globally?
    Q2  Emotion trigger — does it invoke awe/fear/belonging?
    Q3  Low friction — can first value be felt in < 60 seconds?
    Q4  Network effect — does value grow with each new user?
    Q5  Scalable unit economics — can it grow with near-zero marginal cost?
    Q6  Cultural resonance — aligns with an emerging cultural megatrend?
    Q7  Structural readiness — is infrastructure available now?
    Q8  Capital alignment — do VCs/governments fund this category?
    Q9  Timing window — is there a regulatory or tech unlock in the horizon?
    Q10 Author credibility — is the originator a recognized expert?
    """
    scores = {
        "q1_universal_pain":        clamp(row["global_demand_score"] + noise()),
        "q2_emotion_trigger":       clamp(row["emotional_trigger_index"] + noise()),
        "q3_low_friction":          clamp(1 - row["friction_coefficient"] + noise()),
        "q4_network_effect":        clamp(row["network_density_growth"] + noise()),
        "q5_scalable_economics":    clamp(row["share_to_value_ratio"] + noise()),
        "q6_cultural_resonance":    clamp(row["cultural_resonance_score"] + noise()),
        "q7_structural_readiness":  clamp(row["infrastructure_readiness"] + noise()),
        "q8_capital_alignment":     clamp(row["capital_alignment_score"] + noise()),
        "q9_timing_window":         clamp(row["timing_window_score"] + noise()),
        "q10_author_credibility":   clamp(row["aim_score"] + noise()),
    }
    # Composite: weighted average (equal weights for MVP)
    scores["virality_composite_score"] = round(
        sum(scores.values()) / len(scores), 4
    )
    return scores


# ── Author Cognitive Snapshot builder ─────────────────────────────────────────

def build_author_snapshot(row_id: int) -> dict:
    h_index = random.randint(0, 80)
    pub_count = random.randint(1, 400)
    domain_div = round(random.uniform(0.1, 1.0), 3)
    social_inf = round(random.uniform(0.0, 1.0), 3)

    cluster_map = {
        (0,  20): "emerging_voice",
        (20, 40): "specialist",
        (40, 60): "established_expert",
        (60, 80): "thought_leader",
        (80, 101): "visionary",
    }
    cluster = "emerging_voice"
    for (lo, hi), label in cluster_map.items():
        if lo <= h_index < hi:
            cluster = label
            break

    return {
        "author_id":          f"AUTH_{row_id:04d}",
        "profession":         random.choice(PROFESSIONS),
        "city":               random.choice(CITIES),
        "religion":           random.choice(RELIGIONS),
        "h_index":            h_index,
        "publication_count":  pub_count,
        "domain_diversity":   domain_div,
        "social_influence":   social_inf,
        "primary_domain":     random.choice(DOMAINS),
        "secondary_domain":   random.choice(DOMAINS),
        "avg_citation_rate":  round(random.uniform(0.5, 50.0), 2),
        "collab_network_size":random.randint(5, 500),
        "cross_disciplinary": random.choice([True, False]),
        "institutional_rank": random.randint(1, 1000),
        "soft_skills_score":  round(random.uniform(0.3, 1.0), 3),
        "background_score":   round(random.uniform(0.2, 1.0), 3),
        "friendly_circle_reach": random.randint(100, 100000),
        "author_cluster":     cluster,
        "aim_score":          compute_aim_score(h_index, pub_count, domain_div, social_inf),
        "temporal_decay_factor": round(random.uniform(0.3, 1.0), 3),
    }


# ── Main row generator ─────────────────────────────────────────────────────────

def generate_row(row_id: int) -> tuple[dict, dict]:
    author = build_author_snapshot(row_id)

    pub_year = random.randint(1990, 2025)
    citation_count = random.randint(0, 5000)
    patent_count = random.randint(0, 200)

    # Micro virality (Level 1-2)
    invite_rate = round(random.uniform(0.01, 5.0), 3)
    conversion_rate = round(random.uniform(0.01, 0.6), 3)
    k_factor = compute_k_factor(invite_rate, conversion_rate)

    friction = round(random.uniform(0.0, 1.0), 3)
    complexity = round(random.uniform(0.0, 1.0), 3)
    vct = compute_viral_cycle_time(complexity, friction)

    retention_d1 = round(random.uniform(0.1, 0.95), 3)
    retention_d7 = round(retention_d1 * random.uniform(0.4, 0.9), 3)
    retention_d30 = round(retention_d7 * random.uniform(0.3, 0.8), 3)
    stickiness = round(random.uniform(0.05, 0.6), 3)

    network_density = round(random.uniform(0.0, 1.0), 3)
    social_proof_mult = round(random.uniform(1.0, 5.0), 3)
    share_to_value = round(random.uniform(0.0, 1.0), 3)
    invite_init_rate = round(random.uniform(0.0, 1.0), 3)
    aha_conv_24h = round(random.uniform(0.0, 1.0), 3)

    # Macro virality (Level 3-5)
    global_demand = round(random.uniform(0.0, 1.0), 3)
    cultural_resonance = round(random.uniform(0.0, 1.0), 3)
    infrastructure_readiness = round(random.uniform(0.0, 1.0), 3)
    capital_alignment = round(random.uniform(0.0, 1.0), 3)
    timing_window = round(random.uniform(0.0, 1.0), 3)
    emotional_trigger = round(random.uniform(0.0, 1.0), 3)

    # Shock & structural
    geopolitical_tension = round(random.uniform(0.0, 1.0), 3)
    regulatory_disruption = round(random.uniform(0.0, 1.0), 3)
    capital_acceleration = round(random.uniform(0.0, 1.0), 3)
    saf = compute_shock_amplification(geopolitical_tension, regulatory_disruption, capital_acceleration)

    # Temporal
    virality_horizon_years = round(random.uniform(0.1, 100), 2)
    tdf = compute_temporal_decay(virality_horizon_years, saf)

    novelty_score = compute_novelty_score(citation_count, patent_count, pub_year)

    main_row = {
        # Identifiers
        "row_id":                   row_id,
        "idea_title":               random.choice(IDEA_TITLES),
        "domain":                   random.choice(DOMAINS),
        "source_type":              random.choice(SOURCE_TYPES),
        "source_url":               f"https://{random.choice(OPEN_SOURCES)}/doc/{row_id}",
        "publication_year":         pub_year,
        "citation_count":           citation_count,
        "patent_count":             patent_count,
        # Author ref
        "author_id":                author["author_id"],
        "author_profession":        author["profession"],
        "author_city":              author["city"],
        "author_religion":          author["religion"],
        "aim_score":                author["aim_score"],
        # Level 1: Product Virality
        "k_factor":                 k_factor,
        "invite_rate":              invite_rate,
        "conversion_rate":          conversion_rate,
        "viral_cycle_time_days":    vct,
        "aha_conversion_24h":       aha_conv_24h,
        "invite_initiation_rate":   invite_init_rate,
        "social_proof_multiplier":  social_proof_mult,
        "share_to_value_ratio":     share_to_value,
        "friction_coefficient":     friction,
        "complexity_score":         complexity,
        # Level 2: Network Virality
        "retention_d1":             retention_d1,
        "retention_d7":             retention_d7,
        "retention_d30":            retention_d30,
        "stickiness_dau_mau":       stickiness,
        "network_density_growth":   network_density,
        # Level 3-5: Macro Virality
        "global_demand_score":      global_demand,
        "cultural_resonance_score": cultural_resonance,
        "infrastructure_readiness": infrastructure_readiness,
        "capital_alignment_score":  capital_alignment,
        "timing_window_score":      timing_window,
        "emotional_trigger_index":  emotional_trigger,
        # Structural
        "geopolitical_tension":     geopolitical_tension,
        "regulatory_disruption":    regulatory_disruption,
        "capital_acceleration":     capital_acceleration,
        "shock_amplification_factor": saf,
        # Temporal
        "virality_horizon_years":   virality_horizon_years,
        "temporal_decay_factor":    tdf,
        # Novelty
        "novelty_score":            novelty_score,
    }

    # Append 10-criteria scores
    criteria_scores = score_10_criteria(main_row)
    main_row.update(criteria_scores)

    return main_row, author


# ── Write CSVs ─────────────────────────────────────────────────────────────────

def generate_dataset(n_rows: int = 100, out_dir: str = "temp/datasets") -> None:
    os.makedirs(out_dir, exist_ok=True)

    main_rows = []
    author_rows = []

    for i in range(1, n_rows + 1):
        row, author = generate_row(i)
        main_rows.append(row)
        author_rows.append(author)

    # Write main dataset
    main_path = os.path.join(out_dir, "viral_demand_dataset.csv")
    with open(main_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=main_rows[0].keys())
        writer.writeheader()
        writer.writerows(main_rows)
    print(f"✓ Main dataset:  {main_path} ({n_rows} rows, {len(main_rows[0])} columns)")

    # Write author cognitive snapshots
    author_path = os.path.join(out_dir, "author_cognitive_snapshot.csv")
    with open(author_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=author_rows[0].keys())
        writer.writeheader()
        writer.writerows(author_rows)
    print(f"✓ Author snapshot: {author_path} ({n_rows} rows, {len(author_rows[0])} columns)")

    # Print summary stats
    k_factors = [r["k_factor"] for r in main_rows]
    composites = [r["virality_composite_score"] for r in main_rows]
    novelties = [r["novelty_score"] for r in main_rows]
    print(f"\n── Summary Stats ──────────────────────────")
    print(f"K-factor range:        {min(k_factors):.3f} – {max(k_factors):.3f}")
    print(f"Virality composite:    {sum(composites)/len(composites):.3f} avg")
    print(f"Novelty score:         {sum(novelties)/len(novelties):.3f} avg")
    k_gt1 = sum(1 for k in k_factors if k > 1)
    print(f"K > 1 (viral) ideas:   {k_gt1} / {n_rows} ({100*k_gt1/n_rows:.0f}%)")


if __name__ == "__main__":
    generate_dataset(n_rows=100, out_dir="temp/datasets")
