import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:5000"

@pytest.fixture(scope="function")
def auth_page(page: Page, base_url: str):
    """
    Returns an authenticated page object.
    """
    page.goto(f"{base_url}/login")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "securepassword123")
    page.click('button[type="submit"]')
    expect(page).to_have_url(f"{base_url}/")
    return page

