import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.dependencies import get_pool

router = APIRouter()

REQUIRED_COLUMNS = {"ФИО", "Оценка", "Номер группы", "Дата"}
VALID_GRADES = {1, 2, 3, 4, 5}


def _decode(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise HTTPException(status_code=400, detail="Cannot decode file: use UTF-8 or Windows-1251")


@router.post("/upload-grades")
async def upload_grades(file: UploadFile = File(...), pool=Depends(get_pool)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    content = await file.read()
    text = _decode(content)

    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames or [])):
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {', '.join(sorted(missing))}",
        )

    rows = []
    for line_no, row in enumerate(reader, start=2):
        full_name = (row.get("ФИО") or "").strip()
        group_number = (row.get("Номер группы") or "").strip()
        grade_raw = (row.get("Оценка") or "").strip()
        date_raw = (row.get("Дата") or "").strip()

        if not full_name:
            raise HTTPException(status_code=422, detail=f"Row {line_no}: ФИО is empty")
        if not group_number:
            raise HTTPException(status_code=422, detail=f"Row {line_no}: Номер группы is empty")

        try:
            grade = int(grade_raw)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Row {line_no}: grade must be an integer, got '{grade_raw}'",
            )

        if grade not in VALID_GRADES:
            raise HTTPException(
                status_code=422,
                detail=f"Row {line_no}: grade must be between 1 and 5, got {grade}",
            )

        try:
            grade_date = datetime.strptime(date_raw, "%d.%m.%Y").date()
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Row {line_no}: invalid date format '{date_raw}', expected DD.MM.YYYY",
            )

        rows.append((full_name, group_number, grade, grade_date))

    if not rows:
        raise HTTPException(status_code=422, detail="CSV file contains no data rows")

    unique_names = list({r[0] for r in rows})

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("DELETE FROM grades")
            await conn.execute("DELETE FROM students")

            await conn.executemany(
                "INSERT INTO students (full_name) VALUES ($1) ON CONFLICT (full_name) DO NOTHING",
                [(name,) for name in unique_names],
            )

            await conn.executemany(
                """
                INSERT INTO grades (student_id, group_number, grade, grade_date)
                SELECT s.id, $2, $3, $4
                FROM students s
                WHERE s.full_name = $1
                """,
                rows,
            )

    return {
        "status": "ok",
        "records_loaded": len(rows),
        "students": len(unique_names),
    }
