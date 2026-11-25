"""Builds every prompt from four layers: character + style + personality + shot.

Keeping the layers separate is what makes the series consistent: the character and
style text is identical in every shot of every episode; only the shot text changes.
"""
from . import config


def _fill(text: str, char: dict) -> str:
    return " ".join(text.format(name=char["name"]).split())


def keyframe_prompt(shot: dict, ep: dict, style_id: str | None = None) -> str:
    """Style first (so the model commits to the look), then character, then the shot."""
    char = config.character()
    sty = config.style(style_id or ep["style"])
    per = config.personality(shot.get("personality") or ep["personality"])
    if sty.get("bear") and sty.get("world"):
        look = (f"WORLD STYLE (most important, apply to everything except the bear): {' '.join(sty['world'].split())} "
                f"BEAR RENDERING: {' '.join(sty['bear'].split())} ")
    else:
        look = f"VISUAL STYLE (most important, apply to the whole image): {sty['prompt']} "
    return (
        look +
        f"CHARACTER: the reference photos show {char['name']}, a real plush teddy bear; keep his exact "
        f"design: {'; '.join(char['must_keep'])}. Full description: {char['identity']} "
        f"SCENE: {_fill(shot['keyframe'], char)}. "
        f"SETTING: {' '.join(ep['setting'].split())}, rendered in the world style above. "
        f"Personality: {per['label'].lower()}, expressive animated face. "
        f"Vertical 9:16 frame, the bear clearly visible and in focus. Do not copy the backgrounds of the reference images."
    )


def video_prompt(shot: dict, ep: dict, style_id: str | None = None) -> str:
    char = config.character()
    sty = config.style(style_id or ep["style"])
    per = config.personality(shot.get("personality") or ep["personality"])
    return (
        f"{_fill(shot['motion'], char)}. "
        f"Camera: {shot['camera']}. "
        f"Character performance: {per['motion']}; expressive face with {per['expressions']}. "
        f"Continuity: keep everything from the first frame; the same outfit and props stay on the whole time, "
        f"same framing and size. {shot.get('continuity', '')} "
        f"The bear keeps the same curly caramel fur and brown suede nose throughout; his eyes always stay tiny "
        f"glossy black beads, with no white eye whites and no cartoon eyes. "
        f"Sound: {shot.get('sfx', '')}. No voice, no speech, no giggling or laughing sounds "
        f"(at most one brief soft chuckle). "
        f"Style: {sty['prompt']}"
    )


def negative_prompt(ep: dict, style_id: str | None = None) -> str:
    char = config.character()
    sty = config.style(style_id or ep["style"])
    return ", ".join(char["avoid"]) + ", " + sty["negative"] + ", morphing, extra limbs, flicker"


def sfx_prompt(shot: dict) -> str:
    return shot["sfx"]


def music_prompt(ep: dict) -> str:
    mood = ep.get("music", {}).get("mood") or config.personality(ep["personality"])["music_mood"]
    return f"{' '.join(mood.split())}, instrumental, warm, loopable, no vocals, high quality"
