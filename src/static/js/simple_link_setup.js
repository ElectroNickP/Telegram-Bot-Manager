/**
 * ПРОСТОЙ И УДОБНЫЙ ИНТЕРФЕЙС НАСТРОЙКИ УМНЫХ КНОПОК
 * Максимально упрощенный UX для обычных пользователей
 */

class SimpleLinkSetupManager {
    constructor() {
        this.botId = null;
        this.activeRules = [];
        this.isEnabled = false;
        
        this.init();
    }

    init() {
        // Привязка событий при загрузке DOM
        $(document).ready(() => {
            this.bindEvents();
        });
    }

    bindEvents() {
        // Клики по быстрым пресетам
        $(document).on('click', '.quick-preset-btn', (e) => {
            this.handlePresetClick(e);
        });

        // Добавление пользовательского домена
        $('#addCustomPreset').on('click', () => {
            this.addCustomDomain();
        });

        // Простое тестирование
        $('#simpleTestBtn').on('click', () => {
            this.testTransformation();
        });

        // Сохранение настроек
        $('#saveSimpleSettings').on('click', () => {
            this.saveSettings();
        });

        // Переход к расширенным настройкам
        $('#advancedModeBtn').on('click', () => {
            this.openAdvancedMode();
        });

        // Удаление правил
        $(document).on('click', '.remove-rule', (e) => {
            this.removeRule(e);
        });

        // Загрузка конфигурации при открытии модала
        const modalElement = document.getElementById('simpleLinkSetupModal');
        if (modalElement) {
            modalElement.addEventListener('show.bs.modal', () => {
                if (this.botId) {
                    this.loadConfiguration();
                }
            });
        }
    }

    /**
     * Открыть простой мастер для конкретного бота
     */
    openForBot(botId) {
        this.botId = botId;
        
        // Универсальный способ открытия модала
        const modalElement = document.getElementById('simpleLinkSetupModal');
        
        // Попробуем Bootstrap 5
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
        // Fallback на jQuery/Bootstrap 4
        else if (typeof $ !== 'undefined' && $.fn.modal) {
            $('#simpleLinkSetupModal').modal('show');
        }
        // Простое показать/скрыть
        else {
            modalElement.classList.add('show');
            modalElement.style.display = 'block';
            document.body.classList.add('modal-open');
        }
    }

    /**
     * Обработка клика по быстрому пресету
     */
    handlePresetClick(event) {
        const btn = $(event.currentTarget);
        const preset = {
            id: btn.data('preset'),
            name: btn.data('name'),
            domain: btn.data('domain'), 
            buttonText: btn.data('button')
        };

        // Визуальная обратная связь
        btn.addClass('active').siblings().removeClass('active');
        
        // Добавить правило
        this.addPresetRule(preset);
        
        // Показать успех с простым языком
        this.showSimpleSuccess(`✅ Добавлено! Теперь ссылки ${preset.domain} будут кнопками`);
    }

    /**
     * Добавить правило из пресета
     */
    addPresetRule(preset) {
        const rule = {
            id: preset.id,
            name: preset.name,
            match_type: 'domain',
            match_value: preset.domain,
            button_text: preset.buttonText,
            button_emoji: this.extractEmoji(preset.buttonText),
            priority: 100,
            enabled: true,
            remove_original_link: true,
            case_sensitive: false,
            add_preview_text: false,
            preview_text: ''
        };

        // Проверить, не добавлено ли уже
        const existingIndex = this.activeRules.findIndex(r => r.id === rule.id);
        if (existingIndex >= 0) {
            this.activeRules[existingIndex] = rule; // Обновить
        } else {
            this.activeRules.push(rule); // Добавить новое
        }

        this.updateActiveRulesDisplay();
        this.isEnabled = true;
    }

    /**
     * Добавить пользовательский домен
     */
    addCustomDomain() {
        const domain = $('#customDomain').val().trim();
        const buttonText = $('#customButtonText').val().trim() || '🔗 Открыть ссылку';

        if (!domain) {
            this.showSimpleError('❌ Введите домен сайта');
            return;
        }

        // Простая валидация домена
        if (!this.isValidDomain(domain)) {
            this.showSimpleError('❌ Введите правильный домен (например: google.com)');
            return;
        }

        const customPreset = {
            id: `custom_${domain.replace(/[^a-zA-Z0-9]/g, '_')}`,
            name: `Пользовательский: ${domain}`,
            domain: domain,
            buttonText: buttonText
        };

        this.addPresetRule(customPreset);
        
        // Очистить поля
        $('#customDomain, #customButtonText').val('');
        
        this.showSimpleSuccess(`✅ Добавлен домен ${domain}!`);
    }

    /**
     * Простая валидация домена
     */
    isValidDomain(domain) {
        const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-_.]*[a-zA-Z0-9]$/;
        return domainRegex.test(domain) && domain.includes('.');
    }

    /**
     * Извлечь эмодзи из текста кнопки
     */
    extractEmoji(text) {
        const emojiRegex = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu;
        const matches = text.match(emojiRegex);
        return matches ? matches[0] : '🔗';
    }

    /**
     * Обновить отображение активных правил
     */
    updateActiveRulesDisplay() {
        const container = $('#activeRulesList');
        container.empty();

        if (this.activeRules.length === 0) {
            $('#activeRulesSection').hide();
            return;
        }

        $('#activeRulesSection').show();

        this.activeRules.forEach(rule => {
            const badge = $(`
                <span class="badge rule-badge px-3 py-2 position-relative">
                    ${rule.button_emoji || '🔗'} ${rule.match_value}
                    <button type="button" class="remove-rule" data-rule-id="${rule.id}" title="Удалить">×</button>
                </span>
            `);
            container.append(badge);
        });
    }

    /**
     * Удалить правило
     */
    removeRule(event) {
        event.stopPropagation();
        const ruleId = $(event.target).data('rule-id');
        
        this.activeRules = this.activeRules.filter(rule => rule.id !== ruleId);
        this.updateActiveRulesDisplay();
        
        // Убрать выделение с соответствующего пресета
        $(`.quick-preset-btn[data-preset="${ruleId}"]`).removeClass('active');
        
        this.showSimpleSuccess('✅ Правило удалено');
    }

    /**
     * Простое тестирование
     */
    async testTransformation() {
        const text = $('#simpleTestText').val().trim();
        
        if (!text) {
            this.showSimpleError('❌ Введите текст для проверки');
            return;
        }

        if (this.activeRules.length === 0) {
            this.showSimpleError('❌ Сначала добавьте хотя бы одно правило');
            return;
        }

        try {
            $('#simpleTestBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Проверяю...');

            const config = {
                enabled: true,
                transformation_rules: this.activeRules,
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
                this.displayTestResults(result.data, text);
            } else {
                this.showSimpleError(`❌ Ошибка: ${result.message}`);
            }

        } catch (error) {
            console.error('Test error:', error);
            this.showSimpleError('❌ Ошибка при тестировании');
        } finally {
            $('#simpleTestBtn').prop('disabled', false).html('<i class="fas fa-magic"></i> Показать как будет выглядеть');
        }
    }

    /**
     * Показать результаты тестирования простым языком
     */
    displayTestResults(data, originalText) {
        const resultDiv = $('#simpleTestResult');
        
        let html = `
            <div class="border rounded p-3 bg-light">
                <h6 class="text-success mb-3"><i class="fas fa-magic"></i> Результат:</h6>
                
                <div class="mb-3">
                    <strong>Текст сообщения:</strong><br>
                    <div class="bg-white p-2 rounded border">${data.processed_text || originalText}</div>
                </div>
        `;

        if (data.buttons && data.buttons.length > 0) {
            html += `
                <div class="mb-3">
                    <strong>Кнопки под сообщением:</strong><br>
                    <div class="mt-2">
            `;
            
            data.buttons.forEach(button => {
                html += `
                    <button class="btn btn-outline-primary btn-sm me-2 mb-2" disabled>
                        ${button.text}
                    </button>
                `;
            });
            
            html += '</div></div>';
        }

        if (data.transformations_count > 0) {
            html += `
                <div class="alert alert-success small mb-0">
                    <i class="fas fa-check-circle"></i>
                    Преобразовано ссылок: ${data.transformations_count}
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
        
        resultDiv.html(html).show();
    }

    /**
     * Сохранить настройки
     */
    async saveSettings() {
        try {
            $('#saveSimpleSettings').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Сохраняю...');

            const config = {
                enabled: this.activeRules.length > 0,
                transformation_rules: this.activeRules,
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

            // Сохранить все правила
            for (const rule of this.activeRules) {
                const ruleResponse = await fetch(`/api/v2/link-transformation/${this.botId}/rules`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(rule)
                });

                const ruleResult = await ruleResponse.json();
                if (!ruleResult.success) {
                    console.warn(`Failed to save rule ${rule.name}:`, ruleResult.message);
                }
            }

            this.showSimpleSuccess('✅ Настройки сохранены! Умные кнопки активны');
            
            // Закрыть модал через секунду
            setTimeout(() => {
                const modalElement = document.getElementById('simpleLinkSetupModal');
                
                if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) modal.hide();
                } else if (typeof $ !== 'undefined' && $.fn.modal) {
                    $('#simpleLinkSetupModal').modal('hide');
                } else {
                    modalElement.classList.remove('show');
                    modalElement.style.display = 'none';
                    document.body.classList.remove('modal-open');
                }
            }, 1500);

        } catch (error) {
            console.error('Save error:', error);
            this.showSimpleError(`❌ Ошибка сохранения: ${error.message}`);
        } finally {
            $('#saveSimpleSettings').prop('disabled', false).html('<i class="fas fa-save"></i> Сохранить настройки');
        }
    }

    /**
     * Загрузить существующую конфигурацию
     */
    async loadConfiguration() {
        try {
            const response = await fetch(`/api/v2/link-transformation/${this.botId}/config`);
            const result = await response.json();

            if (result.success && result.data) {
                this.isEnabled = result.data.enabled;
                this.activeRules = result.data.transformation_rules || [];
                
                this.updateActiveRulesDisplay();
                this.highlightActivePresets();
            }
        } catch (error) {
            console.error('Load config error:', error);
        }
    }

    /**
     * Подсветить активные пресеты
     */
    highlightActivePresets() {
        $('.quick-preset-btn').removeClass('active');
        
        this.activeRules.forEach(rule => {
            $(`.quick-preset-btn[data-preset="${rule.id}"]`).addClass('active');
        });
    }

    /**
     * Открыть расширенный режим
     */
    openAdvancedMode() {
        // Универсальное закрытие модала
        const modalElement = document.getElementById('simpleLinkSetupModal');
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();
        } else if (typeof $ !== 'undefined' && $.fn.modal) {
            $('#simpleLinkSetupModal').modal('hide');
        } else {
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
        
        // Подождать закрытия модала, потом открыть расширенный
        setTimeout(() => {
            if (window.openLinkTransformationModal) {
                window.openLinkTransformationModal(this.botId);
            }
        }, 300);
    }

    /**
     * Показать успешное сообщение
     */
    showSimpleSuccess(message) {
        this.showSimpleAlert(message, 'success');
    }

    /**
     * Показать ошибку
     */
    showSimpleError(message) {
        this.showSimpleAlert(message, 'danger');
    }

    /**
     * Показать простое уведомление
     */
    showSimpleAlert(message, type = 'info') {
        // Создать временное уведомление
        const alertId = 'simple-alert-' + Date.now();
        const alert = $(`
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999; max-width: 300px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);

        $('body').append(alert);

        // Автоматически удалить через 3 секунды
        setTimeout(() => {
            $(`#${alertId}`).alert('close');
        }, 3000);
    }
}

// Глобальная инициализация
const simpleLinkSetup = new SimpleLinkSetupManager();

// Глобальная функция для открытия простого интерфейса
window.openSimpleLinkSetup = function(botId) {
    simpleLinkSetup.openForBot(botId);
};
