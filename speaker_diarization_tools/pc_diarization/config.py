"""
Configurazione centrale per Speaker Diarization PC Tool
"""

import os

# ─────────────────────────────────────────
# HUGGINGFACE TOKEN
# Ottienilo gratis su: https://huggingface.co/settings/tokens
# Accetta i termini su:
#   https://huggingface.co/pyannote/speaker-diarization-3.1
#   https://huggingface.co/pyannote/segmentation-3.0
# ─────────────────────────────────────────
HUGGINGFACE_TOKEN = "hf_INSERISCI_IL_TUO_TOKEN_QUI"

# ─────────────────────────────────────────
# VOCI EDGE-TTS ITALIANE
# Mappa speaker → voce italiana
# Puoi personalizzare le voci per ogni speaker
# ─────────────────────────────────────────
SPEAKER_VOICES = {
    "spk0": "it-IT-GiuseppeNeural",    # Voce maschile principale
    "spk1": "it-IT-ElsaNeural",         # Voce femminile principale
    "spk2": "it-IT-DiegoNeural",        # Voce maschile secondaria
    "spk3": "it-IT-IsabellaNeural",     # Voce femminile secondaria
    "spk4": "it-IT-GiuseppeNeural",    # Fallback maschile
    "spk5": "it-IT-ElsaNeural",         # Fallback femminile
    "default": "it-IT-GiuseppeNeural", # Voce di default
}

# ─────────────────────────────────────────
# PARAMETRI DIARIZZAZIONE
# ─────────────────────────────────────────
DIARIZATION = {
    "min_speakers": 1,      # Numero minimo speaker (None = auto)
    "max_speakers": 10,     # Numero massimo speaker (None = auto)
    "min_duration_on": 0.1, # Durata minima segmento parlato (sec)
    "min_duration_off": 0.1,# Durata minima silenzio (sec)
}

# ─────────────────────────────────────────
# PARAMETRI TTS
# ─────────────────────────────────────────
TTS = {
    "rate": "+0%",          # Velocità parlato (es. +10%, -5%)
    "volume": "+0%",        # Volume (es. +10%, -5%)
    "pitch": "+0Hz",        # Tono (es. +10Hz, -5Hz)
    "stretch_audio": True,  # Adatta durata audio al timestamp SRT
    "max_stretch": 1.5,     # Massimo allungamento audio (1.5 = 150%)
    "min_stretch": 0.7,     # Minimo accorciamento audio (0.7 = 70%)
}

# ─────────────────────────────────────────
# PARAMETRI OUTPUT
# ─────────────────────────────────────────
OUTPUT = {
    "video_codec": "libx264",
    "audio_codec": "aac",
    "video_crf": 18,            # Qualità video (18=alta, 28=bassa)
    "audio_bitrate": "192k",
    "burn_subtitles": True,     # Incorpora sottotitoli nel video
    "subtitle_font_size": 20,
    "subtitle_font_color": "white",
    "subtitle_outline_color": "black",
    "keep_background_music": True,  # Mantieni musica di sottofondo
    "bg_music_volume": 0.3,         # Volume musica sottofondo (0-1)
}

# ─────────────────────────────────────────
# CARTELLE
# ─────────────────────────────────────────
DIRS = {
    "temp": "temp",
    "output": "output",
    "audio_segments": "temp/audio_segments",
    "tts_segments": "temp/tts_segments",
}

# Crea cartelle se non esistono
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)