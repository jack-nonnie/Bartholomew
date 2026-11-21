"""Builds every prompt from four layers: character + style + personality + shot.

Keeping the layers separate is what makes the series consistent: the character and
style text is identical in every shot of every episode; only the shot text changes.
"""
from . import config


def _fill(text: str, char: dict) -> str:
    return " ".join(text.format(name=char["name"]).split())


def keyframe_prompt(shot: dict, ep: dict, style_id: str | None = None) -> str:
    char = config.character()
    sty = config.style(style_id or ep["style"])
    per = config.personality(ep["personality"])
    return (
        f"Use the reference images as the exact character design. "
        f"The character, {char['name']}, is {char['identity']} "
        f"Scene: {_fill(shot['keyframe'], char)}. "
        f"Setting: {' '.join(ep['setting'].split())}. "
        f"Personality: {per['label'].lower()}, expressive face. "
        f"Style: {sty['prompt']} "
        f"Vertical 9:16 composition, the bear clearly visible and in focus. "
        f"Keep exactly: {'; '.join(char['must_keep'])}."
    )


def video_prompt(shot: dict, ep: dict, style_id: str | None = None) -> str:
    char = config.character()
    sty = config.style(style_id or ep["style"])
    per = config.personality(ep["personality"])
    return (
        f"{_fill(shot['motion'], char)}. "
        f"Camera: {shot['camera']}. "
        f"Character performance: {per['motion']}; expressive face with {per['expressions']}. "
        f"The bear keeps the same curly caramel fur, tiny black bead eyes and brown suede nose throughout. "
        f"Style: {sty['prompt']}"
    )


def negative_prompt(ep: dict, style_id: str | None = None) -> str:
    char = config.character()
    sty = config.style(style_id or ep["style"])
    return ", ".join(char["avoid"]) + ", " + sty["negative"] + ", morphing, extra limbs, flicker"


def sfx_prompt(shot: dict) -> str:
    return shot["sfx"]


def music_prompt(ep: dict) -> str:
    per = config.personality(ep["personality"])
    return f"{per['music_mood']}, instrumental, warm, gentle, loopable, no vocals, high quality"
