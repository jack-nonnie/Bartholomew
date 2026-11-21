"""Build comparison videos for a model bake-off.

reel:  every clip back-to-back with a label and its own audio (to judge sound + motion)
grid:  the models side by side per shot, silent (to judge look + consistency)
"""
import subprocess
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H = 540, 960


def _label(text: str) -> str:
    t = text.replace(":", r"\:").replace("'", "")
    return (f"drawtext=fontfile={FONT}:text='{t}':fontsize=30:fontcolor=white:"
            f"box=1:boxcolor=black@0.55:boxborderw=12:x=(w-text_w)/2:y=40")


def _norm_v(i: int, label: str) -> str:
    return (f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=24,"
            f"format=yuv420p,setsar=1,{_label(label)}")


def has_audio(p: Path) -> bool:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                        "stream=index", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return bool(r.stdout.strip())


def duration(p: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


def reel(items: list[tuple[Path, str]], out: Path) -> Path:
    inputs, f, cat = [], [], []
    for i, (clip, label) in enumerate(items):
        inputs += ["-i", str(clip)]
        f.append(_norm_v(i, label) + f"[v{i}]")
        if has_audio(clip):
            f.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        else:
            f.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{duration(clip):.3f}[a{i}]")
        cat.append(f"[v{i}][a{i}]")
    f.append("".join(cat) + f"concat=n={len(items)}:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(f),
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-c:a", "aac",
                    "-movflags", "+faststart", str(out)], check=True)
    return out


def grid(rows: list[list[tuple[Path, str]]], out: Path) -> Path:
    """rows = one list per shot; each row is the models side by side. Rows play one after another."""
    inputs, f, row_names = [], [], []
    n = 0
    for r, row in enumerate(rows):
        shortest = min(duration(c) for c, _ in row)
        names = []
        for clip, label in row:
            inputs += ["-i", str(clip)]
            f.append(_norm_v(n, label) + f",trim=0:{shortest:.3f},setpts=PTS-STARTPTS[g{n}]")
            names.append(f"[g{n}]")
            n += 1
        f.append("".join(names) + f"hstack=inputs={len(row)}[row{r}]")
        row_names.append(f"[row{r}]")
    f.append("".join(row_names) + f"concat=n={len(rows)}:v=1:a=0[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(f),
                    "-map", "[v]", "-c:v", "libx264", "-crf", "20", "-movflags", "+faststart",
                    str(out)], check=True)
    return out
