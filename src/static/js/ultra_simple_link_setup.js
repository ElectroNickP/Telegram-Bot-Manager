/**
 * УЛЬТРА-ПРОСТОЙ ИНТЕРФЕЙС НАСТРОЙКИ КНОПОК
 * Только самое необходимое - два поля и кнопка
 */

class UltraSimpleLinkSetup {
    constructor() {
        this.botId = null;
        this.rules = [];
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.bindEvents();
            });
        } else {
            this.bindEvents();
        }
    }

    bindEvents() {
        // Добавить правило
        const addBtn = document.getElementById('addSimpleRuleBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                this.addRule();
            });
        }

        // Удалить правило (делегирование событий)
        document.addEventListener('click', (e) => {
            if (e.target && e.target.classList.contains('rule-remove')) {
                this.removeRule(e);
            }
        });

        // Очистить все правила
        const clearAllBtn = document.getElementById('clearAllRulesBtn');
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', () => {
                this.clearAllRules();
            });
        }

        // Быстрый тест
        const testBtn = document.getElementById('quickTestBtn');
        if (testBtn) {
            testBtn.addEventListener('click', () => {
                this.quickTest();
            });
        }

        // Сохранить
        const saveBtn = document.getElementById('saveUltraSimpleSettings');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveSettings();
            });
        }

        // При открытии модала
        const modal = document.getElementById('ultraSimpleLinkSetupModal');
        if (modal) {
            modal.addEventListener('show.bs.modal', () => {
                if (this.botId) {
                    this.loadExisting();
                }
            });
        }
    }

    /**
     * Открыть для бота
     */
    openForBot(botId) {
        this.botId = botId;
        this.showModal();
        // Загружаем существующие правила сразу после открытия
        this.loadExisting();
    }

    /**
     * Показать модал универсально
     */
    showModal() {
        const modalElement = document.getElementById('ultraSimpleLinkSetupModal');
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        } else if (typeof $ !== 'undefined' && $.fn.modal) {
            $('#ultraSimpleLinkSetupModal').modal('show');
        } else {
            modalElement.classList.add('show');
            modalElement.style.display = 'block';
            document.body.classList.add('modal-open');
        }
    }

    /**
     * Добавить простое правило
     */
    addRule() {
        const searchText = $('#searchInLink').val().trim();
        const buttonText = $('#buttonTextInput').val().trim();

        if (!searchText) {
            this.showAlert('❌ Введи текст для поиска в ссылке', 'danger');
            return;
        }

        if (!buttonText) {
            this.showAlert('❌ Введи текст кнопки', 'danger');
            return;
        }

        // Создать простое правило с правильным форматом
        const rule = {
            id: 'rule_' + Date.now(),
            name: `Правило для ${searchText}`,
            match_type: 'url_contains', 
            match_value: searchText,
            button_text: buttonText,
            button_emoji: this.extractEmoji(buttonText),
            priority: 100,
            enabled: true,
            remove_original_link: true,
            case_sensitive: false,
            add_preview_text: false,
            preview_text: ''
        };

        this.rules.push(rule);
        this.updateRulesList();
        
        // Очистить поля
        document.getElementById('searchInLink').value = '';
        document.getElementById('buttonTextInput').value = '';
        
        this.showAlert(`✅ Добавлено правило: ${searchText} → ${buttonText}`, 'success');
    }

    /**
     * Извлечь эмодзи из текста
     */
    extractEmoji(text) {
        const emojiRegex = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu;
        const matches = text.match(emojiRegex);
        return matches ? matches[0] : '🔗';
    }

    /**
     * Обновить список правил
     */
    updateRulesList() {
        const container = document.getElementById('activeRulesContainer');
        const card = document.getElementById('activeRulesCard');
        
        if (this.rules.length === 0) {
            card.style.display = 'none';
            return;
        }

        card.style.display = 'block';
        container.innerHTML = '';

        this.rules.forEach((rule, index) => {
            const ruleElement = document.createElement('div');
            ruleElement.className = 'rule-item';
            ruleElement.innerHTML = `
                <div>
                    <strong>${rule.match_value}</strong> → ${rule.button_text}
                </div>
                <button type="button" class="rule-remove" data-index="${index}" title="Удалить">
                    ×
                </button>
            `;
            container.appendChild(ruleElement);
        });
    }

    /**
     * Удалить правило
     */
    removeRule(event) {
        const index = parseInt(event.target.getAttribute('data-index'));
        this.rules.splice(index, 1);
        this.updateRulesList();
        this.showAlert('✅ Правило удалено', 'success');
    }

    /**
     * Очистить все правила
     */
    clearAllRules() {
        if (this.rules.length === 0) {
            this.showAlert('❌ Нет правил для удаления', 'warning');
            return;
        }

        if (confirm('Удалить все правила? Это действие нельзя отменить.')) {
            this.rules = [];
            this.updateRulesList();
            this.showAlert('✅ Все правила удалены', 'success');
        }
    }

    /**
     * Быстрый тест
     */
    async quickTest() {
        const text = document.getElementById('testTextArea').value.trim();
        
        if (!text) {
            this.showAlert('❌ Введи текст для проверки', 'danger');
            return;
        }

        if (this.rules.length === 0) {
            this.showAlert('❌ Сначала добавь хотя бы одно правило', 'danger');
            return;
        }

        try {
            const testBtn = document.getElementById('quickTestBtn');
            testBtn.disabled = true;
            testBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Проверяю...';

            const config = {
                enabled: true,
                transformation_rules: this.rules,
                max_buttons_per_message: 5,
                button_layout: 'vertical',
                process_ai_responses: true,
                preserve_message_formatting: true
            };

            const response = await fetch(`/api/v2/link-transformation/${this.botId}/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    config: config
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showTestResults(result.data, text);
            } else {
                this.showAlert(`❌ Ошибка: ${result.message}`, 'danger');
            }

        } catch (error) {
            console.error('Test error:', error);
            this.showAlert('❌ Ошибка при тестировании', 'danger');
        } finally {
            const testBtn = document.getElementById('quickTestBtn');
            testBtn.disabled = false;
            testBtn.innerHTML = '<i class="fas fa-magic"></i> Показать как будет выглядеть';
        }
    }

    /**
     * Показать результаты теста
     */
    showTestResults(data, originalText) {
        const container = document.getElementById('testResults');
        
        let html = `
            <div class="border rounded p-3 bg-light">
                <h6 class="text-success mb-3"><i class="fas fa-check-circle"></i> Результат:</h6>
        `;

        if (data.buttons && data.buttons.length > 0) {
            html += `
                <div class="mb-3">
                    <strong>Текст сообщения:</strong><br>
                    <div class="bg-white p-2 rounded border small">${data.processed_text || originalText}</div>
                </div>
                <div class="mb-3">
                    <strong>Кнопки:</strong><br>
            `;
            
            data.buttons.forEach(button => {
                html += `<button class="btn btn-outline-primary btn-sm me-2 mb-2" disabled>${button.text}</button>`;
            });
            
            html += `</div>
                <div class="alert alert-success small mb-0">
                    <i class="fas fa-thumbs-up"></i> Преобразовано ссылок: ${data.transformations_count}
                </div>
            `;
        } else {
            html += `
                <div class="alert alert-warning small mb-0">
                    <i class="fas fa-info-circle"></i>
                    В тексте не найдено подходящих ссылок
                </div>
            `;
        }

        html += '</div>';
        
        container.innerHTML = html;
        container.style.display = 'block';
    }

    /**
     * Сохранить настройки
     */
    async saveSettings() {
        if (this.rules.length === 0) {
            this.showAlert('❌ Добавь хотя бы одно правило перед сохранением', 'danger');
            return;
        }

        try {
            const saveBtn = document.getElementById('saveUltraSimpleSettings');
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохраняю...';

            const config = {
                enabled: true,
                transformation_rules: this.rules,
                max_buttons_per_message: 5,
                button_layout: 'vertical',
                process_ai_responses: true,
                process_user_messages: false,
                preserve_message_formatting: true
            };

            // Сохранить конфигурацию
            const configResponse = await fetch(`/api/v2/link-transformation/${this.botId}/config`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const configResult = await configResponse.json();

            if (!configResult.success) {
                throw new Error(configResult.message);
            }

            // Сначала очищаем все старые правила, потом сохраняем новые
            try {
                // Очистка старых правил
                await fetch(`/api/v2/link-transformation/${this.botId}/rules`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
            } catch (error) {
                console.warn('Failed to clear old rules:', error);
            }

            // Сохранить новые правила
            for (const rule of this.rules) {
                const ruleResponse = await fetch(`/api/v2/link-transformation/${this.botId}/rules`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(rule)
                });

                const ruleResult = await ruleResponse.json();
                if (!ruleResult.success) {
                    console.warn(`Failed to save rule:`, ruleResult.message);
                }
            }

            this.showAlert('✅ Настройки сохранены! Умные кнопки работают', 'success');
            
            // Закрыть модал
            setTimeout(() => {
                this.hideModal();
            }, 1500);

        } catch (error) {
            console.error('Save error:', error);
            this.showAlert(`❌ Ошибка: ${error.message}`, 'danger');
        } finally {
            const saveBtn = document.getElementById('saveUltraSimpleSettings');
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Сохранить';
        }
    }

    /**
     * Скрыть модал
     */
    hideModal() {
        const modalElement = document.getElementById('ultraSimpleLinkSetupModal');
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();
        } else if (typeof $ !== 'undefined' && $.fn.modal) {
            $('#ultraSimpleLinkSetupModal').modal('hide');
        } else {
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    }

    /**
     * Загрузить существующие правила
     */
    async loadExisting() {
        try {
            const response = await fetch(`/api/v2/link-transformation/${this.botId}/config`);
            const result = await response.json();

            if (result.success && result.data && result.data.transformation_rules) {
                // Удаляем дубликаты по ID
                const uniqueRules = [];
                const seenIds = new Set();
                
                for (const rule of result.data.transformation_rules) {
                    if (!seenIds.has(rule.id)) {
                        seenIds.add(rule.id);
                        uniqueRules.push(rule);
                    }
                }
                
                this.rules = uniqueRules;
                this.updateRulesList();
                
                if (uniqueRules.length > 0) {
                    console.log(`Загружено ${uniqueRules.length} правил (удалено ${result.data.transformation_rules.length - uniqueRules.length} дубликатов)`);
                }
            }
        } catch (error) {
            console.error('Load error:', error);
        }
    }

    /**
     * Показать уведомление
     */
    showAlert(message, type = 'info') {
        const alertId = 'ultra-alert-' + Date.now();
        
        // Создаем простое уведомление без Bootstrap алертов
        const alertElement = document.createElement('div');
        alertElement.id = alertId;
        alertElement.className = `alert alert-${type} position-fixed`;
        alertElement.style.cssText = `
            top: 20px; 
            right: 20px; 
            z-index: 9999; 
            max-width: 350px;
            padding: 12px 16px;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: slideIn 0.3s ease-out;
        `;
        
        // Определяем цвета для типов
        const colors = {
            success: { bg: '#d4edda', border: '#c3e6cb', color: '#155724' },
            danger: { bg: '#f8d7da', border: '#f5c6cb', color: '#721c24' },
            warning: { bg: '#fff3cd', border: '#ffeeba', color: '#856404' },
            info: { bg: '#d1ecf1', border: '#bee5eb', color: '#0c5460' }
        };
        
        const color = colors[type] || colors.info;
        alertElement.style.backgroundColor = color.bg;
        alertElement.style.borderColor = color.border;
        alertElement.style.color = color.color;
        alertElement.style.border = `1px solid ${color.border}`;
        
        alertElement.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>${message}</span>
                <button type="button" style="background: none; border: none; font-size: 18px; cursor: pointer; color: ${color.color};" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        document.body.appendChild(alertElement);

        // Автоудаление через 4 секунды
        setTimeout(() => {
            const el = document.getElementById(alertId);
            if (el) {
                el.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => el.remove(), 300);
            }
        }, 4000);
    }
}

// Глобальная инициализация
const ultraSimpleLinkSetup = new UltraSimpleLinkSetup();

// Глобальная функция для открытия
window.openUltraSimpleLinkSetup = function(botId) {
    ultraSimpleLinkSetup.openForBot(botId);
};
