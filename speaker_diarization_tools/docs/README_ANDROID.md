# 🎭 Speaker Identifier - App Android

## Descrizione
App Android che identifica automaticamente chi parla in ogni riga
di un file SRT, aggiungendo tag speaker `[spk0]`, `[spk1]`...

Progettata per lavorare insieme ad **Auto Subtitle Generator**.

---

## 📋 Requisiti
- Android 8.0+ (API 26)
- 3GB RAM libera
- Snapdragon 8 Elite (Honor Magic 7 Pro) → ottimale
- Connessione internet (solo primo avvio per download modello ~50MB)

---

## 🔧 Compilazione APK

### Prerequisiti
- Android Studio Hedgehog (2023.1.1) o superiore
- JDK 17
- Android SDK 34

### Step 1: Apri il progetto
```
Android Studio → File → Open → seleziona cartella android_speaker_id/
```

### Step 2: Sincronizza Gradle
```
File → Sync Project with Gradle Files
```
Attendi il download delle dipendenze (~500MB prima volta)

### Step 3: Compila APK
```
Build → Build Bundle(s) / APK(s) → Build APK(s)
```
APK generato in:
```
android_speaker_id/app/build/outputs/apk/debug/app-debug.apk
```

### Step 4: Installa sul telefono
```
Trasferisci APK via USB o ADB:
adb install app-debug.apk
```
Oppure copia l'APK sul telefono e aprilo dal file manager.

---

## 🎯 Utilizzo

### Flusso completo consigliato

```
STEP 1: Auto Subtitle Generator
├── Carica video in inglese
├── Trascrizione: Whisper large-v3-turbo
├── Traduzione: ML Kit → Italiano
└── Esporta: film_it.srt

STEP 2: Speaker Identifier (questa app)
├── Seleziona video originale
├── Seleziona film_it.srt
├── Imposta numero speaker (0=auto)
├── Scegli modello (Veloce/Preciso)
├── Avvia diarizzazione
└── Esporta/Condividi: film_it_speakers.srt

STEP 3: PC Tool (TTS)
├── Riceve film_it_speakers.srt
├── Genera voci italiane per ogni speaker
└── Produce video doppiato finale
```

### Interfaccia app

```
┌─────────────────────────────────┐
│  🎭 Speaker Identifier          │
├─────────────────────────────────┤
│  📁 FILE DI INPUT               │
│  [Video originale] [Sfoglia]    │
│  [File SRT italiano] [Sfoglia]  │
├─────────────────────────────────┤
│  ⚙️ IMPOSTAZIONI                │
│  Speaker: [−] [0] [+]          │
│  ○ ⚡ Veloce (~30MB)            │
│  ○ 🎯 Preciso (~80MB)          │
├─────────────────────────────────┤
│  [🚀 AVVIA DIARIZZAZIONE]       │
├─────────────────────────────────┤
│  📊 PROGRESSO                   │
│  Analisi speaker... [████░] 65% │
├─────────────────────────────────┤
│  ✅ RISULTATO                   │
│  Speaker: 3 (spk0, spk1, spk2) │
│  [spk0] Ciao come stai?        │
│  [spk1] Bene grazie!           │
│  [💾 Salva SRT] [📤 Condividi] │
└─────────────────────────────────┘
```

---

## 📊 Formato SRT output

### Input (da Auto Subtitle Generator):
```srt
1
00:00:01,000 --> 00:00:03,500
Ciao Giovanni, come stai?

2
00:00:04,000 --> 00:00:06,000
Bene grazie, e tu?

3
00:00:06,500 --> 00:00:09,000
Tutto bene! Hai visto il film?
```

### Output (con speaker tags):
```srt
1
00:00:01,000 --> 00:00:03,500
[spk0] Ciao Giovanni, come stai?

2
00:00:04,000 --> 00:00:06,000
[spk1] Bene grazie, e tu?

3
00:00:06,500 --> 00:00:09,000
[spk0] Tutto bene! Hai visto il film?
```

---

## 🧠 Modelli disponibili

### ⚡ Veloce (wespeaker-voxceleb CAM++)
- Dimensione: ~30MB
- Velocità: ~1 min per 5 min di video
- Qualità: ⭐⭐⭐
- Ottimo per: dialoghi chiari, 2-3 speaker

### 🎯 Preciso (3D-Speaker ERes2Net)
- Dimensione: ~80MB
- Velocità: ~2 min per 5 min di video
- Qualità: ⭐⭐⭐⭐
- Ottimo per: molti speaker, accenti diversi

---

## ⚡ Performance su Honor Magic 7 Pro

| Operazione | Tempo (film 90 min) |
|------------|---------------------|
| Estrazione audio (FFmpeg) | ~2 min |
| Caricamento modello | ~10 sec |
| Diarizzazione (modello veloce) | ~15-20 min |
| Diarizzazione (modello preciso) | ~25-35 min |
| Arricchimento SRT | ~30 sec |
| **Totale (veloce)** | **~18-23 min** |

---

## 🔧 Risoluzione problemi

| Problema | Soluzione |
|----------|-----------|
| App crasha all'avvio | Verifica Android 8.0+ |
| Modello non scarica | Controlla connessione WiFi |
| Speaker confusi | Usa modello "Preciso" |
| SRT non riconosciuto | Verifica encoding UTF-8 |
| Video non selezionabile | Concedi permessi storage |
| Troppo lento | Usa modello "Veloce" |

---

## 📝 Note tecniche

### Algoritmo di diarizzazione
L'app usa un approccio in 3 fasi:
1. **Segmentazione**: divide l'audio in finestre da 1.5 secondi
2. **Embedding**: calcola l'impronta vocale di ogni segmento via ONNX
3. **Clustering**: raggruppa segmenti simili per speaker (cosine similarity)

### Accelerazione hardware
- **NNAPI**: usato automaticamente su Snapdragon 8 Elite
- **CPU**: fallback automatico se NNAPI non disponibile
- **GPU Adreno 830**: non usata direttamente (NNAPI la sfrutta internamente)

### Limitazioni
- Qualità inferiore a pyannote (PC) per modelli più leggeri
- Difficoltà con voci molto simili (es. gemelli)
- Audio con musica forte può ridurre accuratezza
- Massimo 10 speaker identificabili