# 🚀 YosiFix — AI-Powered Innovation Intelligence & Blueprint Platform

[![Vercel Deployment](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet.svg?style=for-the-badge)](LICENSE)
[![Security Headers](https://img.shields.io/badge/Security-Strict%20CSP%20%2B%20HSTS-2dd4bf?style=for-the-badge)](vercel.json)

> **"Don't just generate an idea. Prove it. Improve it. Build it."**
> YosiFix is a high-precision innovation intelligence laboratory that parses, benchmarks, and constructs executable blueprints from raw thought using multi-vector neural modeling.

---

## 🌟 Key Capabilities & Modules

| Module | Route | Purpose & Key Features |
| :--- | :--- | :--- |
| **Landing Portal** | `/index.html` | Instant idea synthesizer, 6-stage analytical pipeline, and core engine overview. |
| **Command Center** | `/dashboard.html` | Operational metrics (Ideas Analyzed, Moats, Research Assets), featured blueprints, and recent analysis feeds. |
| **Problem Definition** | `/new-idea.html` | Synthesis workspace with voice input transcription, context document attachments, and mode selectors. |
| **Analysis Telemetry** | `/analysis-progress.html` | Real-time animated pipeline with live streaming neural console logs and patent vector matching. |
| **Project Repository** | `/my-projects.html` | Interactive filterable project database with innovation gauges and status tracking. |
| **SDG Intelligence** | `/sdg-intelligence.html` | Deep UN SDG correlation matrix (SDG 12, SDG 9, SDG 2) with automated policy rationale and impact evidence. |
| **Similarity Benchmarking** | `/similarity.html` | Competitive overlap analysis (Problem Domain, Feature Set, Stack Moat) and AI architectural divergence panel. |
| **Innovation Gaps** | `/innovation-gaps.html` | Opportunity radar detecting unaddressed market voids and technological moats. |
| **Intelligence Matrix** | `/compare-ideas.html` | Real-time dynamic parameter weighting sliders (*Innovation*, *Feasibility*, *Social Impact*, *Time to Value*) with instant score recalculations. |
| **Blueprint Studio** | `/blueprints.html` | Exportable microservice schemas and production-ready technical architecture specs. |
| **Prompt Studio** | `/prompt-studio.html` | Specialized system prompt generator and audit archetypes (Patent Auditor, Cloud Architect). |
| **Hackathon Mode** | `/hackathon-mode.html` | 60-second MVP scaffolding, 3-minute pitch narratives, and judging criteria moats. |

---

## 📁 Repository Structure

```text
├── index.html               # Landing & Instant Concept Synthesizer
├── dashboard.html           # Command Center Dashboard
├── new-idea.html            # Problem Definition Studio
├── analysis-progress.html   # Live Neural Pipeline Telemetry
├── my-projects.html         # Project Repository with Dynamic Filtering
├── sdg-intelligence.html    # UN SDG Correlation Matrix
├── similarity.html          # Market Similarity & Moat Breakdown
├── innovation-gaps.html     # Market Gap & Opportunity Radar
├── compare-ideas.html       # Intelligence Comparison Matrix (Live Sliders)
├── blueprints.html          # Architectural Blueprint Studio
├── prompt-studio.html       # Prompt Engineering Lab & Archetypes
├── hackathon-mode.html      # Rapid Pitch & MVP Generator
├── 404.html                 # Themed Glassmorphic 404 Error Page
│
├── css/
│   └── styles.css           # Glassmorphic UI, Tech Sliders, Neon Accents, Custom Scrollbars
│
├── js/
│   ├── main.js              # Global search ('/'), notifications, mobile drawer
│   └── analysis.js          # Matrix slider calculation engine, live telemetry logs, filter system
│
├── vercel.json              # High-protection security headers & clean URL rewrites
├── .gitignore               # Git exclusions
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

## 🛡️ Security & Protection Hardening

This project includes hardened **`vercel.json`** headers:
- **Strict Content-Security-Policy (CSP)** preventing cross-site scripting (XSS) and unauthorized script injection.
- **HSTS (`Strict-Transport-Security`)** enforcing TLS 1.3 encryption for 2 years with preloading.
- **X-Frame-Options (`DENY`)** preventing clickjacking attacks.
- **X-Content-Type-Options (`nosniff`)** preventing MIME-sniffing vulnerabilities.
- **Permissions-Policy** disabling unwanted browser APIs (camera, microphone, geolocation).

---

## 🚀 Quick Deployment to Vercel

### Step 1: Initialize Git Repository
```bash
git init
git add .
git commit -m "feat: initial YosiFix Intelligence platform release"
git branch -M main
```

### Step 2: Push to GitHub / GitLab
```bash
git remote add origin https://github.com/YOUR_USERNAME/yosifix.git
git push -u origin main
```

### Step 3: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
2. Select your `yosifix` repository.
3. Framework Preset: **Other** (Static HTML/CSS/JS).
4. Click **Deploy**.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
