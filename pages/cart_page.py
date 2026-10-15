from playwright.sync_api import Page


class CartPage:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.locator('[data-test="title"]')
        self.items = page.locator(".cart_item")
        self.cart_badge = page.locator('[data-test="shopping-cart-badge"]')

    def item(self, name: str):
        return self.items.filter(has=self.page.get_by_text(name, exact=True))

    def item_names(self):
        return self.items.locator(".inventory_item_name")

    def item_price(self, name: str):
        return self.item(name).locator(".inventory_item_price")

    def item_quantity(self, name: str):
        return self.item(name).locator(".cart_quantity")

    def remove_product(self, name: str):
        self.item(name).get_by_role("button", name="Remove", exact=True).click()

    def continue_shopping(self):
        self.page.locator('[data-test="continue-shopping"]').click()

    def checkout(self):
        self.page.locator('[data-test="checkout"]').click()
