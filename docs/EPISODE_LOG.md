# Episode log

One entry per episode, newest first. Record what was made, what it cost, what the user picked, and what to change next time. Lessons that generalize also go into `docs/LESSONS.md`.

---

## Ep 1: Spa Day (2026-11-21), pilot
**Video:** `videos/bartholomew_spa_day.mp4` (23.6s, 1080×1920, Kling native sound effects + music)

**Locked decisions made during the pilot**
- Style: `film3d_bear_storybook_world`. The user picked the bear from "option 2" (cinematic animated-film 3D, rich fur) and the world from "option 4" (pastel storybook). Other styles tried and rejected: stop-motion, live-action, photoreal world, miniature diorama.
- Image model: Nano Banana 2.1 (`google/nano-banana-2.1/edit`), after the original Nano Banana gave samey styles.
- Video model: **Kling 4.0** (`kling/v4/image-to-video`), chosen by the user over Veo 3.1 Fast and Seedance 2.5 for its fun, energetic motion.
- Music: ElevenLabs Music v2.5, playful marimba/pizzicato, 25s.
- Personality: playful. Name: Bartholomew (the real Jellycat Bartholomew Bear).

**Shots (all 5s)**
| # | Shot | Keyframe pick | Notes |
|---|---|---|---|
| 1 | Arrival: robe on, rings the reception bell, grins | v1 | First Kling take lost the robe and got googly eyes; re-rendered with the continuity line and it was fine |
| 2 | Face mask: cucumber slides off, peeks, grins | v2 (B) | |
| 3 | Bubble bath: cannonball, pops up with a bubble crown | v2 | v1 floated in mid-air; the bake-off Kling take was kept (`lock_clip`) |
| 4 | Hot stones: kicks feet, melts happily | v2 (B) | B showed the stones clearly |
| 5 | Finale: towel turban, sips tea, flops back | v2 (B) | |

**Spend:** about $13.80 estimated, with 45 paid calls. That covers the style exploration (about $1.90 in images), the 3-model bake-off (about $8.40) and production (about $3.40 video, $0.54 keyframes, $0.25 music).
**Expected cost of a normal episode now:** about $5 (10 keyframes $0.90 + 5 clips $3.95 + music $0.25).

**User verdict:** happy with the final video and asked to set up for the next episode. (Ask for specific feedback at the start of the next session and record it here.)

**Do differently next time**
- Write literal poses and a `continuity:` line for every shot from the start (now in the template).
- Generate 2 variants per shot in one go.
- Try Kling 4.0 Flash on one shot to see if quality holds at about 60% of the cost.
