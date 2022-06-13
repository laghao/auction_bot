@echo off
set LOGFILE=batch.log
call :LOG > %LOGFILE%
exit /B
:LOG

set INTERVAL=10
:loop
python bot_auctions_table.py
timeout %INTERVAL%
goto:loop