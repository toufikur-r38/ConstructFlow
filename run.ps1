$ErrorActionPreference = "Stop"
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "1"
& "D:\Project-ConstructionTracker\.venv\Scripts\python.exe" "D:\ConstructFlow\main.py"
