# 🚀 Guida: Compilare APK con GitHub Actions

## Cos'è GitHub Actions?
Un servizio **gratuito** di GitHub che compila il tuo codice
nel cloud. Tu carichi il codice, GitHub ti restituisce l'APK
pronto da installare. Zero installazioni sul tuo PC.

---

## 📋 Prerequisiti
- Account GitHub gratuito → https://github.com
- Il file ZIP del progetto (già scaricato)

---

## 🔧 Passo 1: Crea account GitHub

1. Vai su https://github.com
2. Clicca **Sign up**
3. Inserisci email, password, username
4. Verifica email
5. Piano gratuito → **Continue for free**

---

## 📁 Passo 2: Crea un nuovo repository

1. Clicca **+** in alto a destra → **New repository**
2. Impostazioni:
   ```
   Repository name: speaker-identifier
   Visibility:      ● Private  ← consigliato
   Initialize:      ✅ Add a README file
   ```
3. Clicca **Create repository**

---

## 📤 Passo 3: Carica il codice

### Metodo A: Upload diretto (più semplice)

1. Nel tuo repository, clicca **Add file** → **Upload files**
2. Trascina TUTTA la cartella `android_speaker_id/` nella pagina
   ⚠️ Includi anche la cartella `.github/` (potrebbe essere nascosta)
3. In basso: **Commit changes** → **Commit directly to main**
4. Clicca **Commit changes**

### Metodo B: Git da terminale (più veloce)

```bash
# Installa Git da: https://git-scm.com/download/win

cd android_speaker_id
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TUO_USERNAME/speaker-identifier.git
git push -u origin main
```

---

## ⚙️ Passo 4: Verifica il workflow

1. Nel repository, clicca la tab **Actions**
2. Dovresti vedere: **🎭 Build Speaker Identifier APK**
3. Se non parte automaticamente:
   - Clicca sul workflow
   - Clicca **Run workflow** → **Run workflow**

---

## ⏳ Passo 5: Attendi la compilazione

```
Tempo stimato: 5-15 minuti (prima volta ~15 min)
               2-5 minuti (volte successive, grazie alla cache)

Stato:
🟡 In corso  → compilazione in esecuzione
✅ Verde     → APK pronto!
❌ Rosso     → errore (vedi log per dettagli)
```

Puoi seguire il progresso in tempo reale cliccando sul job.

---

## ⬇️ Passo 6: Scarica l'APK

1. Tab **Actions** → clicca sull'ultimo run verde ✅
2. Scorri in basso fino a **Artifacts**
3. Clicca **SpeakerIdentifier-APK**
4. Si scarica uno ZIP → estrailo
5. Dentro trovi: `SpeakerIdentifier_v1.0_YYYYMMDD_HHMM.apk`

---

## 📱 Passo 7: Installa sul telefono

### Sul telefono Honor Magic 7 Pro:

1. **Abilita installazione da sorgenti sconosciute:**
   ```
   Impostazioni → Sicurezza → 
   Installa app sconosciute → 
   seleziona il tuo browser/file manager → ON
   ```

2. **Trasferisci l'APK:**
   - Via USB: copia l'APK nella memoria del telefono
   - Via email: inviati l'APK e aprilo
   - Via Google Drive: carica e scarica sul telefono

3. **Installa:**
   - Apri il file manager
   - Trova l'APK
   - Tocca → **Installa**
   - **Installa comunque** (se avvisa su app sconosciuta)

4. **Avvia:** cerca **Speaker Identifier** nelle app

---

## 🔄 Aggiornamenti futuri

Ogni volta che modifichi il codice e fai push su GitHub,
l'APK viene ricompilato automaticamente in ~5 minuti.

```
Modifica codice → git push → GitHub compila → scarica nuovo APK
```

---

## 🏷️ Creare una Release ufficiale (opzionale)

Per creare una release con APK allegato permanentemente:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub creerà automaticamente una **Release** con l'APK
allegato nella sezione **Releases** del repository.

---

## ❓ Problemi comuni

| Problema | Soluzione |
|----------|-----------|
| Actions non parte | Vai su Actions → abilita workflows |
| Build fallisce (rosso) | Clicca sul job → leggi il log dell'errore |
| `.github/` non caricata | Abilita "mostra file nascosti" nel file manager |
| APK non si installa | Abilita "sorgenti sconosciute" nelle impostazioni |
| Artifact non appare | Aspetta fine build (barra verde) |
| Limite minuti gratuiti | GitHub offre 2000 min/mese gratis (più che sufficiente) |

---

## 💡 Minuti gratuiti GitHub Actions

```
Piano gratuito GitHub:
✅ 2.000 minuti/mese su Linux
✅ Repository privati illimitati
✅ Artifacts fino a 500MB

Ogni build: ~10-15 minuti
→ Puoi fare ~130-200 build al mese gratis!
```