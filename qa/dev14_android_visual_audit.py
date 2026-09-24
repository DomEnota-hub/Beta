#!/usr/bin/env python3
"""Read-only visual evidence sweep for the dev14 user interface."""

import atexit
import base64
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET


PACKAGE = "ru.railbrake.calculator"
OUT = os.environ.get("QA_OUT", "qa-visual-evidence")
os.makedirs(OUT, exist_ok=True)


def adb(*args):
    return subprocess.check_output(["adb", *args])


def dump_tree():
    diagnostic = b""
    data = b""
    for _ in range(8):
        dump = subprocess.run(
            ["adb", "shell", "uiautomator", "dump", "--compressed", "/sdcard/qa-window.xml"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        diagnostic = dump.stdout
        if dump.returncode == 0:
            data = adb("exec-out", "cat", "/sdcard/qa-window.xml")
            if b"</hierarchy>" in data:
                break
        time.sleep(0.75)
    end = data.find(b"</hierarchy>")
    if end < 0:
        with open(os.path.join(OUT, "ui-dump-error.txt"), "ab") as output:
            output.write(diagnostic + b"\n")
        raise AssertionError("uiautomator did not return a hierarchy document")
    document = data[: end + len(b"</hierarchy>")]
    return document, ET.fromstring(document)


def node_text(node):
    return node.get("text") or node.get("content-desc") or ""


def labels(root):
    return [node_text(node) for node in root.iter("node") if node_text(node)]


def dismiss_system_dialog(root):
    current = labels(root)
    if any(label.endswith("isn't responding") for label in current) and "Wait" in current:
        tap("Wait", handle_dialog=False)
        time.sleep(3)
        return True
    return False


def wait_for(value, timeout=55):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        _, root = dump_tree()
        if dismiss_system_dialog(root):
            continue
        if value in labels(root):
            return root
        time.sleep(0.5)
    raise AssertionError(f"Missing UI text: {value}")


def clickable_node(root, value):
    parents = {child: parent for parent in root.iter() for child in parent}
    node = next((item for item in root.iter("node") if node_text(item) == value), None)
    if node is None:
        return None
    while node.get("clickable") != "true" and node in parents:
        node = parents[node]
    return node if node.get("clickable") == "true" else None


def tap(value, handle_dialog=True):
    for _ in range(5):
        _, root = dump_tree()
        if handle_dialog and dismiss_system_dialog(root):
            continue
        node = clickable_node(root, value)
        if node is None:
            raise AssertionError(f"Missing or non-clickable tap target: {value}")
        nums = [int(number) for number in re.findall(r"\d+", node.get("bounds", ""))]
        adb("shell", "input", "tap", str((nums[0] + nums[2]) // 2), str((nums[1] + nums[3]) // 2))
        time.sleep(0.7)
        return
    raise AssertionError(f"System dialog repeatedly blocked tap target: {value}")


def scrollable_bounds(root, anchor=None):
    parents = {child: parent for parent in root.iter() for child in parent}
    if anchor is not None:
        candidates = [item for item in root.iter("node") if node_text(item) == anchor]
        for candidate in candidates:
            node = candidate
            while node.get("scrollable") != "true" and node in parents:
                node = parents[node]
            if node.get("scrollable") == "true":
                return [int(number) for number in re.findall(r"\d+", node.get("bounds", ""))]
    scrollables = [
        item for item in root.iter("node")
        if item.get("scrollable") == "true" and item.get("bounds")
    ]
    if not scrollables:
        raise AssertionError("No scrollable container on the current screen")
    node = max(
        scrollables,
        key=lambda item: (
            lambda nums: (nums[2] - nums[0]) * (nums[3] - nums[1])
        )([int(number) for number in re.findall(r"\d+", item.get("bounds", ""))]),
    )
    return [int(number) for number in re.findall(r"\d+", node.get("bounds", ""))]


def scroll_up_until_visible(target, anchor=None, max_swipes=8):
    for _ in range(max_swipes + 1):
        _, root = dump_tree()
        if dismiss_system_dialog(root):
            continue
        if target in labels(root):
            return root
        nums = scrollable_bounds(root, anchor)
        x = (nums[0] + nums[2]) // 2
        height = nums[3] - nums[1]
        adb(
            "shell", "input", "swipe",
            str(x), str(nums[3] - height // 6),
            str(x), str(nums[1] + height // 6),
            "450",
        )
        time.sleep(0.8)
    raise AssertionError(f"Missing UI text after scrolling: {target}")


def swipe_left_until_visible(anchor, target, max_swipes=4):
    for _ in range(max_swipes + 1):
        _, root = dump_tree()
        if target in labels(root):
            return root
        nums = scrollable_bounds(root, anchor)
        y = (nums[1] + nums[3]) // 2
        width = nums[2] - nums[0]
        adb(
            "shell", "input", "swipe",
            str(nums[2] - width // 6), str(y),
            str(nums[0] + width // 6), str(y),
            "450",
        )
        time.sleep(0.8)
    raise AssertionError(f"Missing UI text after horizontal scrolling: {target}")


def open_screen(title):
    tap("☰")
    wait_for("Главная")
    _, root = dump_tree()
    if title not in labels(root):
        scroll_up_until_visible(title)
    tap(title)


def input_ascii(field_label, value):
    scroll_up_until_visible(field_label)
    tap(field_label)
    adb("shell", "input", "text", value)
    adb("shell", "input", "keyevent", "4")
    time.sleep(0.7)


def capture(name):
    document, root = dump_tree()
    with open(os.path.join(OUT, f"{name}.xml"), "wb") as output:
        output.write(document)
    with open(os.path.join(OUT, f"{name}.txt"), "w", encoding="utf-8") as output:
        output.write("\n".join(labels(root)))
    with open(os.path.join(OUT, f"{name}.png"), "wb") as output:
        subprocess.run(["adb", "exec-out", "screencap", "-p"], check=True, stdout=output)
    with open(os.path.join(OUT, "manifest.tsv"), "a", encoding="utf-8") as output:
        output.write(f"{name}\t{len(labels(root))}\n")


def write_appearance_preferences(theme, palette):
    xml = (
        '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>\n'
        "<map>\n"
        f'    <string name="accent_palette">{palette}</string>\n'
        f'    <string name="theme_mode">{theme}</string>\n'
        "</map>\n"
    )
    encoded = base64.b64encode(xml.encode("utf-8")).decode("ascii")
    command = (
        "mkdir -p shared_prefs && "
        f"echo {encoded} | base64 -d > shared_prefs/calculation_inputs.xml"
    )
    subprocess.run(["adb", "shell", "run-as", PACKAGE, "sh", "-c", command], check=True)


def restart_app(font_scale, theme="LIGHT", palette="BLUE"):
    adb("shell", "settings", "put", "system", "font_scale", font_scale)
    adb("shell", "am", "force-stop", PACKAGE)
    write_appearance_preferences(theme, palette)
    adb("shell", "am", "start", "-W", "-n", LAUNCH_ACTIVITY)
    wait_for("Железнодорожный помощник")


apk = os.environ["APK"]
subprocess.run(["adb", "install", "-r", apk], check=True)
subprocess.run(["adb", "shell", "pm", "clear", PACKAGE], check=True)

font_scale_value = adb("shell", "settings", "get", "system", "font_scale").decode().strip()
original_font_scale = font_scale_value if font_scale_value not in {"", "null"} else "1.0"
atexit.register(
    lambda: subprocess.run(
        ["adb", "shell", "settings", "put", "system", "font_scale", original_font_scale],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
)

resolved = adb("shell", "cmd", "package", "resolve-activity", "--brief", PACKAGE).decode().strip()
LAUNCH_ACTIVITY = next(
    (
        line.strip()
        for line in reversed(resolved.splitlines())
        if re.fullmatch(r"[A-Za-z0-9_.]+/[A-Za-z0-9_.$]+", line.strip())
    ),
    "",
)
if not LAUNCH_ACTIVITY:
    raise AssertionError(f"Unable to resolve launch activity: {resolved}")

adb("logcat", "-c")

# Ten theme/palette combinations on the stable home surface.
for theme in ("LIGHT", "DARK"):
    for palette in ("BLUE", "AMBER", "GREEN", "YELLOW", "PURPLE"):
        restart_app("1.0", theme, palette)
        capture(f"theme-{theme.lower()}-{palette.lower()}-home")

# Main route inventory and explicit empty states at 100%.
restart_app("1.0", "LIGHT", "BLUE")
capture("font100-light-home")
tap("☰")
wait_for("Палитра")
capture("font100-light-drawer")
tap("Главная")

open_screen("Диагностика")
wait_for("Диагностика ВЛ80С")
capture("font100-light-diagnostics")
input_ascii("Симптом или аппарат", "zzzzzz")
wait_for("Ничего не найдено")
capture("font100-light-diagnostics-empty")

open_screen("Локомотивы / атлас")
wait_for("Выберите серию и тип материала")
capture("font100-light-atlas-picker")
tap("Оборудование")
wait_for("Техническая база ВЛ80С")
capture("font100-light-atlas-equipment")
scroll_up_until_visible("Главный выключатель", anchor="Техническая база ВЛ80С")
tap("Главный выключатель")
wait_for("ВЛ80С / Оборудование")
capture("font100-light-atlas-long-detail")

open_screen("Приёмка")
wait_for("Полный осмотр")
capture("font100-light-acceptance")
tap("Полный осмотр")
wait_for("Начать снаружи")
tap("Начать снаружи")
wait_for("Шаг 1 из 81")
scroll_up_until_visible("Статус: Не проверено", anchor="Шаг 1 из 81")
swipe_left_until_visible("Не проверено", "Не применяется")
tap("Не применяется")
wait_for("Статус: Не применяется")
capture("font100-light-acceptance-not-applicable")

open_screen("База знаний")
wait_for("Поиск по базе знаний")
capture("font100-light-knowledge")
input_ascii("Поиск по базе знаний", "zzzzzz")
wait_for("Ничего не найдено")
capture("font100-light-knowledge-empty")

open_screen("Охрана труда")
wait_for("Поиск по охране труда")
capture("font100-light-safety")
input_ascii("Поиск по охране труда", "zzzzzz")
wait_for("Ничего не найдено")
capture("font100-light-safety-empty")

open_screen("Первая помощь")
wait_for("Оказание первой помощи")
capture("font100-light-first-aid")
input_ascii("Найти по симптому или действию", "zzzzzz")
wait_for("Ничего не найдено")
capture("font100-light-first-aid-empty")

open_screen("Расчёты")
wait_for("Инструменты тормозных расчётов вынесены из главной страницы")
capture("font100-light-calculations")
tap("По массе")
wait_for("Готовые масса и количество осей")
capture("font100-light-mass-calculation")

open_screen("История")
wait_for("История пока пуста. После первого расчёта здесь появится запись.")
capture("font100-light-history-empty")

open_screen("Палитра")
wait_for("Тема")
capture("font100-light-settings")

# Representative dark screens beyond the palette matrix.
restart_app("1.0", "DARK", "BLUE")
for title, ready, name in (
    ("Диагностика", "Диагностика ВЛ80С", "font100-dark-diagnostics"),
    ("Приёмка", "Полный осмотр", "font100-dark-acceptance"),
    ("База знаний", "Поиск по базе знаний", "font100-dark-knowledge"),
    ("Охрана труда", "Поиск по охране труда", "font100-dark-safety"),
    ("Первая помощь", "Оказание первой помощи", "font100-dark-first-aid"),
    ("Локомотивы / атлас", "Выберите серию и тип материала", "font100-dark-atlas"),
):
    open_screen(title)
    wait_for(ready)
    capture(name)

# Large-font route inventory. The critical deep flows are covered by the smoke run.
restart_app("1.3", "LIGHT", "BLUE")
capture("font130-light-home")
for title, ready, name in (
    ("Диагностика", "Диагностика ВЛ80С", "font130-light-diagnostics"),
    ("Приёмка", "Полный осмотр", "font130-light-acceptance"),
    ("База знаний", "Поиск по базе знаний", "font130-light-knowledge"),
    ("Охрана труда", "Поиск по охране труда", "font130-light-safety"),
    ("Первая помощь", "Оказание первой помощи", "font130-light-first-aid"),
    ("Расчёты", "Инструменты тормозных расчётов вынесены из главной страницы", "font130-light-calculations"),
    ("История", "История расчётов", "font130-light-history"),
    ("Палитра", "Тема", "font130-light-settings"),
    ("Локомотивы / атлас", "Выберите серию и тип материала", "font130-light-atlas"),
):
    open_screen(title)
    wait_for(ready)
    capture(name)

log = adb("logcat", "-d").decode("utf-8", "replace")
with open(os.path.join(OUT, "logcat.txt"), "w", encoding="utf-8") as output:
    output.write(log)
if "FATAL EXCEPTION" in log:
    raise AssertionError("Android crash in logcat")

print("PASS dev14 full read-only visual audit evidence sweep")
