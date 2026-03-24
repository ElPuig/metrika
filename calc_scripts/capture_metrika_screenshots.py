from __future__ import annotations

import argparse
import importlib
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture Metrika tab screenshots after uploading a CSV file"
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to CSV file to upload",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8501",
        help="Streamlit app URL",
    )
    parser.add_argument(
        "--output-dir",
        default="docs_site/assets/screenshots",
        help="Directory where screenshots are saved",
    )
    parser.add_argument(
        "--headless",
        default="true",
        choices=["true", "false"],
        help="Run browser headless or visible",
    )
    parser.add_argument(
        "--wait-seconds",
        type=float,
        default=1.8,
        help="Extra wait after tab change",
    )
    return parser.parse_args()


def ensure_paths(csv_path: Path, output_dir: Path) -> None:
    if not csv_path.exists() or not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    output_dir.mkdir(parents=True, exist_ok=True)


def click_tab_and_capture(page, tab_name: str, output_file: Path, wait_seconds: float) -> None:
    page.get_by_role("tab", name=tab_name).click()
    time.sleep(wait_seconds)
    page.screenshot(path=str(output_file), full_page=True)


def main() -> int:
    try:
        sync_api = importlib.import_module("playwright.sync_api")
        PlaywrightTimeoutError = sync_api.TimeoutError
        sync_playwright = sync_api.sync_playwright
    except ModuleNotFoundError:
        print("Playwright no esta instal-lat. Executa: pip install -r requirements-test.txt")
        print("Despres executa: python -m playwright install chromium")
        return 1

    args = parse_args()
    csv_path = Path(args.csv).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    headless = args.headless.lower() == "true"

    ensure_paths(csv_path, output_dir)

    tabs_to_capture = [
        ("Grup", "01_grup.png"),
        ("Materia", "02_materia.png"),
        ("Alumne", "03_alumne.png"),
        ("Comparador", "04_comparador.png"),
        ("Exportació", "05_exportacio.png"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        try:
            page.goto(args.url, wait_until="networkidle", timeout=90000)

            # Upload a CSV through Streamlit's file uploader input.
            file_input = page.locator("input[type='file']")
            file_input.set_input_files(str(csv_path))

            # Wait until tab navigation appears after data load.
            page.get_by_role("tab", name="Grup").wait_for(timeout=90000)
            time.sleep(args.wait_seconds)

            for tab_name, file_name in tabs_to_capture:
                output_file = output_dir / file_name
                click_tab_and_capture(page, tab_name, output_file, args.wait_seconds)
                print(f"Saved: {output_file}")

        except PlaywrightTimeoutError as exc:
            print(f"Timeout while interacting with Streamlit app: {exc}")
            return 1
        finally:
            context.close()
            browser.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
