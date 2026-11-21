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
    per = config.personality(ep["personality"])
    return (
        f"VISUAL STYLE (most important, apply to the whole image): {sty['prompt']} "
        f"CHARACTER: the reference photos show {char['name']}, a real plush teddy bear; keep his exact "
        f"design: {'; '.join(char['must_keep'])}. Full description: {char['identity']} "
        f"SCENE: {_fill(shot['keyframe'], char)}. "
        f"SETTING: {' '.join(ep['setting'].split())}, rendered in the visual style above. "
        f"Personality: {per['label'].lower()}, expressive animated face. "
        f"Vertical 9:16 frame, the bear clearly visible and in focus. Do not copy the white photo backgrounds."
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
