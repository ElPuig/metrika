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


def click_main_tab(page, tab_name: str, wait_seconds: float) -> None:
    page.get_by_role("tab", name=tab_name).click()
    time.sleep(wait_seconds)


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


def screenshot_from_locator(page, locator, output_file: Path, timeout_ms: int = 30000) -> None:
    """Capture viewport clipped from a specific locator to the bottom."""
    locator.wait_for(timeout=timeout_ms)
    locator.scroll_into_view_if_needed(timeout=timeout_ms)
    time.sleep(0.35)

    # Normalize scroll so the anchor starts near the top; this avoids tiny clips
    # when the heading is visible but positioned close to the viewport bottom.
    try:
        anchor_handle = locator.element_handle(timeout=timeout_ms)
        if anchor_handle is not None:
            page.evaluate(
                """
                (element) => {
                    const anchorTop = element.getBoundingClientRect().top + window.scrollY;
                    window.scrollTo(0, Math.max(0, anchorTop - 8));
                }
                """,
                anchor_handle,
            )
            time.sleep(0.2)
    except Exception:
        pass

    box = locator.bounding_box()
    if box is None:
        page.screenshot(path=str(output_file), full_page=False)
        return

    viewport = page.viewport_size or {"width": 1600, "height": 1000}
    clip_y = max(0, box["y"] - 8)
    clip_height = max(120, viewport["height"] - clip_y)

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


def capture_heading_section(
    page,
    heading_text: str,
    output_file: Path,
    optional: bool = False,
    timeout_ms: int = 18000,
) -> bool:
    """Capture a section that starts at a heading text."""
    heading = page.get_by_role("heading", name=heading_text).first
    try:
        screenshot_from_locator(page, heading, output_file, timeout_ms=timeout_ms)
        print(f"Saved: {output_file}")
        return True
    except Exception as exc:
        if optional:
            print(f"Skipped (optional): {heading_text} ({exc})")
            return False
        print(f"Missing required heading: {heading_text} ({exc})")
        return False


def capture_text_section(
    page,
    text_value: str,
    output_file: Path,
    optional: bool = False,
    timeout_ms: int = 18000,
) -> bool:
    """Capture a section that starts at an arbitrary visible text."""
    text_locator = page.get_by_text(text_value).first
    try:
        screenshot_from_locator(page, text_locator, output_file, timeout_ms=timeout_ms)
        print(f"Saved: {output_file}")
        return True
    except Exception as exc:
        if optional:
            print(f"Skipped (optional): {text_value} ({exc})")
            return False
        print(f"Missing required text: {text_value} ({exc})")
        return False


def capture_ranking_section(page, output_file: Path, timeout_ms: int = 30000) -> bool:
    """Capture ranking section ensuring dataframe content is visible."""
    heading_text = "Ranking d'alumnes per mitjana numèrica (NA=2.5, AS=5, AN=7.5, AE=10)"
    heading = page.get_by_role("heading", name=heading_text).first

    original_viewport = page.viewport_size or {"width": 1600, "height": 1000}
    tall_viewport = {
        "width": original_viewport.get("width", 1600),
        "height": max(1800, original_viewport.get("height", 1000)),
    }

    try:
        heading.wait_for(timeout=timeout_ms)
        heading.scroll_into_view_if_needed(timeout=timeout_ms)
        page.set_viewport_size(tall_viewport)
        time.sleep(0.45)
        # Keep heading near viewport top before measuring clip bounds.
        heading_handle = heading.element_handle(timeout=timeout_ms)
        if heading_handle is not None:
            page.evaluate(
                """
                (element) => {
                    const headingTop = element.getBoundingClientRect().top + window.scrollY;
                    window.scrollTo(0, Math.max(0, headingTop - 8));
                }
                """,
                heading_handle,
            )
            time.sleep(0.25)

        heading_box = heading.bounding_box()
        viewport = page.viewport_size or tall_viewport

        if heading_box is None:
            screenshot_from_locator(page, heading, output_file, timeout_ms=timeout_ms)
        else:
            clip_y = max(0, heading_box["y"] - 8)
            max_height = max(160, viewport["height"] - clip_y)
            # Keep a large section below the ranking heading so the table is included.
            clip_height = min(max_height, max(900, min(1400, max_height)))

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

        print(f"Saved: {output_file}")
        return True
    except Exception as exc:
        print(f"Missing required ranking section ({exc})")
        return False
    finally:
        try:
            page.set_viewport_size(original_viewport)
            time.sleep(0.2)
        except Exception:
            pass


def click_nested_tab_and_capture(
    page,
    parent_tab_name: str,
    nested_tab_name: str,
    output_file: Path,
    wait_seconds: float,
) -> None:
    click_main_tab(page, parent_tab_name, wait_seconds)
    page.get_by_role("tab", name=nested_tab_name).click()
    time.sleep(wait_seconds)
    align_main_tabs_as_top(page)
    time.sleep(0.2)
    screenshot_from_main_tabs(page, output_file)


def click_main_tab_and_capture(
    page,
    tab_name: str,
    output_file: Path,
    wait_seconds: float,
) -> None:
    click_main_tab(page, tab_name, wait_seconds)
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

    group_section_captures = [
        ("Resum de suspensos per alumne", "01_grup_resum_suspensos_alumne.png", False),
        ("Assignatures més suspeses", "02_grup_assignatures_mes_suspeses.png", False),
        ("Distribució de qualificacions per assignatura", "03_grup_distribucio_qualificacions_assignatura.png", False),
        ("Mapa de calor: Alumnes vs. Assignatures", "04_grup_mapa_calor_alumnes_assignatures.png", False),
    ]

    subject_section_captures = [
        ("Comentaris per alumne", "06_materia_comentaris_per_alumne.png", False),
        ("Distribució de qualificacions", "07_materia_distribucio_qualificacions.png", False),
        ("Aprovats i no aprovats de l'assignatura (inclou adaptacions)", "08_materia_aprovats_no_aprovats.png", False),
    ]

    student_section_captures = [
        ("Nota Mitjana", "09_alumne_nota_mitjana.png", False),
        ("Distribució de Qualificacions", "11_alumne_distribucio_qualificacions.png", False),
        ("⚠️ Matèries Pendents (Cursos Anteriors)", "12_alumne_materies_pendents.png", True),
    ]

    comparator_group_section_captures = [
        ("Distribució de qualificacions per trimestre", "14_comparador_distribucio_qualificacions_trimestre.png", False),
        ("Evolució de mitjana per matèria", "15_comparador_evolucio_mitjana_materia.png", False),
        ("Alumnes que més milloren", "16_comparador_alumnes_milloren.png", False),
        ("Alumnes amb més regressió", "17_comparador_alumnes_regressio.png", False),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()
        required_failures: list[str] = []

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

            # Base captures for each top-level tab.
            click_main_tab_and_capture(page, "Grup", output_dir / "00_grup_overview.png", args.wait_seconds)
            print(f"Saved: {output_dir / '00_grup_overview.png'}")

            for heading_text, file_name, optional in group_section_captures:
                ok = capture_heading_section(page, heading_text, output_dir / file_name, optional=optional)
                if not ok and not optional:
                    required_failures.append(heading_text)

            ranking_ok = capture_ranking_section(
                page,
                output_dir / "05_grup_ranking_mitjana_numerica.png",
            )
            if not ranking_ok:
                required_failures.append("Ranking d'alumnes per mitjana numèrica (NA=2.5, AS=5, AN=7.5, AE=10)")

            click_main_tab_and_capture(page, "Materia", output_dir / "00_materia_overview.png", args.wait_seconds)
            print(f"Saved: {output_dir / '00_materia_overview.png'}")

            for heading_text, file_name, optional in subject_section_captures:
                ok = capture_heading_section(page, heading_text, output_dir / file_name, optional=optional)
                if not ok and not optional:
                    required_failures.append(heading_text)

            alumne_overview = output_dir / "00_alumne_overview.png"
            click_main_tab_and_capture(page, "Alumne", alumne_overview, args.wait_seconds)
            print(f"Saved: {alumne_overview}")

            adaptation_screenshot = output_dir / "10_alumne_flag_adaptacio.png"
            adaptation_screenshot.write_bytes(alumne_overview.read_bytes())
            print(f"Saved: {adaptation_screenshot}")

            for heading_text, file_name, optional in student_section_captures:
                timeout_ms = 6000 if optional else 18000
                ok = capture_heading_section(
                    page,
                    heading_text,
                    output_dir / file_name,
                    optional=optional,
                    timeout_ms=timeout_ms,
                )
                if not ok and not optional:
                    required_failures.append(heading_text)

            # Ensure comparator content is loaded before capturing nested tabs.
            click_main_tab(page, "Comparador", args.wait_seconds)
            page.get_by_role("tab", name="Evolució del grup").wait_for(timeout=90000)
            time.sleep(args.wait_seconds)

            click_nested_tab_and_capture(
                page,
                "Comparador",
                "Evolució del grup",
                output_dir / "13_comparador_evolucio_grup_grafica.png",
                args.wait_seconds,
            )
            print(f"Saved: {output_dir / '13_comparador_evolucio_grup_grafica.png'}")

            for heading_text, file_name, optional in comparator_group_section_captures:
                ok = capture_heading_section(page, heading_text, output_dir / file_name, optional=optional)
                if not ok and not optional:
                    required_failures.append(heading_text)

            click_nested_tab_and_capture(
                page,
                "Comparador",
                "Evolució per alumne",
                output_dir / "18_comparador_evolucio_alumne_overview.png",
                args.wait_seconds,
            )
            print(f"Saved: {output_dir / '18_comparador_evolucio_alumne_overview.png'}")
            table_ok = capture_heading_section(
                page,
                "Taula de comparació per matèria",
                output_dir / "19_comparador_taula_comparacio_materia.png",
                optional=False,
            )
            if not table_ok:
                required_failures.append("Taula de comparació per matèria")

            click_main_tab_and_capture(page, "Exportació", output_dir / "20_exportacio_overview.png", args.wait_seconds)
            print(f"Saved: {output_dir / '20_exportacio_overview.png'}")

            if required_failures:
                deduped_failures = sorted(set(required_failures))
                print("No s'han pogut capturar totes les seccions obligatories:")
                for missing_item in deduped_failures:
                    print(f"- {missing_item}")
                return 1

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
            try:
                context.close()
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
