"""
Modulo 3: Rimontaggio Video
Combina video originale + audio doppiato + sottotitoli
"""

import os
import subprocess
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import OUTPUT, DIRS

console = Console()


def get_video_duration(video_path: str) -> float:
    """Ottieni la durata del video in secondi."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    import json
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def get_video_info(video_path: str) -> dict:
    """Ottieni informazioni sul video (risoluzione, fps, ecc.)."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    import json
    data = json.loads(result.stdout)

    info = {"width": 1920, "height": 1080, "fps": "24"}
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            info["width"] = stream.get("width", 1920)
            info["height"] = stream.get("height", 1080)
            fps_str = stream.get("r_frame_rate", "24/1")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                info["fps"] = str(round(int(num) / int(den), 2))
            break
    return info


def compose_video(video_path: str,
                  dubbed_audio_path: str,
                  srt_path: str,
                  output_path: str = None) -> str:
    """
    Compone il video finale con audio doppiato e sottotitoli.

    Args:
        video_path: Video originale
        dubbed_audio_path: Audio doppiato in italiano
        srt_path: SRT con speaker tags (per sottotitoli)
        output_path: Percorso output video finale

    Returns:
        Percorso video finale
    """
    console.print("\n" + "="*50)
    console.print("[bold magenta]🎬 MODULO 3: COMPOSIZIONE VIDEO FINALE[/bold magenta]")
    console.print("="*50 + "\n")

    # Prepara SRT pulito (senza tag speaker) per sottotitoli
    clean_srt_path = _clean_srt_for_subtitles(srt_path)

    # Percorso output
    if not output_path:
        stem = Path(video_path).stem
        output_path = os.path.join(DIRS["output"], f"{stem}_doppiato_it.mp4")

    os.makedirs(DIRS["output"], exist_ok=True)

    console.print(f"[cyan]🎬 Composizione video finale...[/cyan]")
    console.print(f"   Video: {Path(video_path).name}")
    console.print(f"   Audio: {Path(dubbed_audio_path).name}")
    console.print(f"   SRT:   {Path(clean_srt_path).name}")
    console.print(f"   Output: {Path(output_path).name}\n")

    # Costruisci comando ffmpeg
    if OUTPUT["burn_subtitles"]:
        # Sottotitoli incorporati nel video (hardcoded)
        srt_escaped = clean_srt_path.replace("\\", "/").replace(":", "\\:")
        subtitle_filter = (
            f"subtitles='{srt_escaped}'"
            f":force_style='FontSize={OUTPUT['subtitle_font_size']},"
            f"PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,"
            f"Outline=2,Shadow=1,"
            f"Alignment=2'"
        )
        vf_filter = subtitle_filter
    else:
        vf_filter = None

    # Comando ffmpeg base
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,           # Input video originale
        "-i", dubbed_audio_path,    # Input audio doppiato
        "-map", "0:v:0",            # Prendi video dal primo input
        "-map", "1:a:0",            # Prendi audio dal secondo input
        "-c:v", OUTPUT["video_codec"],
        "-crf", str(OUTPUT["video_crf"]),
        "-c:a", OUTPUT["audio_codec"],
        "-b:a", OUTPUT["audio_bitrate"],
        "-shortest",                # Termina quando finisce il più corto
    ]

    # Aggiungi filtro sottotitoli se richiesto
    if vf_filter:
        cmd.extend(["-vf", vf_filter])

    cmd.append(output_path)

    # Esegui ffmpeg
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Rendering video finale...", total=None)

        result = subprocess.run(cmd, capture_output=True, text=True)
        progress.update(task, completed=True)

    if result.returncode != 0:
        console.print(f"[red]❌ Errore ffmpeg:[/red]")
        console.print(result.stderr[-2000:])  # Ultimi 2000 char dell'errore
        raise RuntimeError("Errore nella composizione video")

    # Verifica output
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        console.print(f"[green]✅ Video finale creato![/green]")
        console.print(f"   📁 {output_path}")
        console.print(f"   📦 Dimensione: {size_mb:.1f} MB")
    else:
        raise RuntimeError("File output non trovato dopo ffmpeg")

    return output_path


def _clean_srt_for_subtitles(srt_path: str) -> str:
    """
    Crea versione pulita del SRT per i sottotitoli:
    - Rimuove tag [spk0], [spk1], ecc.
    - Aggiunge nome speaker come prefisso leggibile (opzionale)
    """
    import srt as srt_lib

    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    subtitles = list(srt_lib.parse(content))

    # Mappa speaker → nome visualizzato (personalizzabile)
    speaker_names = {
        "spk0": "",  # Nessun prefisso per speaker principale
        "spk1": "",
        "spk2": "",
        "spk3": "",
        "default": ""
    }

    cleaned = []
    for sub in subtitles:
        text = sub.content.strip()

        # Rimuovi tag speaker
        if text.startswith("[") and "]" in text:
            tag_end = text.index("]")
            tag = text[1:tag_end].strip()
            if tag.startswith("spk") or tag == "default":
                display_name = speaker_names.get(tag, "")
                text = text[tag_end + 1:].strip()
                if display_name:
                    text = f"{display_name}: {text}"

        sub.content = text
        cleaned.append(sub)

    # Salva SRT pulito
    clean_path = srt_path.replace(".srt", "_clean.srt")
    with open(clean_path, "w", encoding="utf-8") as f:
        f.write(srt_lib.compose(cleaned))

    return clean_path


def export_srt_only(srt_speaker_path: str, output_dir: str = None) -> str:
    """
    Esporta solo il SRT pulito senza processare il video.
    Utile per testare la diarizzazione.
    """
    if not output_dir:
        output_dir = DIRS["output"]

    os.makedirs(output_dir, exist_ok=True)
    stem = Path(srt_speaker_path).stem.replace("_speakers", "")
    output_path = os.path.join(output_dir, f"{stem}_it_speakers.srt")

    import shutil
    shutil.copy2(srt_speaker_path, output_path)

    console.print(f"[green]✅ SRT esportato: {output_path}[/green]")
    return output_path