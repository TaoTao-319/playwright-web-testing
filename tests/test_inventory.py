from playwright.sync_api import expect

from test_data.products import BAG, BAG_PRICE, BIKE_LIGHT, BIKE_LIGHT_PRICE, PRODUCT_COUNT


def test_inventory_product_information(inventory_page):
    expect(inventory_page.items).to_have_count(PRODUCT_COUNT)
    expect(inventory_page.product_price(BAG)).to_have_text(f"${BAG_PRICE}")
    expect(inventory_page.product_price(BIKE_LIGHT)).to_have_text(f"${BIKE_LIGHT_PRICE}")


def test_sort_price_low_to_high(inventory_page):
    inventory_page.select_sort("lohi")
    expect(inventory_page.sort_dropdown).to_have_value("lohi")
    expect(inventory_page.items).to_have_count(PRODUCT_COUNT)
    prices = inventory_page.product_prices()
    assert prices == sorted(prices), f"价格未按升序排列：{prices}"


def test_sort_price_high_to_low(inventory_page):
    inventory_page.select_sort("hilo")
    expect(inventory_page.sort_dropdown).to_have_value("hilo")
    expect(inventory_page.items).to_have_count(PRODUCT_COUNT)
    prices = inventory_page.product_prices()
    assert prices == sorted(prices, reverse=True), f"价格未按降序排列：{prices}"


def test_sort_name_descending_and_restore(inventory_page):
    expect(inventory_page.items).to_have_count(PRODUCT_COUNT)
    inventory_page.select_sort("za")
    expect(inventory_page.sort_dropdown).to_have_value("za")
    names = inventory_page.product_names()
    assert names == sorted(names, reverse=True)
    inventory_page.select_sort("az")
    expect(inventory_page.sort_dropdown).to_have_value("az")
    names = inventory_page.product_names()
    assert names == sorted(names)
