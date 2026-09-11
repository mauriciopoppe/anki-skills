#!/usr/bin/env python3
"""
Sync Lapis note model templates and CSS styling to Anki via AnkiConnect.
"""
import urllib.request
import urllib.error
import json
import os

ANKI_CONNECT_URL = "http://localhost:8765"

def invoke(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
    try:
        req = urllib.request.Request(ANKI_CONNECT_URL, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            res = json.load(response)
            if res.get("error"):
                raise Exception(res["error"])
            return res.get("result")
    except urllib.error.URLError as e:
        raise Exception(f"Failed to connect to AnkiConnect at {ANKI_CONNECT_URL}: {e}")

def main():
    model_name = "Lapis"
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Check current templates of the Lapis model in Anki
    print(f"Checking current templates for model '{model_name}'...")
    current_templates = invoke("modelTemplates", modelName=model_name)
    print("Current templates in Anki:", list(current_templates.keys()))

    # 2. Rename legacy 'Mining' template to 'Comprehension' if present
    if "Mining" in current_templates:
        print("Found legacy template name 'Mining'. Renaming to 'Comprehension'...")
        invoke("modelTemplateRename",
               modelName=model_name,
               oldTemplateName="Mining",
               newTemplateName="Comprehension")
        print("Template renamed successfully.")
        current_templates = invoke("modelTemplates", modelName=model_name)

    # 3. Read local template files
    front_comp_path = os.path.join(script_dir, "front_comprehension.html")
    back_comp_path = os.path.join(script_dir, "back_comprehension.html")
    front_prod_path = os.path.join(script_dir, "front_production.html")
    back_prod_path = os.path.join(script_dir, "back_production.html")
    styling_path = os.path.join(script_dir, "styling.css")

    with open(front_comp_path, "r", encoding="utf-8") as f:
        front_comp = f.read()
    with open(back_comp_path, "r", encoding="utf-8") as f:
        back_comp = f.read()
    with open(front_prod_path, "r", encoding="utf-8") as f:
        front_prod = f.read()
    with open(back_prod_path, "r", encoding="utf-8") as f:
        back_prod = f.read()
    with open(styling_path, "r", encoding="utf-8") as f:
        styling = f.read()

    # 4. Add 'Production' template if missing
    if "Production" not in current_templates:
        print("Template 'Production' not found in model. Adding it via modelTemplateAdd...")
        invoke("modelTemplateAdd",
               modelName=model_name,
               template={
                   "Name": "Production",
                   "Front": front_prod,
                   "Back": back_prod
               })
        print("Template 'Production' added successfully.")

    # 5. Sync templates (updates existing templates with latest local content)
    print("Syncing templates (Comprehension & Production) to Anki...")
    templates_payload = {
        "Comprehension": {
            "Front": front_comp,
            "Back": back_comp
        },
        "Production": {
            "Front": front_prod,
            "Back": back_prod
        }
    }
    invoke("updateModelTemplates", model={"name": model_name, "templates": templates_payload})

    # 6. Sync styling
    print("Syncing styling CSS to Anki...")
    invoke("updateModelStyling", model={"name": model_name, "css": styling})

    print(f"Successfully synchronized '{model_name}' templates and styling to Anki!")

if __name__ == "__main__":
    main()
