"""Generation steps: character sheet, keyframes, animation, audio, final edit."""
import json, subprocess
from pathlib import Path

from . import config, prompts
from .fal import run, download, file_uri, first_url

SHEET_VIEWS = {
    "front":     "full body, facing the camera straight on, sitting",
    "three_q":   "full body, three-quarter view turned to the left, sitting",
    "side":      "full body, side profile facing left, sitting",
    "back":      "full body, seen from behind, sitting",
    "happy":     "close-up portrait, huge delighted open smile, eyes squeezed into happy arcs",
    "surprised": "close-up portrait, wide-eyed surprised expression, little round open mouth",
}


# ---------- model argument builders (each model names its inputs differently) ----------

def image_args(model: str, prompt: str, refs: list[str]) -> dict:
    uris = [file_uri(r) for r in refs]
    if model == "nano_banana":
        return {"prompt": prompt, "image_urls": uris, "num_images": 1,
                "aspect_ratio": "9:16", "output_format": "png"}
    if model == "nano_banana_21":
        return {"prompt": prompt, "image_urls": uris, "num_images": 1, "aspect_ratio": "9:16",
                "resolution": "1K", "output_format": "png"}
    if model == "seedream55":
        return {"prompt": prompt, "image_urls": uris, "num_images": 1, "image_size": "portrait_16_9"}
    if model == "seedream":
        return {"prompt": prompt, "image_urls": uris, "num_images": 1,
                "image_size": {"width": 1152, "height": 2048}}
    if model == "kontext_multi":
        return {"prompt": prompt, "image_urls": uris, "aspect_ratio": "9:16"}
    raise ValueError(model)


def clip_seconds(model: str, duration: int) -> int:
    """Seconds actually billed/generated for a shot (Veo only offers 4/6/8s)."""
    if model.startswith("veo"):
        return 4 if duration <= 4 else 6 if duration <= 6 else 8
    return max(duration, 4 if model.startswith("seedance") else 3)


def video_args(model: str, prompt: str, negative: str, image: str, duration: int) -> dict:
    uri = file_uri(image)
    secs = clip_seconds(model, duration)
    if model.startswith("kling_v4"):
        a = {"prompt": prompt, "start_image_url": uri, "duration": secs, "resolution": "720p"}
        return a
    if model.startswith("veo31"):
        return {"prompt": prompt, "image_url": uri, "duration": f"{secs}s", "negative_prompt": negative,
                "generate_audio": True, "resolution": "720p", "aspect_ratio": "9:16"}
    if model.startswith("seedance25"):
        return {"prompt": prompt, "image_url": uri, "duration": str(secs), "resolution": "720p",
                "aspect_ratio": "9:16", "generate_audio": True}
    raise ValueError(model)


def _ref_images(style_id: str | None = None) -> list[str]:
    """Bear photos (or approved sheet) first, then the style's rendering references last."""
    char = config.character()
    sheet = config.ROOT / "character" / "sheet"
    approved = sorted(sheet.glob("*.png")) if sheet.exists() else []
    refs = [str(p) for p in approved] or char["reference_images"]
    missing = [r for r in refs if not (config.ROOT / r).exists()]
    if missing:
        raise SystemExit(f"Missing reference images: {missing}\nPut the bear photos in character/photos/.")
    refs = refs[:6]
    if style_id:
        refs += config.style(style_id).get("style_refs", [])
    return refs


# ---------- step 1: character sheet ----------

def sheet(style_id: str, image_model: str, views: list[str] | None = None) -> list[Path]:
    m = config.models()["image_models"][image_model]
    char = config.character()
    sty = config.style(style_id)
    out = config.ROOT / "output" / "_sheet" / f"{style_id}_{image_model}"
    log = out.parent / "cost.json"
    files = []
    for view in views or SHEET_VIEWS:
        p = (f"Character turnaround sheet image. Recreate this exact plush from the reference photos: "
             f"{char['identity']} Pose: {SHEET_VIEWS[view]}. Plain soft warm-cream seamless background. "
             f"Style: {sty['prompt']} Keep exactly: {'; '.join(char['must_keep'])}.")
        r = run(m["endpoint"], image_args(image_model, p, char["reference_images"]),
                est_cost=m["est_cost"], log=log, label=f"sheet {style_id}/{image_model}/{view}")
        files.append(download(first_url(r, "images", "image"), out / f"{view}.png"))
    return files


# ---------- step 2: keyframes ----------

def keyframes(ep_name: str, image_model: str | None = None, style_id: str | None = None,
              shot_ids: list[str] | None = None, variants: int = 1) -> list[Path]:
    ep = config.episode(ep_name)
    if not ep.get("approved"):
        raise SystemExit("Episode script not approved yet (set `approved: true` after review).")
    cfg = config.models()
    image_model = image_model or ep.get("image_model") or cfg["defaults"]["image_model"]
    style_id = style_id or ep["style"]
    m = cfg["image_models"][image_model]
    out = config.out_dir(ep_name) / "keyframes" / f"{style_id}_{image_model}"
    log = config.out_dir(ep_name) / "cost.json"
    refs = _ref_images(style_id)
    files = []
    for shot in ep["shots"]:
        if shot_ids and shot["id"] not in shot_ids:
            continue
        p = prompts.keyframe_prompt(shot, ep, style_id)
        for v in range(variants):
            prompt = p if v == 0 else p + f" (variation {v + 1})"
            r = run(m["endpoint"], image_args(image_model, prompt, refs), est_cost=m["est_cost"],
                    log=log, label=f"keyframe {shot['id']} v{v + 1}")
            files.append(download(first_url(r, "images", "image"), out / f"{shot['id']}_v{v + 1}.png"))
    return files


# ---------- step 3: animate ----------

def animate(ep_name: str, keyframe_dir: str, video_model: str | None = None,
            shot_ids: list[str] | None = None, style_id: str | None = None,
            require_approval: bool = True) -> list[Path]:
    ep = config.episode(ep_name)
    if require_approval and not ep.get("keyframes_approved"):
        raise SystemExit("Keyframes not approved yet (set `keyframes_approved: true` after review).")
    cfg = config.models()
    video_model = video_model or ep.get("video_model") or cfg["defaults"]["video_model"]
    m = cfg["video_models"][video_model]
    style_id = style_id or ep["style"]
    kdir = config.ROOT / keyframe_dir
    out = config.out_dir(ep_name) / "clips" / f"{kdir.name}_{video_model}"
    log = config.out_dir(ep_name) / "cost.json"
    files = []
    for shot in ep["shots"]:
        if shot_ids and shot["id"] not in shot_ids:
            continue
        if shot.get("lock_clip") and (out / f"{shot['id']}.mp4").exists():
            print(f"  [locked] {shot['id']} (keeping approved clip)")
            files.append(out / f"{shot['id']}.mp4")
            continue
        chosen = shot.get("keyframe_pick", 1)
        img = kdir / f"{shot['id']}_v{chosen}.png"
        args = video_args(video_model, prompts.video_prompt(shot, ep, style_id),
                          prompts.negative_prompt(ep, style_id), str(img), shot["duration"])
        secs = clip_seconds(video_model, shot["duration"])
        r = run(m["endpoint"], args, est_cost=m["est_cost_per_sec"] * secs, log=log,
                label=f"clip {shot['id']} ({video_model})")
        url = first_url(r, "video")
        (out / f"{shot['id']}.url").parent.mkdir(parents=True, exist_ok=True)
        (out / f"{shot['id']}.url").write_text(url)
        files.append(download(url, out / f"{shot['id']}.mp4"))
    return files


# ---------- step 4: audio ----------

def has_audio(path: Path) -> bool:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                        "stream=index", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return bool(r.stdout.strip())


def add_sfx(ep_name: str, clip_dir: str) -> list[Path]:
    """Give every silent clip matching sound effects (video-to-audio)."""
    ep = config.episode(ep_name)
    m = config.models()["audio_models"]["sfx"]
    cdir = config.ROOT / clip_dir
    log = config.out_dir(ep_name) / "cost.json"
    files = []
    for shot in ep["shots"]:
        clip = cdir / f"{shot['id']}.mp4"
        if not clip.exists():
            continue
        if has_audio(clip):
            files.append(clip)
            continue
        url_file = cdir / f"{shot['id']}.url"
        video_url = url_file.read_text().strip() if url_file.exists() else file_uri(clip)
        r = run(m["endpoint"], {"video_url": video_url, "prompt": prompts.sfx_prompt(shot),
                                "negative_prompt": "music, speech, voices",
                                "duration": shot["duration"]},
                est_cost=m["est_cost"], log=log, label=f"sfx {shot['id']}")
        files.append(download(first_url(r, "video"), cdir / "sfx" / f"{shot['id']}.mp4"))
    return files


def music(ep_name: str) -> Path:
    ep = config.episode(ep_name)
    m = config.models()["audio_models"]["music"]
    log = config.out_dir(ep_name) / "cost.json"
    secs = ep.get("music", {}).get("duration", 25)
    if m["endpoint"].startswith("elevenlabs/music"):
        args = {"prompt": prompts.music_prompt(ep), "music_length_ms": int(secs * 1000),
                "force_instrumental": True}
        name = "music.mp3"
    else:
        args = {"prompt": prompts.music_prompt(ep), "seconds_total": secs}
        name = "music.wav"
    r = run(m["endpoint"], args, est_cost=m["est_cost"], log=log, label="music bed")
    return download(first_url(r, "audio", "audio_file"), config.out_dir(ep_name) / name)


# ---------- step 5: edit ----------

def edit(ep_name: str, clips: list[Path], music_file: Path | None, xfade: float = 0.4) -> Path:
    """Scale to 1080x1920, crossfade clips, apply the series grade, mix music under SFX."""
    out = config.out_dir(ep_name) / "final.mp4"
    grade = "eq=saturation=1.06:contrast=1.03,colorbalance=rs=0.02:bs=-0.02"
    inputs, filters = [], []
    durs = []
    for i, c in enumerate(clips):
        inputs += ["-i", str(c)]
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                  "-of", "csv=p=0", str(c)], capture_output=True, text=True).stdout)
        durs.append(d)
        filters.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                       f"fps=24,format=yuv420p,{grade},setpts=PTS-STARTPTS[v{i}]")
        if has_audio(c):
            filters.append(f"[{i}:a]aresample=48000,asetpts=PTS-STARTPTS[a{i}]")
        else:
            filters.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{d}[a{i}]")
    v, a, offset = "v0", "a0", 0.0
    for i in range(1, len(clips)):
        offset += durs[i - 1] - xfade
        filters.append(f"[{v}][v{i}]xfade=transition=fade:duration={xfade}:offset={offset:.3f}[vx{i}]")
        filters.append(f"[{a}][a{i}]acrossfade=d={xfade}[ax{i}]")
        v, a = f"vx{i}", f"ax{i}"
    total = sum(durs) - xfade * (len(clips) - 1)
    if music_file:
        inputs += ["-i", str(music_file)]
        mi = len(clips)
        filters.append(f"[{mi}:a]aresample=48000,volume=0.35,atrim=0:{total:.3f},"
                       f"afade=t=out:st={max(total - 1.5, 0):.3f}:d=1.5[mus]")
        filters.append(f"[{a}][mus]amix=inputs=2:duration=first:normalize=0[amixed]")
        a = "amixed"
    filters.append(f"[{a}]alimiter=limit=0.89:level=false,afade=t=out:st={max(total - 0.6, 0):.3f}:d=0.6[afinal]")
    a = "afinal"
    filters.append(f"[{v}]fade=t=in:d=0.4,fade=t=out:st={max(total - 0.6, 0):.3f}:d=0.6[vfinal]")
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
           "-map", "[vfinal]", "-map", f"[{a}]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True, capture_output=True)
    return out


def default_dirs(ep_name: str) -> dict:
    """Where this episode's keyframes and clips live, from its own style/model settings."""
    ep = config.episode(ep_name)
    d = config.models()["defaults"]
    style = ep["style"]
    im = ep.get("image_model") or d["image_model"]
    vm = ep.get("video_model") or d["video_model"]
    kdir = f"output/{ep_name}/keyframes/{style}_{im}"
    return {"keyframes": kdir, "clips": f"output/{ep_name}/clips/{style}_{im}_{vm}"}


def estimate(ep_name: str) -> dict:
    ep = config.episode(ep_name)
    cfg = config.models()
    im = cfg["image_models"][ep.get("image_model") or cfg["defaults"]["image_model"]]
    vm_name = ep.get("video_model") or cfg["defaults"]["video_model"]
    vm = cfg["video_models"][vm_name]
    n = len(ep["shots"])
    secs = sum(clip_seconds(vm_name, s["duration"]) for s in ep["shots"])
    sfx = 0 if vm.get("native_audio") else n * cfg["audio_models"]["sfx"]["est_cost"]
    est = {"keyframes": n * im["est_cost"] * 2, "video": secs * vm["est_cost_per_sec"],
           "audio": sfx + cfg["audio_models"]["music"]["est_cost"]}
    est["total_first_pass"] = round(sum(est.values()), 2)
    return est
