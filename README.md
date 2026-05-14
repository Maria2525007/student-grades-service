# Student Grades Service

REST-сервис на FastAPI для загрузки и анализа успеваемости студентов.

## Стек

- **FastAPI** — веб-фреймворк
- **asyncpg** — драйвер PostgreSQL (чистый SQL, без ORM)
- **PostgreSQL 16** — база данных
- **Docker / Docker Compose** — контейнеризация
- **pytest + httpx** — тесты

## Структура CSV-файла

Разделитель — **точка с запятой** (`;`). Кодировка UTF-8 или Windows-1251.

| Колонка        | Тип     | Описание                  |
|----------------|---------|---------------------------|
| `Дата`         | string  | Дата в формате DD.MM.YYYY |
| `Номер группы` | string  | Номер учебной группы      |
| `ФИО`          | string  | ФИО студента              |
| `Оценка`       | integer | Оценка от **1** до **5**  |

Пример:
```
Дата;Номер группы;ФИО;Оценка
01.09.2024;ИВТ-21;Иванов Иван;4
01.09.2024;ИВТ-21;Иванов Иван;2
01.09.2024;ИВТ-21;Петров Пётр;3
```

## Запуск через Docker Compose (рекомендуется)

```bash
docker compose up --build
```

Сервис будет доступен на `http://localhost:8000`.  
Swagger UI: `http://localhost:8000/docs`

Миграция применяется автоматически при первом запуске БД через `docker-entrypoint-initdb.d`.

## Запуск локально

### 1. Создать виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Настроить переменную окружения

```bash
cp .env.example .env
```

### 3. Применить миграции

```bash
python migrate.py
```

### 4. Запустить сервис

```bash
uvicorn app.main:app --reload
```

## API

### `POST /upload-grades`

Загрузка CSV-файла. Каждый вызов **полностью заменяет** данные в БД.

```bash
curl -X POST http://localhost:8000/upload-grades \
     -F "file=@grades.csv"
```

Ответ:
```json
{"status": "ok", "records_loaded": 2000, "students": 40}
```

### `GET /students/more-than-3-twos`

Студенты, у которых оценка **2** встречается **больше 3 раз**.

```bash
curl http://localhost:8000/students/more-than-3-twos
```

Ответ:
```json
[{"full_name": "Иванов Иван", "count_twos": 5}]
```

### `GET /students/less-than-5-twos`

Студенты, у которых оценка **2** встречается **меньше 5 раз**.

```bash
curl http://localhost:8000/students/less-than-5-twos
```

Ответ:
```json
[{"full_name": "Петров Пётр", "count_twos": 2}]
```

## Запуск тестов

```bash
pytest -v
```

## Схема базы данных

```sql
CREATE TABLE students (
    id        SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE grades (
    id           SERIAL PRIMARY KEY,
    student_id   INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    group_number VARCHAR(50) NOT NULL,
    grade_date   DATE NOT NULL,
    grade        SMALLINT NOT NULL CHECK (grade BETWEEN 1 AND 5),
    uploaded_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
