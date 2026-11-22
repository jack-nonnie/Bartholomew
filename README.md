# Bartholomew

AI-generated short videos of Bartholomew the teddy bear doing everyday things.
**Episode 1: [Spa Day](videos/bartholomew_spa_day.mp4)** (23.6s, vertical, with sound).

Built on [fal.ai](https://fal.ai) models (Nano Banana 2.1 for still images, Kling 4.0 for video, ElevenLabs Music) and ffmpeg for editing.

## Making a new video
In a Claude Code session with this repo selected, say something like:
> Let's make a new Bartholomew video: a beach day

Claude follows `.claude/skills/new-episode/SKILL.md`. You approve the script and prompts, then pick the still images, then get the finished video. A typical episode costs about $5.

## How it stays consistent
Every prompt is assembled from four layers, and only the last one changes between videos:

| Layer | File | What it holds |
|---|---|---|
| Character | `character/character.yaml`, `character/photos/`, `character/style_refs/` | What the bear looks like and how he's rendered |
| Style | `styles/film3d_bear_storybook_world.yaml` | The series look: film-quality bear in a pastel storybook world |
| Personality | `personalities/*.yaml` | How he moves and emotes: `playful`, `cozy`, `diva` |
| Episode | `episodes/*.yaml` | The shot list for one video (template: `episodes/_template.yaml`) |

## Commands
```bash
bash scripts/check_env.sh                              # free pre-flight check
python -m studio.cli new beach_day                     # new episode file from the template
python -m studio.cli script beach_day                  # script + exact prompts (approval gate 1)
python -m studio.cli keyframes beach_day --variants 2  # still images
python -m studio.cli review keyframes beach_day        # comparison grid (approval gate 2)
python -m studio.cli animate beach_day                 # video clips
python -m studio.cli review clips beach_day            # frame contact sheet to check consistency
python -m studio.cli finish beach_day                  # music + edit -> videos/bartholomew_beach_day.mp4
```
Results are cached by prompt, so re-running never pays twice for the same shot. Spend is logged to `output/<episode>/cost.json`.

## Docs
- `CLAUDE.md`: project memory, loaded automatically by Claude Code
- `docs/LESSONS.md`: everything learned so far, updated after every episode
- `docs/EPISODE_LOG.md`: what each episode used, cost and what to change next time
- `.claude/skills/model-scout/SKILL.md`: how to check for newer or cheaper models
