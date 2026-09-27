"""
Modulo 2: TTS Multi-voce
Genera audio italiano con voci diverse per ogni speaker
"""

import os
import asyncio
import subprocess
import tempfile
from pathlib import Path
import srt
import edge_tts
from pydub import AudioSegment
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from config import SPEAKER_VOICES, TTS, DIRS

console = Console()


def parse_speaker_srt(srt_path: str) -> list:
    """
    Legge SRT con tag speaker e restituisce lista di segmenti.
    Ogni segmento: {start, end, speaker, text}
    """
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    subtitles = list(srt.parse(content))
    segments = []

    for sub in subtitles:
        text = sub.content.strip()
        speaker = "default"

        # Estrai tag speaker: [spk0] testo → speaker=spk0, text=testo
        if text.startswith("[") and "]" in text:
            tag_end = text.index("]")
            tag = text[1:tag_end].strip()
            if tag.startswith("spk") or tag == "default":
                speaker = tag
                text = text[tag_end + 1:].strip()

        segments.append({
            "index": sub.index,
            "start": sub.start.total_seconds(),
            "end": sub.end.total_seconds(),
            "duration": (sub.end - sub.start).total_seconds(),
            "speaker": speaker,
            "text": text,
            "voice": SPEAKER_VOICES.get(speaker, SPEAKER_VOICES["default"])
        })

    return segments


async def generate_tts_segment(text: str, voice: str, output_path: str,
                                rate: str = "+0%", volume: str = "+0%",
                                pitch: str = "+0Hz"):
    """Genera un segmento audio TTS con Edge-TTS."""
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch
    )
    await communicate.save(output_path)


def stretch_audio(audio: AudioSegment, target_duration_ms: float) -> AudioSegment:
    """
    Adatta la durata dell'audio al target usando ffmpeg.
    Evita distorsioni eccessive limitando il fattore di stretch.
    """
    current_duration = len(audio)
    if current_duration == 0:
        return audio

    ratio = target_duration_ms / current_duration

    # Limita il fattore di stretch
    ratio = max(TTS["min_stretch"], min(TTS["max_stretch"], ratio))

    if abs(ratio - 1.0) < 0.05:  # Differenza < 5% → non modificare
        return audio

    # Usa ffmpeg atempo per stretch audio
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_in:
        audio.export(tmp_in.name, format="wav")
        tmp_in_path = tmp_in.name

    tmp_out_path = tmp_in_path.replace(".wav", "_stretched.wav")

    # atempo accetta valori tra 0.5 e 2.0
    # Per ratio fuori range, concatena filtri
    if 0.5 <= ratio <= 2.0:
        atempo = f"atempo={ratio:.4f}"
    elif ratio < 0.5:
        atempo = f"atempo={ratio*2:.4f},atempo=0.5"
    else:
        atempo = f"atempo=2.0,atempo={ratio/2:.4f}"

    cmd = [
        "ffmpeg", "-y", "-i", tmp_in_path,
        "-filter:a", atempo,
        tmp_out_path
    ]
    subprocess.run(cmd, capture_output=True)

    result = AudioSegment.from_wav(tmp_out_path)

    # Cleanup
    os.unlink(tmp_in_path)
    if os.path.exists(tmp_out_path):
        os.unlink(tmp_out_path)

    return result


def build_audio_track(segments: list, total_duration_sec: float) -> AudioSegment:
    """
    Costruisce la traccia audio completa posizionando
    ogni segmento TTS al timestamp corretto.
    """
    console.print("\n[cyan]🔊 Generazione traccia audio italiana...[/cyan]\n")

    # Crea traccia silenziosa della durata totale
    total_ms = int(total_duration_sec * 1000) + 1000  # +1 sec margine
    track = AudioSegment.silent(duration=total_ms)

    # Mostra tabella speaker → voce
    table = Table(title="🎭 Assegnazione voci", show_header=True)
    table.add_column("Speaker", style="cyan")
    table.add_column("Voce Edge-TTS", style="green")
    table.add_column("Battute", style="yellow")

    speaker_counts = {}
    speaker_voices_used = {}
    for seg in segments:
        spk = seg["speaker"]
        speaker_counts[spk] = speaker_counts.get(spk, 0) + 1
        speaker_voices_used[spk] = seg["voice"]

    for spk in sorted(speaker_voices_used.keys()):
        table.add_row(spk, speaker_voices_used[spk], str(speaker_counts[spk]))

    console.print(table)
    console.print()

    # Genera ogni segmento TTS
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Generazione TTS...", total=len(segments))

        for i, seg in enumerate(segments):
            if not seg["text"].strip():
                progress.advance(task)
                continue

            # Percorso file temporaneo
            seg_path = os.path.join(
                DIRS["tts_segments"],
                f"seg_{i:04d}_{seg['speaker']}.mp3"
            )

            try:
                # Genera TTS
                asyncio.run(generate_tts_segment(
                    text=seg["text"],
                    voice=seg["voice"],
                    output_path=seg_path,
                    rate=TTS["rate"],
                    volume=TTS["volume"],
                    pitch=TTS["pitch"]
                ))

                # Carica audio generato
                audio_seg = AudioSegment.from_mp3(seg_path)

                # Adatta durata al timestamp SRT
                target_ms = seg["duration"] * 1000
                if TTS["stretch_audio"] and target_ms > 0:
                    audio_seg = stretch_audio(audio_seg, target_ms)

                # Posiziona nella traccia al timestamp corretto
                start_ms = int(seg["start"] * 1000)
                track = track.overlay(audio_seg, position=start_ms)

            except Exception as e:
                console.print(f"[red]⚠️  Errore segmento {i} ({seg['speaker']}): {e}[/red]")

            progress.advance(task)

    console.print("\n[green]✅ Traccia audio generata![/green]")
    return track


def mix_with_background(dubbed_track: AudioSegment,
                         original_audio_path: str) -> AudioSegment:
    """
    Mixa la traccia doppiata con la musica di sottofondo originale.
    Separa voce e musica dall'originale, mantiene solo la musica.
    """
    console.print("\n[cyan]🎵 Mixaggio con musica di sottofondo...[/cyan]")
    console.print("[dim]Nota: separazione voce/musica richiede demucs (opzionale)[/dim]")

    try:
        import demucs
        # Se demucs è disponibile, separa voce da musica
        console.print("[yellow]⚠️  demucs non configurato - skip mixaggio BGM[/yellow]")
    except ImportError:
        console.print("[yellow]⚠️  demucs non installato - skip mixaggio BGM[/yellow]")
        console.print("[dim]   Installa con: pip install demucs[/dim]")

    return dubbed_track


def export_audio(track: AudioSegment, output_path: str):
    """Esporta la traccia audio finale."""
    track.export(output_path, format="wav", parameters=["-ar", "44100"])
    console.print(f"[green]✅ Audio esportato: {output_path}[/green]")


def generate_tts(srt_speaker_path: str,
                 total_duration_sec: float,
                 output_audio_path: str = None) -> str:
    """
    Pipeline completa TTS multi-voce.

    Args:
        srt_speaker_path: SRT con tag speaker ([spk0], [spk1], ...)
        total_duration_sec: Durata totale del video in secondi
        output_audio_path: Percorso output audio

    Returns:
        Percorso file audio generato
    """
    console.print("\n" + "="*50)
    console.print("[bold magenta]🔊 MODULO 2: TTS MULTI-VOCE[/bold magenta]")
    console.print("="*50 + "\n")

    # Crea cartelle temp
    os.makedirs(DIRS["tts_segments"], exist_ok=True)

    # Step 1: Leggi SRT con speaker
    segments = parse_speaker_srt(srt_speaker_path)
    console.print(f"[green]✅ Letti {len(segments)} segmenti dal SRT[/green]")

    # Step 2: Costruisci traccia audio
    track = build_audio_track(segments, total_duration_sec)

    # Step 3: Esporta
    if not output_audio_path:
        output_audio_path = os.path.join(DIRS["temp"], "dubbed_audio.wav")

    export_audio(track, output_audio_path)
    return output_audio_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python tts_engine.py speaker.srt durata_secondi [output.wav]")
        sys.exit(1)

    srt_file = sys.argv[1]
    duration = float(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else None

    result = generate_tts(srt_file, duration, out)
    print(f"\nAudio generato: {result}")