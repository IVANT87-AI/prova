# 🎬 Flusso Completo: Doppiaggio Film in Italiano

## Panoramica del sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA COMPLETO                          │
├──────────────────┬──────────────────────────────────────────┤
│   📱 TELEFONO    │              💻 PC                       │
│  Honor Magic 7   │         Ryzen AI 7 350                   │
├──────────────────┼──────────────────────────────────────────┤
│                  │                                          │
│  [App 1]         │  [Script PC]                            │
│  Auto Subtitle   │  diarizer.py                            │
│  Generator       │  → pyannote (qualità max)               │
│  → Whisper       │  → SRT con [spk0][spk1]                 │
│  → ML Kit        │                                          │
│  → SRT italiano  │  [Script PC]                            │
│                  │  tts_engine.py                          │
│  [App 2]         │  → Edge-TTS multi-voce                  │
│  Speaker         │  → Audio italiano                       │
│  Identifier      │                                          │
│  → ONNX          │  [Script PC]                            │
│  → SRT+speaker   │  video_composer.py                      │
│                  │  → ffmpeg rimontaggio                   │
│                  │  → Film doppiato finale                 │
└──────────────────┴──────────────────────────────────────────┘
```

---

## 🔄 Opzione A: Ibrida (consigliata)

### Vantaggi
```
✅ Whisper veloce su Snapdragon 8 Elite
✅ Diarizzazione di qualità con pyannote su PC
✅ TTS multi-voce su PC
✅ Miglior rapporto qualità/velocità
```

### Flusso passo per passo

```
PASSO 1 - TELEFONO (Auto Subtitle Generator)
─────────────────────────────────────────────
① Apri Auto Subtitle Generator
② Carica: film_originale.mp4 (inglese)
③ Impostazioni:
   • Engine: Whisper
   • Modello: large-v3-turbo (o medium)
   • Traduzione: ML Kit → Italiano
   • VAD: ON (salta silenzi, più veloce)
④ Avvia → attendi trascrizione+traduzione
⑤ Esporta: film_it.srt
⑥ Tempo stimato: ~15-25 min per film 90 min

         ↓ Trasferisci al PC (USB/WiFi/Drive)
         film_originale.mp4
         film_it.srt

PASSO 2 - PC (Speaker Diarization Tool)
─────────────────────────────────────────
① Doppio click su avvia.bat
② Scegli: [1] Pipeline completa
   OPPURE: [2] Solo diarizzazione
③ Inserisci percorsi:
   • Video: D:\Film\film_originale.mp4
   • SRT:   D:\Film\film_it.srt
④ Numero speaker: 0 (auto) o numero esatto
⑤ Avvia → attendi elaborazione
⑥ Output: output\film_originale_doppiato_it.mp4
⑦ Tempo stimato: ~50-70 min per film 90 min

RISULTATO FINALE
─────────────────
🎬 film_originale_doppiato_it.mp4
   ✅ Audio italiano multi-voce
   ✅ Sottotitoli italiani incorporati
   ✅ Musica di sottofondo originale
```

---

## 🔄 Opzione B: Solo telefono (qualità inferiore)

### Vantaggi
```
✅ Tutto sul telefono
✅ Nessun PC necessario per diarizzazione
⚠️ Qualità diarizzazione inferiore
⚠️ TTS da fare comunque su PC
```

### Flusso

```
PASSO 1 - TELEFONO (Auto Subtitle Generator)
① Trascrivi + Traduci → film_it.srt

PASSO 2 - TELEFONO (Speaker Identifier)
① Carica film_originale.mp4 + film_it.srt
② Scegli modello: Preciso (migliore qualità)
③ Avvia → attendi ~20-30 min
④ Esporta: film_it_speakers.srt

         ↓ Trasferisci al PC
         film_originale.mp4
         film_it_speakers.srt

PASSO 3 - PC (Solo TTS)
① avvia.bat → [3] Solo TTS
② Inserisci film_it_speakers.srt
③ Output: film_doppiato_it.mp4
④ Tempo: ~30-40 min
```

---

## 🔄 Opzione C: Solo PC (qualità massima)

### Vantaggi
```
✅ Qualità massima (pyannote)
✅ Nessun telefono necessario
⚠️ Più lento (Whisper su CPU)
⚠️ Richiede più RAM
```

### Flusso

```
PC (Pipeline completa)
① avvia.bat → [1] Pipeline completa
② Inserisci solo:
   • Video: film_originale.mp4
   • SRT:   film_it.srt (già tradotto)
③ Tutto automatico
④ Tempo totale: ~2-3 ore per film 90 min
```

---

## 📊 Confronto opzioni

| Criterio | Opzione A (Ibrida) | Opzione B (Solo tel.) | Opzione C (Solo PC) |
|----------|-------------------|----------------------|---------------------|
| **Qualità diarizzazione** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Velocità totale** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Semplicità** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Tempo stimato** | ~70-90 min | ~60-80 min | ~120-180 min |
| **Qualità TTS** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 💡 Consigli pratici

### Per migliore qualità diarizzazione
```
• Specifica il numero esatto di speaker se lo conosci
• Usa audio senza musica di sottofondo forte
• Film con voci molto diverse → risultati migliori
• Film con molti personaggi simili → risultati peggiori
```

### Per migliore qualità TTS
```
• Edge-TTS è gratuito ma voce sintetica
• Per qualità professionale: usa ElevenLabs API (a pagamento)
• Regola velocità in config.py: TTS["rate"] = "-10%"
  (rallenta del 10% per dialoghi più naturali)
```

### Per migliore sincronizzazione
```
• Usa video con frame rate costante (24fps o 30fps)
• Evita video con VFR (Variable Frame Rate)
• Se desincronizzato: converti prima con ffmpeg:
  ffmpeg -i input.mp4 -vf fps=24 output_fixed.mp4
```

---

## 🗂️ Struttura file consigliata

```
D:\Doppiaggio\
├── originali\
│   ├── film.mp4              ← Video originale inglese
│   └── film_it.srt           ← SRT italiano (dal telefono)
├── elaborati\
│   ├── film_it_speakers.srt  ← SRT con speaker tags
│   └── film_doppiato_it.mp4  ← Output finale
└── pc_diarization\           ← Tool PC
    ├── avvia.bat
    └── ...
```