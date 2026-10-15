import pytest
from playwright.sync_api import Locator, Page, expect


DROPDOWN_URL = "https://www.runoob.com/try/try.php?filename=tryhtml_select2"


@pytest.fixture
def dropdown(page: Page) -> Locator:


    page.goto(DROPDOWN_URL, wait_until="domcontentloaded", timeout=30_000)


    page.locator('button[onclick="submitTryit()"]').click(timeout=15_000)


    result = page.frame_locator("#iframeResult")
    cars = result.locator('select[name="cars"]')
    expect(cars).to_be_visible(timeout=15_000)
    return cars


def test_dropdown_default_option(dropdown: Locator):
    expect(dropdown).to_have_value("volvo")


    options = dropdown.locator("option")
    expect(options).to_have_count(4)
    expect(options).to_have_text(["Volvo", "Saab", "Fiat", "Audi"])


    expect(dropdown.locator("option:checked")).to_have_count(1)
    expect(dropdown.locator("option:checked")).to_have_text("Volvo")


def test_dropdown_select_saab_by_value(dropdown: Locator):

    dropdown.select_option("saab")
    expect(dropdown).to_have_value("saab")
    expect(dropdown.locator("option:checked")).to_have_text("Saab")


def test_dropdown_select_audi_by_label(dropdown: Locator):

    dropdown.select_option(label="Audi")
    expect(dropdown).to_have_value("audi")
    expect(dropdown.locator("option:checked")).to_have_text("Audi")


def test_dropdown_switch_and_restore(dropdown: Locator):
    dropdown.select_option("fiat")
    expect(dropdown).to_have_value("fiat")
    expect(dropdown.locator("option:checked")).to_have_text("Fiat")
    expect(dropdown.locator("option:checked")).to_have_count(1)

    dropdown.select_option("volvo")
    expect(dropdown).to_have_value("volvo")
    expect(dropdown.locator("option:checked")).to_have_text("Volvo")
    expect(dropdown.locator("option:checked")).to_have_count(1)
