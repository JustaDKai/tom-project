from flask import Flask, render_template, request
from urllib.parse import quote
from collections import defaultdict

app = Flask(__name__)

TEMPLATE_LIBRARY = {
    "welcome": {
        "label": "Welcome email",
        "subject": "",
        "body": ""
    },
    "closure_confirmation": {
        "label": "Closure confirmation",
        "subject": "",
        "body": ""
    },
    "strike_1": {
        "label": "Strike 1 follow-up",
        "subject": "",
        "body": ""
    },
    "strike_2": {
        "label": "Strike 2 follow-up",
        "subject": "",
        "body": ""
    },
    "strike_3": {
        "label": "Strike 3 temporary archive",
        "subject": "",
        "body": ""
    }
}


SIGNATURE_TEMPLATE = """Best regards,

{engineer_name}
{engineer_role}
Working Hours: {working_hours}
Backup contact: {backup_email}
Manager: {manager_name}
"""


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


def generate_email(data):
    template_type = data.get("template_type", "welcome")
    selected_template = TEMPLATE_LIBRARY.get(template_type, TEMPLATE_LIBRARY["welcome"])

    subject_input = data.get("subject", "").strip()
    body_input = data.get("email_body", "").strip()

    subject_template = selected_template.get("subject", "")
    body_template = selected_template.get("body", "")

    subject = subject_input or apply_placeholders(subject_template, data)
    body = body_input or apply_placeholders(body_template, data)

    signature = build_signature(data)

    if signature:
        if body:
            body = body + "\n\n" + signature
        else:
            body = signature

    return subject, body


@app.route("/", methods=["GET", "POST"])
def home():
    generated_subject = ""
    generated_body = ""
    mailto_link = ""

    form_data = {
        "template_type": "welcome",
        "customer_name": "",
        "customer_role": "",
        "case_id": "",
        "subject": "",
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
        generated_subject, generated_body = generate_email(form_data)

        mailto_link = (
            "mailto:"
            "?subject="
            + quote(generated_subject)
            + "&body="
            + quote(generated_body)
        )

    return render_template(
        "index.html",
        templates=TEMPLATE_LIBRARY,
        form_data=form_data,
        generated_subject=generated_subject,
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
