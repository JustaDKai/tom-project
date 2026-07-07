import json
import re
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATE_DIR = DATA_DIR / "templates"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR))
app.secret_key = "template-manager-dev-secret"
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


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text or "custom_template"


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


@app.route("/", methods=["GET", "POST"])
def manage_templates():
    templates = load_templates()

    selected_key = (
        request.args.get("template_key")
        or request.form.get("template_key")
        or "welcome"
    )

    if selected_key not in templates:
        selected_key = next(iter(templates.keys()))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "save_existing":
            template_key = request.form.get("template_key", "").strip()
            template_label = request.form.get("template_label", "").strip()
            template_body = request.form.get("template_body", "")

            if not template_key:
                flash("Template key is missing.")
                return redirect(url_for("manage_templates"))

            if not template_label:
                template_label = template_key

            templates[template_key] = {
                "label": template_label,
                "body": template_body
            }

            save_templates(templates)
            flash("Template saved successfully.")

            return redirect(url_for("manage_templates", template_key=template_key))

        if action == "add_new":
            new_label = request.form.get("new_template_label", "").strip()
            new_key = request.form.get("new_template_key", "").strip()
            new_body = request.form.get("new_template_body", "")

            if not new_key:
                new_key = slugify(new_label)

            if not new_label:
                new_label = new_key

            templates[new_key] = {
                "label": new_label,
                "body": new_body
            }

            save_templates(templates)
            flash("New template added successfully.")

            return redirect(url_for("manage_templates", template_key=new_key))

        if action == "delete":
            template_key = request.form.get("template_key", "").strip()

            if template_key in templates and len(templates) > 1:
                templates.pop(template_key)
                save_templates(templates)

                next_key = next(iter(templates.keys()))
                flash("Template deleted.")

                return redirect(url_for("manage_templates", template_key=next_key))

            flash("Cannot delete the last template.")
            return redirect(url_for("manage_templates", template_key=template_key))

        if action == "import_defaults":
            for key, value in DEFAULT_TEMPLATES.items():
                templates.setdefault(key, value)

            save_templates(templates)
            flash("Default templates imported.")

            return redirect(url_for("manage_templates", template_key=selected_key))

    selected_template = templates[selected_key]

    return render_template(
        "template_manager.html",
        templates=templates,
        selected_key=selected_key,
        selected_template=selected_template
    )


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)