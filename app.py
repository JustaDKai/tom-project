import json
from pathlib import Path
from collections import defaultdict
from urllib.parse import quote

from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATE_FILE = DATA_DIR / "templates.json"

DEFAULT_TEMPLATES = {
    "welcome": {
        "label": "Welcome email",
        "body": ""
    },
    "closure_confirmation": {
        "label": "Closure confirmation",
        "body": ""
    },
    "strike_1": {
        "label": "Strike 1 follow-up",
        "body": ""
    },
    "strike_2": {
        "label": "Strike 2 follow-up",
        "body": ""
    },
    "strike_3": {
        "label": "Strike 3 temporary archive",
        "body": ""
    }
}

SIGNATURE_TEMPLATE = """Warm regards,

{engineer_name}
{engineer_role}
Working Hours: {working_hours}
Backup contact: {backup_email}
Manager: {manager_name}
"""


def ensure_template_file():
    DATA_DIR.mkdir(exist_ok=True)

    if not TEMPLATE_FILE.exists():
        save_templates(DEFAULT_TEMPLATES)


def load_templates():
    ensure_template_file()

    with TEMPLATE_FILE.open("r", encoding="utf-8") as file:
        templates = json.load(file)

    for key, value in DEFAULT_TEMPLATES.items():
        if key not in templates:
            templates[key] = value

    for key, template in templates.items():
        template.setdefault("label", key)
        template.setdefault("body", "")

    return templates


def save_templates(templates):
    DATA_DIR.mkdir(exist_ok=True)

    with TEMPLATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(templates, file, indent=2, ensure_ascii=False)


class SafeDict(defaultdict):
    def __missing__(self, key):
        return "{" + key + "}"


def apply_placeholders(text, data):
    if not text:
        return ""

    safe_data = SafeDict(str)
    safe_data.update(data)

    return text.format_map(safe_data)


def build_signature(data):
    should_include_signature = data.get("include_signature") == "yes"

    if not should_include_signature:
        return ""

    signature_data = {
        "engineer_name": data.get("engineer_name", "").strip(),
        "engineer_role": data.get("engineer_role", "").strip(),
        "working_hours": data.get("working_hours", "").strip(),
        "backup_email": data.get("backup_email", "").strip(),
        "manager_name": data.get("manager_name", "").strip()
    }

    return SIGNATURE_TEMPLATE.format_map(SafeDict(str, signature_data))


def generate_email(data, templates=None):
    templates = templates or load_templates()

    template_type = data.get("template_type", "welcome")
    selected_template = templates.get(template_type, templates.get("welcome", {"label": "Welcome email", "body": ""}))

    body_input = data.get("email_body", "").strip()

    body_template = selected_template.get("body", "")

    body = body_input or apply_placeholders(body_template, data)

    signature = build_signature(data)

    if signature:
        if body:
            body = body + "\n\n" + signature
        else:
            body = signature

    return body


@app.route("/", methods=["GET", "POST"])
def home():
    generated_body = ""
    mailto_link = ""
    templates = load_templates()

    form_data = {
        "template_type": "welcome",
        "customer_name": "",
        "customer_role": "",
        "case_id": "",
        "email_body": "",
        "engineer_name": "",
        "engineer_role": "",
        "working_hours": "",
        "backup_email": "",
        "manager_name": "",
        "include_signature": "yes"
    }

    if request.method == "POST":
        form_data.update(request.form.to_dict())
        generated_body = generate_email(form_data, templates=templates)

        mailto_link = "mailto:?body=" + quote(generated_body) if generated_body else ""

    return render_template(
        "index.html",
        templates=templates,
        form_data=form_data,
        generated_body=generated_body,
        mailto_link=mailto_link
    )


@app.route("/health")
def health():
    return "OK"


@app.route("/devops")
def devops():
    return "Email Template Generator is running."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
