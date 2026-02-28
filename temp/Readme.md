# Viral Demand Model (VDM)
## Описание функционала и Дорожная карта развития

---

## Что такое Viral Demand Model?

**Viral Demand Model (VDM)** — это система предсказания виральности идей, продуктов и технологий через произвольный временной горизонт (от 0.1 до ∞ лет). Система помогает ответить на вопрос:

> *«Я врач. Живу в Нью-Йорке. Что заинтересует людей разных профессий и городов через 15 лет?»*

VDM оценивает не только продуктовую виральность (K-factor), но и **макро-виральность** — структурные, культурные, законодательные и демографические силы, формирующие массовый спрос в будущем.

---

## Уровни виральности (Virality Levels)

| Уровень | Название | Метрики | Что измеряет |
|---------|----------|---------|-------------|
| **L1** | Product Virality | K-factor, VCT, Aha Moment Rate | Рост внутри продукта |
| **L2** | Network Virality | Network Density, Retention D1/D7/D30 | Рост через сеть пользователей |
| **L3** | Market Virality | Adoption Curve, Global Demand Score | Рост в отрасли/рынке |
| **L4** | Structural Virality | Capital + Law + Infrastructure | Системные предпосылки |
| **L5** | Civilizational Virality | Demography + Culture + Religion | Глубинные культурные силы |

*GrowthMBA-курсы работают на L1–L2. VDM строит предсказания на L3–L5.*

---

## 10 Критериев виральности идеи

Идея считается потенциально вирусной, если положительно отвечает на большинство из 10 вопросов:

| # | Критерий | Вопрос |
|---|----------|--------|
| Q1 | **Universal Pain** | Решает ли идея проблему, ощущаемую глобально? |
| Q2 | **Emotion Trigger** | Вызывает ли она восторг, страх или чувство принадлежности? |
| Q3 | **Low Friction** | Можно ли почувствовать первую ценность за 60 секунд? |
| Q4 | **Network Effect** | Растёт ли ценность с каждым новым пользователем? |
| Q5 | **Scalable Economics** | Может ли идея расти с нулевыми предельными затратами? |
| Q6 | **Cultural Resonance** | Согласуется ли она с мегатрендом текущей культуры? |
| Q7 | **Structural Readiness** | Готова ли инфраструктура для её реализации сегодня? |
| Q8 | **Capital Alignment** | Финансируют ли VC/правительства эту категорию? |
| Q9 | **Timing Window** | Есть ли регуляторный или технологический «разблокиратор» в горизонте? |
| Q10 | **Author Credibility** | Признан ли автор идеи экспертом сообщества? |

---

## Ключевые формулы модели

### K-Factor (Viral Coefficient)
```
K = invite_rate × conversion_rate
K > 1 → экспоненциальный рост
K = 1 → линейный рост
K < 1 → затухание
```

### Novelty Score
```
novelty = exp(-0.1 × age) / (1 + log(citations + patents × 3))
```
Измеряет незаполненность ниши: высокая новизна → низкая насыщенность.

### Shock Amplification Factor (SAF)
```
SAF = (geopolitical_tension + regulatory_disruption + capital_acceleration) / 3
      + geopolitical_tension × regulatory_disruption × 0.3
```
Внешние потрясения (пандемии, войны, регуляторные революции) сжимают временной горизонт виральности.

### Temporal Decay Factor (TDF)
```
TDF = exp(-0.05 × horizon_years / SAF)
```
Без внешних катализаторов (SAF→0) идеи на дальнем горизонте затухают. SAF > 1 восстанавливает жизнеспособность.

---

## Author Intelligence Model (AIM) — Когнитивный Аватар Автора

Вместо повторного парсинга всех публикаций автора система строит **Extended Author Profile (EAP)** — расширенное резюме (в 2–3 раза плотнее стандартного A4 CV), по которому можно:

1. Генерировать статьи о будущем от имени автора
2. Дообучать модель без нового парсинга в течение 10+ лет
3. Кластеризовать авторов для взвешивания идей

### Кластеры авторов
| Кластер | h-index | Описание |
|---------|---------|----------|
| `emerging_voice` | 0–20 | Молодой эксперт |
| `specialist` | 20–40 | Глубокий специалист |
| `established_expert` | 40–60 | Признанный эксперт |
| `thought_leader` | 60–80 | Лидер мнений |
| `visionary` | 80+ | Визионер |

---

## Источники данных для парсинга

| Источник | Доступ | Тип данных |
|----------|--------|------------|
| [OpenAlex](https://openalex.org) | REST API (бесплатно) | Научные статьи |
| [Semantic Scholar](https://semanticscholar.org) | REST API (бесплатно) | Статьи + цитирование |
| [Google Patents](https://patents.google.com) | API + Scraping | Патенты |
| [arXiv](https://arxiv.org) | OAI-PMH | Препринты |
| [Product Hunt](https://producthunt.com) | API | Стартапы |
| [Crunchbase](https://crunchbase.com) | API | Инвестиции |
| [Startup Graveyard](https://killedbygoogle.com) | Scraping | Провалы стартапов |
| Patent Bases (USPTO/EPO) | REST API | Патентный анализ |
| Stock Exchanges (SEC EDGAR) | REST API | Биржевые данные |
| НТИ Дорожная карта | Официальный сайт | Технополитика |
| Законодательные базы | gov API | Законопроекты |

---

## Артефакты в папке /temp

| Файл | Описание |
|------|----------|
| `materials.md` | Исходное техническое задание |
| `dataset_generator.py` | Python-генератор датасета (52 признака, 100 строк) |
| `training_pipeline.py` | End-to-end pipeline обучения модели |
| `analysis.md` | План обучения RAG GigaChat с методологией |
| `Readme.md` | Этот файл — функционал и дорожная карта |
| `datasets/viral_demand_dataset.csv` | Основной датасет (100 строк, 52 колонки) |
| `datasets/author_cognitive_snapshot.csv` | Снапшоты авторов (100 строк, 20 колонок) |
| `model_output/pipeline_results.json` | Результаты тренировки пайплайна |
| `model_output/fastapi_service.py` | FastAPI сервис для онлайн-оценки |

---

## Дорожная карта развития — AI-Агенты и Ансамбли Моделей

### Фаза 0: MVP (текущая) ✅
- [x] Генератор синтетического датасета (100 строк, 52 признака)
- [x] Gradient Boosted модель предсказания виральности
- [x] Author Cognitive Snapshot (AIM)
- [x] FastAPI scaffold для онлайн-оценки
- [x] 10 критериев виральности с формулами
- [x] RAG план для GigaChat

---

### Фаза 1: Сбор реальных данных (Q2 2025)
- [ ] **Парсер-агент**: автоматический сбор из OpenAlex + Semantic Scholar
  - Технология: Python + requests + rate limiting + retry
  - Объём: 100k+ документов
- [ ] **Очистка и нормализация**: дедупликация, языковая фильтрация
- [ ] **Embedding-индекс**: ChromaDB / Qdrant на 100k документов
- [ ] **Citation curve fitting**: обучение временны́х параметров на реальных данных

---

### Фаза 2: RAG-система (Q3 2025)
- [ ] **Retrieval Agent**: Sentence-BERT (multilingual-e5-large) fine-tuning
  - Contrastive learning на парах (query, relevant_doc)
  - Метрика: MRR@10 > 0.7
- [ ] **Cross-encoder Reranker**: ruBERT-based для Top-K переранжирования
- [ ] **GigaChat Integration**: подключение к API GigaChat
- [ ] **Prompt Template Engine**: шаблоны для 10 критериев виральности
- [ ] **Output Parser**: структурированный JSON с цепочкой факторов

---

### Фаза 3: Ансамбль моделей (Q4 2025)
```
              ┌──────────────┐
              │  User Query  │
              └──────┬───────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
  ┌─────────────┐ ┌──────────┐ ┌──────────────┐
  │ Micro-Model │ │ Macro-   │ │  Author AIM  │
  │ (K-factor,  │ │ Model    │ │  Model       │
  │  Retention) │ │ (L3-L5)  │ │  Predictor   │
  └──────┬──────┘ └────┬─────┘ └──────┬───────┘
         └─────────────┼──────────────┘
                       ▼
              ┌────────────────┐
              │  Meta-Learner  │  (stacking ensemble)
              │  GigaChat RAG  │
              └────────┬───────┘
                       ▼
              ┌────────────────┐
              │ Viral Demand   │
              │ Score + Chain  │
              └────────────────┘
```

- [ ] **Micro-Virality Model**: XGBoost на L1–L2 признаках
- [ ] **Macro-Virality Model**: GNN (Graph Neural Network) на данных сетей
- [ ] **Temporal Model**: LSTM / Transformer на citation time series
- [ ] **Meta-Learner**: стекинг ансамбль с GigaChat как оркестратором
- [ ] **Calibration Layer**: isotonic regression для временны́х предсказаний

---

### Фаза 4: AI-Агентная архитектура (Q1 2026)
```
┌─────────────────────────────────────────────┐
│              Orchestrator Agent              │
│         (GigaChat / Claude / GPT-4)          │
└──────────────────────────┬──────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    ▼                      ▼                      ▼
┌──────────┐      ┌──────────────┐      ┌──────────────┐
│ Parsing  │      │  Analysis    │      │  Generation  │
│  Agent   │      │  Agent       │      │  Agent       │
│          │      │              │      │              │
│ - Web    │      │ - Novelty    │      │ - AIM Avatar │
│ - Patents│      │ - SAF calc   │      │ - Report     │
│ - Scholar│      │ - K-factor   │      │ - Chain      │
└──────────┘      └──────────────┘      └──────────────┘
    ▼                      ▼                      ▼
┌──────────┐      ┌──────────────┐      ┌──────────────┐
│ Vector   │      │  Ensemble    │      │  Structured  │
│  Store   │      │  Predictor   │      │  Output JSON │
└──────────┘      └──────────────┘      └──────────────┘
```

Агенты:
- **Parsing Agent**: сбор данных из 12+ источников с авто-ретраем
- **Analysis Agent**: вычисление всех метрик (novelty, SAF, TDF, AIM)
- **Generation Agent**: создание аватара автора + генерация текстов о будущем
- **Orchestrator**: планирование, маршрутизация, консистентность ответов

---

### Фаза 5: VS Code Plugin (Q2 2026)
```
┌─────────────────────────────────────┐
│        VS Code Plugin: VDM          │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  💬 Text Input               │   │
│  │                             │   │
│  │  "Я врач из Нью-Йорка.      │   │
│  │   Что будет вирусным        │   │
│  │   через 15 лет?"            │   │
│  └─────────────┬───────────────┘   │
│                │                   │
│  ┌─────────────▼───────────────┐   │
│  │  📊 Virality Analysis        │   │
│  │                             │   │
│  │  Score: 0.78                │   │
│  │  K-factor: 1.3              │   │
│  │  Horizon: ~12 years         │   │
│  │                             │   │
│  │  Top Ideas:                 │   │
│  │  1. AI Diagnostics (0.82)   │   │
│  │  2. Gene Therapy (0.79)     │   │
│  │  3. Mental AI Coach (0.76)  │   │
│  │                             │   │
│  │  Viral Chain:               │   │
│  │  Pain → Emotion → Network   │   │
│  │  → Capital → Regulation     │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

Технологии:
- Extension Host: TypeScript + VS Code Extension API
- Backend: FastAPI (Python) на localhost или облаке
- UI: Webview Panel с React
- LLM: GigaChat API / Claude API
- Transport: WebSocket / HTTP

---

### Фаза 6: Продуктизация (Q3–Q4 2026)
- [ ] Мультиязычная поддержка (RU, EN, ZH, AR)
- [ ] Интеграция в JetBrains IDE (IntelliJ, PyCharm)
- [ ] API для корпоративных клиентов
- [ ] SaaS-платформа с dashboard
- [ ] Обучение на feedback пользователей (RLHF)
- [ ] Поддержка кастомных источников данных
- [ ] Автообновление AIM-аватаров авторов

---

## Команда разработки

| Роль | Задачи |
|------|--------|
| **Парсинг-специалист** | Сбор данных из 12+ источников, очистка, schema mapping |
| **DS/ML-инженер** | Feature engineering, обучение ансамбля, RAG fine-tuning |
| **Вирусный маркетолог** | Валидация 10 критериев, бизнес-применимость метрик |

### С чего начать команде:
1. Запустить `python dataset_generator.py` → изучить структуру данных
2. Прочитать `analysis.md` → понять план обучения RAG
3. Запустить `python training_pipeline.py` → увидеть пайплайн в действии
4. Определить 2–3 реальных источника для первого парсинга (рекомендуем OpenAlex)
5. Разметить 200–300 пар (запрос, документ) для первого retriever

---

*VDM — это не просто инструмент анализа. Это Future Virality Prediction Engine: система, позволяющая заглянуть в мышление экспертов будущего через структурный анализ настоящего.*
