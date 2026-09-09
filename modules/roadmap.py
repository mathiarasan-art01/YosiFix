"""Stage 9: Roadmap Generation.

Splits gap-derived opportunities and baseline requirements into three
build phases, so the output is directly actionable rather than a wall
of undifferentiated feature ideas.
"""


def generate_roadmap(gap_features, tech_stack):
    mvp = [
        "User authentication (sign up / login)",
        "Core idea/problem input flow",
        "Primary value-delivering feature (the #1 differentiator below)",
    ]
    v2 = ["Polish UX based on early user feedback", "Add analytics/dashboard for usage insights"]
    v3 = ["Scale infrastructure", "Explore integrations / partnerships"]

    if gap_features:
        mvp.append(f"Address top gap: {gap_features[0]}")
        for g in gap_features[1:3]:
            v2.append(f"Address gap: {g}")
        for g in gap_features[3:]:
            v3.append(f"Explore: {g}")

    extras = tech_stack.get("extra_tools", [])
    if extras:
        v2.append(f"Integrate: {extras[0]}")
        for e in extras[1:]:
            v3.append(f"Integrate: {e}")

    return {"mvp": mvp[:6], "v2": v2[:6], "v3": v3[:6]}
