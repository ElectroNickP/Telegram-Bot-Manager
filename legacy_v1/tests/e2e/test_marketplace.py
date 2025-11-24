from playwright.sync_api import Page, expect

def test_marketplace_list(auth_page: Page, base_url: str):
    """
    SCENARIO 3.1: Просмотр каталога
    """
    auth_page.goto(f"{base_url}/marketplace")
    
    # Проверяем заголовок
    expect(auth_page.locator("h1.brand-title")).to_contain_text("ELECTRONICK")
    
    # Проверяем наличие списка ботов (если они есть)
    # D!P$Y должен быть в списке
    expect(auth_page.locator(".bot-holo").filter(has_text="D!P$Y")).to_be_visible()

def test_marketplace_search(auth_page: Page, base_url: str):
    """
    SCENARIO 3.2: Поиск/Фильтрация
    """
    auth_page.goto(f"{base_url}/marketplace")
    
    # Поиск несуществующего бота
    auth_page.fill("#searchInput", "NonExistentBot")
    # Ждем обновления списка (можно проверить отсутствие карточек или текст "No bots found")
    expect(auth_page.locator("text=No bots found")).to_be_visible(timeout=5000)
    expect(auth_page.locator(".bot-holo")).not_to_be_visible()
    
    # Поиск существующего бота
    auth_page.fill("#searchInput", "D!P$Y")
    expect(auth_page.locator(".bot-holo").filter(has_text="D!P$Y")).to_be_visible(timeout=5000)

