"""Класс Answer и функции работы с коллекцией ответов."""

from __future__ import annotations

from datetime import date

from .questions import Question
from .users import User


class Answer:
    """Ответ на вопрос."""

    def __init__(
        self,
        answer_id: int,
        text: str,
        question: Question,
        author: User,
        created_on: date | str | None = None,
    ) -> None:
        """Создать объект ответа.

        Хранит ссылки на объекты Question и User.
        """
        self.id = answer_id
        self.text = text.strip()
        self.question = question
        self.author = author
        if created_on is None:
            self.created_on = date.today().isoformat()
        elif isinstance(created_on, date):
            self.created_on = created_on.isoformat()
        else:
            self.created_on = str(created_on)

    def __str__(self) -> str:
        """Вернуть строковое представление ответа."""
        return (
            f"[{self.created_on}] {self.author.name}: {self.text}"
        )


def add_answer(
    answers: list[Answer],
    question: Question,
    text: str,
    author: User,
    created_on: date | None = None,
) -> Answer | None:
    """Создать объект Answer и добавить его в коллекцию.

    Возвращает None, если вопрос закрыт.
    """
    if question.is_closed:
        return None
    new_id = max((item.id for item in answers), default=0) + 1
    answer = Answer(
        answer_id=new_id,
        text=text,
        question=question,
        author=author,
        created_on=created_on,
    )
    answers.append(answer)
    return answer


def get_answers_for_question(
    answers: list[Answer],
    question_id: int,
) -> list[Answer]:
    """Вернуть ответы для указанного вопроса."""
    return [
        item for item in answers
        if item.question.id == question_id
    ]


def count_answers(answers: list[Answer], question_id: int) -> int:
    """Подсчитать число ответов на вопрос."""
    return len(get_answers_for_question(answers, question_id))


def remove_answer(answers: list[Answer], answer_id: int) -> bool:
    """Удалить ответ по идентификатору."""
    for index, item in enumerate(answers):
        if item.id == answer_id:
            del answers[index]
            return True
    return False
