#!/usr/bin/env bash
# Free pre-flight check for a fresh session. Spends nothing.
# Usage: bash scripts/check_env.sh
cd "$(dirname "$0")/.." || exit 1
ok=1
pass(){ echo "  OK   $1"; }
fail(){ echo "  FAIL $1"; ok=0; }

echo "Tools"
command -v ffmpeg >/dev/null && pass "ffmpeg" || fail "ffmpeg missing (apt-get install -y ffmpeg)"
python3 -c "import fal_client, yaml" 2>/dev/null && pass "python deps" \
  || { pip install -q -r requirements.txt >/dev/null 2>&1 && pass "python deps (installed now)" || fail "pip install -r requirements.txt failed"; }

echo "fal.ai (key is injected by the network proxy; FAL_KEY may be absent or a placeholder)"
# A status request for a fake job: 404 = authenticated, 401 = key problem, 403 from proxy = host not allowed.
code=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Key ${FAL_KEY:-proxy:injected}" \
  "https://queue.fal.run/fal-ai/flux/requests/00000000-0000-0000-0000-000000000000/status")
case $code in
  404) pass "queue.fal.run auth (generation)";;
  401) fail "queue.fal.run returned 401: key missing/invalid. Re-save it with request_credential for host queue.fal.run (prefix Key)";;
  403) fail "queue.fal.run blocked by network policy: add fal hosts to the environment allowlist (see CLAUDE.md)";;
  *)   fail "queue.fal.run unexpected HTTP $code";;
esac
code=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Key ${FAL_KEY:-proxy:injected}" \
  -G "https://api.fal.ai/v1/models/pricing" --data-urlencode "endpoint_id=kling/v4/image-to-video")
[ "$code" = 200 ] && pass "api.fal.ai auth (pricing/catalog)" || fail "api.fal.ai HTTP $code (pricing lookups need the key saved for host api.fal.ai)"
code=$(curl -s -o /dev/null -w "%{http_code}" https://v3b.fal.media/)
[ "$code" != 403 ] && pass "fal media download host reachable" || fail "v3b.fal.media blocked: add fal.media hosts to the allowlist"

echo "Git"
git fetch -q origin 2>/dev/null && pass "can reach GitHub remote" || fail "cannot fetch origin"
git push --dry-run -q origin HEAD 2>/dev/null && pass "push access" \
  || fail "push refused: install/enable the Claude GitHub App for jack-nonnie/Bartholomew"

echo
[ $ok = 1 ] && echo "All checks passed." || { echo "Some checks failed (see above)."; exit 1; }
