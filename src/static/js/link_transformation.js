/**
 * Link Transformation Management JavaScript
 * 
 * This module handles the UI for configuring link-to-button transformation
 * functionality for Telegram bots.
 */

class LinkTransformationManager {
    constructor(botId) {
        this.botId = botId;
        this.currentConfig = null;
        this.currentRules = [];
        this.editingRuleId = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadMatchTypes();
        this.loadRuleTemplates();
    }
    
    bindEvents() {
        // Main modal events - заменено на нативное событие
        // Событие вызывается вручную при открытии модала
        $('#saveLinkTransformationBtn').on('click', () => this.saveConfiguration());
        
        // Settings toggle
        $('#linkTransformationEnabled').on('change', () => this.toggleSettings());
        
        // Rule management
        $('#addRuleBtn').on('click', () => this.openRuleEditor());
        $('#saveRuleBtn').on('click', () => this.saveRule());
        
        // Rule editor events
        $('#matchType').on('change', () => this.updateMatchTypeHelp());
        $('#addPreviewText').on('change', () => this.togglePreviewSettings());
        $('#testRuleBtn').on('click', () => this.testCurrentRule());
        
        // Testing
        $('#testTransformationBtn').on('click', () => this.testTransformation());
        $('#clearTestBtn').on('click', () => this.clearTest());
        
        // Rule editor form validation
        $('#ruleEditorForm input, #ruleEditorForm select').on('input change', () => {
            this.validateRuleForm();
        });
    }
    
    async loadConfiguration() {
        try {
            this.showLoading('Загрузка конфигурации...');
            
            const response = await fetch(`/api/v2/link-transformation/${this.botId}/config`);
            const result = await response.json();
            
            if (result.success) {
                this.currentConfig = result.data;
                this.populateMainSettings(this.currentConfig);
                await this.loadRules();
            } else {
                this.showError('Ошибка загрузки конфигурации: ' + result.error);
            }
        } catch (error) {
            this.showError('Ошибка загрузки конфигурации: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    populateMainSettings(config) {
        $('#linkTransformationEnabled').prop('checked', config.enabled || false);
        $('#maxButtonsPerMessage').val(config.max_buttons_per_message || 5);
        $('#buttonLayout').val(config.button_layout || 'vertical');
        $('#processAiResponses').prop('checked', config.process_ai_responses !== false);
        $('#preserveFormatting').prop('checked', config.preserve_message_formatting !== false);
        
        this.toggleSettings();
    }
    
    toggleSettings() {
        const enabled = $('#linkTransformationEnabled').is(':checked');
        $('#linkTransformationSettings').toggle(enabled);
        
        if (enabled) {
            $('#linkTransformationSettings input, #linkTransformationSettings select')
                .prop('disabled', false);
        } else {
            $('#linkTransformationSettings input, #linkTransformationSettings select')
                .prop('disabled', true);
        }
    }
    
    async loadRules() {
        try {
            const response = await fetch(`/api/v2/link-transformation/${this.botId}/rules`);
            const result = await response.json();
            
            if (result.success) {
                this.currentRules = result.data || [];
                this.renderRules();
            } else {
                this.showError('Ошибка загрузки правил: ' + result.error);
            }
        } catch (error) {
            this.showError('Ошибка загрузки правил: ' + error.message);
        }
    }
    
    renderRules() {
        const container = $('#transformationRules');
        const noRulesMsg = $('#noRulesMessage');
        
        if (this.currentRules.length === 0) {
            container.html('');
            noRulesMsg.show();
            return;
        }
        
        noRulesMsg.hide();
        
        const rulesHtml = this.currentRules.map(rule => this.renderRuleItem(rule)).join('');
        container.html(rulesHtml);
        
        // Bind events for rule items
        $('.edit-rule-btn').on('click', (e) => {
            const ruleId = $(e.target).closest('.rule-item').data('rule-id');
            this.editRule(ruleId);
        });
        
        $('.delete-rule-btn').on('click', (e) => {
            const ruleId = $(e.target).closest('.rule-item').data('rule-id');
            this.deleteRule(ruleId);
        });
        
        $('.toggle-rule-btn').on('click', (e) => {
            const ruleId = $(e.target).closest('.rule-item').data('rule-id');
            this.toggleRule(ruleId);
        });
    }
    
    renderRuleItem(rule) {
        const statusClass = rule.enabled ? 'border-success' : 'border-secondary';
        const statusIcon = rule.enabled ? 'fa-toggle-on text-success' : 'fa-toggle-off text-secondary';
        
        return `
            <div class="rule-item p-3 ${statusClass} ${rule.enabled ? '' : 'disabled'}" data-rule-id="${rule.id}">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">
                            <i class="fas fa-magic text-primary"></i>
                            ${this.escapeHtml(rule.name)}
                            <span class="badge bg-secondary rule-priority-badge ms-2">
                                Приоритет: ${rule.priority}
                            </span>
                        </h6>
                        <div class="text-muted small mb-2">
                            <strong>Тип:</strong> ${this.getMatchTypeDisplay(rule.match_type)} • 
                            <strong>Значение:</strong> <code>${this.escapeHtml(rule.match_value)}</code>
                        </div>
                        <div class="text-muted small">
                            <strong>Кнопка:</strong> "${this.escapeHtml(rule.button_text)}"
                            ${rule.remove_original_link ? ' • <em>Удалять ссылку</em>' : ''}
                        </div>
                    </div>
                    
                    <div class="btn-group">
                        <button type="button" class="btn btn-sm btn-outline-secondary toggle-rule-btn" title="Включить/выключить">
                            <i class="fas ${statusIcon}"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-primary edit-rule-btn" title="Редактировать">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger delete-rule-btn" title="Удалить">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    getMatchTypeDisplay(matchType) {
        const types = {
            'domain': 'По домену',
            'url_contains': 'URL содержит',
            'url_regex': 'Регулярное выражение',
            'full_url': 'Точное совпадение'
        };
        return types[matchType] || matchType;
    }
    
    openRuleEditor(ruleId = null) {
        this.editingRuleId = ruleId;
        
        if (ruleId) {
            // Edit existing rule
            const rule = this.currentRules.find(r => r.id === ruleId);
            if (rule) {
                this.populateRuleEditor(rule);
                $('#ruleEditorTitle').text('Редактировать правило');
            }
        } else {
            // Create new rule
            this.clearRuleEditor();
            $('#ruleEditorTitle').text('Новое правило');
        }
        
        $('#ruleEditorModal').addClass('show').show();
    }
    
    populateRuleEditor(rule) {
        $('#ruleId').val(rule.id);
        $('#ruleName').val(rule.name);
        $('#rulePriority').val(rule.priority || 0);
        $('#matchType').val(rule.match_type);
        $('#matchValue').val(rule.match_value);
        $('#caseSensitive').prop('checked', rule.case_sensitive || false);
        $('#buttonText').val(rule.button_text);
        $('#buttonEmoji').val(rule.button_emoji || '');
        $('#removeOriginalLink').prop('checked', rule.remove_original_link !== false);
        $('#addPreviewText').prop('checked', rule.add_preview_text || false);
        $('#previewText').val(rule.preview_text || '');
        
        this.updateMatchTypeHelp();
        this.togglePreviewSettings();
    }
    
    clearRuleEditor() {
        $('#ruleEditorForm')[0].reset();
        $('#ruleId').val('');
        $('#buttonText').val('🔗 Открыть ссылку');
        $('#rulePriority').val(0);
        $('#removeOriginalLink').prop('checked', true);
        $('#addPreviewText').prop('checked', false);
        
        this.updateMatchTypeHelp();
        this.togglePreviewSettings();
    }
    
    updateMatchTypeHelp() {
        const matchType = $('#matchType').val();
        const helpTexts = {
            'markdown_link': 'Оставьте пустым чтобы обработать все Markdown ссылки [текст](url), или укажите домен для фильтрации',
            'domain': 'Введите домен, например: script.google.com',
            'url_contains': 'Введите текст, который должен содержаться в URL',
            'url_regex': 'Введите регулярное выражение для поиска',
            'full_url': 'Введите полный URL для точного совпадения'
        };
        
        const examples = {
            'markdown_link': 'script.google.com (опционально)',
            'domain': 'script.google.com',
            'url_contains': '/spreadsheets/',
            'url_regex': 'github\\.com\\/[^\\/]+\\/[^\\/]+',
            'full_url': 'https://example.com/page'
        };
        
        $('#matchValueHelp').text(helpTexts[matchType] || 'Введите значение для поиска');
        $('#matchValue').attr('placeholder', examples[matchType] || '');
        
        // For Markdown links, match value is optional
        if (matchType === 'markdown_link') {
            $('#matchValue').removeClass('required');
        } else {
            $('#matchValue').addClass('required');
        }
    }
    
    togglePreviewSettings() {
        const enabled = $('#addPreviewText').is(':checked');
        $('#previewTextSettings').toggle(enabled);
    }
    
    async loadMatchTypes() {
        try {
            const response = await fetch('/api/v2/link-transformation/match-types');
            const result = await response.json();
            
            if (result.success) {
                const options = result.data.map(type => 
                    `<option value="${type.value}">${type.name}</option>`
                ).join('');
                
                $('#matchType').html('<option value="">Выберите тип...</option>' + options);
            }
        } catch (error) {
            console.error('Error loading match types:', error);
        }
    }
    
    async loadRuleTemplates() {
        try {
            const response = await fetch('/api/v2/link-transformation/templates');
            const result = await response.json();
            
            if (result.success) {
                const templatesHtml = result.data.map(template => 
                    `<li><a class="dropdown-item template-item" href="#" data-template-id="${template.id}">
                        <i class="fas fa-template me-2"></i>${template.name}
                        <small class="text-muted d-block">${template.description}</small>
                    </a></li>`
                ).join('');
                
                $('#ruleTemplatesDropdown').html(templatesHtml);
                
                // Bind template selection
                $('.template-item').on('click', (e) => {
                    e.preventDefault();
                    const templateId = $(e.target).closest('.template-item').data('template-id');
                    this.applyTemplate(templateId, result.data);
                });
            }
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }
    
    applyTemplate(templateId, templates) {
        const template = templates.find(t => t.id === templateId);
        if (template) {
            this.editingRuleId = null;
            this.populateRuleEditor(template.rule);
            $('#ruleEditorTitle').text('Новое правило из шаблона');
            $('#ruleEditorModal').addClass('show').show();
        }
    }
    
    validateRuleForm() {
        const name = $('#ruleName').val().trim();
        const matchType = $('#matchType').val();
        const matchValue = $('#matchValue').val().trim();
        const buttonText = $('#buttonText').val().trim();
        
        // For markdown_link type, match_value is optional
        const matchValueRequired = matchType !== 'markdown_link';
        const isValid = name && matchType && buttonText && (!matchValueRequired || matchValue);
        
        $('#saveRuleBtn').prop('disabled', !isValid);
        
        return isValid;
    }
    
    async saveRule() {
        if (!this.validateRuleForm()) {
            this.showError('Заполните все обязательные поля');
            return;
        }
        
        const ruleData = {
            id: $('#ruleId').val() || this.generateRuleId(),
            name: $('#ruleName').val().trim(),
            enabled: true,
            match_type: $('#matchType').val(),
            match_value: $('#matchValue').val().trim(),
            case_sensitive: $('#caseSensitive').is(':checked'),
            button_text: $('#buttonText').val().trim(),
            button_emoji: $('#buttonEmoji').val().trim(),
            remove_original_link: $('#removeOriginalLink').is(':checked'),
            add_preview_text: $('#addPreviewText').is(':checked'),
            preview_text: $('#previewText').val().trim(),
            priority: parseInt($('#rulePriority').val()) || 0
        };
        
        try {
            this.showLoading('Сохранение правила...');
            
            const url = this.editingRuleId ? 
                `/api/v2/link-transformation/${this.botId}/rules/${this.editingRuleId}` :
                `/api/v2/link-transformation/${this.botId}/rules`;
            
            const method = this.editingRuleId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(ruleData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                $('#ruleEditorModal').removeClass('show').hide();
                await this.loadRules();
                this.showSuccess('Правило сохранено успешно');
            } else {
                this.showError('Ошибка сохранения правила: ' + result.error);
            }
        } catch (error) {
            this.showError('Ошибка сохранения правила: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    editRule(ruleId) {
        this.openRuleEditor(ruleId);
    }
    
    async deleteRule(ruleId) {
        const rule = this.currentRules.find(r => r.id === ruleId);
        if (!rule) return;
        
        if (!confirm(`Удалить правило "${rule.name}"?`)) return;
        
        try {
            this.showLoading('Удаление правила...');
            
            const response = await fetch(`/api/v2/link-transformation/${this.botId}/rules/${ruleId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                await this.loadRules();
                this.showSuccess('Правило удалено');
            } else {
                this.showError('Ошибка удаления правила: ' + result.error);
            }
        } catch (error) {
            this.showError('Ошибка удаления правила: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    async toggleRule(ruleId) {
        const rule = this.currentRules.find(r => r.id === ruleId);
        if (!rule) return;
        
        rule.enabled = !rule.enabled;
        
        try {
            const response = await fetch(`/api/v2/link-transformation/${this.botId}/rules/${ruleId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(rule)
            });
            
            const result = await response.json();
            
            if (result.success) {
                await this.loadRules();
            } else {
                this.showError('Ошибка обновления правила: ' + result.error);
            }
        } catch (error) {
            this.showError('Ошибка обновления правила: ' + error.message);
        }
    }
    
    async testCurrentRule() {
        const testUrls = $('#testUrls').val().split('\n').filter(url => url.trim());
        
        if (testUrls.length === 0) {
            this.showError('Введите URL для тестирования');
            return;
        }
        
        const ruleData = {
            match_type: $('#matchType').val(),
            match_value: $('#matchValue').val().trim(),
            case_sensitive: $('#caseSensitive').is(':checked')
        };
        
        try {
            const response = await fetch(`/api/v2/link-transformation/${this.botId}/rules/test/test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    urls: testUrls,
                    rule: ruleData
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayRuleTestResults(result.data.test_results);
            } else {
                this.showError('Ошибка тестирования правила: ' + result.error);
            }
        } catch (error) {
            this.showError('Ошибка тестирования правила: ' + error.message);
        }
    }
    
    displayRuleTestResults(results) {
        const resultsHtml = results.map(result => {
            const matchClass = result.matches ? 'test-result-match' : 'test-result-no-match';
            const matchText = result.matches ? 'Совпадение' : 'Нет совпадения';
            const matchIcon = result.matches ? 'fa-check' : 'fa-times';
            
            return `
                <div class="alert ${matchClass} py-2">
                    <i class="fas ${matchIcon} me-2"></i>
                    <strong>${matchText}:</strong> ${this.escapeHtml(result.url)}
                </div>
            `;
        }).join('');
        
        $('#ruleTestResults').html(resultsHtml).show();
    }
    
    async testTransformation() {
        const text = $('#testText').val().trim();
        
        if (!text) {
            this.showError('Введите текст для тестирования');
            return;
        }
        
        const config = this.getCurrentConfig();
        
        try {
            this.showLoading('Тестирование преобразования...');
            
            const response = await fetch(`/api/v2/link-transformation/${this.botId}/test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, config: config })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayTransformationResults(result.data);
            } else {
                this.showError('Ошибка тестирования: ' + result.error);
            }
        } catch (error) {
            this.showError('Ошибка тестирования: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    displayTransformationResults(data) {
        $('#originalText').text(data.original_text);
        $('#processedText').text(data.processed_text);
        
        // Display buttons
        const buttonsHtml = data.buttons.map(button => 
            `<a href="${button.url}" class="preview-button" target="_blank">${this.escapeHtml(button.text)}</a>`
        ).join(' ');
        
        $('#previewButtons').html(buttonsHtml || '<em class="text-muted">Нет кнопок</em>');
        
        // Display stats
        const stats = data.stats;
        $('#testStats').text(
            `Найдено ссылок: ${stats.total_urls}, Преобразовано: ${stats.transformed_urls}, ` +
            `Применено: ${stats.transformation_applied ? 'Да' : 'Нет'}`
        );
        
        $('#testResults').show();
    }
    
    getCurrentConfig() {
        return {
            enabled: $('#linkTransformationEnabled').is(':checked'),
            max_buttons_per_message: parseInt($('#maxButtonsPerMessage').val()) || 5,
            button_layout: $('#buttonLayout').val() || 'vertical',
            process_ai_responses: $('#processAiResponses').is(':checked'),
            preserve_message_formatting: $('#preserveFormatting').is(':checked'),
            transformation_rules: this.currentRules
        };
    }
    
    clearTest() {
        $('#testText').val('');
        $('#testResults').hide();
    }
    
    async saveConfiguration() {
        const config = this.getCurrentConfig();
        
        try {
            this.showLoading('Сохранение конфигурации...');
            
            const response = await fetch(`/api/v2/link-transformation/${this.botId}/config`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Настройки сохранены успешно');
                // Close modal after showing success message
                setTimeout(() => {
                    try {
                        $('#linkTransformationModal').removeClass('show').hide();
                    } catch (modalError) {
                        console.warn('Modal close error (non-critical):', modalError);
                        // Fallback - close modal with native DOM
                        const modal = document.getElementById('linkTransformationModal');
                        if (modal) {
                            modal.classList.remove('show');
                            modal.style.display = 'none';
                        }
                    }
                }, 1000);
            } else {
                this.showError('Ошибка сохранения: ' + result.error);
            }
        } catch (error) {
            // Only show error for actual API failures
            if (error.name === 'TypeError' || error.name === 'NetworkError') {
                this.showError('Ошибка сети: ' + error.message);
            } else {
                this.showError('Ошибка сохранения: ' + error.message);
            }
        } finally {
            this.hideLoading();
        }
    }
    
    generateRuleId() {
        return 'rule_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showLoading(message = 'Загрузка...') {
        // Implementation depends on your loading component
        console.log('Loading:', message);
    }
    
    hideLoading() {
        // Implementation depends on your loading component
        console.log('Loading finished');
    }
    
    showSuccess(message) {
        // Implementation depends on your notification system
        console.log('Success:', message);
        alert('Успешно: ' + message);
    }
    
    showError(message) {
        // Implementation depends on your notification system
        console.error('Error:', message);
        alert('Ошибка: ' + message);
    }
}

// Global function to initialize link transformation for a bot
function initLinkTransformation(botId) {
    return new LinkTransformationManager(botId);
}


