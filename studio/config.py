"""Loads project YAML files (character, style, personality, episode, models)."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


def load(rel: str) -> dict:
    with open(ROOT / rel) as f:
        return yaml.safe_load(f)


def character() -> dict:
    return load("character/character.yaml")


def models() -> dict:
    return load("config.yaml")


def episode(name: str) -> dict:
    ep = load(f"episodes/{name}.yaml")
    ep["_name"] = name
    return ep


def style(sid: str) -> dict:
    return load(f"styles/{sid}.yaml")


def personality(pid: str) -> dict:
    return load(f"personalities/{pid}.yaml")


def out_dir(ep_name: str) -> Path:
    d = ROOT / "output" / ep_name
    d.mkdir(parents=True, exist_ok=True)
    return d
