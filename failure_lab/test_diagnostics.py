from playwright.sync_api import expect


def test_product_title_diagnostics(inventory_page, request):
    expected = "Wrong Products Title" if request.config.getoption("--failure-demo") else "Products"
    expect(inventory_page.title).to_have_text(expected)
