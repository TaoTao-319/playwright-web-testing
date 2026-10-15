import base64
import hashlib
import json
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from test_data.accounts import PASSWORD, STANDARD_USER


SCRIPT_CACHE_DIR = Path(__file__).parent / "artifacts" / "sauce-script-cache"


def pytest_addoption(parser):
    parser.addoption("--failure-demo", action="store_true", default=False,
                     help="仅用于 failure_lab：故意使用错误预期，验证截图和追踪文件。")


def _load_cached_script(url):
    cache_file = SCRIPT_CACHE_DIR / f"{hashlib.sha256(url.encode()).hexdigest()}.json"
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        body = base64.b64decode(data["body"], validate=True)
        if (data["url"] != url or data["status"] != 200
                or not isinstance(data["headers"], dict)
                or hashlib.sha256(body).hexdigest() != data["sha256"]):
            return None
        return {"status": data["status"], "headers": data["headers"], "body": body}
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _save_cached_script(url, response):
    SCRIPT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = SCRIPT_CACHE_DIR / f"{hashlib.sha256(url.encode()).hexdigest()}.json"
    data = {"url": url, "status": response["status"], "headers": response["headers"],
            "body": base64.b64encode(response["body"]).decode("ascii"),
            "sha256": hashlib.sha256(response["body"]).hexdigest()}
    temporary_file = cache_file.with_suffix(".tmp")
    temporary_file.write_text(json.dumps(data), encoding="utf-8")
    temporary_file.replace(cache_file)


@pytest.fixture(scope="session")
def sauce_script_cache():

    return {}


@pytest.fixture(autouse=True)
def reuse_sauce_scripts(request, sauce_script_cache):

    if request.node.path.is_relative_to(Path(__file__).parent / "checks"):
        yield
        return
    context = request.getfixturevalue("context")
    pattern = re.compile(r"^https://www\.saucedemo\.com/assets/[^/?]+\.js(?:\?.*)?$")

    def handle_script(route):
        url = route.request.url
        if url not in sauce_script_cache:
            cached = _load_cached_script(url)
            if cached is not None:
                sauce_script_cache[url] = cached
        if url not in sauce_script_cache:
            response = route.fetch(timeout=45_000, max_retries=2)
            if not response.ok:
                route.fulfill(response=response)
                response.dispose()
                return

            headers = {key: value for key, value in response.headers.items()
                       if key.lower() not in {"content-encoding", "content-length", "transfer-encoding"}}
            sauce_script_cache[url] = {"status": response.status, "headers": headers, "body": response.body()}
            response.dispose()
            if sauce_script_cache[url]["status"] == 200:
                _save_cached_script(url, sauce_script_cache[url])
        route.fulfill(**sauce_script_cache[url])

    context.route(pattern, handle_script)
    yield
    context.unroute(pattern, handle_script)


@pytest.fixture
def login_page(page: Page):
    page.set_default_timeout(10_000)
    return LoginPage(page)


@pytest.fixture
def inventory_page(page: Page, login_page: LoginPage):

    login_page.open()
    login_page.login(STANDARD_USER, PASSWORD)
    inventory = InventoryPage(page)
    expect(inventory.title).to_have_text("Products")
    return inventory


@pytest.fixture
def cart_page(page: Page):
    return CartPage(page)


@pytest.fixture
def checkout_page(page: Page):
    return CheckoutPage(page)
