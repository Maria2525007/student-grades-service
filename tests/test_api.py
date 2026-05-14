import io
import csv

import pytest

from app.main import app
from app.dependencies import get_pool
from tests.conftest import override_pool


def make_csv(*rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["Дата", "Номер группы", "ФИО", "Оценка"], delimiter=";")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def csv_file(content, filename="grades.csv"):
    return {"file": (filename, io.BytesIO(content), "text/csv")}


@pytest.mark.asyncio
async def test_upload_valid_csv(client):
    app.dependency_overrides[get_pool] = override_pool()
    data = make_csv(
        {"Дата": "01.09.2024", "Номер группы": "ИВТ-21", "ФИО": "Иванов Иван", "Оценка": 4},
        {"Дата": "01.09.2024", "Номер группы": "ИВТ-21", "ФИО": "Иванов Иван", "Оценка": 2},
        {"Дата": "01.09.2024", "Номер группы": "ИВТ-21", "ФИО": "Петров Пётр", "Оценка": 3},
    )
    resp = await client.post("/upload-grades", files=csv_file(data))
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["records_loaded"] == 3
    assert body["students"] == 2
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_invalid_extension(client):
    app.dependency_overrides[get_pool] = override_pool()
    resp = await client.post(
        "/upload-grades",
        files={"file": ("grades.txt", io.BytesIO(b"data"), "text/plain")},
    )
    assert resp.status_code == 400
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_missing_columns(client):
    app.dependency_overrides[get_pool] = override_pool()
    data = "ФИО;Оценка\nИванов Иван;4\n".encode("utf-8")
    resp = await client.post("/upload-grades", files=csv_file(data))
    assert resp.status_code == 422
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_invalid_grade_value(client):
    app.dependency_overrides[get_pool] = override_pool()
    data = make_csv({"Дата": "01.09.2024", "Номер группы": "ИВТ-21", "ФИО": "Иванов Иван", "Оценка": 6})
    resp = await client.post("/upload-grades", files=csv_file(data))
    assert resp.status_code == 422
    assert "grade" in resp.json()["detail"]
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_non_integer_grade(client):
    app.dependency_overrides[get_pool] = override_pool()
    data = "Дата;Номер группы;ФИО;Оценка\n01.09.2024;ИВТ-21;Иванов Иван;abc\n".encode("utf-8")
    resp = await client.post("/upload-grades", files=csv_file(data))
    assert resp.status_code == 422
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_empty_csv(client):
    app.dependency_overrides[get_pool] = override_pool()
    data = "Дата;Номер группы;ФИО;Оценка\n".encode("utf-8")
    resp = await client.post("/upload-grades", files=csv_file(data))
    assert resp.status_code == 422
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_empty_full_name(client):
    app.dependency_overrides[get_pool] = override_pool()
    data = make_csv({"Дата": "01.09.2024", "Номер группы": "ИВТ-21", "ФИО": "", "Оценка": 3})
    resp = await client.post("/upload-grades", files=csv_file(data))
    assert resp.status_code == 422
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_invalid_date(client):
    app.dependency_overrides[get_pool] = override_pool()
    data = "Дата;Номер группы;ФИО;Оценка\n2024-09-01;ИВТ-21;Иванов Иван;4\n".encode("utf-8")
    resp = await client.post("/upload-grades", files=csv_file(data))
    assert resp.status_code == 422
    assert "date" in resp.json()["detail"]
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_more_than_3_twos_returns_list(client):
    fake_rows = [
        {"full_name": "Иванов Иван", "count_twos": 5},
        {"full_name": "Сидоров Сидор", "count_twos": 4},
    ]
    app.dependency_overrides[get_pool] = override_pool(fetch_result=fake_rows)
    resp = await client.get("/students/more-than-3-twos")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    assert body[0]["full_name"] == "Иванов Иван"
    assert body[0]["count_twos"] == 5
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_more_than_3_twos_empty(client):
    app.dependency_overrides[get_pool] = override_pool(fetch_result=[])
    resp = await client.get("/students/more-than-3-twos")
    assert resp.status_code == 200
    assert resp.json() == []
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_less_than_5_twos_returns_list(client):
    fake_rows = [
        {"full_name": "Петров Пётр", "count_twos": 2},
    ]
    app.dependency_overrides[get_pool] = override_pool(fetch_result=fake_rows)
    resp = await client.get("/students/less-than-5-twos")
    assert resp.status_code == 200
    body = resp.json()
    assert body[0]["full_name"] == "Петров Пётр"
    assert body[0]["count_twos"] == 2
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_less_than_5_twos_empty(client):
    app.dependency_overrides[get_pool] = override_pool(fetch_result=[])
    resp = await client.get("/students/less-than-5-twos")
    assert resp.status_code == 200
    assert resp.json() == []
    app.dependency_overrides.clear()
