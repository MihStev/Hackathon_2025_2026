

https://github.com/user-attachments/assets/2dcfd9ba-a9f5-407d-a6aa-c6a3e27e0a3d

# 💼 FinStat AI

> **AI-powered financial management platform for small and medium-sized enterprises (SMEs)**

FinStat AI combines a real-time analytics dashboard with an autonomous AI financial strategist powered by **Google Gemini 2.5 Flash**. Banking transactions, employee payroll, and tax obligations are unified in a single interface — queryable via natural language.

---

## 🚀 Features

- **Real-time KPI Dashboard** — Live overview of income, expenses, and cash flow
- **Retrospective Analytics** — Month-over-month comparisons and business health scoring
- **90-Day Cash Flow Forecasting** — Predictive engine built into the analytics module
- **AI Financial Advisor** — Conversational agent that reads and writes financial data autonomously
- **Natural Language Queries** — Ask questions like *"What were our top expenses last month?"* and get instant answers
- **Unified Data View** — Employees, invoices, expenses, and payroll in one place

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Streamlit Frontend            │
│  Home │ Analytics │ Advisor │ Settings  │
└──────────────────┬──────────────────────┘
                   │
         ┌─────────▼──────────┐
         │    AI Agent Layer   │
         │  Gemini 2.5 Flash   │
         │  (Function Calling) │
         └─────────┬──────────┘
                   │
     ┌─────────────▼─────────────┐
     │   Financial Tools Engine  │
     │  (src/tools.py)           │
     │  - SQL read/write tools   │
     │  - Health score engine    │
     │  - Forecast generator     │
     └─────────────┬─────────────┘
                   │
         ┌─────────▼──────────┐
         │   SQLite Database   │
         │  database/finance.db│
         └────────────────────┘
```

---

## 📁 Project Structure

```
FinStat AI/
├── src/
│   ├── main.py          # Streamlit dashboard (UI entry point)
│   ├── ai_agent.py      # Gemini agent setup and orchestration
│   ├── tools.py         # AI tools + analytics engines
│   └── database.py      # DB connection and schema initialization
├── database/
│   └── finance.db       # SQLite persistence file
├── seed_tr.py           # Seed script (generates Feb–Apr 2026 history)
├── .env                 # Environment variables (API key)
└── requirements.txt     # Python dependencies
```

---

## 🗄️ Database Schema

| Table | Description |
|-------|-------------|
| `zaposleni` | Employee records and payroll data |
| `troskovi` | Business expenses |
| `fakture` | Invoices |
| `chat_poruke` | AI conversation history |

---

## ⚙️ Getting Started

### 1. Prerequisites

- Python 3.9+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/MihStev/Hackathon_2025_2026.git
cd Hackathon_2025_2026

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Initialize the Database

```bash
python src/database.py
```

### 5. Seed Sample Data

This generates a three-month business history (February – April 2026):

```bash
python seed_tr.py
```

### 6. Run the Application

```bash
streamlit run src/main.py
```

The app will be available at `http://localhost:8501`.

---

## 🤖 AI Agent

The agent (powered by **Gemini 2.5 Flash**) is restricted to the financial domain via a strict `system_instruction`. It can:

- **Read data** — execute SQL queries via `citaj_bazu_sql`
- **Write data** — add records via `dodaj_trosak` and related tools
- **Reason autonomously** — chain multiple tool calls to answer complex queries

Example prompts:
- *"Prikaži mi ukupne troškove za mart."*
- *"Dodaj novi trošak: kancelarijski materijal, 15,000 RSD."*
- *"Koji zaposleni ima najveću platu?"*

---

## 📊 Dashboard Tabs

| Tab | Serbian Name | Content |
|-----|-------------|---------|
| Home | Početna | KPI cards, recent activity feed |
| Analytics | Analitika | Health score, comparisons, 90-day forecast |
| Advisor | Savetnik | Conversational AI interface |
| Settings | Podešavanja | System configuration |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | [Streamlit](https://streamlit.io/) |
| AI Model | Google Gemini 2.5 Flash |
| AI SDK | `google-generativeai` |
| Database | SQLite |
| Language | Python 3.9+ |

---

## 📄 License

This project was developed for **Hackathon 2025/2026**. See repository for license details.

---

<p align="center">
  Built with ❤️ for SMEs — because every small business deserves enterprise-grade financial intelligence.
</p>
