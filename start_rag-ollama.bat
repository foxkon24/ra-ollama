@echo off

@if not "%~0"=="%~dp0.\%~nx0" start /min cmd /c,"%~dp0.\%~nx0" %* & goto :eof

cd D:\laragon\www\test\rag-ollama

cd %~dp0

python main.py

pause

