# Bartholomew: AI video series

Short AI-generated videos of **Bartholomew**, the user's girlfriend's real Jellycat teddy bear, doing everyday activities. Episode 1, Spa Day, is done: `videos/bartholomew_spa_day.mp4`. The pipeline is a Python package (`studio/`) driving fal.ai models, with ffmpeg for editing.

## Start here
- **New video, or changing an existing one:** use the **`new-episode` skill** (`.claude/skills/new-episode/SKILL.md`). It's the complete runbook.
- **Choosing or replacing a model, or cutting costs:** use the **`model-scout` skill**.
- **Before any episode:** read `docs/LESSONS.md` (what worked and what failed, plus the user's preferences) and the top of `docs/EPISODE_LOG.md`.
- **Free pre-flight check:** `bash scripts/check_env.sh`

## The user's standing preferences
- **Two mandatory approval gates:** (1) the script **and exact prompts** before any paid call, and (2) keyframe picks before any video. These are enforced by `approved:` / `keyframes_approved:` in the episode yaml.
- Offer options with a clear recommendation. State the cost before spending and the running total after.
- Spending more early for quality is OK. Over time, drive the cost per episode down (currently about $5).
- Expressive and playful bear, no on-screen text, music + sound effects (no voice), vertical 9:16, 15–30s.
- The user isn't a git expert, so give exact GitHub click paths when they need to do something.

## Locked series decisions (don't change without the user asking)
| What | Choice | Why |
|---|---|---|
| Look | `styles/film3d_bear_storybook_world.yaml` | The user's pick: cinematic film-3D bear with rich realistic fur, in a pastel storybook world |
| Bear identity | `character/character.yaml` + 4 photos in `character/photos/Bartholomew/` + `character/style_refs/film_bear.png` | The photos lock his design; the style reference locks how he's rendered |
| Keyframes | `google/nano-banana-2.1/edit` (~$0.09) | The old Nano Banana made every style look the same |
| Video | `kling/v4/image-to-video` (~$0.79/5s, native audio) | The user's pick for its fun motion. It drifts unless the prompt has the continuity line (built in) |
| Music | `elevenlabs/music/v2.5` (~$0.25) | Instrumental, exact length |
| Personality | `personalities/playful.yaml` | Swappable per episode |

## Environment facts (cloud session)
- **fal key:** the network proxy injects it for `queue.fal.run` and `api.fal.ai` (prefix `Key`). `FAL_KEY` can be a placeholder (`studio/fal.py` defaults to `proxy:injected`). Local files are sent as data URIs, so no upload host is needed.
- **Allowed fal hosts:** `fal.run`, `queue.fal.run`, `api.fal.ai`, `rest.alpha.fal.ai`, `fal.media`, `v2/v3/v3b.fal.media`.
- **Images the user pastes into chat never reach the disk.** They must upload files to the repo on GitHub (Add file → Upload files), then `git pull`.
- `output/` is gitignored and **disappears with the session**. Anything worth keeping goes in the repo: final videos in `videos/`, approved style references in `character/style_refs/`.
- This repo has a SessionStart hook that installs `requirements.txt`.

## Working rules
- **Commit and push after every meaningful step** (a stop hook checks this). Remote: `https://github.com/jack-nonnie/Bartholomew.git`.
- Run renders in the background; the session is notified when they finish. Tell the user they don't need to prompt again.
- **Look at every image or contact sheet yourself before sending it** (`studio.cli review keyframes|clips`). You can't hear audio, so check levels with `volumedetect` and ask the user to listen.
- Check fal's live catalog and prices before adding or switching any model. Memory of model versions goes stale.
- After every episode, do the **retro**: update `docs/LESSONS.md` and `docs/EPISODE_LOG.md`, and build recurring fixes into the code or template.
