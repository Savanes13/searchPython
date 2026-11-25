# CLAUDE.md

Пет-проект: API для поиска товаров в каталоге одежды. Цель — пройти путь от наивного поиска до своего полнотекстового поиска с индексом, ранжированием, фильтрами, автодополнением и исправлением опечаток. План по шагам — в `ROADMAP.md`, текущие задачи — в `TODO.md`.

## Стек

- Python ≥ 3.12, FastAPI (`fastapi[standard]`)
- PostgreSQL (БД `catalog` на localhost) через SQLAlchemy 2.x (sync, `psycopg` v3)
- Миграции — Alembic
- Зависимости в `pyproject.toml`, есть `uv.lock`

## Команды (Windows / PowerShell)

```powershell
# окружение
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .            # или: uv sync

# dev-сервер, документация на http://127.0.0.1:8000/docs
fastapi dev app/main.py

# проверить подключение к БД
python check_db.py

# миграции
alembic upgrade head
alembic revision --autogenerate -m "описание"

# загрузить каталог из CSV в БД (полностью перезаписывает таблицу products)
python -m scripts.import_products
```

Скрипты запускать из корня проекта: пути (`data/styles.csv`) и импорты `app.*` относительные к корню.

## Структура

- `app/database.py` — `DATABASE_URL`, `engine`, `SessionLocal`, `Base`
- `app/models.py` — ORM-модели (сейчас только `Product`)
- `app/main.py` — FastAPI-приложение и эндпоинты (пока заглушки)
- `migrations/` — Alembic; `env.py` берёт URL из `app.database.DATABASE_URL`, а не из `alembic.ini`
- `scripts/import_products.py` — импорт `data/styles.csv` в таблицу `products`
- `data/styles.csv` — исходный датасет (~44k строк, Fashion Product Images, англоязычные названия)
- `check_db.py`, `test_product.py` — одноразовые проверочные скрипты, не тесты

## Данные

- `id` товара берётся из CSV (`autoincrement=False`).
- Импорт пропускает битые строки и категории `Free Items`, `Home`, `Sporting Goods`.
- `brand` эвристически извлекается из названия (слова до первого «гендерного» слова — Men, Women и т. п.).
- `price` в датасете нет — генерируется детерминированно от `id` (`random.Random(product_id)`) в диапазоне по `master_category`, заканчивается на `90`.
- Значения `''` и `NA` в CSV превращаются в `None`.

## Соглашения

- Изменения схемы — только через новую Alembic-миграцию, существующие миграции не править.
- После изменения `app/models.py` — `alembic revision --autogenerate`, проверить сгенерированный файл глазами.
- Отступы в файлах сейчас разные (2 пробела в `scripts/` и `database.py`, 4 в остальных) — при правке придерживаться стиля конкретного файла.
- Комментарии, сообщения и документация — на русском.
- Поиск (токенизация, нормализация, инвертированный индекс, ранжирование) по roadmap пишется своими руками, а не через Elasticsearch / `tsvector` — не предлагать готовые движки без запроса.

## Известные моменты

- Строка подключения к БД с паролем захардкожена в `app/database.py`. Если трогаем конфиг — выносить в `.env` (он уже в `.gitignore`).
- Тестов и линтера пока нет.
- Репозиторий ещё не инициализирован как git.
