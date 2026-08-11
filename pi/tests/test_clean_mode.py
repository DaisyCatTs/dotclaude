"""Regression for pi bridge clean mode (see features/clean-mode.feature)."""

import os
import re
import unittest

PI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT = os.path.join(PI_DIR, "agents", "pi-agent.md")
DELEGATE = os.path.join(PI_DIR, "skills", "delegate", "SKILL.md")
REVIEW = os.path.join(PI_DIR, "skills", "review", "SKILL.md")
DELEGATE_SETTINGS = os.path.join(
    PI_DIR, "skills", "delegate", "references", "settings.md"
)
REVIEW_SETTINGS = os.path.join(
    PI_DIR, "skills", "review", "references", "settings.md"
)


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestPiCleanMode(unittest.TestCase):
    def test_agent_defaults_to_no_extensions_and_no_skills(self):
        content = read(AGENT)
        # Default isolation flags must appear in the command assembly block.
        self.assertIn("--no-extensions", content)
        self.assertIn("--no-skills", content)
        self.assertIn("--no-session", content)
        self.assertIn("--no-context-files", content)
        self.assertIn("--approve", content)

        # Clean flags are gated so WITH_PACKAGES=true can opt out.
        self.assertRegex(
            content,
            r'WITH_PACKAGES.*!=\s*"true"|\[ "\$WITH_PACKAGES" != "true" \]',
        )
        # When WITH_PACKAGES is true, clean flags must not be forced unconditionally.
        # Require an if/else (or equivalent) around the clean flags, not bare CMD+= lines only.
        clean_block = re.search(
            r"WITH_PACKAGES[\s\S]{0,400}?--no-extensions[\s\S]{0,80}?--no-skills",
            content,
        )
        self.assertIsNotNone(
            clean_block,
            "expected WITH_PACKAGES-gated --no-extensions/--no-skills block",
        )

    def test_delegate_exposes_with_packages_escape_hatch(self):
        skill = read(DELEGATE)
        settings = read(DELEGATE_SETTINGS)
        self.assertIn("--with-packages", skill)
        self.assertIn("WITH_PACKAGES", skill)
        self.assertIn("withPackages", settings)

    def test_review_exposes_with_packages_escape_hatch(self):
        skill = read(REVIEW)
        settings = read(REVIEW_SETTINGS)
        self.assertIn("--with-packages", skill)
        self.assertIn("WITH_PACKAGES", skill)
        self.assertIn("withPackages", settings)


if __name__ == "__main__":
    unittest.main()
