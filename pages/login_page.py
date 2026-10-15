import warnings

from playwright.sync_api import Error, Page, TimeoutError as PlaywrightTimeoutError

from config import BASE_URL, NAVIGATION_TIMEOUT


class LoginPage:

    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator('[id="user-name"]')
        self.password_input = page.locator("#password")
        self.login_button = page.locator("#login-button")
        self.error_message = page.locator('[data-test="error"]')

    def open(self):


        for attempt in range(2):
            try:
                response = self.page.goto(BASE_URL, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT)
                if response is not None and not response.ok:
                    raise RuntimeError(f"Sauce Demo 首页返回 HTTP {response.status}")
                self.username_input.wait_for(state="visible", timeout=10_000)
                return
            except Error as error:
                transient = isinstance(error, PlaywrightTimeoutError) or any(
                    code in str(error) for code in ("net::ERR_CONNECTION_RESET", "net::ERR_TIMED_OUT", "net::ERR_CONNECTION_CLOSED")
                )
                if attempt == 1 or not transient:
                    raise
                warnings.warn("Sauce Demo 首页加载超时或连接中断，正在重新打开一次。", RuntimeWarning, stacklevel=2)

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
