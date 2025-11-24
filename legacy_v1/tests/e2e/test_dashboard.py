from playwright.sync_api import Page, expect

def test_bot_status(auth_page: Page):
    """
    SCENARIO 2.1: Отображение статуса бота
    """
    # Ищем карточку бота D!P$Y
    card = auth_page.locator(".bot-card").filter(has_text="D!P$Y")
    expect(card).to_be_visible()
    
    # Проверяем статус (Running или Stopped)
    # Мы не знаем начальный статус, но проверим наличие бейджа
    expect(card.locator(".status-badge")).to_be_visible()

def test_bot_lifecycle(auth_page: Page):
    """
    SCENARIO 2.2 & 2.3: Остановка и Запуск бота
    """
    card = auth_page.locator(".bot-card").filter(has_text="D!P$Y")
    start_btn = card.locator(".start-btn")
    stop_btn = card.locator(".stop-btn")
    status_badge = card.locator(".status-badge")

    # Проверяем текущий статус
    if status_badge.get_attribute("class") and "running" in status_badge.get_attribute("class"):
        # Если запущен - останавливаем
        stop_btn.click()
        expect(status_badge).to_have_text("Stopped", timeout=10000)
        expect(start_btn).to_be_enabled()
        expect(stop_btn).to_be_disabled()
        
        # Запускаем обратно
        start_btn.click()
        expect(status_badge).to_have_text("Running", timeout=10000)
        expect(start_btn).to_be_disabled()
        expect(stop_btn).to_be_enabled()
    else:
        # Если остановлен - запускаем
        start_btn.click()
        expect(status_badge).to_have_text("Running", timeout=10000)
        expect(start_btn).to_be_disabled()
        expect(stop_btn).to_be_enabled()
        
        # Останавливаем обратно
        stop_btn.click()
        expect(status_badge).to_have_text("Stopped", timeout=10000)
        expect(start_btn).to_be_enabled()
        expect(stop_btn).to_be_disabled()

