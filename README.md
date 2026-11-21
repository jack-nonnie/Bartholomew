# Bartholomew

AI-generated short videos of Bartholomew the teddy bear doing everyday things (first episode: **Spa Day**).
Built on [fal.ai](https://fal.ai) models, with ffmpeg for editing.

## How it stays consistent
Every prompt is assembled from four layers, and only the last one changes between videos:

| Layer | File | What it holds |
|---|---|---|
| Character | `character/character.yaml` + `character/photos/` | What the bear looks like (the "character bible") and reference photos |
| Style | `styles/*.yaml` | The look: `stopmotion`, `pixar3d`, `liveaction` |
| Personality | `personalities/*.yaml` | How he moves and emotes: `playful`, `cozy`, `diva` |
| Episode | `episodes/*.yaml` | The shot list for one video |

## Workflow (every paid step has an approval gate)
```bash
pip install fal-client pyyaml          # plus ffmpeg on PATH; set FAL_KEY

python -m studio.cli script spa_day                     # free: script + exact prompts -> review
# set `approved: true` in the episode file
python -m studio.cli keyframes spa_day --variants 2     # still images per shot (cheap)
# pick keyframes (`keyframe_pick:` per shot), set `keyframes_approved: true`
python -m studio.cli animate spa_day --keyframes output/spa_day/keyframes/<style>_<model>
python -m studio.cli finish  spa_day --clips output/spa_day/clips/<dir>   # sfx + music + edit -> final.mp4
```
Results are cached by prompt, so re-running never pays twice for the same shot. Spend is logged to `output/<episode>/cost.json`.

## New episode
Copy `episodes/spa_day.yaml`, rewrite the shots, keep `style` and `personality` the same, then run the workflow.

## Models (prices from fal, Nov 2026, per 5s 720p clip)
- Images: `fal-ai/nano-banana/edit` (~$0.04/image)
- Video: Kling 4.0 (~$0.79), Veo 3.1 Fast (~$0.90 for 6s, includes audio), Seedance 2.5 (~$2.30, includes audio); cheaper Flash/Lite tiers are configured in `config.yaml`
- Audio: `fal-ai/mmaudio-v2` (sound effects), `fal-ai/stable-audio` (music)
