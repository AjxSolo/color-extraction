import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv, find_dotenv
from tqdm.auto import tqdm

# ─────────────────────────────────────────────────────────────
# CONFIGURE LOGGING
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ─────────────────────────────────────────────────────────────
# LOAD ENVIRONMENT (.env)
# ─────────────────────────────────────────────────────────────
dotenv_path = find_dotenv(filename=".env", raise_error_if_not_found=False)
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("OPENAI_API_KEY not found in .env file.")
    raise RuntimeError("Missing OpenAI API key.")

client = OpenAI(api_key=api_key)

# ─────────────────────────────────────────────────────────────
# HELPER: Use GPT to extract dominant colors
# ─────────────────────────────────────────────────────────────
def get_dominant_colors(image_url: str) -> tuple[str, str]:
    try:
        head_resp = requests.head(image_url, timeout=5)
        head_resp.raise_for_status()
    except Exception as e:
        logging.warning(f"Skipping invalid image URL: {image_url} → {e}")
        return "", ""

    prompt = (
        "You are a vision model assistant. The image shows a product on a white background. "
        "Identify up to 2 dominant colors of the product. The primary color must cover most of the product. "
        "Only include a secondary color if it clearly covers at least 15% of the product. "
        "Return only common color names like 'red', 'blue', 'green', 'black', 'white', etc. "
        "Avoid branding or specific tones (e.g. use 'green' instead of 'paramedic green'). "
        "Respond in this exact JSON format: {\"primary\": \"<color>\", \"secondary\": \"<color>\"} or {\"primary\": \"<color>\"}"
    )

    messages = [
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": image_url}}
        ]},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        color_data = json.loads(content)
        primary = color_data.get("primary", "")
        secondary = color_data.get("secondary", "")
        return primary, secondary
    except Exception as e:
        logging.error(f"Color detection failed for {image_url}: {e}")
        return "", ""

# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────
def process_colors(input_csv: str):
    script_dir = Path(__file__).parent
    input_path = script_dir / input_csv

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    df = pd.read_csv(input_path)

    required_cols = {"ID", "Image Src"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Input CSV must contain columns: {required_cols}")

    # Initialize columns
    df["Primary Color"] = ""
    df["Secondary Color"] = ""

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Analyzing colors"):
        time.sleep(1)
        img_url = row["Image Src"]
        primary, secondary = get_dominant_colors(img_url)
        df.at[idx, "Primary Color"] = primary
        df.at[idx, "Secondary Color"] = secondary

    # Output CSV
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = script_dir / f"color_output_{ts}.csv"
    df.to_csv(output_path, index=False)
    logging.info(f"Color detection complete. Output saved to: {output_path}")

# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python detect_colors.py <input.csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    process_colors(input_file)
