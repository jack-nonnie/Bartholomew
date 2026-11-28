---
name: new-episode
description: Produce a new Bartholomew teddy-bear video episode end to end (idea → script approval → keyframe approval → Kling animation → music + edit → retro). Use whenever the user wants a new Bartholomew video, a new activity/episode, or to redo/fix shots of an existing episode.
---

# New Bartholomew episode: production guide

Quality bar: match or beat `videos/bartholomew_spa_day.mp4`. Two approval gates are **mandatory**: no paid call before the user approves the script, and no video before they pick the keyframes. Commit and push after every step. Keep user messages short, give a recommendation with every choice, and state the cost before spending and the running total after.

## 0. Pre-flight (free)
```bash
bash scripts/check_env.sh
```
- If anything fails, the script prints the fix. Common fixes: re-save the fal key with `request_credential` (host `queue.fal.run`, prefix `Key`; also `api.fal.ai`), add a fal host to the allowlist, or have the user enable the Claude GitHub App for the repo.
- **Read `docs/LESSONS.md` and the latest entry in `docs/EPISODE_LOG.md`.** If the last entry's "User verdict" asks for feedback, ask the user for it first and record it.

## 1. Idea → episode file (free)
1. If the user hasn't named an activity, offer 3 quick ideas that suit a playful bear and his storybook world, e.g. baking, beach day, gardening or camping. Ask about any gags they want included.
2. Run `python -m studio.cli new <snake_name>`, then fill in `episodes/<snake_name>.yaml`. Follow the comments in `_template.yaml`:
   - 4–6 shots × 5s. Arc: arrival → 2–3 activity gags → payoff finale.
   - **One beat per shot** (an action plus a reaction).
   - `motion`: **rich, step-by-step detail** (the user asked for this): how it starts, exactly how the body and props move, where he ends up, his final expression, plus timing for the key change. Short, vague motion lines get skipped.
   - `keyframe`: the literal first-frame pose; say what is NOT happening yet.
   - `continuity`: outfits and props that must not change.
   - `sfx`: what should be heard.
   - Keep `style`, `image_model`, `video_model` and `personality` exactly as in the template unless the user asks.
3. **Props and outfits:** keep them simple and readable, like the robe, cucumber slices and towel turban in Spa Day. Avoid tiny text, hands-free juggling, or anything with many fingers.

## 2. Script → GATE 1 (free)
```bash
python -m studio.cli script <ep>     # writes output/<ep>/script_<style>.md
```
- Send the file (SendUserFile, `display: render`) with a 3–5 line summary: the story beats, length, and estimated cost.
- Iterate on wording until the user approves. **Then** set `approved: true` in the yaml, commit and push.

## 3. Keyframes → GATE 2 (~$0.09/image)
```bash
python -m studio.cli keyframes <ep> --variants 2      # ~$0.18 per shot
python -m studio.cli review keyframes <ep>            # output/<ep>/review/keyframes_grid.png
```
- **Look at the grid yourself first** with the Read tool. Check for:
  - the bear on-model: curly caramel fur, tiny black bead eyes, brown suede nose, round ears, chubby body;
  - the pose matching the shot;
  - props present;
  - the storybook world style;
  - nothing floating or merged.
- Re-roll a clearly broken shot (`--shots <id> --variants 3` adds a v3) **before** showing it. Fix the prompt wording if the same mistake repeats.
- Send the grid and say "columns = shots, rows = A/B", with a recommendation per shot.
- After the user picks: set `keyframe_pick: N` per shot and `keyframes_approved: true`, then commit and push.

## 4. Animate (~$0.79 per 5s clip, Kling 4.0)
```bash
python -m studio.cli animate <ep>                     # run_in_background: true (≈3–7 min per clip)
```
- Tell the user it's rendering and that you'll be notified automatically.
- When it's done, run `python -m studio.cli review clips <ep>` and Read `output/<ep>/review/clips_contact_sheet.png`. Check:
  - outfits and props stay on and keep their colors;
  - eyes stay small black beads (no googly eyes);
  - the bear doesn't morph;
  - the action matches the script.
- Re-roll at most **one** bad shot without asking:
  1. Strengthen its `continuity:` or `motion:` text.
  2. Re-run `animate <ep> --shots <id>`.
  3. Set `lock_clip: true` on the good shots first, so they're never re-billed.
- Ask before spending more than that.

## 5. Finish (music ~$0.25, edit free)
```bash
python -m studio.cli finish <ep>      # music + crossfades + grade + limiter -> videos/bartholomew_<ep>.mp4
```
- The command prints the audio levels: max should be about −1 dB and mean about −16 to −22 dB.
- Spot-check frames across the final with ffmpeg `-ss` grabs, like the contact sheet.
- Commit the video in `videos/` and push. Send it with a caption, and tell the user that you can't hear audio, so they should listen.

## 6. Retro (required: this is how the series improves)
1. Ask the user: "What did you love, and what should change next time?"
2. Add an entry at the top of `docs/EPISODE_LOG.md`: date, shots and picks, re-rolls, spend (sum of `output/<ep>/cost.json`), the user's verdict, and what to do differently.
3. Add any new general lessons to `docs/LESSONS.md` in the right section, and tick or update "Open ideas" you tried.
4. If a fix recurred, **promote it**: put it in `episodes/_template.yaml`, `studio/prompts.py`, `character/character.yaml` or a style file, and mark the lesson *(built in)*.
5. Commit and push.

## Fixing an existing episode
Edit the shot text, set `lock_clip: true` on the shots to keep, re-run only the shots that need it (`keyframes`/`animate --shots`), then run `finish` again (music is cached, so it's free the second time).

## Costs (Nov 2026, re-check with the model-scout skill if they seem off)
| Item | Model | Cost |
|---|---|---|
| Keyframe | google/nano-banana-2.1/edit | ~$0.09 |
| 5s clip | kling/v4/image-to-video | ~$0.79 ($0.157/s) |
| Music 25s | elevenlabs/music/v2.5 | ~$0.25 |
| **Typical 5-shot episode** | | **~$5** |
