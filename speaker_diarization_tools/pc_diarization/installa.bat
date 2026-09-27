@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║     Speaker Diarization PC Tool - Installazione     ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato!
    echo Scarica Python 3.11 da: https://www.python.org/downloads/
    echo IMPORTANTE: spunta "Add Python to PATH" durante l'installazione
    pause
    exit /b 1
)

echo [OK] Python trovato
python --version

:: Verifica pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] pip non trovato!
    pause
    exit /b 1
)

echo [OK] pip trovato
echo.

:: Crea ambiente virtuale
echo [1/5] Creazione ambiente virtuale...
if not exist "venv" (
    python -m venv venv
    echo [OK] Ambiente virtuale creato
) else (
    echo [OK] Ambiente virtuale gia' esistente
)

:: Attiva ambiente virtuale
echo.
echo [2/5] Attivazione ambiente virtuale...
call venv\Scripts\activate.bat
echo [OK] Ambiente virtuale attivato

:: Aggiorna pip
echo.
echo [3/5] Aggiornamento pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip aggiornato

:: Installa dipendenze PyTorch (CPU - compatibile AMD)
echo.
echo [4/5] Installazione PyTorch (CPU mode per AMD)...
echo Questo puo' richiedere 5-10 minuti...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
if errorlevel 1 (
    echo [ERRORE] Installazione PyTorch fallita
    pause
    exit /b 1
)
echo [OK] PyTorch installato

:: Installa altre dipendenze
echo.
echo [5/5] Installazione dipendenze...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERRORE] Installazione dipendenze fallita
    pause
    exit /b 1
)
echo [OK] Dipendenze installate

:: Verifica ffmpeg
echo.
echo Verifica ffmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ATTENZIONE] ffmpeg non trovato nel PATH!
    echo.
    echo Installa ffmpeg:
    echo 1. Scarica da: https://www.gyan.dev/ffmpeg/builds/
    echo    File: ffmpeg-release-essentials.zip
    echo 2. Estrai in C:\ffmpeg
    echo 3. Aggiungi C:\ffmpeg\bin al PATH di sistema:
    echo    - Cerca "variabili d'ambiente" nel menu Start
    echo    - Path ^> Modifica ^> Nuovo ^> C:\ffmpeg\bin
    echo 4. Riavvia il terminale
    echo.
) else (
    echo [OK] ffmpeg trovato
)

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║              Installazione completata!               ║
echo ╠══════════════════════════════════════════════════════╣
echo ║                                                      ║
echo ║  PROSSIMI PASSI:                                     ║
echo ║  1. Apri config.py con un editor di testo           ║
echo ║  2. Inserisci il tuo token HuggingFace              ║
echo ║     (ottienilo su huggingface.co/settings/tokens)   ║
echo ║  3. Accetta i termini su:                           ║
echo ║     huggingface.co/pyannote/speaker-diarization-3.1 ║
echo ║     huggingface.co/pyannote/segmentation-3.0        ║
echo ║  4. Avvia con: avvia.bat                            ║
echo ║                                                      ║
echo ╚══════════════════════════════════════════════════════╝
echo.
pause