"""Shared vocabularies. Used to validate AI output against canonical values."""

CLAIM_STATUSES = ["known", "evidence-backed", "estimated", "unknown", "needs-validation"]

CLAIM_STATUS_LABELS = {
    "known": "Known fact",
    "evidence-backed": "Evidence-backed",
    "estimated": "Estimated",
    "unknown": "Unknown",
    "needs-validation": "Needs validation",
}

EVIDENCE_TYPES = {
    "github": {"label": "Open-source code", "icon": "bi-github"},
    "paper": {"label": "Research paper", "icon": "bi-journal-text"},
    "dataset": {"label": "Dataset", "icon": "bi-database"},
    "product": {"label": "Product / launch", "icon": "bi-bag"},
    "discussion": {"label": "Community discussion", "icon": "bi-chat-square-text"},
    "documentation": {"label": "Reference", "icon": "bi-book"},
}

# UN Sustainable Development Goals (canonical names; AI-provided names are replaced by these)
SDGS = {
    1: "No Poverty", 2: "Zero Hunger", 3: "Good Health and Well-being", 4: "Quality Education",
    5: "Gender Equality", 6: "Clean Water and Sanitation", 7: "Affordable and Clean Energy",
    8: "Decent Work and Economic Growth", 9: "Industry, Innovation and Infrastructure",
    10: "Reduced Inequalities", 11: "Sustainable Cities and Communities",
    12: "Responsible Consumption and Production", 13: "Climate Action", 14: "Life Below Water",
    15: "Life on Land", 16: "Peace, Justice and Strong Institutions", 17: "Partnerships for the Goals",
}

SDG_KEYWORDS = {
    1: ["poverty", "income", "low-income", "livelihood", "microfinance"],
    2: ["food", "hunger", "crop", "farm", "agricultur", "nutrition", "harvest", "farmer"],
    3: ["health", "medical", "disease", "patient", "clinic", "mental", "wellbeing", "hospital"],
    4: ["education", "learn", "student", "school", "teach", "skill", "course"],
    5: ["women", "gender", "girl", "female"],
    6: ["water", "sanitation", "irrigation", "hygiene"],
    7: ["energy", "solar", "electricity", "renewable", "battery", "power"],
    8: ["job", "employment", "msme", "small business", "productivity", "gig", "worker"],
    9: ["infrastructure", "industry", "manufactur", "innovation", "iot", "connectivity"],
    10: ["inclusion", "accessib", "disabilit", "rural", "underserved", "marginal", "multilingual"],
    11: ["city", "urban", "traffic", "transport", "housing", "waste", "smart city", "parking"],
    12: ["recycl", "waste", "supply chain", "consumption", "circular", "packaging"],
    13: ["climate", "carbon", "emission", "flood", "drought", "weather"],
    14: ["ocean", "marine", "fish", "coastal"],
    15: ["forest", "biodiversity", "wildlife", "soil", "land", "deforest"],
    16: ["justice", "legal", "corruption", "governance", "transparen", "fraud", "safety"],
    17: ["partnership", "open data", "collaborat", "ngo"],
}

# Mutation strategies. ``terms`` are used to scan retrieved evidence for coverage gaps.
MUTATION_STRATEGIES = {
    "privacy_first": {
        "title": "Privacy-first", "icon": "bi-shield-lock",
        "terms": ["privacy", "on-device", "federated", "encrypt", "anonymi", "gdpr", "local-first"],
        "pitch": "Keep sensitive data on the user's device and minimise what is ever uploaded.",
    },
    "offline_first": {
        "title": "Offline-first", "icon": "bi-wifi-off",
        "terms": ["offline", "low-bandwidth", "edge", "on-device", "no internet", "sms", "tflite"],
        "pitch": "Work fully without connectivity and sync opportunistically.",
    },
    "accessibility_first": {
        "title": "Accessibility-first", "icon": "bi-universal-access",
        "terms": ["accessib", "screen reader", "voice", "blind", "visually impaired", "disabilit", "wcag"],
        "pitch": "Design for users with disabilities and low digital literacy from day one.",
    },
    "research_first": {
        "title": "Research-first", "icon": "bi-mortarboard",
        "terms": ["benchmark", "dataset", "evaluation", "reproducib", "ablation", "baseline"],
        "pitch": "Contribute a benchmark, dataset or measurable evaluation the field lacks.",
    },
    "low_cost": {
        "title": "Low-cost", "icon": "bi-currency-rupee",
        "terms": ["low-cost", "affordable", "cheap", "raspberry", "arduino", "frugal", "free"],
        "pitch": "Hit a price point an order of magnitude below incumbents.",
    },
    "multilingual": {
        "title": "Multilingual", "icon": "bi-translate",
        "terms": ["multilingual", "language", "tamil", "hindi", "regional", "translation", "vernacular", "localiz"],
        "pitch": "Serve users in their own language, including low-resource languages.",
    },
    "security_first": {
        "title": "Security-first", "icon": "bi-shield-check",
        "terms": ["security", "tamper", "authentication", "audit", "fraud", "zero-trust", "integrity"],
        "pitch": "Make tamper-resistance and auditability the core differentiator.",
    },
    "sustainability_first": {
        "title": "Sustainability-first", "icon": "bi-tree",
        "terms": ["sustainab", "carbon", "energy-efficient", "green", "recycl", "solar"],
        "pitch": "Minimise energy and material footprint and measure it.",
    },
    "community_first": {
        "title": "Community-first", "icon": "bi-people",
        "terms": ["community", "crowdsourc", "peer", "volunteer", "open-source", "citizen"],
        "pitch": "Let the community contribute data, validation and support.",
    },
    "performance_first": {
        "title": "Performance-first", "icon": "bi-lightning-charge",
        "terms": ["real-time", "latency", "fast", "lightweight", "optimiz", "quantiz", "low-latency"],
        "pitch": "Win on speed: real-time results on modest hardware.",
    },
}

TECH_LAYERS = ["Frontend", "Backend", "Database", "AI / ML", "Infrastructure", "Integrations"]
