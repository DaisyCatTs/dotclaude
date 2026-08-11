"""git-agent Claude Code plugin must not depend on pi-coding-agent."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[1]
FORBIDDEN = (
    "@earendil-works/pi-coding-agent",
    "pi-coding-agent",
    '"pi-package"',
    "Package for Pi",
    'peerDependencies',
)


class TestNoPiCodingAgent(unittest.TestCase):
    def test_no_pi_package_surface(self) -> None:
        self.assertFalse(
            (PLUGIN_DIR / "extensions").exists(),
            "extensions/ is pi-only; Claude Code uses hooks/",
        )
        self.assertFalse(
            (PLUGIN_DIR / "package.json").exists(),
            "package.json was the pi package manifest; remove it from this plugin",
        )

    def test_no_forbidden_strings_in_plugin_sources(self) -> None:
        # Skip tests/features: they intentionally name the forbidden surface.
        skip_dirs = {"__pycache__", ".git", "tests", "features"}
        for root, dirs, files in os.walk(PLUGIN_DIR):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for name in files:
                if name.endswith((".pyc", ".png", ".jpg")):
                    continue
                path = Path(root) / name
                text = path.read_text(encoding="utf-8", errors="ignore")
                for token in FORBIDDEN:
                    self.assertNotIn(
                        token,
                        text,
                        f"found {token!r} in {path.relative_to(PLUGIN_DIR)}",
                    )


if __name__ == "__main__":
    unittest.main()
