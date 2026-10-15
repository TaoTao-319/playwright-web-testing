from decimal import Decimal

from playwright.sync_api import Page


class InventoryPage:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.locator('[data-test="title"]')
        self.items = page.locator(".inventory_item")
        self.sort_dropdown = page.locator('[data-test="product-sort-container"]')
        self.cart_link = page.locator('[data-test="shopping-cart-link"]')
        self.cart_badge = page.locator('[data-test="shopping-cart-badge"]')

    def product(self, name: str):

        return self.items.filter(has=self.page.get_by_text(name, exact=True))

    def add_product(self, name: str):
        self.add_button(name).click()

    def add_button(self, name: str):
        return self.product(name).get_by_role("button", name="Add to cart", exact=True)

    def remove_button(self, name: str):
        return self.product(name).get_by_role("button", name="Remove", exact=True)

    def product_price(self, name: str):
        return self.product(name).locator(".inventory_item_price")

    def open_cart(self):
        self.cart_link.click()

    def select_sort(self, value: str):

        self.sort_dropdown.select_option(value)

    def product_names(self):
        return self.items.locator(".inventory_item_name").all_text_contents()

    def product_prices(self):
        return [Decimal(text.replace("$", "")) for text in self.items.locator(".inventory_item_price").all_text_contents()]

    def logout(self):
        self.page.get_by_role("button", name="Open Menu", exact=True).click()
        self.page.locator('[data-test="logout-sidebar-link"]').click()
