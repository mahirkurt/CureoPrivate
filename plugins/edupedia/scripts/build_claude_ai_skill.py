#!/usr/bin/env python3
"""Geriye uyum: claude.ai skill zip'ini edupedia 1.0.0'dan beri scripts/build_surfaces.py üretir.

    python3 plugins/edupedia/scripts/build_claude_ai_skill.py
    → plugins/edupedia/dist/edupedia-claude-ai.zip   (claude.ai → Skills → Upload)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_surfaces  # noqa: E402

if __name__ == "__main__":
    sys.exit(build_surfaces.main(["--zip"]))
