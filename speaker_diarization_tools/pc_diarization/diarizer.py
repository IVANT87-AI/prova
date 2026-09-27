"""
Modulo 1: Diarizzazione Speaker
Analizza l'audio e identifica chi parla quando
"""

import os
import json
import torch
from pathlib import Path
from pyannote.audio import Pipeline
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import srt
from datetime import timedelta

from config import HUGGINGFACE_TOKEN, DIARIZATION, DIRS

console = Console()


def load_pipeline():
    """Carica il modello pyannote per la diarizzazione."""
    console.print("\n[bold cyan]🔄 Caricamento modello pyannote...[/bold cyan]")
    console.print("[dim]Al primo avvio scarica ~1GB di modelli. Attendi...[/dim]\n")

    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=HUGGINGFACE_TOKEN
        )

        # Usa GPU se disponibile (DirectML/CUDA), altrimenti CPU
        if torch.cuda.is_available():
            pipeline = pipeline.to(torch.device("cuda"))
            console.print("[green]✅ GPU CUDA rilevata - accelerazione attiva[/green]")
        else:
            console.print("[yellow]⚠️  Nessuna GPU CUDA - uso CPU (più lento)[/yellow]")
            console.print("[dim]   Per AMD: installa ROCm su Linux per accelerazione GPU[/dim]")

        console.print("[green]✅ Modello caricato con successo![/green]\n")
        return pipeline

    except Exception as e:
        console.print(f"[red]❌ Errore caricamento modello: {e}[/red]")
        console.print("\n[yellow]Possibili cause:[/yellow]")
        console.print("  1. Token HuggingFace non valido → controlla config.py")
        console.print("  2. Termini non accettati → vai su huggingface.co/pyannote/speaker-diarization-3.1")
        console.print("  3. Nessuna connessione internet (primo avvio)")
        raise


def extract_audio(video_path: str) -> str:
    """Estrae l'audio dal video in formato WAV mono 16kHz."""
    import subprocess

    audio_path = os.path.join(DIRS["temp"], "audio_mono.wav")
    console.print(f"[cyan]🎵 Estrazione audio da: {Path(video_path).name}[/cyan]")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",                    # No video
        "-acodec", "pcm_s16le",   # PCM 16-bit
        "-ar", "16000",           # 16kHz (richiesto da pyannote)
        "-ac", "1",               # Mono
        audio_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Errore ffmpeg: {result.stderr}")

    console.print(f"[green]✅ Audio estratto: {audio_path}[/green]\n")
    return audio_path


def run_diarization(audio_path: str, num_speakers: int = None) -> dict:
    """
    Esegue la diarizzazione sull'audio.
    Restituisce dizionario: {(start, end): "spkX"}
    """
    pipeline = load_pipeline()

    console.print("[cyan]🎙️  Avvio diarizzazione speaker...[/cyan]")
    console.print("[dim]Questo è il passaggio più lento. Attendi...[/dim]\n")

    # Parametri diarizzazione
    params = {}
    if num_speakers:
        params["num_speakers"] = num_speakers
    else:
        if DIARIZATION["min_speakers"]:
            params["min_speakers"] = DIARIZATION["min_speakers"]
        if DIARIZATION["max_speakers"]:
            params["max_speakers"] = DIARIZATION["max_speakers"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analisi speaker in corso...", total=None)
        diarization = pipeline(audio_path, **params)
        progress.update(task, completed=True)

    # Converti risultati in dizionario
    segments = {}
    speaker_set = set()

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        # Normalizza nome speaker: SPEAKER_00 → spk0
        spk_num = speaker.split("_")[-1].lstrip("0") or "0"
        spk_label = f"spk{spk_num}"
        segments[(turn.start, turn.end)] = spk_label
        speaker_set.add(spk_label)

    console.print(f"\n[green]✅ Diarizzazione completata![/green]")
    console.print(f"[bold]   Speaker identificati: {len(speaker_set)} → {sorted(speaker_set)}[/bold]\n")

    # Salva risultati grezzi per debug
    debug_path = os.path.join(DIRS["temp"], "diarization_raw.json")
    with open(debug_path, "w") as f:
        json.dump(
            {f"{s:.3f}-{e:.3f}": spk for (s, e), spk in segments.items()},
            f, indent=2
        )

    return segments


def find_speaker_for_timestamp(start_sec: float, end_sec: float, segments: dict) -> str:
    """
    Trova lo speaker per un dato intervallo temporale.
    Usa overlap massimo per assegnare lo speaker corretto.
    """
    best_speaker = "default"
    best_overlap = 0.0

    for (seg_start, seg_end), speaker in segments.items():
        # Calcola overlap tra segmento SRT e segmento diarizzazione
        overlap_start = max(start_sec, seg_start)
        overlap_end = min(end_sec, seg_end)
        overlap = max(0, overlap_end - overlap_start)

        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = speaker

    return best_speaker


def enrich_srt(srt_path: str, segments: dict, output_path: str = None) -> str:
    """
    Arricchisce il file SRT con i tag speaker.
    Input:  "Ciao come stai?"
    Output: "[spk0] Ciao come stai?"
    """
    console.print(f"[cyan]📝 Arricchimento SRT con speaker tags...[/cyan]")

    # Leggi SRT
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    subtitles = list(srt.parse(content))
    enriched = []
    speaker_stats = {}

    for sub in subtitles:
        start_sec = sub.start.total_seconds()
        end_sec = sub.end.total_seconds()

        speaker = find_speaker_for_timestamp(start_sec, end_sec, segments)

        # Aggiungi tag speaker al testo
        # Rimuovi eventuali tag precedenti
        text = sub.content.strip()
        if text.startswith("[spk"):
            text = text.split("]", 1)[-1].strip()

        sub.content = f"[{speaker}] {text}"
        enriched.append(sub)

        # Statistiche
        speaker_stats[speaker] = speaker_stats.get(speaker, 0) + 1

    # Salva SRT arricchito
    if not output_path:
        base = Path(srt_path).stem
        output_path = os.path.join(DIRS["temp"], f"{base}_speakers.srt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(enriched))

    console.print(f"[green]✅ SRT arricchito salvato: {output_path}[/green]")
    console.print("\n[bold]📊 Statistiche speaker:[/bold]")
    for spk, count in sorted(speaker_stats.items()):
        console.print(f"   {spk}: {count} battute")

    return output_path


def diarize(video_path: str, srt_path: str,
            num_speakers: int = None,
            output_srt_path: str = None) -> str:
    """
    Pipeline completa di diarizzazione.

    Args:
        video_path: Percorso video originale
        srt_path: Percorso SRT tradotto (dal telefono)
        num_speakers: Numero speaker noti (None = auto-detect)
        output_srt_path: Percorso output SRT arricchito

    Returns:
        Percorso del SRT arricchito con speaker tags
    """
    console.print("\n" + "="*50)
    console.print("[bold magenta]🎭 MODULO 1: DIARIZZAZIONE SPEAKER[/bold magenta]")
    console.print("="*50 + "\n")

    # Step 1: Estrai audio
    audio_path = extract_audio(video_path)

    # Step 2: Diarizzazione
    segments = run_diarization(audio_path, num_speakers)

    # Step 3: Arricchisci SRT
    enriched_srt = enrich_srt(srt_path, segments, output_srt_path)

    return enriched_srt


if __name__ == "__main__":
    # Test standalone
    import sys
    if len(sys.argv) < 3:
        print("Uso: python diarizer.py video.mp4 sottotitoli.srt [num_speakers]")
        sys.exit(1)

    video = sys.argv[1]
    srt_file = sys.argv[2]
    n_speakers = int(sys.argv[3]) if len(sys.argv) > 3 else None

    result = diarize(video, srt_file, n_speakers)
    print(f"\nSRT arricchito: {result}")