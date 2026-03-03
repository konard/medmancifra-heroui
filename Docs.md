# Тестирование Deno + Supabase (Well Repairs)

Инструкция по локальному запуску и тестированию Edge Functions для модуля управления ремонтами скважин.

---

## Предварительные требования

| Инструмент | Версия | Ссылка |
|---|---|---|
| Deno | v2.x | https://deno.com/manual/getting_started/installation |
| Supabase CLI | latest | https://supabase.com/docs/guides/cli |
| Docker Desktop | latest | https://www.docker.com/products/docker-desktop (нужен для локального Supabase) |

---

## 1. Установка инструментов

```bash
# macOS / Linux (Deno)
curl -fsSL https://deno.land/install.sh | sh

# macOS (Supabase CLI через Homebrew)
brew install supabase/tap/supabase

# или через npm
npm install -g supabase
```

---

## 2. Запуск локального Supabase

```bash
# Инициализировать проект Supabase (если ещё не сделано)
supabase init

# Запустить локальный стек (PostgreSQL + API + Studio)
supabase start
```

После старта в терминале появятся:
- **API URL**: `http://127.0.0.1:54321`
- **Studio URL**: `http://127.0.0.1:54323`
- **anon key** и **service_role key**

---

## 3. Применение миграции (схема БД + начальные данные)

```bash
supabase db push
```

Или вручную через SQL-редактор в Supabase Studio — скопируйте содержимое файла:

```
supabase/migrations/20240101000000_well_repairs_schema.sql
```

Файл создаёт таблицы `fields`, `repair_types`, `wells`, `repairs` и заполняет их тестовыми данными (месторождения, типы ремонтов, скважины, ремонты).

---

## 4. Локальный запуск Edge Functions через Deno

Supabase CLI запускает все функции локально с помощью Deno:

```bash
supabase functions serve
```

По умолчанию функции доступны на `http://127.0.0.1:54321/functions/v1/`.

---

## 5. Тестирование API вручную

### Получить список месторождений

```bash
curl http://127.0.0.1:54321/functions/v1/fields \
  -H "Authorization: Bearer <anon_key>"
```

### Получить список типов ремонтов

```bash
curl http://127.0.0.1:54321/functions/v1/repair-types \
  -H "Authorization: Bearer <anon_key>"
```

### Получить все скважины

```bash
curl http://127.0.0.1:54321/functions/v1/wells \
  -H "Authorization: Bearer <anon_key>"
```

### Обновить скважину

```bash
curl -X PUT http://127.0.0.1:54321/functions/v1/wells/<well_id> \
  -H "Authorization: Bearer <anon_key>" \
  -H "Content-Type: application/json" \
  -d '{"cluster": "К-999"}'
```

### Получить ремонты конкретной скважины

```bash
curl "http://127.0.0.1:54321/functions/v1/repairs?well_id=w-1" \
  -H "Authorization: Bearer <anon_key>"
```

### Обновить ремонт (закрыть — указать дату окончания)

```bash
curl -X PUT http://127.0.0.1:54321/functions/v1/repairs/<repair_id> \
  -H "Authorization: Bearer <anon_key>" \
  -H "Content-Type: application/json" \
  -d '{"end_date": "2025-04-01"}'
```

> Замените `<anon_key>` на значение из вывода `supabase start`.

---

## 6. Деплой на Supabase Cloud (через GitHub Actions)

В workflow файле `.github/workflows/deploy-supabase-functions.yml` настроен автоматический деплой при пуше в `main` (если изменены файлы в `supabase/functions/`).

Для активации добавьте в настройках репозитория (Settings → Secrets and variables → Actions) два секрета:

| Secret | Где взять |
|---|---|
| `SUPABASE_ACCESS_TOKEN` | https://app.supabase.com/account/tokens |
| `SUPABASE_PROJECT_ID` | Supabase Dashboard → Settings → General → Reference ID |

Ручной запуск деплоя:

```bash
export SUPABASE_ACCESS_TOKEN=<ваш_токен>
supabase functions deploy wells       --project-ref <project_id>
supabase functions deploy repairs     --project-ref <project_id>
supabase functions deploy fields      --project-ref <project_id>
supabase functions deploy repair-types --project-ref <project_id>
```

После деплоя функции доступны по URL вида:

```
https://<project_id>.supabase.co/functions/v1/<function_name>
```

---

## 7. Структура файлов

```
supabase/
├── functions/
│   ├── wells/index.ts          # GET /wells, PUT /wells/:id
│   ├── repairs/index.ts        # GET /repairs[?well_id=...], PUT /repairs/:id
│   ├── fields/index.ts         # GET /fields
│   └── repair-types/index.ts   # GET /repair-types
└── migrations/
    └── 20240101000000_well_repairs_schema.sql  # DDL + seed data
```

---

## 8. Остановка локального окружения

```bash
supabase stop
```
