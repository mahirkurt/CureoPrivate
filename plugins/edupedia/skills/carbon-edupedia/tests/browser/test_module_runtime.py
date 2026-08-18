from pathlib import Path
import re

import pytest


SKILL_ROOT = Path(__file__).parents[2]
TEMPLATE = SKILL_ROOT / "assets" / "module-template.html"


@pytest.fixture(scope="session")
def chromium_browser():
    playwright_api = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright Python paketi yok; browser suite atlandı.",
    )
    manager = playwright_api.sync_playwright().start()
    try:
        browser = manager.chromium.launch(headless=True)
    except playwright_api.Error as exc:
        manager.stop()
        pytest.skip(
            "Playwright Chromium bulunamadı; "
            "`python3 -m playwright install chromium` çalıştırın. "
            f"Ayrıntı: {exc}"
        )
    yield browser
    browser.close()
    manager.stop()


@pytest.fixture
def page(chromium_browser):
    context = chromium_browser.new_context(viewport={"width": 900, "height": 900})
    current = context.new_page()
    yield current
    context.close()


def open_offline(page):
    external_requests = []

    def record_request(request):
        if re.match(r"^https?://", request.url):
            external_requests.append(request.url)

    page.on("request", record_request)
    page.route(re.compile(r"^https?://"), lambda route: route.abort())
    page.goto(TEMPLATE.resolve().as_uri(), wait_until="load")
    page.wait_for_selector("#stage [data-stage-heading='true']")
    return external_requests


def single_segment_html(segment_type):
    source = TEMPLATE.read_text(encoding="utf-8")
    marker = "/* ==========================================================================\n   MOTOR (ENGINE)"
    assert marker in source
    injection = (
        "MODULE_DATA.segments = MODULE_DATA.segments"
        f'.filter((segment) => segment.type === "{segment_type}").slice(0, 1);\n\n'
    )
    return source.replace(marker, injection + marker, 1)


def open_single_segment(page, segment_type):
    external_requests = []
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on(
        "request",
        lambda request: external_requests.append(request.url)
        if re.match(r"^https?://", request.url)
        else None,
    )
    page.route(re.compile(r"^https?://"), lambda route: route.abort())
    page.set_content(single_segment_html(segment_type), wait_until="load")
    page.wait_for_selector("#stage [data-stage-heading='true']")
    assert external_requests == []
    assert errors == []


def tab_until(page, selector, max_tabs=40):
    for _ in range(max_tabs):
        if page.evaluate(
            "(selector) => document.activeElement?.matches(selector) || false",
            selector,
        ):
            return
        page.keyboard.press("Tab")
    active = page.evaluate(
        "() => ({tag:document.activeElement?.tagName, "
        "id:document.activeElement?.id, className:document.activeElement?.className})"
    )
    pytest.fail(f"Klavye odağı {selector!r} seçicisine ulaşmadı; aktif öğe: {active}")


def keyboard_activate(page, selector):
    page.locator(selector).focus()
    page.keyboard.press("Enter")


def assert_no_viewport_overflow(page, selectors):
    metrics = page.evaluate(
        """(selectors) => ({
          viewport: window.innerWidth,
          documentWidth: document.documentElement.scrollWidth,
          boxes: selectors.flatMap((selector) =>
            Array.from(document.querySelectorAll(selector)).map((node) => {
              const rect = node.getBoundingClientRect();
              return {selector, left: rect.left, right: rect.right, width: rect.width};
            })
          )
        })""",
        selectors,
    )
    assert metrics["documentWidth"] <= metrics["viewport"] + 1, metrics
    for box in metrics["boxes"]:
        assert box["left"] >= -1, box
        assert box["right"] <= metrics["viewport"] + 1, box


def test_offline_fonts_are_registered_and_load_from_inline_data(page):
    external = open_offline(page)
    result = page.evaluate(
        """async () => {
          const probes = [
            ["400 18px 'IBM Plex Sans'", "Aa Ğğ Şş"],
            ["500 18px 'IBM Plex Sans'", "Aa Ğğ Şş"],
            ["600 18px 'IBM Plex Sans'", "Aa Ğğ Şş"],
            ["700 18px 'IBM Plex Sans'", "Aa Ğğ Şş"],
            ["400 18px 'IBM Plex Serif'", "Aa Ğğ Şş"],
            ["600 18px 'IBM Plex Serif'", "Aa Ğğ Şş"],
            ["italic 400 18px 'IBM Plex Serif'", "Aa Ğğ Şş"],
            ["400 18px 'IBM Plex Mono'", "Aa Ğğ Şş"],
            ["600 18px 'IBM Plex Mono'", "Aa Ğğ Şş"],
            ["700 18px 'IBM Plex Mono'", "Aa Ğğ Şş"],
          ];
          for (const [descriptor, text] of probes) {
            await document.fonts.load(descriptor, text);
          }
          await document.fonts.ready;
          const faces = Array.from(document.fonts)
            .filter((face) => face.family.includes("IBM Plex"))
            .map((face) => ({
              family: face.family.replaceAll('"', ""),
              style: face.style,
              weight: Number(face.weight),
              status: face.status,
            }));
          return {
            faces,
            bodyFamily: getComputedStyle(document.body).fontFamily,
            checks: probes.map(([descriptor, text]) =>
              document.fonts.check(descriptor, text)
            ),
          };
        }"""
    )
    assert external == []
    assert len(result["faces"]) == 20
    assert all(face["status"] == "loaded" for face in result["faces"])
    assert all(result["checks"])
    assert result["bodyFamily"].lstrip("\"'").startswith("IBM Plex Sans")


def test_keyboard_core_flow_and_quiz_retry_focus(page):
    open_offline(page)
    assert page.locator(".objectives").is_visible()
    assert page.evaluate(
        "() => document.activeElement?.matches(\"#stage [data-stage-heading='true']\")"
    )

    tab_until(page, "#stage .hook-opt")
    page.keyboard.press("Enter")
    assert page.locator("#stage .hook-opt[aria-pressed='true']").count() == 1

    tab_until(page, "#nextBtn")
    page.keyboard.press("Enter")
    assert page.locator("#stage h2").inner_text() == "Maddenin Üç Hâli"
    assert page.evaluate(
        "() => document.activeElement?.matches(\"#stage [data-stage-heading='true']\")"
    )

    tab_until(page, "#nextBtn")
    page.keyboard.press("Enter")
    assert page.locator("#stage h2").inner_text() == "Kavram Kartları"

    for _ in range(3):
        keyboard_activate(page, "#fctrl .btn--primary")
        keyboard_activate(page, "#fctrl .btn--primary")

    assert page.locator("#stage h2").inner_text() == "Mini Yarışma"
    keyboard_activate(page, "#stage .opt:nth-child(2)")
    assert "Tekrar dene" in page.locator("#qfb").inner_text()
    assert page.evaluate(
        "() => document.activeElement?.matches('#stage .opt:not([disabled])')"
    )

    page.keyboard.press("Enter")
    assert "Doğru" in page.locator("#qfb").inner_text()
    assert page.evaluate(
        "() => document.activeElement?.matches('#stage > .btn--primary')"
    )

    page.keyboard.press("Enter")
    assert re.sub(r"\s+", " ", page.locator(".streak").inner_text()).strip() == "Soru 2 / 2"
    assert page.evaluate(
        "() => document.activeElement?.matches(\"#stage [data-stage-heading='true']\")"
    )

    keyboard_activate(page, "#stage .opt:nth-child(2)")
    assert page.evaluate(
        "() => document.activeElement?.matches('#stage > .btn--primary')"
    )


@pytest.mark.parametrize(
    "segment_type",
    [
        "selfExplain",
        "brainbreak",
        "match",
        "conceptMap",
        "worked",
        "sim",
        "fillblank",
        "checkpoint",
    ],
)
def test_remaining_demo_interactions_keyboard_smoke(chromium_browser, segment_type):
    context = chromium_browser.new_context(viewport={"width": 900, "height": 900})
    current = context.new_page()
    try:
        open_single_segment(current, segment_type)

        if segment_type == "selfExplain":
            keyboard_activate(current, ".se-reveal")
            assert current.locator("#seModel").is_visible()
        elif segment_type == "brainbreak":
            keyboard_activate(current, "#nextBtn")
            assert current.locator("#stage [data-seg='summary'], #stage .summary").count() == 1
        elif segment_type == "match":
            keyboard_activate(current, '[data-side="L"][data-i="0"]')
            keyboard_activate(current, '[data-side="R"][data-origin="0"]')
            assert current.locator('[data-side="L"][data-i="0"]').is_disabled()
        elif segment_type == "conceptMap":
            first_edge = current.evaluate("MODULE_DATA.segments[0].targetEdges[0]")
            keyboard_activate(current, f'.cmap-node[data-id="{first_edge[0]}"]')
            keyboard_activate(current, f'.cmap-node[data-id="{first_edge[1]}"]')
            assert current.locator("#cmapEdgeList li").count() == 1
        elif segment_type == "worked":
            answer = current.evaluate(
                """() => {
                  const segment = MODULE_DATA.segments[0];
                  return segment.steps[segment.fadeFrom].answer[0];
                }"""
            )
            current.locator(".worked-input").first.focus()
            current.keyboard.type(answer)
            current.keyboard.press("Tab")
            current.keyboard.press("Enter")
            assert "Çözdün" in current.locator("#wfb").inner_text()
        elif segment_type == "sim":
            slider = current.locator('.sim-param input[type="range"]').first
            before = slider.input_value()
            slider.focus()
            current.keyboard.press("ArrowRight")
            assert slider.input_value() != before
        elif segment_type == "fillblank":
            answer = current.evaluate("MODULE_DATA.segments[0].items[0].answer[0]")
            current.evaluate(
                """(answer) => Array.from(document.querySelectorAll(".chip-btn"))
                  .find((button) => button.dataset.w === answer).focus()""",
                answer,
            )
            current.keyboard.press("Enter")
            assert "Doğru" in current.locator("#ffb").inner_text()
        elif segment_type == "checkpoint":
            keyboard_activate(current, "#stage > .btn--primary")
            correct = current.evaluate(
                "MODULE_DATA.segments[0].mixedQuestions[0].correctIndex"
            )
            keyboard_activate(current, f"#stage .opt:nth-child({correct + 1})")
            assert "Doğru" in current.locator("#qfb").inner_text()
    finally:
        context.close()


@pytest.mark.parametrize("width", [320, 360])
def test_mobile_primary_chrome_stays_inside_viewport(chromium_browser, width):
    context = chromium_browser.new_context(viewport={"width": width, "height": 900})
    current = context.new_page()
    try:
        open_offline(current)
        assert_no_viewport_overflow(
            current,
            [
                ".wrap",
                ".topbar",
                ".topbar__hero",
                ".topbar__status",
                ".topbar__row",
                ".topbar__r",
                "#stage",
                ".nav",
                ".hook-opt",
            ],
        )
    finally:
        context.close()


def test_two_hundred_percent_text_zoom_keeps_core_controls_usable(chromium_browser):
    context = chromium_browser.new_context(viewport={"width": 360, "height": 900})
    current = context.new_page()
    try:
        open_offline(current)
        current.evaluate("document.documentElement.style.fontSize = '200%'")
        current.wait_for_function(
            "() => parseFloat(getComputedStyle(document.documentElement).fontSize) >= 31"
        )
        assert current.locator("#nextBtn").is_visible()
        assert current.locator(".hook-opt").first.is_visible()
        assert_no_viewport_overflow(
            current,
            [".wrap", ".topbar", "#stage", ".nav", ".hook-opt", "#nextBtn"],
        )
    finally:
        context.close()


def test_storage_failures_degrade_without_breaking_module(chromium_browser):
    context = chromium_browser.new_context(viewport={"width": 900, "height": 900})
    current = context.new_page()
    errors = []
    current.on("pageerror", lambda error: errors.append(str(error)))
    current.add_init_script(
        """for (const name of ["localStorage", "sessionStorage"]) {
          Object.defineProperty(window, name, {
            configurable: true,
            get() { throw new DOMException("storage disabled by test", "SecurityError"); }
          });
        }"""
    )
    try:
        open_offline(current)
        keyboard_activate(current, "#nextBtn")
        assert current.locator("#stage h2").inner_text() == "Maddenin Üç Hâli"
        assert errors == []
    finally:
        context.close()
