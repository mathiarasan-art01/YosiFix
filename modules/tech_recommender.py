"""Stage 7: Tech Stack Recommendation.

Decision-tree style rule engine. Defaults toward a lean stack suitable
for a hackathon/student project, and escalates specific pieces only
when the idea text signals a genuine need for them.
"""


def recommend_stack(idea_text, domain):
    text = idea_text.lower()

    backend = "Flask + SQLAlchemy"
    database = "SQLite (upgrade to PostgreSQL if traffic grows)"
    frontend = "Server-rendered HTML/Jinja2 + Bootstrap 5"
    extras = []
    reasoning = ["Defaulting to a lean, fast-to-ship stack suited for an MVP/hackathon timeline."]

    if any(k in text for k in ["real-time", "realtime", "live chat", "live tracking", "live update"]):
        extras.append("Flask-SocketIO (WebSockets for real-time updates)")
        reasoning.append("Real-time behaviour requested — adding WebSocket support via Flask-SocketIO.")

    if any(k in text for k in ["mobile app", "android app", "ios app", "app for phone"]):
        frontend = "Progressive Web App (PWA) shell, or React Native if a native app is required"
        reasoning.append("Mobile-first usage implied — recommending a PWA first (cheaper to ship) with React Native as a native fallback.")

    if any(k in text for k in ["ai", "machine learning", "ml", "predict", "recommend", "detect", "classif"]):
        extras.append("scikit-learn for lightweight ML, or an LLM API (Claude/Groq) for language-heavy tasks")
        reasoning.append("AI/ML capability implied — scikit-learn covers structured-data tasks; an LLM API covers open-ended text tasks.")

    if any(k in text for k in ["image", "photo", "camera", "detect disease", "identify"]):
        extras.append("OpenCV / a vision model API for image analysis")
        reasoning.append("Image-based functionality implied — adding a computer-vision component.")

    if any(k in text for k in ["large scale", "enterprise", "production", "millions of users", "high traffic"]):
        database = "PostgreSQL + Redis (caching)"
        extras.append("Docker + Nginx for deployment; Celery for background jobs")
        reasoning.append("Scale requirements mentioned — upgrading database and adding caching/containerization.")

    if any(k in text for k in ["multilingual", "multiple language", "regional language", "tamil", "hindi"]):
        extras.append("i18n translation layer (as used in this app itself) + optional translation API")
        reasoning.append("Multilingual requirement detected — planning an i18n layer from day one.")

    if domain in ("Fintech & Payments",):
        extras.append("Payment gateway SDK (Razorpay/Stripe) + stricter input validation & encryption at rest")
        reasoning.append("Financial domain — flagging payment-gateway integration and data-security requirements.")

    if domain in ("Healthcare",):
        extras.append("Attention to data-privacy compliance (e.g. DPDP Act in India) for health records")
        reasoning.append("Health domain — flagging data-privacy compliance as a design constraint, not an afterthought.")

    return {
        "frontend": frontend,
        "backend": backend,
        "database": database,
        "extra_tools": extras,
        "reasoning": reasoning,
    }
