# PHIA — Personal Health Insights Agent

> An LLM agent and Streamlit app that turn wearable-style health data into personalized, data-grounded insights.

PHIA explores how large language models can answer open-ended and numerical questions about personal health and fitness data (sleep, activity, heart rate, stress, and more). The repository combines two complementary pieces:

1. **A ReAct reasoning agent** that answers health questions by writing and executing Python over a user's wearable data and, when needed, searching the web for supporting context. This work is a reproduction/extension of Google Research's PHIA approach to personal health insights with LLM agents, run against synthetic wearable personas.
2. **An interactive Streamlit app** (with a lightweight Flask demo variant) that lets a user log daily metrics, visualize trends, and chat with an AI health analyst powered by Google Gemini.

> Note: PHIA is a research and prototyping project. It is **not** a medical device and does not provide medical advice. See [Limitations](#limitations).

---

## Features

### ReAct health agent (`phia_agent.py`, `run_phia.py`, `run_with_api.py`)
- **Reason + Act loop** built on the [`onetwo`](https://github.com/google-deepmind/onetwo) ReAct agent, with a bounded number of reasoning steps.
- **Code-execution tool** that runs generated Python against pandas DataFrames of a persona's summary, activity, and profile data.
- **Web search tool** via the Tavily API for grounding answers in external health/wellness information (falls back to a mock search when no key is provided).
- **Few-shot exemplars** authored as Jupyter notebooks in `few_shots/`, parsed into ReAct demonstrations (see `prompt_templates.py` and `few_shots/README.md`).
- **Synthetic wearable personas** in `synthetic_wearable_users/` used as the data the agent reasons over.
- **Time-aware data utilities** (`data_utils.py`) including a `ChiaDataFrame` that supports natural-language time filters like "yesterday" or "last 7 days".

### Streamlit health app (`streamlit_app.py`, `mvp_app.py`)
- **User accounts** with registration/login and hashed passwords, backed by a local SQLite database.
- **Daily metric logging**: sleep hours, steps, heart rate, stress score, weight, and mood.
- **Dashboards** with interactive Plotly charts and short-term vs. longer-term trend comparisons.
- **AI health chat** powered by Google Gemini, answering questions against the user's own logged data.
- **Goal tracking and correlation analytics** in the fuller MVP variant.

### Flask demo (`app.py`)
- A minimal, deployable web demo (templated `index.html`) exposing JSON endpoints for a health summary and a keyword-based Q&A, intended as a lightweight hosted entry point.

---

## Tech stack

- **Language:** Python 3.11
- **Agent / LLM:** `onetwo` (ReAct), Google Gemini (`google-generativeai`), Tavily search (`tavily-python`)
- **Web / UI:** Streamlit, Plotly (interactive app); Flask + Gunicorn (demo)
- **Data:** pandas, NumPy, SQLite
- **Config:** `python-dotenv`
- **Notebooks:** Jupyter (few-shot exemplars and analysis figures)

Dependency sets are split by entry point:

| File | Use |
|------|-----|
| `requirements.txt` | Streamlit app (pinned) |
| `requirements-mvp.txt` / `requirements-streamlit.txt` | Streamlit app variants |
| `requirements-web.txt` | Flask demo + full agent stack (onetwo, Tavily, etc.) |

---

## Getting started

### Prerequisites
- Python 3.11 (`runtime.txt` pins `python-3.11.9`)
- A Google Gemini API key — https://aistudio.google.com
- (Agent only) A Tavily API key for web search — https://tavily.com — optional; the agent falls back to mock search without one

### Install
```bash
git clone https://github.com/hrakashchauhan/phia-health-insights.git
cd phia-health-insights

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Pick the requirements file for what you want to run:
pip install -r requirements.txt          # Streamlit app
# pip install -r requirements-web.txt    # Flask demo + ReAct agent
```

### Environment variables
Copy the example file and fill in your keys:
```bash
cp .env.example .env
```
```bash
GOOGLE_API_KEY=your_gemini_api_key_here   # required
TAVILY_API_KEY=your_tavily_api_key_here   # optional, for the agent's web search
```
For Streamlit Cloud, configure the same keys via `.streamlit/secrets.toml` (see `.streamlit/secrets.toml.example`).

### Run the Streamlit app
```bash
streamlit run streamlit_app.py
# then open http://localhost:8501
```

### Run the Flask demo
```bash
python app.py            # local, http://localhost:5000
# production: gunicorn --bind 0.0.0.0:$PORT app:app   (see render.yaml)
```

### Run the ReAct agent
```bash
python run_phia.py       # prompts for your Gemini (and optional Tavily) keys
```

---

## Project structure

```
phia-health-insights/
├── phia_agent.py            # ReAct agent: code-exec + Tavily search tools
├── prompt_templates.py      # Agent preamble, ReAct prompt, exemplar builder
├── data_utils.py            # Data loading + time-aware ChiaDataFrame
├── run_phia.py              # CLI entry point for the agent
├── run_with_api.py          # Agent runner with API keys
│
├── streamlit_app.py         # Streamlit app (Gemini chat + dashboards)
├── mvp_app.py               # Fuller MVP (goals, analytics, subscription tiers)
├── app.py                   # Minimal Flask demo
├── templates/index.html     # Flask UI template
│
├── few_shots/               # Notebook exemplars → ReAct demonstrations
├── synthetic_wearable_users/# Synthetic persona data the agent reasons over
├── data/                    # Benchmark questions + evaluation outputs
├── figs/                    # Analysis notebooks and figure PDFs
│
├── requirements*.txt        # Dependency sets per entry point
├── .env.example             # Environment variable template
├── render.yaml              # Render deployment config (Flask)
└── runtime.txt              # Pinned Python version
```

---

## Limitations

- **Not medical advice.** Outputs are AI-generated and intended for research and prototyping only.
- **Synthetic data.** The agent reasons over synthetic wearable personas, not real personal data.
- **API keys required.** Gemini is needed for AI features; Tavily is needed for live web search (otherwise mock search is used).
- **Prototype storage.** The Streamlit app uses a local SQLite database with SHA-256 password hashing — suitable for demos, not production-grade auth.
- **Research lineage.** The agent design follows Google Research's PHIA work; this repository is an independent reproduction/extension for learning and experimentation.

---

## License

Released under the MIT License — see [LICENSE](LICENSE).

## Author

**Akash Kumar** — [@hrakashchauhan](https://github.com/hrakashchauhan)
