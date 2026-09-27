# 🎬 Speaker Diarization PC Tool

## Descrizione
Script Python per Windows che:
1. **Diarizza** l'audio del video (identifica chi parla quando)
2. **Arricchisce** il file SRT con tag speaker `[spk0]`, `[spk1]`...
3. **Genera** audio doppiato in italiano con voci diverse per speaker
4. **Rimonta** il video finale con audio italiano e sottotitoli

---

## 📋 Requisiti di sistema
- Windows 10/11
- Python 3.9 o superiore
- 8GB RAM libera (16GB consigliati)
- Connessione internet (primo avvio per download modelli)
- ffmpeg installato nel PATH

---

## 🚀 Installazione

### Step 1: Installa Python
1. Vai su https://www.python.org/downloads/
2. Scarica Python 3.11
3. ⚠️ **IMPORTANTE**: spunta "Add Python to PATH"
4. Installa

### Step 2: Installa ffmpeg
1. Scarica da: https://www.gyan.dev/ffmpeg/builds/
   - File: `ffmpeg-release-essentials.zip`
2. Estrai in `C:\ffmpeg`
3. Aggiungi `C:\ffmpeg\bin` al PATH:
   - Cerca "variabili d'ambiente" nel menu Start
   - `Path` → `Modifica` → `Nuovo` → `C:\ffmpeg\bin`
4. Riavvia il terminale

### Step 3: Ottieni token HuggingFace (gratuito)
1. Registrati su https://huggingface.co
2. Vai su https://huggingface.co/settings/tokens
3. Crea token "read" → copia il codice `hf_xxxxx`
4. Accetta i termini su:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0

### Step 4: Configura il tool
1. Apri `config.py` con Notepad
2. Inserisci il token:
   ```python
   HUGGINGFACE_TOKEN = "hf_il_tuo_token_qui"
   ```
3. Personalizza le voci (opzionale):
   ```python
   SPEAKER_VOICES = {
       "spk0": "it-IT-GiuseppeNeural",  # Protagonista maschile
       "spk1": "it-IT-ElsaNeural",       # Protagonista femminile
       "spk2": "it-IT-DiegoNeural",      # Personaggio secondario
   }
   ```

### Step 5: Installa dipendenze
Doppio click su `installa.bat`

---

## 🎯 Utilizzo

### Avvio
Doppio click su `avvia.bat`

### Menu principale
```
1 → Pipeline completa (diarizzazione + TTS + video)
2 → Solo diarizzazione → SRT con speaker
3 → Solo TTS → video doppiato da SRT
4 → Configura voci speaker
```

### Flusso consigliato per film

**Con app Android (Speaker Identifier):**
```
📱 Telefono:
   Auto Subtitle Generator → SRT italiano
   Speaker Identifier → SRT con [spk0][spk1]
         ↓
💻 PC:
   Modalità 3 (Solo TTS) → video doppiato
```

**Solo PC:**
```
💻 PC:
   Modalità 1 (Pipeline completa)
   → inserisci video originale + SRT italiano
   → tutto automatico
```

### Da riga di comando
```bash
# Pipeline completa
python main.py --video film.mp4 --srt film_it.srt --mode full

# Solo diarizzazione
python main.py --video film.mp4 --srt film_it.srt --mode diarize --speakers 3

# Solo TTS (da SRT già diarizzato)
python main.py --video film.mp4 --srt film_it_speakers.srt --mode tts
```

---

## 📁 Struttura cartelle
```
pc_diarization/
├── main.py              ← Avvio principale
├── diarizer.py          ← Modulo diarizzazione
├── tts_engine.py        ← Modulo TTS multi-voce
├── video_composer.py    ← Modulo rimontaggio video
├── config.py            ← Configurazione
├── requirements.txt     ← Dipendenze Python
├── installa.bat         ← Script installazione
├── avvia.bat            ← Script avvio
├── temp/                ← File temporanei (auto-creata)
└── output/              ← Video doppiati (auto-creata)
```

---

## ⚙️ Configurazione avanzata

### Voci Edge-TTS disponibili (italiano)
| Voce | Genere | Qualità |
|------|--------|---------|
| `it-IT-GiuseppeNeural` | Maschile | ⭐⭐⭐⭐⭐ |
| `it-IT-DiegoNeural` | Maschile | ⭐⭐⭐⭐ |
| `it-IT-ElsaNeural` | Femminile | ⭐⭐⭐⭐⭐ |
| `it-IT-IsabellaNeural` | Femminile | ⭐⭐⭐⭐ |

### Parametri diarizzazione
```python
DIARIZATION = {
    "min_speakers": 1,   # Minimo speaker
    "max_speakers": 10,  # Massimo speaker
}
```

### Qualità video output
```python
OUTPUT = {
    "video_crf": 18,     # 18=alta qualità, 28=file piccolo
    "audio_bitrate": "192k",
    "burn_subtitles": True,
}
```

---

## 🔧 Risoluzione problemi

| Problema | Soluzione |
|----------|-----------|
| Token HuggingFace non valido | Verifica che inizi con `hf_` |
| Modello non scarica | Controlla connessione internet |
| ffmpeg non trovato | Aggiungi `C:\ffmpeg\bin` al PATH |
| RAM insufficiente | Chiudi altre applicazioni |
| Audio desincronizzato | Usa video con frame rate costante |
| Voce robotica | Normale con Edge-TTS gratuito |

---

## ⏱️ Tempi stimati (Ryzen AI 7 350, CPU mode)

| Operazione | Film 90 min |
|------------|-------------|
| Diarizzazione | ~20-30 min |
| TTS multi-voce | ~25-35 min |
| Rimontaggio video | ~5 min |
| **Totale** | **~50-70 min** |