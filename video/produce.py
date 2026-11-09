#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import FILMS
from engine import build_audio, check_scripts, find_speaker, preview, render_video, thumbnail


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    slugs = sys.argv[2:] or [f["slug"] for f in FILMS]
    if cmd == "check":
        raise SystemExit(0 if check_scripts() else 1)
    if cmd == "preview":
        for slug in slugs:
            preview(slug)
        return
    if cmd == "audio":
        speaker, name, style = find_speaker()
        print("speaker", speaker, name, style)
        for slug in slugs:
            build_audio(slug, speaker)
        return
    if cmd == "render":
        for slug in slugs:
            render_video(slug)
        return
    if cmd == "thumb":
        for slug in slugs:
            thumbnail(slug)
        return
    raise SystemExit(f"unknown {cmd}")


if __name__ == "__main__":
    main()
