from playwright.sync_api import Page, expect

def test_login_success(page: Page, base_url: str):
    """
    SCENARIO 1.1: Успешный вход в систему
    """
    page.goto(f"{base_url}/login")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "securepassword123")
    page.click('button[type="submit"]')
    
    # Ожидаем редирект на главную
    expect(page).to_have_url(f"{base_url}/")
    
    # Проверяем наличие элементов дашборда
    expect(page.locator("text=Dashboard")).to_be_visible()
    expect(page.locator(".sidebar-header")).to_contain_text("ELECTRONICK")

def test_login_failure(page: Page, base_url: str):
    """
    SCENARIO 1.2: Неудачный вход (Неверный пароль)
    """
    page.goto(f"{base_url}/login")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "wrongpassword")
    page.click('button[type="submit"]')
    
    # Ожидаем, что остались на странице логина
    expect(page).to_have_url(f"{base_url}/login")
    
    # Проверяем сообщение об ошибке
    # Текст может быть "Неверные учетные данные" или что-то подобное, проверим наличие .alert
    expect(page.locator(".alert")).to_be_visible()
    expect(page.locator(".alert")).to_contain_text("Неверные учетные данные")

def test_logout(auth_page: Page, base_url: str):
    """
    SCENARIO 1.3: Выход из системы
    """
    # Обработка диалогового окна confirm
    auth_page.on("dialog", lambda dialog: dialog.accept())
    
    # Используем фикстуру auth_page, которая уже залогинена
    auth_page.click("text=Logout")
    
    # Ожидаем редирект на логин
    expect(auth_page).to_have_url(f"{base_url}/login")

