from __future__ import annotations

import argparse
import importlib
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture Metrika tab screenshots after uploading one or more CSV files"
    )
    parser.add_argument(
        "--csv",
        required=True,
        nargs="+",
        help="Path(s) to CSV files to upload. Use at least two files to enable evolution in Comparador.",
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


def ensure_paths(csv_paths: list[Path], output_dir: Path) -> None:
    if not csv_paths:
        raise ValueError("No CSV files were provided")

    missing_files = [str(path) for path in csv_paths if not path.exists() or not path.is_file()]
    if missing_files:
        missing_list = "\n".join(f"- {path}" for path in missing_files)
        raise FileNotFoundError(f"CSV file(s) not found:\n{missing_list}")

    output_dir.mkdir(parents=True, exist_ok=True)


def click_tab_and_capture(page, tab_name: str, output_file: Path, wait_seconds: float) -> None:
    page.get_by_role("tab", name=tab_name).click()
    time.sleep(wait_seconds)
    page.screenshot(path=str(output_file), full_page=True)


def collapse_sidebar(page, wait_seconds: float) -> None:
    """Collapse Streamlit sidebar if it is visible."""
    collapse_selectors = [
        "button[aria-label='Collapse sidebar']",
        "button[aria-label='Close sidebar']",
        "button[title='Collapse sidebar']",
        "button[title='Close sidebar']",
        "[data-testid='stSidebarCollapseButton'] button",
        "[data-testid='collapsedControl']",
    ]

    for selector in collapse_selectors:
        control = page.locator(selector).first
        if control.count() == 0:
            continue

        try:
            if control.is_visible():
                control.click(timeout=2500)
                time.sleep(wait_seconds)
                return
        except Exception:
            continue

    # Fallback shortcut commonly used by Streamlit to toggle sidebar.
    try:
        page.keyboard.press("Control+b")
        time.sleep(wait_seconds)
    except Exception:
        pass


def force_hide_sidebar(page) -> None:
    """Hard fallback: hide sidebar via CSS if toggle controls are not available."""
    page.add_style_tag(
        content="""
        section[data-testid='stSidebar'] { display: none !important; }
        [data-testid='collapsedControl'] { display: none !important; }
        .stMainBlockContainer, [data-testid='stMainBlockContainer'] {
            margin-left: 0 !important;
            padding-left: 1rem !important;
        }
        """
    )


def align_main_tabs_as_top(page) -> None:
    """Scroll so the main tabs row is at the top of the viewport."""
    script = """
    () => {
        const tab = Array.from(document.querySelectorAll('[role="tab"]'))
            .find((el) => (el.textContent || '').trim() === 'Grup');
        if (!tab) {
            return false;
        }
        const y = tab.getBoundingClientRect().top + window.scrollY - 8;
        window.scrollTo(0, Math.max(0, y));
        return true;
    }
    """
    page.evaluate(script)


def screenshot_from_main_tabs(page, output_file: Path) -> None:
    """Capture viewport clipped from the main tabs row to the bottom."""
    main_tab = page.get_by_role("tab", name="Grup").first
    main_tab.wait_for(timeout=30000)
    box = main_tab.bounding_box()

    if box is None:
        page.screenshot(path=str(output_file), full_page=False)
        return

    viewport = page.viewport_size or {"width": 1600, "height": 1000}
    clip_y = max(0, box["y"] - 8)
    clip_height = max(100, viewport["height"] - clip_y)

    page.screenshot(
        path=str(output_file),
        full_page=False,
        clip={
            "x": 0,
            "y": clip_y,
            "width": viewport["width"],
            "height": clip_height,
        },
    )


def click_nested_tab_and_capture(
    page,
    parent_tab_name: str,
    nested_tab_name: str,
    output_file: Path,
    wait_seconds: float,
) -> None:
    page.get_by_role("tab", name=parent_tab_name).click()
    time.sleep(wait_seconds)
    page.get_by_role("tab", name=nested_tab_name).click()
    time.sleep(wait_seconds)
    align_main_tabs_as_top(page)
    time.sleep(0.2)
    screenshot_from_main_tabs(page, output_file)


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
    csv_paths = [Path(csv_value).expanduser().resolve() for csv_value in args.csv]
    output_dir = Path(args.output_dir).expanduser().resolve()
    headless = args.headless.lower() == "true"

    ensure_paths(csv_paths, output_dir)

    comparator_tabs_to_capture = [
        ("Evolució del grup", "04_comparador_grup.png"),
        ("Evolució per alumne", "05_comparador_alumne.png"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        try:
            page.goto(args.url, wait_until="networkidle", timeout=90000)

            # Upload a CSV through Streamlit's file uploader input.
            file_input = page.locator("input[type='file']")
            file_input.set_input_files([str(path) for path in csv_paths])

            print("Uploaded CSV files:")
            for path in csv_paths:
                print(f"- {path}")

            # Wait until tab navigation appears after data load.
            page.get_by_role("tab", name="Grup").wait_for(timeout=90000)
            time.sleep(args.wait_seconds)

            collapse_sidebar(page, args.wait_seconds)
            force_hide_sidebar(page)
            time.sleep(args.wait_seconds)

            # Ensure comparator content is loaded before capturing nested tabs.
            page.get_by_role("tab", name="Comparador").click()
            page.get_by_role("tab", name="Evolució del grup").wait_for(timeout=90000)
            time.sleep(args.wait_seconds)

            for nested_tab_name, file_name in comparator_tabs_to_capture:
                output_file = output_dir / file_name
                click_nested_tab_and_capture(
                    page,
                    "Comparador",
                    nested_tab_name,
                    output_file,
                    args.wait_seconds,
                )
                print(f"Saved: {output_file}")

        except PlaywrightTimeoutError as exc:
            print(f"Timeout while interacting with Streamlit app: {exc}")
            return 1
        except Exception as exc:
            error_text = str(exc)
            if "Executable doesn't exist" in error_text:
                print("No s'ha trobat el navegador de Playwright.")
                print("Executa: python -m playwright install chromium")
            else:
                print(f"Error inesperat: {error_text}")
            return 1
        finally:
            context.close()
            browser.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
