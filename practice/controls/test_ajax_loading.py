import pytest
from playwright.sync_api import FrameLocator, Page, expect


AJAX_URL = "https://www.runoob.com/try/try.php?filename=tryjquery_ajax_load"
INITIAL_HEADING = "使用 jQuery AJAX 修改文本内容"
LOADED_HEADING = "jQuery AJAX 是个非常棒的功能！"
LOADED_PARAGRAPH = "这是段落的一些文本。"


@pytest.fixture
def ajax_page(page: Page) -> FrameLocator:
    page.goto(AJAX_URL, wait_until="domcontentloaded", timeout=30_000)
    page.locator('button[onclick="submitTryit()"]').click(timeout=15_000)
    result = page.frame_locator("#iframeResult")
    expect(result.locator("#div1")).to_be_visible(timeout=15_000)
    expect(result.locator("#div1 h2")).to_have_text(INITIAL_HEADING)
    return result


def test_ajax_initial_state(ajax_page: FrameLocator):
    content = ajax_page.locator("#div1")
    expect(content.locator("h2")).to_be_visible()
    expect(content.locator("h2")).to_have_text(INITIAL_HEADING)
    expect(content.locator("#p1")).to_have_count(0)
    expect(content).not_to_contain_text(LOADED_HEADING)
    expect(ajax_page.get_by_role("button", name="获取外部内容", exact=True)).to_be_visible()


def test_ajax_load_new_content(ajax_page: FrameLocator, page: Page):
    content = ajax_page.locator("#div1")


    with page.expect_response("**/try/ajax/demo_test.txt", timeout=10_000) as response_info:
        ajax_page.get_by_role("button", name="获取外部内容", exact=True).click()
    response = response_info.value
    assert response.ok, f"AJAX 请求失败：HTTP {response.status}，{response.url}"


    expect(content.locator("h2")).to_have_text(LOADED_HEADING, timeout=10_000)
    expect(content.locator("h2")).to_be_visible(timeout=10_000)
    expect(content.locator("#p1")).to_be_visible(timeout=10_000)
    expect(content.locator("#p1")).to_have_text(LOADED_PARAGRAPH, timeout=10_000)
    expect(content).not_to_contain_text(INITIAL_HEADING)
