"""Bartholomew studio CLI. Full runbook: .claude/skills/new-episode/SKILL.md

  python -m studio.cli new       beach_day              # free: copy episodes/_template.yaml
  python -m studio.cli script    beach_day              # free: script + exact prompts -> GATE 1
  python -m studio.cli keyframes beach_day --variants 2 # ~$0.09/image
  python -m studio.cli review    keyframes beach_day    # free: variants grid for self-review + user -> GATE 2
  python -m studio.cli animate   beach_day              # ~$0.79/5s clip (Kling 4.0), run in background
  python -m studio.cli review    clips beach_day        # free: frame contact sheet to check drift
  python -m studio.cli finish    beach_day              # music + edit -> videos/<name>_<episode>.mp4
"""
import argparse, json, shutil, subprocess
from pathlib import Path

from . import config, prompts, pipeline


def script(ep_name: str, style_id: str | None = None) -> Path:
    ep = config.episode(ep_name)
    char = config.character()
    style_id = style_id or ep["style"]
    sty, per = config.style(style_id), config.personality(ep["personality"])
    est = pipeline.estimate(ep_name)
    total = sum(s["duration"] for s in ep["shots"])
    L = [f"# {char['name']}'s {ep['title']} — script for approval", "",
         f"**Style:** {sty['label']} · **Personality:** {per['label']} · **Length:** ~{total}s, 9:16 · "
         f"**Shots:** {len(ep['shots'])}", "",
         f"**Estimated cost (first pass):** ~${est['total_first_pass']} "
         f"(keyframes ${est['keyframes']:.2f}, video ${est['video']:.2f}, audio ${est['audio']:.2f})", "",
         "## Story", ""]
    for i, s in enumerate(ep["shots"], 1):
        L.append(f"{i}. **{s['beat']}** ({s['duration']}s): {' '.join(s['motion'].format(name=char['name']).split())}")
    L += ["", f"**Music:** {prompts.music_prompt(ep)}", "",
          "## Exact prompts", "",
          "The character and style text repeats in every shot on purpose; it keeps the bear consistent.", ""]
    for i, s in enumerate(ep["shots"], 1):
        L += [f"### Shot {i}: {s['beat']} (`{s['id']}`)", "",
              "**Keyframe (image) prompt**", "", "> " + prompts.keyframe_prompt(s, ep, style_id), "",
              "**Animation (video) prompt**", "", "> " + prompts.video_prompt(s, ep, style_id), "",
              f"**Sound effects:** {s['sfx']}", ""]
    L += ["### Negative prompt (all shots)", "", "> " + prompts.negative_prompt(ep, style_id), ""]
    out = config.out_dir(ep_name) / f"script_{style_id}.md"
    out.write_text("\n".join(L))
    return out


def new_episode(name: str) -> Path:
    dest = config.ROOT / "episodes" / f"{name}.yaml"
    if dest.exists():
        raise SystemExit(f"{dest} already exists")
    shutil.copy(config.ROOT / "episodes" / "_template.yaml", dest)
    return dest


def _ff(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def review_keyframes(ep_name: str) -> Path:
    """Grid: one column per shot, one row per variant (v1, v2, ...). Missing cells are blank."""
    ep = config.episode(ep_name)
    kdir = config.ROOT / pipeline.default_dirs(ep_name)["keyframes"]
    shots = [s["id"] for s in ep["shots"]]
    nvar = max([int(p.stem.rsplit("_v", 1)[1]) for p in kdir.glob("*_v*.png")] or [0])
    if not nvar:
        raise SystemExit(f"No keyframes in {kdir}")
    inputs, f, rows = [], [], []
    n = 0
    for v in range(1, nvar + 1):
        cells = []
        for sid in shots:
            img = kdir / f"{sid}_v{v}.png"
            if img.exists():
                inputs += ["-i", str(img)]
                f.append(f"[{n}:v]scale=480:854:force_original_aspect_ratio=decrease,"
                         f"pad=480:854:(ow-iw)/2:(oh-ih)/2:white,setsar=1[c{n}]")
            else:
                inputs += ["-f", "lavfi", "-i", "color=white:s=480x854:d=1"]
                f.append(f"[{n}:v]setsar=1[c{n}]")
            cells.append(f"[c{n}]")
            n += 1
        f.append("".join(cells) + (f"hstack=inputs={len(cells)}" if len(cells) > 1 else "null") + f"[r{v}]")
        rows.append(f"[r{v}]")
    f.append("".join(rows) + (f"vstack=inputs={len(rows)}" if len(rows) > 1 else "null"))
    out = config.out_dir(ep_name) / "review" / "keyframes_grid.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    _ff([*inputs, "-frames:v", "1", "-filter_complex", ";".join(f), str(out)])
    print(f"Columns = shots {shots}; rows = variants v1..v{nvar}")
    return out


def review_clips(ep_name: str, times=(0.3, 1.5, 2.7, 3.9, 4.9)) -> Path:
    """Contact sheet: one row per shot, 5 frames across its duration. Use it to spot drift."""
    ep = config.episode(ep_name)
    cdir = config.ROOT / pipeline.default_dirs(ep_name)["clips"]
    clips = [cdir / f"{s['id']}.mp4" for s in ep["shots"] if (cdir / f"{s['id']}.mp4").exists()]
    if not clips:
        raise SystemExit(f"No clips in {cdir}")
    inputs, f, rows, n = [], [], [], 0
    for r, c in enumerate(clips):
        cells = []
        for t in times:
            inputs += ["-ss", str(t), "-i", str(c)]
            f.append(f"[{n}:v]scale=216:384,setsar=1[f{n}]")
            cells.append(f"[f{n}]")
            n += 1
        f.append("".join(cells) + f"hstack=inputs={len(cells)}[r{r}]")
        rows.append(f"[r{r}]")
    f.append("".join(rows) + (f"vstack=inputs={len(rows)}" if len(rows) > 1 else "null"))
    out = config.out_dir(ep_name) / "review" / "clips_contact_sheet.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    _ff([*inputs, "-frames:v", "1", "-filter_complex", ";".join(f), str(out)])
    print("Rows = " + ", ".join(c.stem for c in clips) + f"; columns = t={list(times)}s")
    return out


def finish(ep_name: str, clip_dir: str | None, use_music: bool = True) -> Path:
    clip_dir = clip_dir or pipeline.default_dirs(ep_name)["clips"]
    clips = pipeline.add_sfx(ep_name, clip_dir)  # only adds SFX to silent clips
    mus = pipeline.music(ep_name) if use_music else None
    final = pipeline.edit(ep_name, clips, mus)
    name = config.character()["name"].lower()
    dest = config.ROOT / "videos" / f"{name}_{ep_name}.mp4"
    dest.parent.mkdir(exist_ok=True)
    shutil.copy(final, dest)
    r = subprocess.run(["ffmpeg", "-i", str(dest), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    levels = [l.split("] ")[-1] for l in r.splitlines() if "_volume" in l]
    print("Audio levels:", "; ".join(levels), "(max should be about -1 dB, mean about -16 to -22 dB)")
    return dest


def main():
    ap = argparse.ArgumentParser(prog="studio")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("new"); s.add_argument("episode")
    s = sub.add_parser("review"); s.add_argument("what", choices=["keyframes", "clips"]); s.add_argument("episode")
    s = sub.add_parser("script"); s.add_argument("episode"); s.add_argument("--style")
    s = sub.add_parser("sheet"); s.add_argument("--style", required=True)
    s.add_argument("--image-model", default="nano_banana"); s.add_argument("--views")
    s = sub.add_parser("keyframes"); s.add_argument("episode"); s.add_argument("--style")
    s.add_argument("--image-model"); s.add_argument("--shots"); s.add_argument("--variants", type=int, default=1)
    s = sub.add_parser("animate"); s.add_argument("episode"); s.add_argument("--keyframes")
    s.add_argument("--video-model"); s.add_argument("--shots"); s.add_argument("--style")
    s.add_argument("--test", action="store_true", help="bake-off mode: skip keyframe approval gate")
    s = sub.add_parser("finish"); s.add_argument("episode"); s.add_argument("--clips")
    s.add_argument("--no-music", action="store_true")
    a = ap.parse_args()
    shots = a.shots.split(",") if getattr(a, "shots", None) else None

    if a.cmd == "new":
        print(new_episode(a.episode))
    elif a.cmd == "review":
        print(review_keyframes(a.episode) if a.what == "keyframes" else review_clips(a.episode))
    elif a.cmd == "script":
        print(script(a.episode, a.style))
    elif a.cmd == "sheet":
        for f in pipeline.sheet(a.style, a.image_model, a.views.split(",") if a.views else None):
            print(f)
    elif a.cmd == "keyframes":
        for f in pipeline.keyframes(a.episode, a.image_model, a.style, shots, a.variants):
            print(f)
    elif a.cmd == "animate":
        kdir = a.keyframes or pipeline.default_dirs(a.episode)["keyframes"]
        for f in pipeline.animate(a.episode, kdir, a.video_model, shots, a.style,
                                  require_approval=not a.test):
            print(f)
    elif a.cmd == "finish":
        print(finish(a.episode, a.clips, not a.no_music))
    log = config.out_dir(getattr(a, "episode", "_sheet")) / "cost.json"
    if log.exists():
        spent = sum(e["est_cost"] for e in json.loads(log.read_text()))
        print(f"Estimated spend so far for this episode: ${spent:.2f}")


if __name__ == "__main__":
    main()
