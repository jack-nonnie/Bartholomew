---
name: model-scout
description: Check fal.ai's live catalog, prices and input schemas, and run a cheap 1–2 shot bake-off to compare or replace a model (video, image or music). Use when choosing or changing a model, when a newer/cheaper model may exist, when costs need cutting (e.g. trying Kling 4.0 Flash), or when a fal call fails with a schema error.
---

# Model scout (fal.ai)

Never pick a model from memory: fal's lineup changes monthly. All of these calls are free. The proxy injects the key for `api.fal.ai`, so any placeholder header works.

## Search the catalog
```bash
curl -s -H "Authorization: Key x:y" -G https://api.fal.ai/v1/models \
  --data-urlencode "q=kling" --data-urlencode "limit=40" | python3 -c "
import sys,json
for m in json.load(sys.stdin)['models']:
  md=m['metadata']; print(m['endpoint_id'],'|',md.get('category'),'|',md.get('date','')[:10])"
```
Useful queries: `kling`, `veo`, `seedance`, `wan`, `minimax`, `nano banana`, `image edit`, `seedream`, `music`.

## Price
```bash
curl -s -H "Authorization: Key x:y" -G https://api.fal.ai/v1/models/pricing --data-urlencode "endpoint_id=kling/v4/image-to-video"
# token-billed or unclear units -> typical cost per call (rate-limited: wait ~3s between calls)
curl -s -X POST -H "Authorization: Key x:y" -H "Content-Type: application/json" \
  https://api.fal.ai/v1/models/pricing/estimate \
  -d '{"estimate_type":"historical_api_price","endpoints":{"bytedance/seedance-2.5/us/image-to-video":{"call_quantity":1}}}'
```

## Input schema (do this before writing an args builder)
```bash
curl -s -H "Authorization: Key x:y" -G https://api.fal.ai/v1/models \
  --data-urlencode "endpoint_id=kling/v4/image-to-video" --data-urlencode "expand=openapi-3.0" | python3 -c "
import sys,json
d=json.load(sys.stdin)['models'][0]; c=d['openapi']['components']['schemas']
for k in c:
  if k.endswith('Input'):
    for p,v in c[k]['properties'].items():
      en=v.get('enum') or [x.get('enum') for x in v.get('anyOf',[]) if x.get('enum')]
      print(p,'*' if p in c[k].get('required',[]) else '', en or '', 'default=',v.get('default'))"
```

## Add a model
1. Add the endpoint to `config.yaml`: `est_cost` or `est_cost_per_sec`, `native_audio` (verify with `ffprobe` on a real output) and `min_sec`.
2. Add a branch to `pipeline.image_args` / `pipeline.video_args`, and to `pipeline.clip_seconds` if its durations are restricted.
3. Check that the music endpoint's args branch matches its schema in `pipeline.music`.

## Cheap bake-off
1. Reuse an approved episode's keyframes. Pick 2 shots: one calm and one action-heavy (e.g. `s1_arrival`, `s3_bubble_bath`).
2. Render each candidate:
   ```bash
   python -m studio.cli animate spa_day --video-model <model_key> --shots s1_arrival,s3_bubble_bath --test
   ```
   This writes to `output/spa_day/clips/<style>_<image>_<model_key>/`. `--test` skips the gate, so get the user's OK on the spend first.
3. Build comparison videos:
   ```python
   from pathlib import Path; from studio import compare
   # compare.grid([[(clip, "Model A"), (clip, "Model B")], ...], Path("output/spa_day/bakeoff_side_by_side.mp4"))
   # compare.reel([(clip, "1. Model A"), ...], Path("output/spa_day/bakeoff_reel_with_sound.mp4"))
   ```
4. Review frames yourself (an ffmpeg contact sheet), then send both videos with a table covering consistency, motion, audio, cost and a recommendation.
5. Record the results in `docs/LESSONS.md` under "Model selection", and in "Video generation" if relevant.
