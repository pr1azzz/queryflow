"""ORM-запросы интерфейса: реальные списки, поиск и статистика ПР9."""

from django.db.models import BooleanField, Case, Count, F, Q, When

from answers.models import Answer
from categories.models import Category
from participants.models import User
from questions.models import Question

SORTS = {
    "newest": ("-created_on", "-pk"),
    "oldest": ("created_on", "pk"),
    "category": ("category__name", "-created_on", "-pk"),
    "author": ("author__name", "-created_on", "-pk"),
}


def question_rows(queryset=None):
    queryset = Question.objects.all() if queryset is None else queryset
    return queryset.annotate(
        category_name=F("category__name"), author_name=F("author__name"),
        answers_count=Count("answers"),
        is_closed=Case(When(status=Question.Status.CLOSED, then=True),
                       default=False, output_field=BooleanField()),
    ).values("id", "text", "category_id", "author_id", "is_closed",
             "created_on", "category_name", "author_name", "answers_count",
             "status", "text_length")


def answer_rows(queryset=None):
    queryset = Answer.objects.all() if queryset is None else queryset
    return queryset.annotate(
        author_name=F("author__name"), question_text=F("question__text"),
        category_name=F("question__category__name"),
    ).values("id", "text", "created_on", "question_id", "author_name",
             "question_text", "category_name")


def filtered_questions(data, queryset=None):
    qs = Question.objects.all() if queryset is None else queryset
    if data.get("q"):
        qs = qs.filter(text__icontains=data["q"])
    if data.get("category"):
        qs = qs.filter(category_id=data["category"])
    if data.get("author"):
        qs = qs.filter(author_id=data["author"])
    if data.get("since"):
        qs = qs.filter(created_on__gte=data["since"])
    if data.get("date"):
        qs = qs.for_date(data["date"])
    if data.get("status"):
        qs = qs.filter(status=data["status"])
    if data.get("related"):
        qs = qs.filter(Q(category__name__icontains=data["related"]) |
                       Q(author__name__icontains=data["related"]))
    return qs.order_by(*SORTS[data.get("sort") or "newest"])


def statistics_context(minimum):
    return {
        "question_summary": Question.objects.aggregate(
            total=Count("pk"),
            open_count=Count("pk", filter=Q(status=Question.Status.OPEN)),
            closed_count=Count("pk", filter=Q(status=Question.Status.CLOSED)),
            withdrawn_count=Count("pk",
                                  filter=Q(status=Question.Status.WITHDRAWN))),
        "answer_summary": Answer.objects.aggregate(
            total=Count("pk"), authors_count=Count("author", distinct=True)),
        "category_statistics": Category.objects.annotate(
            questions_count=Count("questions")
        ).filter(questions_count__gte=minimum).order_by(
            "-questions_count", "pk"),
        "author_statistics": User.objects.annotate(
            answers_count=Count("answers")).order_by("-answers_count", "pk"),
        "users": User.objects.all(), "minimum": minimum,
    }
