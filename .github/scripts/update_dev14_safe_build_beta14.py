from pathlib import Path

path = Path('.github/workflows/dev14-safe-build.yml')
text = path.read_text()
text = text.replace('Verify Beta11 identity', 'Verify Beta14 identity')
text = text.replace("versionCode = 156", "versionCode = 159")
text = text.replace('1.2.2-dev14-beta11', '1.2.2-dev14-beta14')

anchor = '          cmp app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt patch/app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt\n'
extra = '''          cmp app/src/main/java/ru/railbrake/calculator/data/DiagnosticSessionRepository.kt patch/app/src/main/java/ru/railbrake/calculator/data/DiagnosticSessionRepository.kt
          cmp app/src/main/java/ru/railbrake/calculator/data/SecretAccessRepository.kt patch/app/src/main/java/ru/railbrake/calculator/data/SecretAccessRepository.kt
          cmp app/src/main/java/ru/railbrake/calculator/ui/KnowledgeBaseScreen.kt patch/app/src/main/java/ru/railbrake/calculator/ui/KnowledgeBaseScreen.kt
          cmp app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt patch/app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt
          cmp app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt
          cmp app/src/main/java/ru/railbrake/calculator/core/TechnicalPresentation.kt patch/app/src/main/java/ru/railbrake/calculator/core/TechnicalPresentation.kt
'''
if extra not in text:
    if anchor not in text:
        raise SystemExit('mirror anchor not found')
    text = text.replace(anchor, anchor + extra, 1)

check_anchor = '          grep -Fq \'BLUE("Холодный синий", Color(0xFF82A9FF), Color(0xFF182947))\' app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt\n'
checks = '''          grep -Fq 'AMBER("Янтарный", RailAmber, RailAmberSoft)' app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt
          grep -Fq 'IconButton(onClick = { query = "" })' app/src/main/java/ru/railbrake/calculator/ui/KnowledgeBaseScreen.kt
          grep -Fq 'Показывать материалы в справочнике' app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt
          grep -Fq 'KEY_SHOW_IN_KNOWLEDGE' app/src/main/java/ru/railbrake/calculator/data/SecretAccessRepository.kt
          grep -Fq 'getSharedPreferences("calculation_inputs"' app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt
          grep -Fq 'Локальный журнал Ермака' app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt
          grep -Fq 'profileId = DiagnosticSessionRepository.PROFILE_ERMAK' app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt
          grep -Fq 'loadForProfile(DiagnosticSessionRepository.PROFILE_VL80S)' app/src/main/java/ru/railbrake/calculator/ui/DiagnosticScreen.kt
'''
if checks not in text:
    if check_anchor not in text:
        raise SystemExit('check anchor not found')
    text = text.replace(check_anchor, check_anchor + checks, 1)

path.write_text(text)
