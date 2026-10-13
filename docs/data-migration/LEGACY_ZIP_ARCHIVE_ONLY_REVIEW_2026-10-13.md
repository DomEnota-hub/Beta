# Donor ZIP members without a same-path file in the pinned Test tree

Input: `RailBrakeCalculator.zip` at donor commit `3176d6ee228f0ed4b78371f45209e10c1c724eff`, Git blob `6c3c7edc1713c1c901a566fd8a81a2494ee4ac58`. The [60-member manifest](legacy-zip-member-manifest.json) pins every byte and records all exact blob matches. This review concerns the 13 members for which neither the same relative path nor its `patch/app` counterpart exists as a separate file in that tree. It does not assign a final migration disposition based on path absence alone.

| Archive-relative path | Member blob | Observed role and present decision |
| --- | --- | --- |
| `gradle/wrapper/gradle-wrapper.properties` | `b82aa23a4f05d39d81870f8355ca43324f027298` | Historical Gradle 8.7 wrapper configuration; code/build comparison deferred. |
| `gradle.properties` | `f0a2e55f89e383466d2c6b481c8c468a3aa0b13d` | Historical JVM/AndroidX build configuration; no content object promoted. |
| `settings.gradle.kts` | `2685bd06c71e6617ace3729599382599d599775e` | Single `:app` project setup; modular Beta configuration takes precedence at runtime. |
| `build.gradle.kts` | `017d90996969ec2fc080d15d578bd7ec1230ccf8` | Historical Android/Kotlin plugin pins; not a technical source. |
| `app/src/main/java/ru/railbrake/calculator/data/HistoryRepository.kt` | `d95a2ce465e2f09bb96d74b8318f36b16d21afd0` | Calculation history format recovered and pinned in the manifest. User-data migration and the Beta storage gate remain open. |
| `app/src/main/java/ru/railbrake/calculator/data/FavoriteArticleRepository.kt` | `059d3039020edae2f401bd82b093dbaffff06f77` | `favorite_articles` SharedPreferences, key `article_ids`, a string set of article IDs. Preserve user preference identity only after article-ID mapping; no automatic import. |
| `app/src/main/res/values/themes.xml` | `988b7790a7dedf94972e95c679337875013cf174` | Historical Android theme. Visual parity review deferred. |
| `app/src/main/res/values/colors.xml` | `cf20da8973979bae25937699137a48d620dfc8e5` | Historical `launcher_background` value `#10151D`; no palette change inferred. |
| `app/src/main/res/values-v27/themes.xml` | `82b414c5be812bdc85fb6ecdf9c5c4268ddfe9a7` | API 27 theme override; visual parity review deferred. |
| `app/src/main/res/drawable-nodpi/vl80s_pneumatic_scheme.jpg` | `0e5c901af74973df5b13453e1bceb4f820d210e1` | Raster pneumatic scheme, 1181×573. VL80S candidate, no technical approval or runtime import. |
| `app/src/main/res/drawable-nodpi/vl80s_layout_section1.png` | `a778f2fe6ea67c7a0a76cee2244f2d50a7b22e6e` | Raster section layout, 1667×626. VL80S candidate, no technical approval or runtime import. |
| `legacy/Тормоза_расширенная_версия.cxx` | `098e8888c4957d772e9f5cdc9008e7f46227c420` | Legacy 1544-line C++ calculator with mass/slope, appendix 12, available-shoe and local history flows. Formulas and rounding require source-by-source contract review; do not adopt operational values from this file alone. |
| `tools/__pycache__/generate_exam_questions.cpython-312.pyc` | `29bf256141517dc3480abe20ebe39eed810980e6` | Compiled Python cache; the archive's `tools/generate_exam_questions.py` is byte-identical to the pinned tree source. Do not execute or treat the cache as a separate question corpus. |

The remaining 33 nonmatching archive members have a same-path or patch-path counterpart with different bytes. Those require semantic diffs, especially the older plaintext `exam_questions.json` (329 questions) against the current encoded asset and its access policy. The public Test repository already exposes the old archive; this review does not copy its question text into Beta. The ZIP itself is not committed to Beta.
