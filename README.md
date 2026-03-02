# Alma — Document-to-Form Automation

Upload a passport and G-28 form → extract structured data via Claude Vision → auto-fill an immigration form in a live browser.

## Demo Flow

1. Start the local server
2. Open http://localhost:8000
3. Upload a passport scan and a G-28 PDF
4. Claude Vision extracts structured data from both documents
5. A Chrome window opens and fills the [target form](https://mendrika-alma.github.io/form-submission/) in real time
6. The browser stays open so you can inspect the filled form

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
make install

# Install Playwright browser
cd backend && uv run playwright install chromium && cd ..

# Set your Anthropic API key
echo 'ANTHROPIC_API_KEY=sk-ant-...' > backend/.env

# Start the server
make dev
```

Then open http://localhost:8000.

## Sample Documents

Test documents are in `samples/`:

| File | Description |
|------|-------------|
| `passport-us-female.jpeg` | US passport specimen (female) |
| `passport-us-male.jpg` | US passport specimen (male) |
| `passport-utopia-specimen.jpg` | ICAO specimen with MRZ |
| `g28-sample-filled.pdf` | Filled G-28 form |
| `g28-blank-uscis.pdf` | Blank G-28 (current edition) |

## Architecture

```
backend/
  app/
    api/
      upload.py          # POST /api/upload — accepts files, runs pipeline
      health.py          # GET /api/health
    services/
      extract.py         # Claude Vision extraction (PassportData, G28Data)
      form_filler.py     # Playwright form automation
    static/
      index.html         # Upload UI
    core/
      config.py          # Environment config
    main.py              # FastAPI app
```

**Stack**: FastAPI, Claude Vision API (claude-sonnet-4-20250514), Playwright

## How It Works

1. **Upload**: User uploads passport + G-28 via the web UI
2. **Extract**: Each document is sent to Claude Vision API which returns structured JSON (names, dates, addresses, etc.)
3. **Fill**: Playwright opens a visible Chrome window, navigates to the target form, and fills every field with extracted data
4. **Review**: The browser stays open — user can review, edit, or submit the form

## Commands

```bash
make install    # Install Python dependencies
make dev        # Run dev server on :8000
make test       # Run tests
make lint       # Ruff check
make format     # Ruff format
```
