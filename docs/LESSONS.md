# Lessons learned

This is a living document. **Read it before starting any episode**, and **append to it after every episode** (the retro step in `.claude/skills/new-episode/SKILL.md`). When a lesson keeps coming up, build the fix into the code, the template or the prompts, then mark it here as *(built in)*.

---

## The user's preferences (standing instructions)
- **Approval gate 1:** before any paid generation, show the script **and the exact prompts**. The user wants to approve them first.
- **Approval gate 2:** the user picks the keyframes (still images) before any video is generated.
- They like **options with a clear recommendation**: "here are A/B, I'd pick B because…". When asked for "more options", vary one dimension at a time; the world-realism ladder worked well.
- **Budget:** spending more early to get the product right is fine. Over time, push costs down. Always state the cost before spending and the running total after.
- **Look:** expressive animation (expressions don't need to be subtle), playful personality (configurable), no on-screen text, music + sound effects with no voice, vertical 9:16, 15–30s.
- Keep messages short: say what's happening, show results, ask one clear question.
- The user is non-technical with git/GitHub. Give exact click paths (e.g. "Add file → Upload files").

## Setup and environment *(mostly built into scripts/check_env.sh and CLAUDE.md)*
- **Images pasted into chat never reach the disk.** The user must upload files to the repo on GitHub (e.g. `character/photos/`) so they can be pulled. Don't promise to save chat images.
- **fal.ai hosts must be on the environment allowlist:** `fal.run`, `queue.fal.run`, `api.fal.ai`, `rest.alpha.fal.ai`, `fal.media`, `v2.fal.media`, `v3.fal.media`, `v3b.fal.media`. Saved on the Default environment on 2026-11-21.
- **The fal key** is saved as a proxy-injected network credential for `queue.fal.run` (generation) and `api.fal.ai` (catalog, pricing, schemas), with prefix `Key`. Code may send any placeholder in `FAL_KEY`, because the proxy overwrites the header. The `FAL_KEY` environment variable was also fixed, but env-var edits only apply after a restart.
- **Avoid the upload host:** local files go to fal as **data URIs** (`fal_client.encode_file`), so `rest.alpha.fal.ai` is never needed. *(built in: `studio/fal.py`)*
- **GitHub repo creation:** this environment can't create repos. The user creates them, then `add_repo` attaches one. If a push is refused (403), the Claude GitHub App needs access to the repo (github.com/apps/claude/installations/select_target).
- The remote must be `https://github.com/jack-nonnie/Bartholomew.git` (capital B), otherwise git prints a "repository moved" notice.
- A stop hook insists on committing and pushing. **Commit and push after every meaningful step.**
- **Run long jobs in the background** (video renders take about 3–7 minutes per clip). The session is notified when they finish, so the user doesn't need to prompt again. Tell them so.

## Model selection
- **My memory of fal's model lineup is out of date. Check the live catalog every time** (see `.claude/skills/model-scout/SKILL.md`). On day one my config pointed at Kling 2.1, Veo 3 and Seedance 1, while Kling 4.0, Veo 3.1 and Seedance 2.5 were live.
- Prices come from the pricing API: `GET api.fal.ai/v1/models/pricing?endpoint_id=…`. For token-billed models, use `POST /v1/models/pricing/estimate` with `historical_api_price`. The estimate endpoint rate-limits quickly, so space calls about 3s apart.
- **Seedance bills per token, not per second:** about 108k tokens for 5s of 720p, which is about $2.30 per clip. That's expensive, so don't assume per-second pricing.
- Catalog listings can be incomplete: **Kling 4.0 returned native audio** even though its listing has no audio tag. Inspect real outputs with `ffprobe`.

## Image generation (keyframes)
- **The original `fal-ai/nano-banana/edit` rendered every style nearly the same** (stop-motion, 3D and live-action all looked alike). **Nano Banana 2.1 (`google/nano-banana-2.1/edit`) plus a style-first prompt** fixed it. *(built in: prompt order is style → character → scene → setting)*
- **Bear and world are rendered separately.** The chosen look is a cinematic film bear (rich, realistic curly fur) in a stylized pastel storybook world. The style YAML has separate `bear:` and `world:` texts, and the prompt says outright that the bear is *more realistic than the world*. *(built in: `styles/film3d_bear_storybook_world.yaml`)*
- **A style reference image anchors the bear's look.** `character/style_refs/film_bear.png` is passed after the 4 real photos, with "render the bear like the LAST reference image". Keep doing this. If the bear starts drifting in future episodes, add a second reference (a full-body shot from an approved episode).
- **Use literal, physical pose wording, and say what is NOT happening yet.** "Standing on the rim, about to jump in" produced a bear already *in* the foam. "Standing on top of the wide wooden rim, completely dry and NOT yet in the water, knees bent" worked, after one floating miss.
- **Always generate 2 variants per shot** (about $0.18). Roughly 1 in 3 first takes has a pose or framing problem. Variant B won all three shots in the second batch.
- **The character description must not contradict the personality.** "No visible mouth stitching" fought against "big smiles". It now reads: "no stitched mouth at rest (a small soft mouth appears only when he smiles, laughs or gasps)".
- Nano Banana 2.1 output is 768×1376 at 1K. That's plenty for 720p video.

## Video generation
- **Bake-off results** (2 shots, same keyframes, 2026-11-21):
  - **Kling 4.0** (~$0.79/5s): the most energetic, fun motion and the best bath gag (a bubble crown), but it **drifted**: the robe vanished and one frame had cartoon googly eyes. **The user chose this one.**
  - **Veo 3.1 Fast** (~$0.90 for 6s; only 4, 6 or 8s): a big splash, but it changed the white robe to blue-grey, and the wet fur looked blotchy.
  - **Seedance 2.5** (~$2.30/5s): the most faithful to the keyframe, but calmer and 3× the price.
- **Kling's drift was fixed with a continuity line** in every video prompt: "keep everything from the first frame; the same outfit and props stay on; eyes always stay tiny glossy black beads, no white eye whites, no cartoon eyes", plus a per-shot `continuity:` field. After that, all 4 production clips stayed on-model. *(built in: `studio/prompts.py`, the template's `continuity:`)*
- Kling v4 parameters: `start_image_url`, `duration` (integer, 3–30), `resolution` (720p/1080p/4k), optional `end_image_url`/`multi_prompt`. **There's no negative-prompt field**, so anything that must not change goes in the positive prompt.
- **One beat per 5s shot.** Kling plays "action + reaction" well, e.g. "takes a sip, grins at camera, flops back".
- **Lock good clips.** `lock_clip: true` keeps an approved take when prompt text changes, which otherwise changes the cache key and re-bills. *(built in)*
- After rendering, **always run `review clips` and look at the contact sheet** before showing the user. Re-roll at most one bad shot without asking; ask before spending more.

## Audio
- **All three video models produce usable native audio** (sound effects and ambience), so the separate sound-effects step (MMAudio) isn't needed for Kling. `add_sfx` only touches silent clips.
- **Music:** `elevenlabs/music/v2.5` ($0.60/min, `music_length_ms`, `force_instrumental: true`) gave a good 25s marimba and pizzicato track. `google/lyria-3.5` ($0.10 per track) is a cheaper alternative worth trying.
- **I can't hear audio.** Check with `ffmpeg -af volumedetect`; music should have a mean around −20 dB. **Ask the user to listen** to the final cut.
- **Clipping:** mixing Kling's audio with music at 35% hit 0 dB. A limiter (`alimiter=limit=0.89`) now keeps peaks around −1 dB. *(built in: `pipeline.edit`)*

## Editing
- The finished edit has 0.4s crossfades, one shared color grade (`eq` + `colorbalance`), 1080×1920 at 24fps, a 0.4s fade-in, a 0.6s video and audio fade-out, and music fading out over the last 1.5s. *(built in)*
- 5 × 5s clips with crossfades come to about 23.6s.

## Bugs fixed (so they don't come back)
- `fal.download()` skipped existing files, so a regenerated image with the same filename showed the **old** image. It now always overwrites. *(built in)*
- `video_args` builders differ per model family (Kling uses `start_image_url`, Veo durations look like `"6s"`, Seedance durations are strings). Keep them in `pipeline.video_args`.

## Process
- **Before sending anything visual, look at it yourself first**, using a grid or contact sheet. Twice I caught problems before the user saw them: styles too similar, and a floating bear.
- Tell the user honestly when results miss the brief, then fix them cheaply before asking for a decision.
- Run tests on 2 representative shots (one calm, one action-heavy) before spending on a full episode.

## Open ideas (try these, then record the result above)
- [ ] **Kling 4.0 Flash** (`kling/v4/flash/image-to-video`, ~$0.47/5s) to cut video cost by about 40%. Test 1 shot against standard Kling.
- [ ] **Kling 4.0 reference-to-video** (`kling/v4/reference-to-video`, `elements` + `image_urls`) for even stronger character lock. It takes the photos and `film_bear.png`.
- [ ] A **canonical character sheet** (front, 3/4, side, back, plus expressions) in the locked style, via `python -m studio.cli sheet`. Use it as references instead of raw photos once approved.
- [ ] An **end frame** (`end_image_url`) for shots with a big pose change, to stop drift mid-action.
- [ ] Try `google/lyria-3.5` for music ($0.10 vs $0.25).
- [ ] Generate keyframes at `resolution: 2K` if a final at 1080p looks soft.
