# Generate Image Plugin

Generate or edit images via two backends: Google Gemini (`gemini-3-pro-image`) or any OpenAI-compatible endpoint (`gpt-image-2`, `dall-e-3`, ...).

**Version**: 0.1.0
**Display Name**: Generate Image

## Installation

```bash
claude plugin install generate-image@frad-dotclaude
```

## Quick Start

### 1. Setup API Keys

```bash
export GEMINI_API_KEY="your_gemini_key"  # gemini backend
export OPENAI_API_KEY="your_openai_key"  # openai backend
```

Get your API keys:
- **GEMINI_API_KEY**: Get from [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- **OPENAI_API_KEY**: Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

The skill resolves its key progressively — a shell `export`, a `.env` file, or a `--api-key` flag all work.

### 2. Use the Generate Image Skill

```bash
/generate-image:generate-image "RayNeo AR glasses product hero shot" --backend gemini -o hero.png --aspect-ratio 16:9 --size 2K
/generate-image:generate-image "swap the sky to a sunset, keep everything else" --backend gemini -i street.png -o street_sunset.png
```

## Features

- Two explicit backends (`--backend gemini|openai`) — native Gemini API or any OpenAI-compatible endpoint
- Text-to-image and image editing/composition (one or more `-i` reference images)
- Aspect ratio (`1:1` … `21:9`), resolution tier (`1K`/`2K`/`4K`), multiple candidates
- Progressive configuration — key/model resolved via flag → env → `.env` → default

**Prerequisites:** `uv`, and the API key for the chosen backend.

## Architecture

```
generate-image/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata (displayName: Generate Image)
├── lib/
│   └── progressive_env.py   # Progressive config resolver (flag → env → .env → default)
└── skills/
    └── generate-image/      # Image generation (command, gemini / openai backends)
        ├── SKILL.md
        ├── scripts/generate_image.py
        └── references/prompting.md
```

## Author

Frad LEE (fradser@gmail.com)

## License

MIT
