"""Stage 8: Architecture Diagram Generation.

Builds a Mermaid.js flowchart definition from the recommended stack so
it can be rendered client-side (see templates/idea_result.html).
"""


def generate_architecture_diagram(tech_stack, domain):
    frontend = tech_stack.get("frontend", "Frontend")
    backend = tech_stack.get("backend", "Backend")
    database = tech_stack.get("database", "Database")
    extras = tech_stack.get("extra_tools", [])

    lines = ["flowchart TD"]
    lines.append(f'    U["User"] --> F["{_clean(frontend)}"]')
    lines.append(f'    F --> B["{_clean(backend)} API"]')
    lines.append(f'    B --> D[("{_clean(database)}")]')
    lines.append(f'    B --> KB["Domain Knowledge Base<br/>({domain})"]')

    prev = "B"
    for i, extra in enumerate(extras):
        node_id = f"X{i}"
        lines.append(f'    {prev} --> {node_id}["{_clean(extra)}"]')

    lines.append('    B --> RES["Blueprint / Analysis Result"]')
    lines.append('    RES --> F')

    return "\n".join(lines)


def _clean(text):
    return text.replace('"', "'").split(" (")[0][:60]
