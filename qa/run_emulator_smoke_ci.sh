#!/usr/bin/env bash
set -uo pipefail

evidence_dir="$GITHUB_WORKSPACE/qa-evidence"
apk_path="$GITHUB_WORKSPACE/buildsrc/RailBrakeCalculator/app/build/outputs/apk/debug/app-debug.apk"
mkdir -p "$evidence_dir"

set +e
APK="$apk_path" QA_OUT="$evidence_dir" python3 "$GITHUB_WORKSPACE/qa/dev14_android_smoke.py"
smoke_status=$?

adb shell wm size > "$evidence_dir/device.txt" 2>&1
adb shell wm density >> "$evidence_dir/device.txt" 2>&1
adb shell settings get system font_scale >> "$evidence_dir/device.txt" 2>&1
adb logcat -d > "$evidence_dir/logcat-final.txt" 2>&1

exit "$smoke_status"
