# Viral Demand Model — RAG Training Plan
## План обучения RAG GigaChat / Analysis & Methods

---

## 1. Обзор подхода

Цель — создать **Retrieval-Augmented Generation (RAG)** систему поверх GigaChat (или аналогичного LLM), способную:

1. Получать запрос пользователя с горизонтом предсказания (0.1 — ∞ лет) и контекстом (профессия, город, религия)
2. Извлекать из векторной базы релевантные документы по 10 критериям виральности
3. Генерировать структурированный ответ с оценкой виральности идеи и цепочкой факторов

---

## 2. Архитектура RAG-системы

```
User Query
    │
    ▼
[Query Encoder]
    │  Sentence-BERT / multilingual-e5-large
    ▼
[Vector Store]  ←── Indexed Documents (ChromaDB / Weaviate / Qdrant)
    │                 (academic papers, patents, news, policy docs)
    ▼
[Top-K Retrieval]  (k = 5–10)
    │
    ▼
[Prompt Builder]
    │  Combines user query + retrieved context + virality criteria template
    ▼
[GigaChat API]
    │
    ▼
[Structured Output]
    │  JSON: virality_score, 10-criteria breakdown, idea chain, horizon_years
    ▼
[Response Formatter]
```

---

## 3. Данные для обучения и индексации

### 3.1 Источники документов (парсинг)

| Источник | Тип | Метод доступа | Приоритет |
|----------|-----|---------------|-----------|
| OpenAlex (openalex.org) | Академические статьи | REST API (бесплатно) | ★★★★★ |
| Semantic Scholar | Академические статьи | REST API (бесплатно) | ★★★★★ |
| Google Patents | Патенты | REST API / Scraping | ★★★★☆ |
| arXiv | Препринты | OAI-PMH / RSS | ★★★★☆ |
| bioRxiv / medRxiv | Биомед препринты | REST API | ★★★★☆ |
| SSRN | Соцнауки, экономика | Scraping | ★★★☆☆ |
| Product Hunt | Стартапы | API / Scraping | ★★★★☆ |
| Crunchbase | Инвестиции | API (платный) / Scraping | ★★★☆☆ |
| Startup Graveyard | Провалы стартапов | Scraping | ★★★☆☆ |
| Законодательные базы | Законопроекты | gov API / Scraping | ★★★★☆ |
| Биржа (SEC filings, EDGAR) | Финансы | REST API | ★★★☆☆ |
| Патентная база USPTO / EPO | Патенты | REST API | ★★★★☆ |
| Дорожная карта НТИ | Технополитика | Официальный сайт | ★★★☆☆ |

### 3.2 Поля для извлечения из документов (CSV schema)

```
document_id, source_url, source_type, title, abstract, authors,
publication_date, citation_count, patent_class, domain_tags,
novelty_score, k_factor_proxy, geographic_scope, language,
emotional_valence, capital_raised_usd, regulatory_flag,
horizon_years_estimated, author_h_index, institution_rank,
virality_composite_score [target label]
```

---

## 4. Feature Engineering — Группы весов признаков

### Группа A: Академические/Научные признаки (вес 0.25)
- `citation_count` → нормализованный логарифм
- `novelty_score` = exp(-0.1 × age) / (1 + log(citations + patents×3))
- `h_index_author` → нормализация [0, 1]
- `cross_domain_citations` → граф-метрика

### Группа B: Рыночные/Бизнес признаки (вес 0.25)
- `funding_amount_usd` → log-нормализация
- `k_factor_proxy` из данных о росте продукта
- `market_adoption_rate` → S-кривая подгонка
- `competitor_count` → обратная метрика

### Группа C: Структурные/Регуляторные признаки (вес 0.20)
- `regulatory_disruption_score` → sentiment из законопроектов
- `infrastructure_readiness` → прокси из отчётов
- `patent_grant_rate` → процент одобренных патентов

### Группа D: Культурно-Демографические признаки (вес 0.15)
- `cultural_resonance_score` → NLP из соцсетей
- `demographic_fit` → совпадение с растущим населением
- `religious_acceptance_proxy` → regional cultural index

### Группа E: Временны́е признаки (вес 0.15)
- `temporal_decay_factor` = exp(-λ × T / SAF)
- `shock_amplification_factor` = (GT + RD + CA) / 3 + cross-term
- `virality_horizon_years` ∈ [0.1, ∞)

---

## 5. Методы вычисления Novelty Score

```python
def novelty_score(citation_count, patent_count, pub_year, current_year=2025):
    """
    Рецентность × (1 / (1 + насыщение))
    """
    age = current_year - pub_year
    recency_weight = exp(-0.1 * age)          # Экспоненциальный распад
    saturation = log1p(citation_count + patent_count * 3)
    return clamp(recency_weight / (1 + saturation * 0.2))
```

**Интерпретация:**
- `0.8 – 1.0` → Очень новая, незаполненная ниша
- `0.4 – 0.8` → Молодая идея, умеренное насыщение
- `0.1 – 0.4` → Зрелая тема, конкуренция высокая
- `< 0.1`     → Устаревшая / перенасыщенная ниша

---

## 6. Методы обучения модели

### 6.1 Этап 1: Embedding-based Retrieval
**Метод:** Fine-tuned Sentence-BERT (multilingual-e5-large)
- Обучение: contrastive learning на парах (запрос, релевантный документ)
- Negative sampling: hard negatives из похожих, но не релевантных документов
- Метрика: MRR@10, NDCG@10

### 6.2 Этап 2: Cross-encoder Reranker
**Метод:** Cross-encoder (ruBERT-based) для переранжирования Top-K
- Вход: (query, candidate_doc) → релевантность [0, 1]
- Обучение на annotated pairs с human labels
- Метрика: MAP@10

### 6.3 Этап 3: GigaChat Fine-tuning (опционально)
**Метод:** Instruction fine-tuning / PEFT (LoRA)
- Датасет: (query, context_docs, target_output) триплеты
- Target output: JSON с оценками 10 критериев виральности
- Метрика: BLEU, BERTScore, JSON validity rate

### 6.4 Этап 4: Temporal Calibration
**Метод:** Isotonic regression / Platt scaling
- Калибровка горизонта предсказания (0.1 – ∞ лет)
- Обучение на citation-growth кривых реальных статей
- Метрика: Expected Calibration Error (ECE)

---

## 7. Citation Growth Curve — обучение временны́х параметров

Используем реальную историческую кривую цитирования (из OpenAlex):

```
c(t) = c_max × (1 - exp(-k × t))^n   # S-кривая Гомперца
```

Параметры `k`, `n`, `c_max` оцениваются по domain-кластерам.
Это даёт нам **базовый темп виральности** без привязки к конкретному горизонту.

---

## 8. Author Cognitive Snapshot — Author Intelligence Model (AIM)

**Концепция:** Вместо парсинга всех публикаций автора — создаём "расширенное резюме" (Extended Author Profile, EAP), 2–3× плотнее стандартного CV.

**Поля EAP:**
```
hard_skills: [список технологий, методов]
soft_skills: [коммуникация, лидерство, ...]
background: [образование, карьера]
domain_expertise: [primary, secondary, tertiary]
cognitive_style: [analytic/synthetic/creative]
collaboration_network: [граф коллег]
publication_fingerprint: [частотный словарь тем]
temporal_focus: [past/present/future orientation]
geographic_scope: [local/national/global]
cultural_lenses: [scientific/humanistic/technical]
aim_score: float [0, 1]
author_cluster: [emerging/specialist/expert/thought_leader/visionary]
```

**Выгода:** 10 лет без повторного парсинга этого автора (экономия ~90% API-вызовов)

---

## 9. Кластеризация авторов

**Метод:** K-Means / DBSCAN на пространстве AIM-признаков

| Кластер | h-index | pub_count | cross_disciplinary | Описание |
|---------|---------|-----------|-------------------|----------|
| emerging_voice | 0–20 | 1–50 | — | Молодой эксперт |
| specialist | 20–40 | 50–150 | false | Глубокий специалист |
| established_expert | 40–60 | 150–300 | mixed | Признанный эксперт |
| thought_leader | 60–80 | 300–500 | true | Лидер мнений |
| visionary | 80+ | 500+ | true | Визионер |

---

## 10. Shock Amplification Factor (SAF) — 3 модельные траектории

### Траектория 1: "Тихий рост" (SAF < 0.3)
- Нет регуляторных потрясений
- Капитал растёт медленно
- Горизонт виральности: 20–100 лет
- Пример: квантовые вычисления в 2000-е

### Траектория 2: "Ускоренный запуск" (SAF 0.3 – 0.8)
- Умеренная геополитическая напряжённость
- Умеренный приток капитала
- Горизонт виральности: 5–20 лет
- Пример: CRISPR после 2012

### Траектория 3: "Шоковая волна" (SAF > 0.8)
- Высокая геополитическая напряжённость (пандемия, война)
- Массивный государственный + частный капитал
- Горизонт виральности: 0.1–5 лет
- Пример: мРНК-вакцины после COVID-19 (2020)

**Важно:** Модель НЕ привязана к конкретным горизонтам. SAF лишь сжимает/растягивает временную шкалу.

---

## 11. Метрики качества пайплайна

| Метрика | Цель | Инструмент |
|---------|------|------------|
| Retrieval MRR@10 | > 0.7 | BEIR benchmark |
| Reranker MAP@10 | > 0.65 | Custom eval |
| Novelty Score Corr. | > 0.6 Pearson с citation data | OpenAlex |
| SAF Calibration ECE | < 0.05 | Isotonic regression |
| AIM Cluster Purity | > 0.75 | Clustering metrics |
| JSON validity rate | > 95% | Schema validation |

---

## 12. Следующие шаги

1. [ ] Запустить парсинг 10k документов из OpenAlex + Semantic Scholar
2. [ ] Построить embedding индекс в ChromaDB
3. [ ] Разметить 1000 пар (query, relevance) для fine-tuning
4. [ ] Обучить reranker на размеченных данных
5. [ ] Интегрировать с GigaChat API
6. [ ] Запустить FastAPI сервис
7. [ ] Подключить VS Code plugin
