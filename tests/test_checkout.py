import pytest
from playwright.sync_api import expect

from config import BASE_URL
from test_data.checkout import FIRST_NAME, LAST_NAME, POSTAL_CODE
from test_data.products import BAG, BIKE_LIGHT, TWO_ITEMS_SUBTOTAL


def test_checkout_subtotal(inventory_page, cart_page, checkout_page):
    inventory_page.add_product(BAG)
    inventory_page.add_product(BIKE_LIGHT)
    inventory_page.open_cart()
    cart_page.checkout()
    checkout_page.fill_information(FIRST_NAME, LAST_NAME, POSTAL_CODE)
    expect(checkout_page.title).to_have_text("Checkout: Overview")
    expect(checkout_page.item_names).to_have_text([BAG, BIKE_LIGHT])
    expect(checkout_page.subtotal).to_have_text(f"Item total: ${TWO_ITEMS_SUBTOTAL}")
    checkout_page.cancel()
    expect(inventory_page.title).to_have_text("Products")


@pytest.mark.parametrize("first_name,last_name,postal_code,error", [
    pytest.param("", LAST_NAME, POSTAL_CODE, "Error: First Name is required", id="missing-first-name"),
    pytest.param(FIRST_NAME, "", POSTAL_CODE, "Error: Last Name is required", id="missing-last-name"),
    pytest.param(FIRST_NAME, LAST_NAME, "", "Error: Postal Code is required", id="missing-postal-code"),
])
def test_checkout_required_fields(inventory_page, cart_page, checkout_page, page,
                                  first_name, last_name, postal_code, error):
    inventory_page.add_product(BAG)
    inventory_page.open_cart()
    cart_page.checkout()
    checkout_page.fill_information(first_name, last_name, postal_code)
    expect(checkout_page.error_message).to_have_text(error)
    expect(checkout_page.title).to_have_text("Checkout: Your Information")
    expect(page).to_have_url(BASE_URL + "checkout-step-one.html")


def test_complete_purchase(inventory_page, cart_page, checkout_page, page):
    inventory_page.add_product(BAG)
    inventory_page.add_product(BIKE_LIGHT)
    inventory_page.open_cart()
    cart_page.checkout()
    checkout_page.fill_information(FIRST_NAME, LAST_NAME, POSTAL_CODE)
    expect(checkout_page.title).to_have_text("Checkout: Overview")
    expect(checkout_page.item_names).to_have_text([BAG, BIKE_LIGHT])
    expect(checkout_page.subtotal).to_have_text(f"Item total: ${TWO_ITEMS_SUBTOTAL}")
    checkout_page.finish()
    expect(page).to_have_url(BASE_URL + "checkout-complete.html")
    expect(checkout_page.title).to_have_text("Checkout: Complete!")
    expect(checkout_page.complete_header).to_have_text("Thank you for your order!")
    expect(checkout_page.cart_badge).to_have_count(0)
    checkout_page.back_to_products()
    expect(inventory_page.title).to_have_text("Products")
    inventory_page.open_cart()
    expect(cart_page.items).to_have_count(0)
