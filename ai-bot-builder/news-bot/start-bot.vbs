' AI News Bot — 背景啟動（無黑窗）
Dim WshShell
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\relerwang\OneDrive - International Games System\部門管理\5.AI\1.AiAgent\ai-workshop\.kiro\skills\ai-bot-builder\news-bot"
WshShell.Run "C:\Users\relerwang\AppData\Local\Programs\Python\Python311\python.exe -m src.bot.main", 0, False
Set WshShell = Nothing
