import pytest
from playwright.sync_api import Locator, Page, expect


CHECKBOXES_URL = "https://www.runoob.com/try/try.php?filename=tryhtml_checkbox"


@pytest.fixture
def checkboxes(page: Page) -> tuple[Locator, Locator]:
    page.goto(CHECKBOXES_URL, wait_until="domcontentloaded", timeout=30_000)


    page.locator('button[onclick="submitTryit()"]').click(timeout=15_000)
    result = page.frame_locator("#iframeResult")


    bike = result.locator('input[type="checkbox"][value="Bike"]')
    car = result.locator('input[type="checkbox"][value="Car"]')
    expect(bike).to_be_visible(timeout=15_000)
    expect(car).to_be_visible(timeout=15_000)


    bike.uncheck()
    car.uncheck()
    expect(bike).not_to_be_checked()
    expect(car).not_to_be_checked()


    return bike, car


def test_checkbox_check_bike(checkboxes: tuple[Locator, Locator]):
    bike, car = checkboxes


    bike.check()
    expect(bike).to_be_checked()
    expect(car).not_to_be_checked()


def test_checkbox_uncheck_bike(checkboxes: tuple[Locator, Locator]):
    bike, car = checkboxes


    bike.check()
    expect(bike).to_be_checked()

    bike.uncheck()
    expect(bike).not_to_be_checked()
    expect(car).not_to_be_checked()


def test_checkbox_check_both(checkboxes: tuple[Locator, Locator]):
    bike, car = checkboxes

    bike.check()
    expect(bike).to_be_checked()
    expect(car).not_to_be_checked()

    car.check()
    expect(bike).to_be_checked()
    expect(car).to_be_checked()


def test_checkbox_uncheck_car_keeps_bike(checkboxes: tuple[Locator, Locator]):
    bike, car = checkboxes

    bike.check()
    car.check()
    expect(bike).to_be_checked()
    expect(car).to_be_checked()

    car.uncheck()
    expect(car).not_to_be_checked()
    expect(bike).to_be_checked()
