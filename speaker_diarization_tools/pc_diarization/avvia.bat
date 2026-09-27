@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║        Speaker Diarization PC Tool v1.0             ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: Verifica ambiente virtuale
if not exist "venv\Scripts\activate.bat" (
    echo [ERRORE] Ambiente virtuale non trovato!
    echo Esegui prima: installa.bat
    pause
    exit /b 1
)

:: Attiva ambiente virtuale
call venv\Scripts\activate.bat

:: Avvia applicazione
python main.py %*

:: Se esce con errore
if errorlevel 1 (
    echo.
    echo [ERRORE] L'applicazione e' uscita con un errore.
    echo Controlla i messaggi sopra per dettagli.
    pause
)