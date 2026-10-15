import pytest
from playwright.sync_api import expect

from config import BASE_URL
from pages.inventory_page import InventoryPage
from test_data.accounts import (
    EMPTY_PASSWORD_ERROR, EMPTY_USERNAME_ERROR, LOCKED_USER, LOCKED_USER_ERROR,
    PASSWORD, STANDARD_USER, WRONG_PASSWORD, WRONG_PASSWORD_ERROR,
)


def test_login_success(login_page, page):
    login_page.open()
    login_page.login(STANDARD_USER, PASSWORD)
    expect(page).to_have_url(BASE_URL + "inventory.html")
    expect(InventoryPage(page).title).to_have_text("Products")
    expect(InventoryPage(page).title).to_be_visible()
    expect(InventoryPage(page).items).to_have_count(6)


@pytest.mark.parametrize("username,password,error", [
    pytest.param(STANDARD_USER, WRONG_PASSWORD, WRONG_PASSWORD_ERROR, id="wrong-password"),
    pytest.param(LOCKED_USER, PASSWORD, LOCKED_USER_ERROR, id="locked-account"),
    pytest.param("", PASSWORD, EMPTY_USERNAME_ERROR, id="empty-username"),
    pytest.param(STANDARD_USER, "", EMPTY_PASSWORD_ERROR, id="empty-password"),
])
def test_login_rejected(login_page, page, username, password, error):
    login_page.open()
    login_page.login(username, password)
    expect(login_page.error_message).to_be_visible()
    expect(login_page.error_message).to_have_text(error)
    expect(page).to_have_url(BASE_URL)
    expect(login_page.login_button).to_be_visible()


def test_login_retry_after_wrong_password(login_page, page):
    login_page.open()
    login_page.login(STANDARD_USER, WRONG_PASSWORD)
    expect(login_page.error_message).to_be_visible()
    expect(login_page.error_message).to_have_text(WRONG_PASSWORD_ERROR)
    expect(page).to_have_url(BASE_URL)


    login_page.login(STANDARD_USER, PASSWORD)
    expect(page).to_have_url(BASE_URL + "inventory.html")
    expect(InventoryPage(page).title).to_have_text("Products")
    expect(InventoryPage(page).title).to_be_visible()
    expect(InventoryPage(page).items).to_have_count(6)
    expect(login_page.error_message).to_be_hidden()
