"""臨時 lint 檢查腳本。"""
from src.wiki.engine import WikiEngine

e = WikiEngine()
issues = e.lint()
if issues:
    for i in issues:
        print(i)
else:
    print("No issues found")
