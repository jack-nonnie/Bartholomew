# Episode log

One entry per episode, newest first. Record what was made, what it cost, what the user picked, and what to change next time. Lessons that generalize also go into `docs/LESSONS.md`.

---

## Ep 2: Gym Day (2026-11-25)
**Video:** `videos/bartholomew_gym_day.mp4` (23.6s, 1080×1920, Kling native sound effects + workout-montage music)
**Approved keyframes + final script:** `episodes/assets/gym_day/`
**Outfit:** a red terry sweatband and red wristbands, which stayed on in every clip.

**Shots (all 5s)**
| # | Shot | Keyframe pick | Notes |
|---|---|---|---|
| 1 | Warm-up: toe touch, topple, pop back up | v2 (B) | Kling turned the topple into a goofy airborne tumble. Kept. |
| 2 | Big lift: gummy-bear barbell, red gummy slides off, he topples | v1 (A) | The user's gag idea (gummy bears as weights). Came out exactly as scripted. |
| 3 | Treadmill: legs blur, face-plant onto the mat, grin | v1 (A) | He flew over the front instead of off the back. Reads well. Also used for the Flash test. |
| 4 | Jump rope: rope wraps him like a parcel | v1 (A) | Excellent. The detailed wrap description worked. |
| 5 | Tuckered out: sleepy personality, naps hugging the red gummy (callback) | v1 (A) | Take 1 only closed his eyes. Take 2, with detailed motion + static camera, tipped him onto the bench asleep. |

**Spend:** about $6.33 over 18 calls: keyframes $0.90, 5 clips $3.92, one shot 5 re-roll $0.79, Flash test $0.47, music $0.25. Without the test and the re-roll it would have been about $5.07.

**Code changes:** per-episode `music.mood`, per-shot `personality:`, a new `personalities/sleepy.yaml`, a no-giggle line in the video prompt, "giggling" removed from playful, and Kling Flash `native_audio: true`.

**User verdict:** "the videos came back great". They want **more detail in the video-model descriptions** from now on, which is now in the template, skill and LESSONS. Spa Day feedback recorded: too much giggling, which is fixed. Kling Flash: no decision yet.

**Do differently next time**
- Write every `motion:` as rich step-by-step detail from the start: start, movement, end position, expression, timing.
- Use a static camera for body-movement beats, since the push-in hid the tip-over.
- Ask the user about Kling Flash before Ep 3. It would save about $1.60 per episode.

---

## Ep 1: Spa Day (2026-11-21), pilot
**Video:** `videos/bartholomew_spa_day.mp4` (23.6s, 1080×1920, Kling native sound effects + music)
**Approved keyframes + final script:** `episodes/assets/spa_day/` (reusable as extra bear references)

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

**User verdict:** happy with the final video. Feedback given later: the giggling was overdone, a little is fine (fixed in Ep 2).

**Do differently next time**
- Write literal poses and a `continuity:` line for every shot from the start (now in the template).
- Generate 2 variants per shot in one go.
- Try Kling 4.0 Flash on one shot to see if quality holds at about 60% of the cost.
