from playwright.sync_api import expect

from config import BASE_URL
from test_data.products import BAG, BAG_PRICE, BIKE_LIGHT, BIKE_LIGHT_PRICE


def test_add_one_product(inventory_page, cart_page):
    inventory_page.add_product(BAG)
    expect(inventory_page.cart_badge).to_have_text("1")
    expect(inventory_page.remove_button(BAG)).to_be_visible()
    inventory_page.open_cart()
    expect(cart_page.title).to_have_text("Your Cart")
    expect(cart_page.items).to_have_count(1)
    expect(cart_page.item_names()).to_have_text([BAG])
    expect(cart_page.item_price(BAG)).to_have_text(f"${BAG_PRICE}")
    expect(cart_page.item_quantity(BAG)).to_have_text("1")


def test_add_two_products(inventory_page, cart_page):
    inventory_page.add_product(BAG)
    inventory_page.add_product(BIKE_LIGHT)
    expect(inventory_page.cart_badge).to_have_text("2")
    inventory_page.open_cart()
    expect(cart_page.items).to_have_count(2)
    expect(cart_page.item_names()).to_have_text([BAG, BIKE_LIGHT])
    expect(cart_page.item_price(BAG)).to_have_text(f"${BAG_PRICE}")
    expect(cart_page.item_price(BIKE_LIGHT)).to_have_text(f"${BIKE_LIGHT_PRICE}")


def test_cart_keeps_products_after_returning_to_inventory(inventory_page, cart_page):

    inventory_page.add_product(BAG)
    inventory_page.add_product(BIKE_LIGHT)
    inventory_page.open_cart()
    expect(cart_page.title).to_have_text("Your Cart")
    expect(cart_page.items).to_have_count(2)
    expect(cart_page.item_names()).to_have_text([BAG, BIKE_LIGHT])

    cart_page.continue_shopping()
    expect(inventory_page.title).to_have_text("Products")
    expect(inventory_page.cart_badge).to_have_text("2")

    inventory_page.open_cart()
    expect(cart_page.title).to_have_text("Your Cart")
    expect(cart_page.items).to_have_count(2)
    expect(cart_page.item_names()).to_have_text([BAG, BIKE_LIGHT])
    expect(cart_page.item_quantity(BAG)).to_have_text("1")
    expect(cart_page.item_quantity(BIKE_LIGHT)).to_have_text("1")


def test_remove_one_keeps_other(inventory_page, cart_page):
    inventory_page.add_product(BAG)
    inventory_page.add_product(BIKE_LIGHT)
    inventory_page.open_cart()
    cart_page.remove_product(BAG)
    expect(cart_page.item(BAG)).to_have_count(0)
    expect(cart_page.item_names()).to_have_text([BIKE_LIGHT])
    expect(cart_page.cart_badge).to_have_text("1")
    cart_page.continue_shopping()
    expect(inventory_page.title).to_have_text("Products")
    expect(inventory_page.add_button(BAG)).to_be_visible()


def test_readd_product_after_removing(inventory_page, cart_page):

    inventory_page.add_product(BAG)
    inventory_page.add_product(BIKE_LIGHT)
    inventory_page.open_cart()
    expect(cart_page.items).to_have_count(2)
    expect(cart_page.item_names()).to_have_text([BAG, BIKE_LIGHT])

    cart_page.remove_product(BAG)
    expect(cart_page.item(BAG)).to_have_count(0)
    expect(cart_page.item_names()).to_have_text([BIKE_LIGHT])
    expect(cart_page.cart_badge).to_have_text("1")

    cart_page.continue_shopping()
    expect(inventory_page.title).to_have_text("Products")
    expect(inventory_page.add_button(BAG)).to_be_visible()
    inventory_page.add_product(BAG)
    expect(inventory_page.cart_badge).to_have_text("2")

    inventory_page.open_cart()
    expect(cart_page.title).to_have_text("Your Cart")
    expect(cart_page.items).to_have_count(2)
    expect(cart_page.item(BAG)).to_have_count(1)
    expect(cart_page.item(BIKE_LIGHT)).to_have_count(1)
    expect(cart_page.item_quantity(BAG)).to_have_text("1")
    expect(cart_page.item_quantity(BIKE_LIGHT)).to_have_text("1")


def test_remove_all_products(inventory_page, cart_page):
    inventory_page.add_product(BAG)
    inventory_page.open_cart()
    cart_page.remove_product(BAG)

    expect(cart_page.items).to_have_count(0)
    expect(cart_page.cart_badge).to_have_count(0)
    expect(cart_page.title).to_have_text("Your Cart")


def test_logout_returns_to_login(inventory_page, login_page, page):

    inventory_page.logout()
    expect(page).to_have_url(BASE_URL)
    expect(login_page.username_input).to_be_visible()
    expect(login_page.login_button).to_be_visible()
