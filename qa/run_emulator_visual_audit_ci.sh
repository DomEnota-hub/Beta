#!/usr/bin/env bash
set -euo pipefail

export APK="$GITHUB_WORKSPACE/buildsrc/RailBrakeCalculator/app/build/outputs/apk/debug/app-debug.apk"
export QA_OUT="$GITHUB_WORKSPACE/qa-visual-evidence"

mkdir -p "$QA_OUT"

collect_final_evidence() {
  adb shell wm size > "$QA_OUT/device.txt" 2>&1 || true
  adb shell wm density >> "$QA_OUT/device.txt" 2>&1 || true
  adb shell settings get system font_scale >> "$QA_OUT/device.txt" 2>&1 || true
  adb logcat -d > "$QA_OUT/logcat-final.txt" 2>&1 || true
}

trap collect_final_evidence EXIT
python3 "$GITHUB_WORKSPACE/qa/dev14_android_visual_audit.py"
