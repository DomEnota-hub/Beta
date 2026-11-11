# Post-15 remediation group 7/8 — Android startup, lifecycle, integration QA

**11.11.2026. Status: PARTIAL / CI PENDING.** Main stages fully complete remain **11/15**. This run worked only group 7. Groups 1–6 are not closed. Group 8 Sherpa-ONNX remains a separate mandatory TODO. Donor Test- pinned at `3176d6ee228f0ed4b78371f45209e10c1c724eff` was not modified. Full crew-permissions audit remains FUTURE/PARKED.

## Actual Kotlin/Compose changes

- `MainActivity` no longer synchronously loads and validates the entire VL80S runtime before the first model-picker frame. After an explicit **published VL80S** selection, the complete original source/profile/link/diagnostic safety validation is performed in `Dispatchers.IO` via `produceState`. All original checks remain; no content is promoted or hidden for new reasons.
- New `Vl80sBootstrapPolicy` prevents VL80S parsing for no selection, unknown model, and seven other model IDs. Reference-only family and common sections can start without VL80S registry dependency.
- `key(workingModel.id.value)` isolates the actual state slot and cancels the previous composition coroutine on model switch; merely keying `produceState`'s effect would retain a stale VL80S `Result` during the switch. This is a cross-model safety requirement, not just a speed optimization.
- The UI distinguishes **loading** from **failed source validation**. VL80S route loading provides explicit navigation back to Home/model picker; the Assistant continues to show independent readable reference lanes while its published VL80S catalog loads.
- Added `SystemClock.elapsedRealtime()` load-duration logging for a later on-device cold-start measurement. **No latency improvement or duration is claimed without physical measurement.**

## Test changes

- Added `Vl80sBootstrapPolicyTest`: 2 JUnit tests, explicit VL80S positive and null/unknown/seven-other-model negatives.
- Six existing Android instrumentation smoke suites now wait for the asynchronous VL80S Atlas/diagnostic screen before asserting, instead of assuming synchronous bootstrap.
- Added Android instrumentation source for **VL80S → CHME3 → Assistant** switching, asserting that the old published VL80S engine cannot leak into the other model. **Instrumentation compiled only when CI completes; no device execution yet.**

## Commit ledger and CI

- `bd033f69`: defer heavy VL80S bootstrap off UI thread.
- `6a8d48d0`: typed explicit-model bootstrap policy.
- `0613cfd1`: JUnit negatives.
- `7dc5a324`, `643679f9`: assistant loading UX.
- `906e493a`: latency logging.
- `19cd733a`: six Android smoke test wait updates.
- `1c2cca7f`: fix stale state across model switches.
- **Final code/test SHA `35aa5dcd0e953a2d84e8d633d0f943c50d5ec511`**: cross-model regression source.

**CI currently QUEUED, not terminal** at checkpoint creation: [Stage 15 run #42977661177](https://github.com/DomEnota-hub/Beta/actions/runs/42977661177), [Stage 9 #42977660948](https://github.com/DomEnota-hub/Beta/actions/runs/42977660948), [Stage 2 #42977660987](https://github.com/DomEnota-hub/Beta/actions/runs/42977660987). These IDs were read from GitHub; the queue is not a pass. Check final SHA after all workflow jobs complete; fix compiler/lint/test failures before any claim of verification.

## Blockers / required acceptance

1. Android CI queue and full unit/lint/assembleDebug/AndroidTest **compilation** pending. If a Debug APK is produced, download its artifact, validate content and SHA256, and **upload to Google Drive `Rail`**, folder ID `1IkcRbUhf8HMU7VwtPVOpI5SBZKPJHzFd`. Do not call delivery complete before Drive metadata confirms it.
2. No physical device startup timing, memory/ANR baseline, accessibility audit, dark-mode, lifecycle, offline and installed signed upgrade tests. Instrumentation **execution** remains final manual QA.
3. Whole-app release acceptance depends on groups 1–6, source rights, normative calculation gates, group 8 Sherpa-ONNX and explicit user approval. Do not release production.
4. Earlier group 6 assistant code has its own pending CI and missing latest QA APK delivery; keep it in its own backlog, do not claim group 6 complete.

**Next scheduled position:** group 8/8 Sherpa-ONNX, separately. After first pass, revisit unresolved groups 1–7 and group 8 as required. If this group's CI fails, record the exact failure and fix it in the permitted follow-up without marking group 7 done. Issue #4 remains OPEN.

## Verified carry-over delivery check (group 6 APK, not group 7)

While group 7 CI remained queued, the **previous group 6** Stage 15 run [#42975011351](https://github.com/DomEnota-hub/Beta/actions/runs/42975011351) reached **SUCCESS (terminal)** on SHA `c56e85da62feb8f6377f5a678f3739505967814d`. Artifact ID `13836517214`, `railbrake-stage15-debug-qa-unapproved`, downloaded ZIP **9,259,405 bytes**, SHA256 `81e44197e068a62c5a642efb8bb26f18c65c9f7f59365d6607dca00b6804da32` (matches GitHub artifact digest). ZIP integrity check passed and contains `app-shell-debug.apk` **9,642,701 bytes**, SHA256 `e4e2f9ca23a38b9bfb6b5bb902931637c8d942601ee8c60999bfbb1018a191d5`. The APK ZIP structure passed integrity check; actual assets count 87, VL80S path entries 79, forbidden family directories 0. This is **older group 6 code**, not group 7.

**Google Drive delivery FAILED, NOT DONE:** attempted `mcp__Google_Drive__upload_file` into existing `Rail` folder with the GitHub artifact connector file ID and then the local APK reference. Both failed with exact error **`BLOCKED_FILE_REFERENCE: this file is unavailable for connector egress`**. Passing a signed download URL also failed because the upload action requires a connector file reference. No new Drive file ID was returned, and no upload is claimed. The existing prior group 5 APK in Rail remains intact. Next authorized attempt must use a connector-supported uploadable file reference or another verified direct-to-Drive transfer path; independently read Drive metadata after upload. **Do not substitute a GitHub artifact link for Drive delivery.**
