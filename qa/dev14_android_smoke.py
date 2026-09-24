#!/usr/bin/env python3
"""Fresh-tree Android smoke for the dev14 critical user paths."""
import os
import re
import subprocess
import time
import atexit
import xml.etree.ElementTree as ET

PACKAGE = "ru.railbrake.calculator"
OUT = os.environ.get("QA_OUT", "qa-evidence")
os.makedirs(OUT, exist_ok=True)
snapshot_number = 0

def adb(*args):
    return subprocess.check_output(["adb", *args])

def tree():
    global snapshot_number
    data = b""
    diagnostic = b""
    for _ in range(8):
        dump = subprocess.run(
            ["adb", "shell", "uiautomator", "dump", "--compressed", "/sdcard/qa-window.xml"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        diagnostic = dump.stdout
        if dump.returncode == 0:
            data = adb("exec-out", "cat", "/sdcard/qa-window.xml")
            if b"</hierarchy>" in data:
                break
        time.sleep(.75)
    xml_end = data.find(b"</hierarchy>")
    if xml_end < 0:
        with open(os.path.join(OUT, "ui-dump-error.txt"), "ab") as output:
            output.write(diagnostic + b"\n")
        raise AssertionError("uiautomator did not return a hierarchy document after retries")
    document = data[:xml_end + len(b"</hierarchy>")]
    snapshot_number += 1
    with open(os.path.join(OUT, f"ui-{snapshot_number:02d}.xml"), "wb") as output:
        output.write(document)
    return ET.fromstring(document)

def text(node):
    return node.get("text") or node.get("content-desc") or ""

def labels(root):
    return [text(node) for node in root.iter("node") if text(node)]

def wait_for(value, timeout=55):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        root = tree()
        current_labels = labels(root)
        if "System UI isn't responding" in current_labels and "Wait" in current_labels:
            # API 29 can show this transient dialog immediately after a cold boot.
            # It belongs to the emulator, not to the application under test.
            tap("Wait")
            time.sleep(3)
            continue
        if value in current_labels:
            return root
        time.sleep(.5)
    raise AssertionError(f"Missing UI text: {value}")

def tap(value):
    root = tree()
    parents = {child: parent for parent in root.iter() for child in parent}
    node = next((node for node in root.iter("node") if text(node) == value), None)
    if node is None:
        raise AssertionError(f"Missing tap target: {value}")
    while node.get("clickable") != "true" and node in parents:
        node = parents[node]
    if node.get("clickable") != "true":
        raise AssertionError(f"No clickable ancestor: {value}")
    nums = [int(n) for n in re.findall(r"\d+", node.get("bounds", ""))]
    adb("shell", "input", "tap", str((nums[0] + nums[2]) // 2), str((nums[1] + nums[3]) // 2))
    time.sleep(.6)

def scrollable_ancestor(root, value):
    parents = {child: parent for parent in root.iter() for child in parent}
    for candidate in (node for node in root.iter("node") if text(node) == value):
        node = candidate
        while node.get("scrollable") != "true" and node in parents:
            node = parents[node]
        if node.get("scrollable") == "true":
            return node
    raise AssertionError(f"No scrollable ancestor: {value}")

def scroll_up_until_visible(anchor, target, max_swipes=4):
    root = tree()
    node = scrollable_ancestor(root, anchor)
    nums = [int(n) for n in re.findall(r"\d+", node.get("bounds", ""))]
    x = (nums[0] + nums[2]) // 2
    height = nums[3] - nums[1]
    for _ in range(max_swipes):
        if target in labels(root):
            return root
        adb(
            "shell", "input", "swipe",
            str(x), str(nums[3] - height // 5),
            str(x), str(nums[1] + height // 5),
            "450"
        )
        time.sleep(.8)
        root = tree()
    raise AssertionError(f"Missing UI text after scrolling: {target}")

def swipe_left_in_scrollable(value):
    node = scrollable_ancestor(tree(), value)
    nums = [int(n) for n in re.findall(r"\d+", node.get("bounds", ""))]
    y = (nums[1] + nums[3]) // 2
    width = nums[2] - nums[0]
    adb(
        "shell", "input", "swipe",
        str(nums[2] - width // 5), str(y),
        str(nums[0] + width // 5), str(y),
        "450"
    )
    time.sleep(.8)

def open_screen(title):
    tap("☰")
    wait_for(title)
    time.sleep(.8)
    tap(title)

def screenshot(name):
    with open(os.path.join(OUT, f"{name}.png"), "wb") as output:
        subprocess.run(["adb", "exec-out", "screencap", "-p"], check=True, stdout=output)

apk = os.environ["APK"]
subprocess.run(["adb", "install", "-r", apk], check=True)
font_scale_value = adb("shell", "settings", "get", "system", "font_scale").decode().strip()
original_font_scale = font_scale_value if font_scale_value not in {"", "null"} else "1.0"
atexit.register(
    lambda: subprocess.run(
        ["adb", "shell", "settings", "put", "system", "font_scale", original_font_scale],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
)
adb("shell", "settings", "put", "system", "font_scale", "1.3")
adb("logcat", "-c")
adb("shell", "am", "force-stop", PACKAGE)
resolved_activity = adb("shell", "cmd", "package", "resolve-activity", "--brief", PACKAGE).decode().strip()
launch_activity = next(
    (
        line.strip()
        for line in reversed(resolved_activity.splitlines())
        if re.fullmatch(r"[A-Za-z0-9_.]+/[A-Za-z0-9_.$]+", line.strip())
    ),
    ""
)
if not launch_activity:
    raise AssertionError(f"Unable to resolve launch activity: {resolved_activity}")
adb("shell", "am", "start", "-W", "-n", launch_activity)
wait_for("Железнодорожный помощник")

open_screen("Приёмка")
wait_for("Полный осмотр")
screenshot("acceptance-toolbar-large-font-before-scroll")
swipe_left_in_scrollable("Отключено")
wait_for("?")
tap("?")
wait_for("Настройка приёмки")
screenshot("acceptance-help-large-font-before-scroll")
scroll_up_until_visible(
    "Вы можете отключать отдельные шаги проверки, если они не требуются по местным инструкциям.",
    "Настройки ВЛ80С и Ермака хранятся отдельно."
)
screenshot("acceptance-help-large-font-after-scroll")
tap("Понятно")
wait_for("Полный осмотр")
tap("Полный осмотр")
wait_for("Начать снаружи")
tap("Начать снаружи")
wait_for("Шаг 1 из")
wait_for("Статус: Не проверено")
tap("Проверено")
wait_for("Статус: Проверено")
screenshot("acceptance-checked")

open_screen("Диагностика")
wait_for("Диагностика ВЛ80С")
tap("Ермак")
wait_for("Техническая база Ермак")
tap("ВЛ80С")
wait_for("Диагностика ВЛ80С")
screenshot("diagnostics-family-roundtrip")

open_screen("Первая помощь")
wait_for("Оказание первой помощи")
wait_for("Общий порядок действий")
tap("Найти по симптому или действию")
adb("shell", "input", "text", "cpr")
wait_for("Найдено: 1")
wait_for("Не дышит / СЛР")
wait_for("Что делать")
screenshot("first-aid-search-cpr")

open_screen("Локомотивы / атлас")
wait_for("Техническая база ВЛ80С")
tap("Главный выключатель")
wait_for("ВЛ80С / Оборудование")
tap("ВЛ80С / Оборудование")
wait_for("Недавние материалы")
screenshot("atlas-breadcrumbs-recents-large-font")

log = adb("logcat", "-d").decode("utf-8", "replace")
with open(os.path.join(OUT, "logcat.txt"), "w", encoding="utf-8") as output:
    output.write(log)
if "FATAL EXCEPTION" in log:
    raise AssertionError("Android crash in logcat")
print("PASS dev14 scrollable acceptance help, acceptance, first-aid search, Atlas breadcrumbs/recents and 1.3x font scale")
