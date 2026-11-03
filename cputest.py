
#!/usr/bin/env python3

import curses
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

# ==========================================
# THERMALBENCH CONFIGURATION
# ==========================================

VERSION = "1.1"

# Максимальная температура CPU.
# None = отключить автоматическое ограничение.
TEMP_LIMIT = None

# Рекомендованная продолжительность теста.
DEFAULT_DURATION = 300

# Максимальное время ручного теста.
MAX_DURATION = 3600

BASE_DIR = Path(__file__).resolve().parent


# ==========================================
# SYSTEM FUNCTIONS
# ==========================================

def get_sensors():
    try:
        result = subprocess.run(
            ["sensors"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return result.stdout

        return result.stderr

    except Exception as e:
        return f"Ошибка sensors: {e}"


def get_max_temperature(output):
    temps = re.findall(
        r"^\s*(?:Package id \d+|Core \d+):\s*"
        r"([+-]?\d+(?:\.\d+)?)\s*°C",
        output,
        re.MULTILINE
    )

    return max(map(float, temps)) if temps else None


def save_snapshot(filename):
    output = get_sensors()

    path = BASE_DIR / filename
    path.write_text(output, encoding="utf-8")

    return output, path


def run_stress(workers, duration):
    if not shutil.which("stress"):
        raise RuntimeError(
            "Программа stress не установлена!\n"
            "Установи: sudo apt install stress"
        )

    return subprocess.Popen(
        [
            "stress",
            "--cpu", str(workers),
            "--timeout", str(duration)
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# ==========================================
# INTERFACE
# ==========================================

def draw(stdscr, lines, selected=0):
    stdscr.erase()

    h, w = stdscr.getmaxyx()

    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(1, 2, f"THERMALBENCH v{VERSION}")
    stdscr.attroff(curses.color_pair(1))

    stdscr.addstr(2, 2, "CPU THERMAL TESTING UTILITY")
    stdscr.addstr(3, 2, "-" * min(w - 4, 55))

    for i, line in enumerate(lines):
        y = 5 + i

        if y >= h - 2:
            break

        if i == selected:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(y, 4, line[:w - 8])
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(y, 4, line[:w - 8])

    stdscr.addstr(
        h - 2, 2,
        "UP/DOWN: выбор | ENTER: подтвердить | Q: назад"
    )

    stdscr.refresh()


def menu(stdscr, title, options):
    selected = 0

    while True:
        draw(stdscr, [title, ""] + options, selected + 2)

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)

        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)

        elif key in (10, 13, curses.KEY_ENTER):
            return selected

        elif key in (ord("q"), ord("Q")):
            return None


def ask_number(stdscr, title, default, minimum, maximum):
    curses.echo()
    curses.curs_set(1)

    while True:
        stdscr.clear()

        stdscr.addstr(2, 2, title)
        stdscr.addstr(
            4, 2,
            f"Значение ({minimum}-{maximum}) [{default}]: "
        )

        stdscr.refresh()

        value = stdscr.getstr(4, 45, 10).decode().strip()

        if not value:
            value = str(default)

        try:
            number = int(value)

            if minimum <= number <= maximum:
                curses.noecho()
                curses.curs_set(0)
                return number

        except ValueError:
            pass

        stdscr.addstr(6, 2, "Некорректное значение!")
        stdscr.refresh()
        time.sleep(1)


# ==========================================
# STRESS TEST
# ==========================================

def run_test(stdscr, filename, workers, duration):

    try:
        process = run_stress(workers, duration)

    except Exception as e:
        stdscr.clear()
        stdscr.addstr(3, 2, str(e)[:100])
        stdscr.addstr(6, 2, "Нажми любую клавишу...")
        stdscr.refresh()
        stdscr.getch()
        return

    start = time.monotonic()
    aborted = False
    path = BASE_DIR / filename
    snapshot = None

    stdscr.timeout(1000)

    try:
        while process.poll() is None:

            elapsed = time.monotonic() - start
            remaining = max(
                0,
                duration - int(elapsed)
            )

            sensors_output = get_sensors()
            temperature = get_max_temperature(sensors_output)

            stdscr.erase()

            stdscr.addstr(1, 2, "THERMALBENCH - CPU STRESS TEST")
            stdscr.addstr(3, 2, f"Файл записи: {filename}")
            stdscr.addstr(5, 2, f"CPU workers: {workers}")
            stdscr.addstr(
                6, 2,
                f"Время: {int(elapsed)} / {duration} сек."
            )
            stdscr.addstr(
                7, 2,
                f"Осталось: {remaining} сек."
            )

            temp_text = (
                f"{temperature:.1f} °C"
                if temperature is not None
                else "Нет данных"
            )

            stdscr.addstr(9, 2, f"Температура CPU: {temp_text}")

            limit_text = (
                f"{TEMP_LIMIT} °C"
                if TEMP_LIMIT is not None
                else "OFF"
            )

            stdscr.addstr(
                11, 2,
                f"Температурный лимит: {limit_text}"
            )

            stdscr.addstr(13, 2, "Нагрузка CPU: ACTIVE")
            stdscr.addstr(15, 2, "ESC - остановить тест")

            stdscr.refresh()

            key = stdscr.getch()

            if key == 27:
                aborted = True
                break

            if (
                TEMP_LIMIT is not None
                and temperature is not None
                and temperature >= TEMP_LIMIT
            ):
                aborted = True
                break

        # ==================================
        # SNAPSHOT BEFORE STOPPING STRESS
        # ==================================

        snapshot, path = save_snapshot(filename)

    except KeyboardInterrupt:
        aborted = True

        # Даже при Ctrl+C сначала пытаемся сохранить sensors.
        snapshot, path = save_snapshot(filename)

    finally:

        # Остановка нагрузки ТОЛЬКО после снимка.
        if process.poll() is None:
            process.terminate()

        try:
            process.wait(timeout=5)

        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

        stdscr.timeout(-1)

    stdscr.clear()

    stdscr.addstr(3, 2, "ТЕСТ ЗАВЕРШЁН")
    stdscr.addstr(5, 2, f"Снимок: {path}")
    stdscr.addstr(7, 2, "Нагрузка CPU остановлена.")

    if aborted:
        stdscr.addstr(9, 2, "Тест остановлен досрочно.")

    stdscr.addstr(12, 2, "Нажми любую клавишу...")
    stdscr.refresh()
    stdscr.getch()


# ==========================================
# COMPARISON
# ==========================================

def show_comparison(stdscr):

    before_path = BASE_DIR / "before.txt"
    after_path = BASE_DIR / "after.txt"

    stdscr.clear()

    stdscr.addstr(2, 2, "THERMALBENCH - COMPARISON")

    if not before_path.exists() or not after_path.exists():

        stdscr.addstr(5, 2, "Не найдены оба файла!")
        stdscr.addstr(7, 2, "Необходимы before.txt и after.txt")

        stdscr.addstr(11, 2, "Нажми любую клавишу...")
        stdscr.refresh()
        stdscr.getch()
        return

    before = before_path.read_text(encoding="utf-8")
    after = after_path.read_text(encoding="utf-8")

    t_before = get_max_temperature(before)
    t_after = get_max_temperature(after)

    stdscr.addstr(4, 2, "BEFORE:")

    stdscr.addstr(
        5, 4,
        f"{t_before:.1f} °C"
        if t_before is not None
        else "Нет данных"
    )

    stdscr.addstr(7, 2, "AFTER:")

    stdscr.addstr(
        8, 4,
        f"{t_after:.1f} °C"
        if t_after is not None
        else "Нет данных"
    )

    if t_before is not None and t_after is not None:

        difference = t_before - t_after

        stdscr.addstr(
            11, 2,
            f"Разница: {difference:+.1f} °C"
        )

        if difference > 0:
            stdscr.addstr(13, 2, "Температура после замены ниже.")

        elif difference < 0:
            stdscr.addstr(13, 2, "Температура после замены выше.")

        else:
            stdscr.addstr(13, 2, "Температура не изменилась.")

        stdscr.addstr(15, 2, "BEFORE  " + "#" * min(int(t_before), 70))
        stdscr.addstr(16, 2, "AFTER   " + "#" * min(int(t_after), 70))

    else:
        stdscr.addstr(11, 2, "Не удалось сравнить температуры.")

    stdscr.addstr(19, 2, "Нажми любую клавишу...")
    stdscr.refresh()
    stdscr.getch()


# ==========================================
# MAIN
# ==========================================

def main(stdscr):

    curses.curs_set(0)
    curses.start_color()

    curses.init_pair(
        1,
        curses.COLOR_CYAN,
        curses.COLOR_BLACK
    )

    while True:

        choice = menu(
            stdscr,
            "ГЛАВНОЕ МЕНЮ",
            [
                "[1] Запись ДО замены термопасты",
                "[2] Запись ПОСЛЕ замены термопасты",
                "[3] Сравнение температур",
                "[4] Выход"
            ]
        )

        if choice is None or choice == 3:
            break

        if choice == 2:
            show_comparison(stdscr)
            continue

        filename = (
            "before.txt"
            if choice == 0
            else "after.txt"
        )

        test_mode = menu(
            stdscr,
            "ВЫБОР РЕЖИМА НАГРУЗКИ",
            [
                "Автоматический - все логические потоки",
                "Ручной - выбрать количество процессов"
            ]
        )

        if test_mode is None:
            continue

        max_workers = os.cpu_count() or 1

        if test_mode == 0:
            workers = max_workers

        else:
            workers = ask_number(
                stdscr,
                "Количество процессов CPU",
                max_workers,
                1,
                max_workers
            )

        time_mode = menu(
            stdscr,
            "ПРОДОЛЖИТЕЛЬНОСТЬ ТЕСТА",
            [
                f"Рекомендованное время - {DEFAULT_DURATION} секунд",
                "Ручной ввод времени"
            ]
        )

        if time_mode is None:
            continue

        if time_mode == 0:
            duration = DEFAULT_DURATION

        else:
            duration = ask_number(
                stdscr,
                "Продолжительность в секундах",
                DEFAULT_DURATION,
                10,
                MAX_DURATION
            )

        run_test(
            stdscr,
            filename,
            workers,
            duration
        )


if __name__ == "__main__":
    if not shutil.which("stress"):
        print("Установи stress: sudo apt install stress")
        raise SystemExit(1)

    curses.wrapper(main)
