from playwright.sync_api import Page


class CheckoutPage:

    def __init__(self, page: Page):
        self.page = page
        self.title = page.locator('[data-test="title"]')
        self.item_names = page.locator(".cart_item .inventory_item_name")
        self.subtotal = page.locator('[data-test="subtotal-label"]')
        self.error_message = page.locator('[data-test="error"]')
        self.complete_header = page.locator('[data-test="complete-header"]')
        self.cart_badge = page.locator('[data-test="shopping-cart-badge"]')

    def fill_information(self, first_name: str, last_name: str, postal_code: str):
        self.page.locator('[data-test="firstName"]').fill(first_name)
        self.page.locator('[data-test="lastName"]').fill(last_name)
        self.page.locator('[data-test="postalCode"]').fill(postal_code)
        self.page.locator('[data-test="continue"]').click()

    def cancel(self):
        self.page.locator('[data-test="cancel"]').click()

    def finish(self):
        self.page.locator('[data-test="finish"]').click()

    def back_to_products(self):
        self.page.locator('[data-test="back-to-products"]').click()
