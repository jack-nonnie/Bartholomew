"""plush-studio CLI.

  python -m studio.cli script  spa_day                 # free: writes the script + exact prompts for review
  python -m studio.cli sheet   --style pixar3d --image-model nano_banana
  python -m studio.cli keyframes spa_day [--variants 2] [--shots s1_arrival,...]
  python -m studio.cli animate spa_day --keyframes output/spa_day/keyframes/pixar3d_nano_banana
  python -m studio.cli finish  spa_day --clips output/spa_day/clips/<dir>
"""
import argparse, json
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


def main():
    ap = argparse.ArgumentParser(prog="studio")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("script"); s.add_argument("episode"); s.add_argument("--style")
    s = sub.add_parser("sheet"); s.add_argument("--style", required=True)
    s.add_argument("--image-model", default="nano_banana"); s.add_argument("--views")
    s = sub.add_parser("keyframes"); s.add_argument("episode"); s.add_argument("--style")
    s.add_argument("--image-model"); s.add_argument("--shots"); s.add_argument("--variants", type=int, default=1)
    s = sub.add_parser("animate"); s.add_argument("episode"); s.add_argument("--keyframes", required=True)
    s.add_argument("--video-model"); s.add_argument("--shots"); s.add_argument("--style")
    s.add_argument("--test", action="store_true", help="bake-off mode: skip keyframe approval gate")
    s = sub.add_parser("finish"); s.add_argument("episode"); s.add_argument("--clips", required=True)
    s.add_argument("--no-music", action="store_true")
    a = ap.parse_args()
    shots = a.shots.split(",") if getattr(a, "shots", None) else None

    if a.cmd == "script":
        print(script(a.episode, a.style))
    elif a.cmd == "sheet":
        for f in pipeline.sheet(a.style, a.image_model, a.views.split(",") if a.views else None):
            print(f)
    elif a.cmd == "keyframes":
        for f in pipeline.keyframes(a.episode, a.image_model, a.style, shots, a.variants):
            print(f)
    elif a.cmd == "animate":
        for f in pipeline.animate(a.episode, a.keyframes, a.video_model, shots, a.style,
                                  require_approval=not a.test):
            print(f)
    elif a.cmd == "finish":
        clips = pipeline.add_sfx(a.episode, a.clips)
        mus = None if a.no_music else pipeline.music(a.episode)
        print(pipeline.edit(a.episode, clips, mus))
    log = config.out_dir(getattr(a, "episode", "_sheet")) / "cost.json"
    if log.exists():
        spent = sum(e["est_cost"] for e in json.loads(log.read_text()))
        print(f"Estimated spend so far for this episode: ${spent:.2f}")


if __name__ == "__main__":
    main()
