# AI Resume Coach 🎯

An AI-powered REST API that analyses your resume against a job description and delivers a match score, keyword gap analysis, rewritten bullet points, and actionable improvement tips.

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **PDF and DOCX resume parsing** — extract clean text from uploaded resumes
- **Keyword gap analysis** — see which job-description keywords are present or missing
- **AI-powered bullet point rewrites** — get 3 improved bullet points with explanations
- **Actionable improvement suggestions** — receive 4 concrete tips tailored to the role
- **Fast REST API** — built on FastAPI with automatic Swagger docs at `/docs`

---

## Tech Stack

| Component     | Technology                            | Purpose                             |
| ------------- | ------------------------------------- | ----------------------------------- |
| API Framework | FastAPI 0.115                         | High-performance async REST API     |
| LLM Provider  | OpenRouter                            | Unified gateway to free LLMs        |
| Free Model    | meta-llama/llama-3.1-8b-instruct:free | Resume coaching via chat completion |
| PDF Parsing   | PyMuPDF (fitz) 1.24                   | Extract text from PDF files         |
| DOCX Parsing  | python-docx 1.1                       | Extract text from Word documents    |
| Validation    | Pydantic v2 + pydantic-settings       | Type-safe config and schemas        |
| Testing       | pytest + pytest-asyncio + httpx       | Async integration & unit tests      |

---

## Getting Started

### Prerequisites

- Python 3.11+
- A free [OpenRouter](https://openrouter.ai) API key

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/ai-resume-coach.git
cd ai-resume-coach
```

**2. Create and activate a virtual environment**

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
# venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Configure environment variables**

```bash
cp .env.example .env
```

Open `.env` and set your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**5. Run the development server**

```bash
python run.py
```

The API is now live at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

### Free Models Available

You can swap `MODEL_NAME` in `.env` to use any of these free OpenRouter models:

| Model Name                              | Provider | Notes                        |
| --------------------------------------- | -------- | ---------------------------- |
| `meta-llama/llama-3.1-8b-instruct:free` | Meta     | Default, fast and capable    |
| `google/gemma-2-9b-it:free`             | Google   | Strong instruction following |
| `mistralai/mistral-7b-instruct:free`    | Mistral  | Lightweight, good quality    |

> **Tip:** Change `MODEL_NAME` in your `.env` file to switch models instantly without any code changes.

---

## API Reference

### GET /health

Check the service status and active model.

**Request:**

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "ok",
  "model": "meta-llama/llama-3.1-8b-instruct:free",
  "version": "1.0.0"
}
```

---

### POST /api/v1/resume/analyze

Upload a resume and job description to receive a full AI-powered analysis.

**Form Fields:**

| Field             | Type   | Required | Description                                 |
| ----------------- | ------ | -------- | ------------------------------------------- |
| `resume_file`     | File   | Yes      | PDF or DOCX resume (max 5 MB)               |
| `job_description` | string | Yes      | Target job description text (50–5000 chars) |

**Example curl:**

```bash
curl -X POST http://localhost:8000/api/v1/resume/analyze \
  -F "resume_file=@/path/to/resume.pdf" \
  -F "job_description=We are seeking a Python engineer with experience in machine \
learning, cloud infrastructure, and agile development. The ideal candidate has \
strong communication skills and a passion for data-driven solutions."
```

**Example JSON Response:**

```json
{
  "match_score": 68,
  "score_label": "Good",
  "keyword_gap": {
    "missing_keywords": ["communication", "data-driven", "leadership"],
    "present_keywords": ["python", "machine", "learning", "cloud", "agile"],
    "match_percentage": 68.42
  },
  "bullet_rewrites": [
    {
      "original": "Worked on Python scripts for data processing",
      "improved": "Engineered Python automation scripts that reduced data processing time by 40%",
      "reason": "Adds quantifiable impact and stronger action verb"
    },
    {
      "original": "Helped deploy cloud infrastructure",
      "improved": "Architected and deployed scalable cloud infrastructure on AWS, supporting 1M+ requests/day",
      "reason": "Specifies platform and quantifies scale"
    },
    {
      "original": "Part of agile team",
      "improved": "Contributed to 2-week sprint cycles within a 6-person agile team, consistently meeting delivery targets",
      "reason": "Quantifies team size and demonstrates reliability"
    }
  ],
  "overall_suggestions": [
    "Add measurable achievements with percentages or numbers to each bullet point",
    "Include cloud certifications (AWS, GCP, Azure) prominently in a dedicated section",
    "Tailor your professional summary to mirror the job description's key terms",
    "Add a link to your GitHub or portfolio to demonstrate hands-on Python work"
  ],
  "processing_time_ms": 1842
}
```

---

## Project Structure

```
ai-resume-coach/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app entry point, middleware, global handlers
│   ├── config.py             # Settings via pydantic-settings, loaded from .env
│   ├── dependencies.py       # Shared FastAPI dependency injection helpers
│   ├── routers/
│   │   ├── __init__.py
│   │   └── resume.py         # POST /api/v1/resume/analyze endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── parser.py         # PDF/DOCX text extraction via PyMuPDF & python-docx
│   │   ├── scorer.py         # Keyword intersection scoring logic
│   │   └── llm.py            # OpenRouter API integration via OpenAI SDK
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py        # Pydantic v2 request/response models
│   └── utils/
│       ├── __init__.py
│       └── text.py           # Text cleaning and keyword extraction helpers
├── tests/
│   ├── __init__.py
│   ├── test_parser.py        # Unit tests for resume file parsing
│   ├── test_scorer.py        # Unit tests for keyword scoring logic
│   └── test_resume_router.py # Async integration tests for the API endpoints
├── .env.example              # Environment variable template
├── .gitignore                # Ignored files (venv, .env, __pycache__, etc.)
├── requirements.txt          # Pinned Python dependencies
├── README.md                 # This file
└── run.py                    # Development server launcher (uvicorn)
```

---

## How It Works

The API processes each request through a four-step pipeline:

1. **Parse** — The uploaded PDF or DOCX is read into memory. PyMuPDF extracts text page-by-page from PDFs; python-docx extracts paragraphs from Word documents. File size and extension are validated before extraction.

2. **Score** — Keywords are extracted from both the resume and the job description by tokenising on word boundaries, lowercasing, and filtering out stopwords and short words. The match percentage is calculated as the ratio of overlapping keywords to total job-description keywords.

3. **Analyse** — The resume text, job description, and list of missing keywords are sent to the configured LLM via OpenRouter. The model is prompted to return exactly three bullet-point rewrites and four improvement suggestions as a strict JSON object.

4. **Respond** — All results (match score, score label, keyword gap, rewrites, suggestions, and processing time) are assembled into a `ResumeAnalysisResponse` and returned to the client as JSON.

---

## Running Tests

```bash
pytest tests/ -v
```

All tests run without a real API key — external LLM calls are mocked.

---

## Contributing

Contributions are welcome! Feel free to open an issue to report bugs or suggest features, or submit a pull request with your improvements. Please ensure all tests pass and new code follows the existing style (type hints, docstrings, logging over print).

---
