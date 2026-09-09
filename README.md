# 🚀 YosiFix — AI-Powered Project Idea Validation & Innovation Platform

<div align="center">

[![Vercel Deployment](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%7C%20Vite%20%7C%20Tailwind-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-7c5cff.svg?style=for-the-badge)](LICENSE)
[![Security: Hardened](https://img.shields.io/badge/Security-Strict%20CSP%20%2B%20HSTS-2dd4bf?style=for-the-badge)](vercel.json)

**“Don’t just generate an idea — prove it, improve it, and build it.”**

`IDEA` ➔ `EVIDENCE` ➔ `VALIDATION` ➔ `GAP` ➔ `INNOVATION` ➔ `PLAN` ➔ `BUILD`

</div>

---

## 🌟 Overview

**YosiFix** (*Your Opportunity, Solution & Innovation Fix*) is an AI-powered platform designed to transform raw project ideas and problem statements into evidence-backed, innovation-focused, UN SDG-aligned, and build-ready project blueprints.

Students, researchers, developers, hackathon teams, and innovators often have promising concepts but struggle with critical questions:
- 🔍 *Has this idea already been implemented in academic literature or open source?*
- 📚 *What similar projects exist, and what are their limitations?*
- 🧩 *Where is the defensible innovation gap?*
- 🌍 *Which UN Sustainable Development Goals (SDGs) does it genuinely support?*
- 🏗️ *What technical architecture, database design, and tech stack should be used?*
- ⏱️ *Can this realistically be built within a 24/48-hour hackathon?*

YosiFix brings all these research, validation, gap detection, and architecture generation tasks into **one unified, intelligent workflow**.

---

## 🎯 The Core Problem & Solution

### ❌ The Old Approach (High Failure Rate)
```text
[ Raw Idea ] ──► [ Immediate Coding ] ──► [ Late Discovery of Existing Identical Project ] (Wasted Time)
```

### ✅ The YosiFix Approach (Engineered Innovation)
```text
[ Raw Idea ] ──► [ Research & Evidence ] ──► [ Gap Detection ] ──► [ Moat Synthesis ] ──► [ Build-Ready Blueprint ]
```

---

## 🔄 The 15-Stage Analytical Pipeline

```text
 User Idea (Text / Voice / Multilingual)
   │
   ▼
 Idea Understanding & Semantic Entity Extraction
   │
   ▼
 Existing Solution Discovery (Web, GitHub, ArXiv, USPTO)
   │
   ▼
 Evidence Collection & Credibility Scoring (High / Med / Low)
   │
   ▼
 Multi-Dimensional Similarity Analysis (Problem, Tech, Users)
   │
   ▼
 Advantages & Limitations Extraction
   │
   ▼
 Innovation Gap Detection (Existing Capability ➔ Missing Moat)
   │
   ▼
 Innovation Opportunity Generator (Accept / Reject / Customize)
   │
   ▼
 Future Roadmap Generator (MVP ➔ V2 ➔ V3 ➔ Long Term)
   │
   ▼
 UN SDG Intelligence & Policy Target Mapping (e.g., SDG 12, 9, 2)
   │
   ▼
 Technology Stack Recommendation (Free / Low-Cost / Production)
   │
   ▼
 System Architecture & Microservice Topology Generator
   │
   ▼
 Database Schema & Entity Relationship Design
   │
   ▼
 AI Prompt Studio (Master prompts for Cursor, Claude, ChatGPT)
   │
   ▼
 📋 Final Project Blueprint (PDF / DOCX / Markdown Export)
```

---

## ✨ Key Features & Capabilities

### 🧠 1. AI Idea Analysis & Multilingual Input
- Normalizes raw problem statements in multiple languages (English, Tamil, Hindi, Spanish, etc.) into high-dimensional semantic vector spaces.
- Extracts problem domain, target users, core requirements, and technical constraints.

### 🎙️ 2. Voice-to-Blueprint Interface
- Hands-free voice interface supporting real-time streaming speech recognition with visual states (`Idle` ➔ `Listening` ➔ `Processing` ➔ `Speaking` ➔ `Completed`).

### 🔎 3. Multi-Source Evidence Discovery
- Deep queries across academic repositories (OpenAlex, arXiv), public patent registries, GitHub repositories, and open-source project directories.

### 📊 4. Multi-Dimensional Similarity Engine
- Evaluates similarity across 5 independent vectors:
  1. **Problem Domain Similarity** (Are they addressing the exact same root problem?)
  2. **Core Feature Redundancy** (Do duplicate workflows already exist?)
  3. **Technology Stack Overlap** (Are identical frameworks and libraries utilized?)
  4. **Target User Overlap** (Is the demographic identical?)
  5. **Workflow Topology** (Does data flow in the same architectural pattern?)

### 🧩 5. Innovation Gap & Moat Detector
- Maps existing capabilities against unaddressed market voids:
  $$	ext{Existing Capability} \longrightarrow 	ext{Missing Capability} \longrightarrow 	ext{Defensible Innovation Opportunity}$$

### 🌍 6. UN Sustainable Development Goal (SDG) Intelligence
- Evidence-backed mapping to the 17 UN SDGs with specific target justifications (e.g., Target 12.2 & 12.5 for resource efficiency and waste minimization).

### ⚖️ 7. Dynamic Intelligence Matrix (Idea Comparison)
- Interactive real-time parameter weighting sliders (*Innovation*, *Feasibility*, *Social Impact*, *Time to Value*) that dynamically recalculate project match scores.

### ⏱️ 8. Hackathon Rapid Prototyping Mode
- Classifies features into **🔥 Build First (MVP Demo)**, **🟡 Build If Time Remains**, and **🔴 Avoid (Time Sink)** to ensure hackathon victory.

### 🤖 9. AI Prompt Studio
- Generates hardened master development prompts tailored for Cursor, Claude, ChatGPT, Gemini, and GitHub Copilot with complete OpenAPI specifications.

---

## 🏛️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                              YosiFix User                               │
│                (Web Browser • Voice Input • Mobile PWA)                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTPS / WSS
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Vercel Edge Network                              │
│         Hardened Security: Strict CSP • HSTS Preload • X-Frame DENY     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      React / Vite Frontend Workspace                    │
│      Dashboard • Idea Studio • Matrix • Blueprints • Telemetry          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ REST API / JSON
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend Core                            │
├───────────────┬─────────────────┬─────────────────┬─────────────────────┤
│ Idea Analyzer │ Research Engine │ Similarity Eng  │ Gap & Moat Engine   │
├───────────────┼─────────────────┼─────────────────┼─────────────────────┤
│ SDG Engine    │ Tech Recommender│ Architecture Gen│ AI Prompt Studio    │
└───────────────┴─────────────────┴─────────────────┴─────────────────────┘
                                     │
            ┌────────────────────────┴────────────────────────┐
            ▼                                                 ▼
┌───────────────────────────────┐ ┌───────────────────────────────────────┐
│     PostgreSQL + pgvector     │ │        External Research Feeds        │
│ (Vector Embeddings & Projects)│ │  (OpenAlex • USPTO • GitHub • arXiv)  │
└───────────────────────────────┘ └───────────────────────────────────────┘
```

---

## 📂 Repository Structure

```text
yosifix/
│
├── frontend/                     # React / Static Frontend Application
│   ├── index.html                # Landing Portal & Instant Concept Synthesizer
│   ├── dashboard.html            # Command Center with Telemetry Bento Grid
│   ├── new-idea.html             # Problem Definition Studio (Voice & Modes)
│   ├── analysis-progress.html    # Real-Time AI Analysis Pipeline & Console
│   ├── my-projects.html          # Project Repository with Dynamic Filtering
│   ├── sdg-intelligence.html     # UN SDG Correlation Matrix (SDG 12, 9, 2)
│   ├── similarity.html           # Competitive Overlap & Moat Breakdown
│   ├── innovation-gaps.html      # Market Gap & Opportunity Radar
│   ├── compare-ideas.html        # Intelligence Matrix with Dynamic Sliders
│   ├── blueprints.html           # Architectural Blueprint Studio
│   ├── prompt-studio.html        # Prompt Engineering Lab & Moat Archetypes
│   ├── hackathon-mode.html       # Rapid Prototyping & Pitch Scaffolding
│   ├── 404.html                  # Glassmorphic 404 Error Page
│   │
│   ├── css/
│   │   └── styles.css            # Deep Space Theme, Glassmorphism, Tech Sliders
│   └── js/
│       ├── main.js               # Global search ('/'), notifications, mobile drawer
│       └── analysis.js           # Matrix slider calculation engine & telemetry
│
├── backend/                      # FastAPI Python Application
│   ├── app/
│   │   ├── api/                  # REST API Route Endpoints
│   │   ├── core/                 # App Configuration, CORS, Security
│   │   ├── models/               # SQLAlchemy Models & pgvector Schemas
│   │   ├── schemas/              # Pydantic Validation Schemas
│   │   └── services/             # AI Client, Research & Similarity Engines
│   ├── requirements.txt          # Python Backend Dependencies
│   └── main.py                   # FastAPI Application Entrypoint
│
├── vercel.json                   # Bank-Grade HTTP Security Headers & Clean URLs
├── .gitignore                    # Git Exclusion Rules
├── docker-compose.yml            # Container Orchestration
├── LICENSE                       # MIT License
└── README.md                     # Project Master Documentation
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend UI** | HTML5, Tailwind CSS, JavaScript (ES6+), Space Grotesk & Inter Typography, Material Symbols |
| **Styling & Theme** | Deep Space Glassmorphism (`#0d0b1f`), Neon Violet (`#7c5cff`) & Teal (`#2dd4bf`) Accents |
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2, Uvicorn, HTTPX |
| **Database & Vectors** | PostgreSQL 16, `pgvector` for 1536-dimensional semantic similarity indexing |
| **AI Orchestration** | Gemini API / Claude / OpenAI GPT-4o, Semantic Vector Embeddings |
| **Security & Edge** | Vercel Edge Network, Strict CSP, HSTS 2-Year Preload, Clickjacking Protection |

---

## ⚡ Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/yosifix.git
cd yosifix
```

### 2. Frontend Local Setup
Open `index.html` or `dashboard.html` directly in your browser, or serve locally:
```bash
# Using Python built-in HTTP server
python -m http.server 3000
```
Visit: **`http://localhost:3000`**

### 3. Backend Setup (FastAPI)
```bash
# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8000
```
Visit API Documentation: **`http://localhost:8000/docs`**

### 4. Docker Deployment
```bash
docker compose up --build -d
```

---

## 🌐 Deploy to Vercel with Maximum Protection

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "feat: complete YosiFix platform release"
   git push origin main
   ```
2. Import the repository into [vercel.com](https://vercel.com).
3. The included **`vercel.json`** automatically enforces:
   - **Strict Content Security Policy (CSP)**
   - **HSTS (HTTP Strict Transport Security)** with preloading
   - **X-Frame-Options: DENY** (Anti-Clickjacking)
   - **X-Content-Type-Options: nosniff** (Anti-MIME Sniffing)
   - **Clean URLs** (e.g., `/dashboard` instead of `/dashboard.html`)

---

## 📜 Ethical AI & Responsible Use

YosiFix is an **AI-assisted decision support system**:
- Similarity percentages and innovation scores are heuristic estimates derived from indexed vector spaces.
- Results do not constitute legal patent clearance or academic originality certification.
- Innovators are encouraged to verify references against primary sources before commercial or academic publication.

---

## 🤝 Contributing

Contributions are warmly welcome!
1. Fork the Project (`https://github.com/YOUR_USERNAME/yosifix/fork`)
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">

**Built with curiosity, research rigor, and AI innovation.**  
*© 2026 YosiFix Intelligence. All rights reserved.*

</div>
