"""Вспомогательные функции безопасного ввода."""


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число."""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число.")


def input_nonempty(prompt: str) -> str:
    """Запросить непустую строку."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Ошибка: значение не должно быть пустым.")
