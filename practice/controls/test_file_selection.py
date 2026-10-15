from pathlib import Path

import pytest
from playwright.sync_api import Locator, Page, expect


FILE_SELECTION_URL = "https://www.runoob.com/try/try2.php?filename=bootstrap3-form-basic"


TEST_DATA_DIR = Path(__file__).resolve().parents[2] / "test_data"
SAMPLE_FILE = TEST_DATA_DIR / "sample.txt"
SPACE_FILE = TEST_DATA_DIR / "sample with space.txt"


@pytest.fixture
def file_input(page: Page) -> Locator:
    assert SAMPLE_FILE.is_file(), f"找不到普通样本：{SAMPLE_FILE}"
    assert SPACE_FILE.is_file(), f"找不到含空格文件名的样本：{SPACE_FILE}"

    page.goto(FILE_SELECTION_URL, wait_until="domcontentloaded", timeout=30_000)
    page.locator('button[onclick="submitTryit()"]').click(timeout=15_000)
    result = page.frame_locator("#iframeResult")
    upload = result.locator('input[type="file"]')
    expect(upload).to_be_visible(timeout=15_000)


    upload.set_input_files([])
    assert upload.evaluate("(element) => element.files.length") == 0
    return upload


def test_select_plain_text_file(file_input: Locator):

    file_input.set_input_files(SAMPLE_FILE)


    assert file_input.evaluate("(element) => element.files.length") == 1
    assert file_input.evaluate("(element) => element.files[0].name") == "sample.txt"


def test_select_filename_with_spaces(file_input: Locator):
    file_input.set_input_files(SPACE_FILE)

    assert file_input.evaluate("(element) => element.files.length") == 1
    assert file_input.evaluate("(element) => element.files[0].name") == "sample with space.txt"


def test_replace_selected_file(file_input: Locator):

    file_input.set_input_files(SAMPLE_FILE)
    assert file_input.evaluate("(element) => element.files.length") == 1
    assert file_input.evaluate("(element) => element.files[0].name") == "sample.txt"

    file_input.set_input_files(SPACE_FILE)
    assert file_input.evaluate("(element) => element.files.length") == 1
    assert file_input.evaluate("(element) => element.files[0].name") == "sample with space.txt"
