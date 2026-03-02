# Alma — Document-to-Form Automation

## What This Does

Upload a passport and G-28 form (PDF/image) → extract structured data → auto-fill a web form via Playwright.

## Architecture

Single FastAPI backend serving a static HTML frontend. No build step, no bundler.

```
backend/
  app/
    api/         # FastAPI route modules
    core/        # Config, shared utilities
    services/    # Document extraction, form filling logic
    static/      # HTML/CSS/JS served by FastAPI
    main.py      # Entry point
  tests/
  pyproject.toml
```

## Stack

- **Backend**: FastAPI (Python 3.11+), uvicorn
- **Frontend**: Static HTML/CSS/JS served from `backend/app/static/`
- **Document extraction**: Claude API (vision) for OCR/extraction
- **Form filling**: Playwright (async)
- **Package manager**: uv
- **Linter**: ruff
- **Testing**: pytest

## Commands

```bash
make install     # Install Python deps
make dev         # Start dev server on :8000
make test        # Run tests
make lint        # Ruff check
make format      # Ruff format
```

## Conventions

- Absolute imports only: `from app.services.extract import ...`
- Async/await everywhere
- Keep it simple — no ORM, no auth, no database
- One working flow: upload → extract → fill form
