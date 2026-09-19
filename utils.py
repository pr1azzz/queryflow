"""Вспомогательные функции безопасного ввода и консоли."""

from __future__ import annotations

import sys


def configure_console() -> None:
    """Настроить UTF-8 для stdout/stderr/stdin в Windows-терминале.

    Без этого кириллица в Cursor/PowerShell может отображаться «кракозябрами»
    или ломать ввод при кодовой странице CP1251.
    """
    for stream_name in ("stdout", "stderr", "stdin"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except Exception:
            pass


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


def input_choice(prompt: str) -> str:
    """Запросить пункт меню: пустой ввод — просто повторить меню."""
    return input(prompt).strip()
