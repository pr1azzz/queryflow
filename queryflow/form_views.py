"""Общая транзакционная обработка валидной ModelForm."""

from django.db import DatabaseError, IntegrityError, transaction
from django.shortcuts import redirect, render


def form_response(request, form, title):
    status = 200
    if request.method == "POST":
        status = 400
        if form.is_valid():
            try:
                with transaction.atomic():
                    obj = form.save()
            except IntegrityError:
                form.add_error(None, "Запись конфликтует с существующими "
                               "данными. Проверьте значения и повторите.")
            except DatabaseError:
                form.add_error(None, "Не удалось сохранить данные. "
                               "Повторите попытку позже.")
                status = 503
            else:
                return redirect(obj)
    return render(request, "form.html", {"form": form, "heading": title},
                  status=status)
