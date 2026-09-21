import json, argparse
from .parser_food import food_contact
from .parser_terms import component, material
from .parser_thickness import thickness
from .pdf_extractor import extract_text

def parse_current_component(text):
    return {"component": component(text), "current_material": material(text),
            "thickness": thickness(text), "food_contact": food_contact(text)}

def parse_pdf(path):
    return parse_current_component(extract_text(path))

def main(argv=None):
    cli = argparse.ArgumentParser(); cli.add_argument("pdf_path")
    print(json.dumps(parse_pdf(cli.parse_args(argv).pdf_path), indent=2)); return 0

if __name__ == "__main__":
    raise SystemExit(main())
