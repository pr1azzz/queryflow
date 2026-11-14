"""ПР9: проверка параметров до формирования ORM-запроса."""

from datetime import date

from questions.queries import SORTS
from questions.models import Question


def parse_parameters(params):
    data = {k: params.get(k, "").strip() for k in
            ("q", "related", "category", "author", "since", "date",
             "sort", "status")}
    if len(data["q"]) > 200 or len(data["related"]) > 120:
        raise ValueError("Слишком длинная поисковая строка.")
    for key in ("category", "author"):
        if data[key]:
            data[key] = int(data[key])
            if not 0 < data[key] < 2 ** 63:
                raise ValueError("Некорректный идентификатор.")
    for key in ("date", "since"):
        if data[key]:
            parsed = date.fromisoformat(data[key])
            if parsed.isoformat() != data[key]:
                raise ValueError("Нужен формат ГГГГ-ММ-ДД.")
            data[key] = parsed
    if data["sort"] not in ("", *SORTS):
        raise ValueError("Неизвестная сортировка.")
    if data["status"] not in ("", *Question.Status.values):
        raise ValueError("Неизвестный статус.")
    data["page"] = int(params.get("page", "1"))
    if not 1 <= data["page"] <= 1000000:
        raise ValueError("Некорректная страница.")
    return data
