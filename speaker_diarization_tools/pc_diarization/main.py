"""
Speaker Diarization PC Tool - Main Entry Point
Interfaccia a riga di comando con menu interattivo
"""

import os
import sys
import time
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich import box

console = Console()


def print_banner():
    console.print(Panel.fit(
        "[bold magenta]🎬 Speaker Diarization PC Tool[/bold magenta]\n"
        "[dim]Diarizzazione + TTS Multi-voce per film[/dim]\n"
        "[dim]Versione 1.0 - Settembre 2026[/dim]",
        border_style="magenta"
    ))


def check_dependencies():
    """Verifica che tutte le dipendenze siano installate."""
    console.print("\n[cyan]🔍 Verifica dipendenze...[/cyan]")
    missing = []

    deps = {
        "pyannote.audio": "pyannote.audio",
        "torch": "torch",
        "edge_tts": "edge-tts",
        "pydub": "pydub",
        "srt": "srt",
        "rich": "rich",
        "ffmpeg": None,  # Verifica separata
    }

    for module, package in deps.items():
        if module == "ffmpeg":
            import subprocess
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True
            )
            if result.returncode != 0:
                missing.append("ffmpeg (installa da ffmpeg.org)")
            else:
                console.print(f"  [green]✅ ffmpeg[/green]")
        else:
            try:
                __import__(module)
                console.print(f"  [green]✅ {module}[/green]")
            except ImportError:
                console.print(f"  [red]❌ {module}[/red]")
                missing.append(package)

    if missing:
        console.print(f"\n[red]❌ Dipendenze mancanti:[/red]")
        for m in missing:
            console.print(f"   pip install {m}")
        console.print("\n[yellow]Installa con:[/yellow]")
        console.print("  pip install -r requirements.txt")
        return False

    console.print("\n[green]✅ Tutte le dipendenze sono installate![/green]")
    return True


def check_config():
    """Verifica la configurazione."""
    from config import HUGGINGFACE_TOKEN

    if "INSERISCI" in HUGGINGFACE_TOKEN or not HUGGINGFACE_TOKEN.startswith("hf_"):
        console.print("\n[red]❌ Token HuggingFace non configurato![/red]")
        console.print("   Apri config.py e inserisci il tuo token HuggingFace")
        console.print("   Ottienilo su: https://huggingface.co/settings/tokens")

        # Chiedi token interattivamente
        token = Prompt.ask("\n[yellow]Inserisci il token HuggingFace ora[/yellow]")
        if token.startswith("hf_"):
            # Salva nel config
            config_path = os.path.join(os.path.dirname(__file__), "config.py")
            with open(config_path, "r") as f:
                content = f.read()
            content = content.replace(
                'HUGGINGFACE_TOKEN = "hf_INSERISCI_IL_TUO_TOKEN_QUI"',
                f'HUGGINGFACE_TOKEN = "{token}"'
            )
            with open(config_path, "w") as f:
                f.write(content)
            console.print("[green]✅ Token salvato in config.py[/green]")
            return True
        else:
            console.print("[red]❌ Token non valido (deve iniziare con hf_)[/red]")
            return False

    console.print("[green]✅ Token HuggingFace configurato[/green]")
    return True


def mode_full_pipeline():
    """Modalità 1: Pipeline completa (diarizzazione + TTS + video)."""
    console.print(Panel(
        "[bold]Modalità: Pipeline Completa[/bold]\n"
        "Diarizzazione → TTS Multi-voce → Video Finale",
        border_style="cyan"
    ))

    # Input video
    video_path = Prompt.ask("\n📹 Percorso video originale (inglese)")
    if not os.path.exists(video_path):
        console.print(f"[red]❌ File non trovato: {video_path}[/red]")
        return

    # Input SRT
    srt_path = Prompt.ask("📄 Percorso SRT italiano (dal telefono)")
    if not os.path.exists(srt_path):
        console.print(f"[red]❌ File non trovato: {srt_path}[/red]")
        return

    # Numero speaker
    console.print("\n[dim]Quanti personaggi parlano nel video?[/dim]")
    console.print("[dim](0 = rilevamento automatico, consigliato per film)[/dim]")
    n_speakers = IntPrompt.ask("Numero speaker", default=0)
    num_speakers = None if n_speakers == 0 else n_speakers

    # Mostra voci assegnate
    from config import SPEAKER_VOICES
    table = Table(title="🎭 Voci assegnate", box=box.ROUNDED)
    table.add_column("Speaker", style="cyan")
    table.add_column("Voce Edge-TTS", style="green")
    for spk, voice in list(SPEAKER_VOICES.items())[:6]:
        if spk != "default":
            table.add_row(spk, voice)
    console.print(table)

    change_voices = Confirm.ask("\nVuoi modificare le voci?", default=False)
    if change_voices:
        _configure_voices_interactive()

    # Conferma
    console.print(f"\n[bold]Riepilogo:[/bold]")
    console.print(f"  Video: {video_path}")
    console.print(f"  SRT:   {srt_path}")
    console.print(f"  Speaker: {'auto' if not num_speakers else num_speakers}")

    if not Confirm.ask("\n▶️  Avvia elaborazione?", default=True):
        return

    start_time = time.time()

    try:
        # Step 1: Diarizzazione
        from diarizer import diarize
        speaker_srt = diarize(video_path, srt_path, num_speakers)

        # Step 2: Ottieni durata video
        from video_composer import get_video_duration
        duration = get_video_duration(video_path)

        # Step 3: TTS
        from tts_engine import generate_tts
        dubbed_audio = generate_tts(speaker_srt, duration)

        # Step 4: Composizione video
        from video_composer import compose_video
        output_video = compose_video(video_path, dubbed_audio, speaker_srt)

        elapsed = time.time() - start_time
        console.print(Panel(
            f"[bold green]🎉 COMPLETATO![/bold green]\n\n"
            f"📁 Video doppiato: [cyan]{output_video}[/cyan]\n"
            f"⏱️  Tempo totale: [yellow]{elapsed/60:.1f} minuti[/yellow]",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]❌ Errore: {e}[/red]")
        import traceback
        traceback.print_exc()


def mode_diarization_only():
    """Modalità 2: Solo diarizzazione → produce SRT con speaker."""
    console.print(Panel(
        "[bold]Modalità: Solo Diarizzazione[/bold]\n"
        "Produce SRT con tag speaker [spk0], [spk1]...",
        border_style="cyan"
    ))

    video_path = Prompt.ask("\n📹 Percorso video originale")
    if not os.path.exists(video_path):
        console.print(f"[red]❌ File non trovato: {video_path}[/red]")
        return

    srt_path = Prompt.ask("📄 Percorso SRT italiano")
    if not os.path.exists(srt_path):
        console.print(f"[red]❌ File non trovato: {srt_path}[/red]")
        return

    n_speakers = IntPrompt.ask("Numero speaker (0=auto)", default=0)
    num_speakers = None if n_speakers == 0 else n_speakers

    start_time = time.time()

    try:
        from diarizer import diarize
        from video_composer import export_srt_only

        speaker_srt = diarize(video_path, srt_path, num_speakers)
        output_srt = export_srt_only(speaker_srt)

        elapsed = time.time() - start_time
        console.print(Panel(
            f"[bold green]✅ Diarizzazione completata![/bold green]\n\n"
            f"📄 SRT con speaker: [cyan]{output_srt}[/cyan]\n"
            f"⏱️  Tempo: [yellow]{elapsed/60:.1f} minuti[/yellow]\n\n"
            f"[dim]Trasferisci questo file all'app TTS[/dim]",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]❌ Errore: {e}[/red]")
        import traceback
        traceback.print_exc()


def mode_tts_only():
    """Modalità 3: Solo TTS da SRT con speaker già identificati."""
    console.print(Panel(
        "[bold]Modalità: Solo TTS[/bold]\n"
        "Genera audio doppiato da SRT con speaker tags",
        border_style="cyan"
    ))

    srt_path = Prompt.ask("\n📄 Percorso SRT con speaker tags")
    if not os.path.exists(srt_path):
        console.print(f"[red]❌ File non trovato: {srt_path}[/red]")
        return

    video_path = Prompt.ask("📹 Percorso video originale (per durata)")
    if not os.path.exists(video_path):
        console.print(f"[red]❌ File non trovato: {video_path}[/red]")
        return

    start_time = time.time()

    try:
        from video_composer import get_video_duration, compose_video
        from tts_engine import generate_tts

        duration = get_video_duration(video_path)
        dubbed_audio = generate_tts(srt_path, duration)
        output_video = compose_video(video_path, dubbed_audio, srt_path)

        elapsed = time.time() - start_time
        console.print(Panel(
            f"[bold green]🎉 COMPLETATO![/bold green]\n\n"
            f"📁 Video: [cyan]{output_video}[/cyan]\n"
            f"⏱️  Tempo: [yellow]{elapsed/60:.1f} minuti[/yellow]",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[red]❌ Errore: {e}[/red]")
        import traceback
        traceback.print_exc()


def mode_configure_voices():
    """Modalità 4: Configura voci per speaker."""
    _configure_voices_interactive()


def _configure_voices_interactive():
    """Interfaccia interattiva per configurare le voci."""
    console.print("\n[bold]🎭 Configurazione voci Edge-TTS[/bold]")

    available_voices = [
        ("it-IT-GiuseppeNeural", "Maschile - Naturale ⭐⭐⭐⭐⭐"),
        ("it-IT-DiegoNeural",    "Maschile - Alternativo ⭐⭐⭐⭐"),
        ("it-IT-ElsaNeural",     "Femminile - Naturale ⭐⭐⭐⭐⭐"),
        ("it-IT-IsabellaNeural", "Femminile - Alternativa ⭐⭐⭐⭐"),
    ]

    table = Table(title="Voci disponibili", box=box.ROUNDED)
    table.add_column("N.", style="dim")
    table.add_column("Voce", style="cyan")
    table.add_column("Descrizione", style="green")
    for i, (voice, desc) in enumerate(available_voices):
        table.add_row(str(i+1), voice, desc)
    console.print(table)

    from config import SPEAKER_VOICES
    import config

    for spk in ["spk0", "spk1", "spk2", "spk3"]:
        current = SPEAKER_VOICES.get(spk, SPEAKER_VOICES["default"])
        console.print(f"\n[cyan]{spk}[/cyan] (attuale: {current})")
        choice = IntPrompt.ask(
            f"Scegli voce per {spk} (1-{len(available_voices)}, 0=mantieni)",
            default=0
        )
        if 1 <= choice <= len(available_voices):
            SPEAKER_VOICES[spk] = available_voices[choice-1][0]
            console.print(f"  → {available_voices[choice-1][0]}")

    console.print("\n[green]✅ Voci configurate![/green]")
    console.print("[dim]Nota: per salvare permanentemente, modifica config.py[/dim]")


def main():
    print_banner()

    # Verifica dipendenze
    if not check_dependencies():
        sys.exit(1)

    # Verifica config
    if not check_config():
        sys.exit(1)

    # Menu principale
    while True:
        console.print("\n" + "─"*50)
        console.print("[bold]📋 MENU PRINCIPALE[/bold]\n")
        console.print("  [cyan]1[/cyan] Pipeline completa (diarizzazione + TTS + video)")
        console.print("  [cyan]2[/cyan] Solo diarizzazione → SRT con speaker")
        console.print("  [cyan]3[/cyan] Solo TTS → video doppiato da SRT")
        console.print("  [cyan]4[/cyan] Configura voci speaker")
        console.print("  [cyan]0[/cyan] Esci")
        console.print()

        choice = Prompt.ask("Scelta", choices=["0","1","2","3","4"], default="1")

        if choice == "0":
            console.print("\n[dim]Arrivederci! 🎬[/dim]\n")
            break
        elif choice == "1":
            mode_full_pipeline()
        elif choice == "2":
            mode_diarization_only()
        elif choice == "3":
            mode_tts_only()
        elif choice == "4":
            mode_configure_voices()


if __name__ == "__main__":
    # Supporto anche argomenti da riga di comando
    parser = argparse.ArgumentParser(
        description="Speaker Diarization PC Tool"
    )
    parser.add_argument("--video", help="Percorso video originale")
    parser.add_argument("--srt", help="Percorso SRT italiano")
    parser.add_argument("--speakers", type=int, default=0,
                        help="Numero speaker (0=auto)")
    parser.add_argument("--mode", choices=["full","diarize","tts"],
                        default="full", help="Modalità operativa")
    parser.add_argument("--output", help="Percorso output")

    args = parser.parse_args()

    # Se argomenti forniti → modalità non interattiva
    if args.video and args.srt:
        num_speakers = None if args.speakers == 0 else args.speakers

        if args.mode in ["full", "diarize"]:
            from diarizer import diarize
            speaker_srt = diarize(args.video, args.srt, num_speakers)

        if args.mode == "full":
            from video_composer import get_video_duration, compose_video
            from tts_engine import generate_tts
            duration = get_video_duration(args.video)
            dubbed_audio = generate_tts(speaker_srt, duration)
            compose_video(args.video, dubbed_audio, speaker_srt, args.output)

        elif args.mode == "tts" and args.srt:
            from video_composer import get_video_duration, compose_video
            from tts_engine import generate_tts
            duration = get_video_duration(args.video)
            dubbed_audio = generate_tts(args.srt, duration)
            compose_video(args.video, dubbed_audio, args.srt, args.output)
    else:
        # Modalità interattiva
        main()