import pytest
from playwright.sync_api import FrameLocator, Page, expect


VISIBILITY_URL = "https://www.runoob.com/try/try.php?filename=tryjquery_hide_show"
PARAGRAPH_TEXT = "如果你点击“隐藏” 按钮，我将会消失。"


@pytest.fixture
def visibility_page(page: Page) -> FrameLocator:
    page.goto(VISIBILITY_URL, wait_until="domcontentloaded", timeout=30_000)
    page.locator('button[onclick="submitTryit()"]').click(timeout=15_000)
    result = page.frame_locator("#iframeResult")

    paragraph = result.locator("p")
    expect(paragraph).to_be_visible(timeout=15_000)
    expect(paragraph).to_have_text(PARAGRAPH_TEXT)
    return result


def test_hide_visible_paragraph(visibility_page: FrameLocator):
    paragraph = visibility_page.locator("p")
    visibility_page.locator("#hide").click()


    expect(paragraph).to_be_hidden(timeout=10_000)

    expect(paragraph).to_have_count(1)
    expect(paragraph).to_have_text(PARAGRAPH_TEXT)
    expect(visibility_page.locator("#hide")).to_be_visible()
    expect(visibility_page.locator("#show")).to_be_visible()


def test_show_hidden_paragraph(visibility_page: FrameLocator):
    paragraph = visibility_page.locator("p")


    visibility_page.locator("#hide").click()
    expect(paragraph).to_be_hidden(timeout=10_000)

    visibility_page.locator("#show").click()
    expect(paragraph).to_be_visible(timeout=10_000)
    expect(paragraph).to_have_text(PARAGRAPH_TEXT)
