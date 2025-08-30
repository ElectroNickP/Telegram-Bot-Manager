/**
 * MODERN SMART BUTTONS INTERFACE
 * Professional UI for link transformation management
 */

class SmartButtonsManager {
    constructor(botId) {
        this.botId = botId;
        this.rules = [];
        this.isDirty = false;
        this.autoSaveTimeout = null;
        this.editingRuleId = null; // ID правила, которое сейчас редактируем
        
        this.initDragAndDrop();
    }

    // Метод для инициализации модала при открытии
    initModal() {
        this.bindEvents(); // Привязываем события когда модальное окно точно существует
        this.loadExisting(); // Загружаем существующие правила
        
        // Инициализируем поля и валидацию
        setTimeout(() => {
            this.clearInputs(); // Очищаем поля
            
            // ПРИНУДИТЕЛЬНО устанавливаем начальное состояние кнопки
            const addBtn = document.getElementById('addRuleBtn');
            if (addBtn) {
                addBtn.disabled = true;
                addBtn.setAttribute('disabled', 'disabled');
                addBtn.style.opacity = '0.6';
                addBtn.style.cursor = 'not-allowed';
                console.log('Button initialized as DISABLED');
            }
            
            this.initValidation(); // Инициализируем валидацию
            console.log('Modal initialized for real user interaction');
        }, 100); // Небольшая задержка для инициализации DOM
    }

    bindEvents() {
        const modal = document.getElementById('smartButtonsModal');
        if (!modal) {
            console.warn('Modal not found, cannot bind events');
            return;
        }

        // Если события уже привязаны, не привязываем снова
        if (modal.dataset.eventsBound === 'true') {
            console.log('Events already bound to modal');
            return;
        }
        
        // Привязываем события к модальному окну с делегированием
        modal.addEventListener('click', (e) => {
            if (e.target.id === 'addRuleBtn' || e.target.closest('#addRuleBtn')) {
                e.preventDefault();
                const btn = document.getElementById('addRuleBtn');
                if (btn && !btn.disabled) {
                    console.log('Add rule button clicked - executing addRule()');
                    this.addRule();
                } else {
                    console.log('Add rule button clicked but disabled - ignoring');
                }
            } else if (e.target.id === 'testRuleBtn' || e.target.closest('#testRuleBtn')) {
                e.preventDefault();
                this.quickTest();
            } else if (e.target.id === 'saveSettingsBtn' || e.target.closest('#saveSettingsBtn')) {
                e.preventDefault();
                this.saveSettings();
            } else if (e.target.id === 'clearAllRulesBtn' || e.target.closest('#clearAllRulesBtn')) {
                e.preventDefault();
                this.clearAllRules();
            } else if (e.target.id === 'cancelBtn' || e.target.closest('#cancelBtn')) {
                e.preventDefault();
                console.log('Cancel button clicked');
                this.closeModal();
            } else if (e.target.classList.contains('modal-close') || 
                      e.target.closest('.modal-close') ||
                      e.target.textContent.includes('Закрыть')) {
                console.log('Close button clicked');
                this.closeModal();
            }
        });
        
        // Валидация в реальном времени
        modal.addEventListener('input', (e) => {
            console.log('Input event triggered:', e.target.id, e.target.value);
            if (e.target.id === 'searchInLink' || e.target.id === 'buttonTextInput') {
                console.log('Validating inputs due to user input...');
                this.validateInputs();
            }
        });
        
        // Дополнительные события для надежности
        modal.addEventListener('keyup', (e) => {
            if (e.target.id === 'searchInLink' || e.target.id === 'buttonTextInput') {
                console.log('KeyUp event triggered:', e.target.id, e.target.value);
                this.validateInputs();
            }
        });
        
        modal.addEventListener('change', (e) => {
            if (e.target.id === 'searchInLink' || e.target.id === 'buttonTextInput') {
                console.log('Change event triggered:', e.target.id, e.target.value);
                this.validateInputs();
            }
        });
        
        // Enter для создания правила
        modal.addEventListener('keypress', (e) => {
            if (e.target.id === 'buttonTextInput' && e.key === 'Enter') {
                const addBtn = document.getElementById('addRuleBtn');
                if (addBtn && !addBtn.disabled) {
                    e.preventDefault();
                    this.addRule();
                }
            }
        });
        
        // Автосохранение отключено для предотвращения race condition
        // document.addEventListener('ruleChanged', () => this.scheduleAutoSave());
        
        // Помечаем, что события привязаны
        modal.dataset.eventsBound = 'true';
        console.log('Events bound to modal for bot:', this.botId);
    }

    initValidation() {
        this.validateInputs();
    }

    validateInputs() {
        // ИСПРАВЛЕНИЕ: Находим ВИДИМЫЕ элементы, а не первые найденные по ID
        const allSearchInputs = document.querySelectorAll('#searchInLink');
        const allTextInputs = document.querySelectorAll('#buttonTextInput');
        
        const searchInput = Array.from(allSearchInputs).find(input => input.offsetParent !== null);
        const textInput = Array.from(allTextInputs).find(input => input.offsetParent !== null);
        const addBtn = document.getElementById('addRuleBtn');
        const preview = document.getElementById('buttonPreview');
        const previewButton = document.getElementById('previewButton');
        
        // Проверяем что все элементы существуют
        if (!searchInput || !textInput || !addBtn) {
            console.warn('Required form elements not found', {
                searchInput: !!searchInput,
                textInput: !!textInput, 
                addBtn: !!addBtn
            });
            return;
        }
        
        const searchValue = searchInput.value.trim();
        const textValue = textInput.value.trim();
        
        // Валидация поиска
        const searchValidation = document.getElementById('searchValidation');
        if (searchValidation) {
            if (searchValue.length === 0) {
                searchValidation.textContent = '';
                searchValidation.className = 'validation-message';
            } else if (searchValue.length < 3) {
                searchValidation.textContent = '⚠️ Минимум 3 символа';
                searchValidation.className = 'validation-message error';
            } else if (this.isDuplicateSearch(searchValue)) {
                searchValidation.textContent = '⚠️ Такое правило уже существует';
                searchValidation.className = 'validation-message error';
            } else {
                searchValidation.textContent = '✅ Подходящий критерий поиска';
                searchValidation.className = 'validation-message success';
            }
        }
        
        // Валидация текста кнопки
        const textValidation = document.getElementById('textValidation');
        if (textValidation) {
            if (textValue.length === 0) {
                textValidation.textContent = '';
                textValidation.className = 'validation-message';
            } else if (textValue.length < 2) {
                textValidation.textContent = '⚠️ Минимум 2 символа';
                textValidation.className = 'validation-message error';
            } else if (textValue.length > 30) {
                textValidation.textContent = '⚠️ Максимум 30 символов';
                textValidation.className = 'validation-message error';
            } else {
                textValidation.textContent = '✅ Подходящий текст для кнопки';
                textValidation.className = 'validation-message success';
            }
        }
        
        // Активация кнопки создания
        const isValid = searchValue.length >= 3 && 
                       textValue.length >= 2 && 
                       textValue.length <= 30 && 
                       !this.isDuplicateSearch(searchValue);
        
        console.log('Validation check:', { 
            searchValid: searchValue.length >= 3,
            textValid: textValue.length >= 2 && textValue.length <= 30,
            notDuplicate: !this.isDuplicateSearch(searchValue),
            finalResult: isValid 
        });
        
        // ПРИНУДИТЕЛЬНО активируем/деактивируем кнопку С ПОЛНЫМ ОБНОВЛЕНИЕМ DOM
        if (isValid) {
            addBtn.disabled = false;
            addBtn.removeAttribute('disabled'); // Удаляем атрибут из HTML
            addBtn.classList.remove('disabled');
            addBtn.style.opacity = '1';
            addBtn.style.cursor = 'pointer';
            
            // ДОПОЛНИТЕЛЬНАЯ проверка что атрибут действительно удален
            if (addBtn.hasAttribute('disabled')) {
                addBtn.removeAttribute('disabled');
                console.warn('Had to force remove disabled attribute');
            }
            
            console.log('✅ Button ENABLED for user interaction');
            console.log('Button state check:', {
                disabled: addBtn.disabled,
                hasDisabledAttr: addBtn.hasAttribute('disabled')
            });
        } else {
            addBtn.disabled = true;
            addBtn.setAttribute('disabled', 'disabled'); // Устанавливаем атрибут в HTML
            addBtn.classList.add('disabled');
            addBtn.style.opacity = '0.6';
            addBtn.style.cursor = 'not-allowed';
            console.log('❌ Button DISABLED');
        }
        
        // Показ превью
        if (isValid) {
            if (preview) {
                preview.style.display = 'block';
                preview.style.animation = 'fadeIn 0.3s ease';
            }
            if (previewButton) {
                previewButton.innerHTML = `<i class="fas fa-link"></i> ${textValue}`;
            }
        } else {
            if (preview) {
                preview.style.display = 'none';
            }
        }
    }

    isDuplicateSearch(searchValue) {
        return this.rules.some(rule => {
            // При редактировании исключаем текущее правило из проверки
            if (this.editingRuleId && rule.id === this.editingRuleId) {
                return false;
            }
            return rule.match_value.toLowerCase() === searchValue.toLowerCase();
        });
    }

    addRule() {
        // ИСПРАВЛЕНИЕ: Находим ВИДИМЫЕ элементы для добавления правила
        const allSearchInputs = document.querySelectorAll('#searchInLink');
        const allTextInputs = document.querySelectorAll('#buttonTextInput');
        
        const searchInput = Array.from(allSearchInputs).find(input => input.offsetParent !== null);
        const textInput = Array.from(allTextInputs).find(input => input.offsetParent !== null);
        
        if (!searchInput || !textInput) {
            console.warn('Cannot find visible inputs for addRule');
            return;
        }
        
        const searchValue = searchInput.value.trim();
        const textValue = textInput.value.trim();
        
        console.log('addRule called with:', { searchValue, textValue });
        
        if (!searchValue || !textValue) {
            console.warn('Empty values in addRule:', { searchValue, textValue });
            return;
        }
        
        // Проверяем, редактируем ли мы существующее правило
        if (this.editingRuleId) {
            // Находим и обновляем существующее правило
            const existingRuleIndex = this.rules.findIndex(r => r.id === this.editingRuleId);
            if (existingRuleIndex !== -1) {
                this.rules[existingRuleIndex].match_value = searchValue;
                this.rules[existingRuleIndex].button_text = textValue;
                this.rules[existingRuleIndex].name = `Rule for ${searchValue}`;
                
                // Перерисовываем все правила
                document.getElementById('rulesContainer').innerHTML = '';
                this.rules.forEach(rule => this.renderRule(rule));
                
                this.showNotification('✏️ Правило обновлено', 'success');
            }
            
            // Сбрасываем режим редактирования
            this.editingRuleId = null;
        } else {
            // Создаем новое правило
            const rule = {
                id: this.generateRuleId(),
                name: `Rule for ${searchValue}`,
                match_type: 'url_contains',
                match_value: searchValue,
                button_text: textValue,
                priority: this.rules.length + 1,
                enabled: true
            };
            
            this.rules.push(rule);
            this.renderRule(rule);
            this.showNotification('✅ Правило добавлено', 'success');
        }
        
        this.updateRulesDisplay();
        this.clearInputs();
        this.markDirty();
    }

    generateRuleId() {
        return 'rule_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    renderRule(rule) {
        const template = document.getElementById('ruleTemplate');
        if (!template || !template.content) {
            console.error('Rule template not found or invalid');
            return;
        }
        const clone = template.content.cloneNode(true);
        
        const ruleCard = clone.querySelector('.rule-card');
        ruleCard.setAttribute('data-rule-id', rule.id);
        
        // Заполняем данные
        clone.querySelector('.search-text').textContent = rule.match_value;
        clone.querySelector('.button-text').textContent = rule.button_text;
        clone.querySelector('.priority-value').textContent = rule.priority;
        
        // Привязываем события
        clone.querySelector('.btn-edit-rule').addEventListener('click', () => this.editRule(rule.id));
        clone.querySelector('.btn-delete-rule').addEventListener('click', () => this.deleteRule(rule.id));
        
        // Добавляем в контейнер
        const container = document.getElementById('rulesContainer');
        if (!container) {
            console.error('Rules container not found');
            return;
        }
        container.appendChild(clone);
        
        // Принудительная проверка видимости для Яндекс браузера
        setTimeout(() => {
            const addedCard = container.querySelector(`[data-rule-id="${rule.id}"]`);
            if (addedCard) {
                // Убеждаемся, что карточка видима
                addedCard.style.display = 'block';
                addedCard.style.opacity = '1';
                addedCard.style.visibility = 'visible';
                addedCard.style.position = 'relative';
                addedCard.style.width = '100%';
                addedCard.style.boxSizing = 'border-box';
                
                // Анимация появления
                addedCard.style.animation = 'fadeIn 0.5s ease';
                
                // Принудительный reflow
                addedCard.offsetHeight;
                
                // Дополнительная проверка через 100ms
                setTimeout(() => {
                    if (addedCard.offsetHeight === 0) {
                        console.warn('Rule card not visible, forcing display');
                        addedCard.style.display = 'block !important';
                        addedCard.style.height = 'auto';
                        addedCard.style.minHeight = '80px';
                    }
                }, 100);
            }
        }, 10);
    }

    editRule(ruleId) {
        const rule = this.rules.find(r => r.id === ruleId);
        if (!rule) {
            console.error('Rule not found for editing:', ruleId);
            return;
        }
        
        // ИСПРАВЛЕНИЕ: Находим ВИДИМЫЕ элементы ввода
        const allSearchInputs = document.querySelectorAll('#searchInLink');
        const allTextInputs = document.querySelectorAll('#buttonTextInput');

        const searchInput = Array.from(allSearchInputs).find(input => input.offsetParent !== null);
        const textInput = Array.from(allTextInputs).find(input => input.offsetParent !== null);

        if (!searchInput || !textInput) {
            console.error('Input fields not found for editing');
            this.showNotification('❌ Ошибка: поля ввода не найдены', 'error');
            return;
        }

        // Запоминаем ID правила, которое редактируем
        this.editingRuleId = ruleId;
        
        // Заполняем поля для редактирования
        searchInput.value = rule.match_value;
        textInput.value = rule.button_text;
        
        // Активируем валидацию
        this.validateInputs();
        
        // Фокус на первом поле
        searchInput.focus();
        
        this.showNotification('✏️ Правило загружено для редактирования. Нажмите "Создать правило" для применения изменений', 'info');
    }

    deleteRule(ruleId, showNotification = true) {
        this.rules = this.rules.filter(r => r.id !== ruleId);
        
        const ruleElement = document.querySelector(`[data-rule-id="${ruleId}"]`);
        if (ruleElement) {
            ruleElement.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                ruleElement.remove();
                this.updateRulesDisplay();
            }, 300);
        }
        
        this.markDirty();
        
        if (showNotification) {
            this.showNotification('🗑️ Правило удалено', 'warning');
        }
    }

    clearAllRules() {
        if (this.rules.length === 0) return;
        
        if (!confirm(`Удалить все ${this.rules.length} правил? Это действие нельзя отменить.`)) {
            return;
        }
        
        this.rules = [];
        document.getElementById('rulesContainer').innerHTML = '';
        this.updateRulesDisplay();
        this.markDirty();
        
        this.showNotification('🧹 Все правила удалены', 'warning');
    }

    updateRulesDisplay() {
        const container = document.getElementById('rulesContainer');
        const emptyState = document.getElementById('emptyState');
        const clearAllBtn = document.getElementById('clearAllRulesBtn');
        const rulesCount = document.getElementById('rulesCount');
        
        // Принудительное обновление для кросс-браузерной совместимости
        setTimeout(() => {
            if (this.rules.length === 0) {
                if (emptyState && !container.contains(emptyState)) {
                    container.appendChild(emptyState);
                }
                if (clearAllBtn) clearAllBtn.style.display = 'none';
                if (rulesCount) rulesCount.textContent = 'Нет правил';
            } else {
                if (emptyState && container.contains(emptyState)) {
                    container.removeChild(emptyState);
                }
                if (clearAllBtn) clearAllBtn.style.display = 'flex';
                if (rulesCount) rulesCount.textContent = `${this.rules.length} ${this.getWordForm(this.rules.length, ['правило', 'правила', 'правил'])}`;
                
                // Дополнительная проверка видимости карточек для Яндекс браузера
                const ruleCards = container.querySelectorAll('.rule-card');
                ruleCards.forEach((card, index) => {
                    if (card) {
                        card.style.display = 'block';
                        card.style.opacity = '1';
                        card.style.visibility = 'visible';
                        card.style.position = 'relative';
                        // Принудительный reflow
                        card.offsetHeight;
                    }
                });
                
                // Принудительное обновление скролла контейнера
                container.scrollTop = 0;
                setTimeout(() => container.scrollTop = 0, 100);
            }
        }, 10);
    }

    getWordForm(number, forms) {
        const cases = [2, 0, 1, 1, 1, 2];
        return forms[(number % 100 > 4 && number % 100 < 20) ? 2 : cases[Math.min(number % 10, 5)]];
    }

    clearInputs() {
        // ИСПРАВЛЕНИЕ: Находим ВИДИМЫЕ элементы для очистки
        const allSearchInputs = document.querySelectorAll('#searchInLink');
        const allTextInputs = document.querySelectorAll('#buttonTextInput');
        
        const searchInput = Array.from(allSearchInputs).find(input => input.offsetParent !== null);
        const textInput = Array.from(allTextInputs).find(input => input.offsetParent !== null);
        const preview = document.getElementById('buttonPreview');
        
        if (searchInput) {
            searchInput.value = '';
            console.log('Search input cleared');
        }
        if (textInput) {
            textInput.value = '';
            console.log('Text input cleared');
        }
        if (preview) preview.style.display = 'none';
        
        // Сбрасываем режим редактирования
        this.editingRuleId = null;
        
        console.log('Inputs cleared, validating...');
        this.validateInputs();
    }

    async quickTest() {
        // ИСПРАВЛЕНИЕ: Находим ВИДИМЫЕ элементы для тестирования
        const allTestAreas = document.querySelectorAll('#testTextArea');
        const allTestBtns = document.querySelectorAll('#quickTestBtn');

        const testTextArea = Array.from(allTestAreas).find(area => area.offsetParent !== null);
        const testBtn = Array.from(allTestBtns).find(btn => btn.offsetParent !== null);

        if (!testTextArea || !testBtn) {
            console.error('Test elements not found');
            this.showNotification('❌ Ошибка: элементы тестирования не найдены', 'error');
            return;
        }

        const testText = testTextArea.value.trim();
        if (!testText) {
            this.showNotification('⚠️ Введите текст для тестирования', 'warning');
            return;
        }
        const originalText = testBtn.innerHTML;
        testBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Тестирую...</span>';
        testBtn.disabled = true;

        try {
            const response = await fetch(`/api/v2/link-transformation/${this.botId}/test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: testText,
                    rules: this.rules
                })
            });

            if (!response.ok) throw new Error('Ошибка API');

            const result = await response.json();
            this.showTestResults(result);

        } catch (error) {
            console.error('Test error:', error);
            this.showNotification('❌ Ошибка при тестировании', 'error');
        } finally {
            testBtn.innerHTML = originalText;
            testBtn.disabled = false;
        }
    }

    showTestResults(result) {
        const resultsDiv = document.getElementById('testResults');
        
        let html = '<div class="test-result-content">';
        
        if (result.transformations_count > 0) {
            html += `<div class="test-success">
                <h6><i class="fas fa-check-circle"></i> Найдено ${result.transformations_count} совпадений</h6>
                <div class="test-text">${result.processed_text}</div>`;
            
            if (result.buttons && result.buttons.length > 0) {
                html += '<div class="test-buttons"><h6>Созданные кнопки:</h6>';
                result.buttons.forEach(button => {
                    html += `<div class="telegram-button-preview" onclick="window.open('${button.url}', '_blank')">
                        <i class="fas fa-external-link-alt"></i> ${button.text}
                    </div>`;
                });
                html += '</div>';
            }
            html += '</div>';
        } else {
            html += `<div class="test-warning">
                <h6><i class="fas fa-exclamation-triangle"></i> Совпадений не найдено</h6>
                <p>Ни одно правило не сработало для данного текста.</p>
            </div>`;
        }
        
        html += '</div>';
        
        resultsDiv.innerHTML = html;
        resultsDiv.style.display = 'block';
        resultsDiv.style.animation = 'fadeIn 0.3s ease';
    }

    async loadExisting() {
        try {
            // Загружаем правила из API
            const rulesResponse = await fetch(`/api/v2/link-transformation/${this.botId}/rules`);
            if (rulesResponse.ok) {
                const rulesData = await rulesResponse.json();
                if (rulesData.success && rulesData.data) {
                    this.rules = rulesData.data.filter((rule, index, self) => 
                        index === self.findIndex(r => r.id === rule.id)
                    );
                    
                    console.log(`Loaded ${this.rules.length} existing rules for bot ${this.botId}`);
                    
                    // Очищаем контейнер и рендерим правила
                    const container = document.getElementById('rulesContainer');
                    container.innerHTML = '';
                    
                    this.rules.forEach(rule => this.renderRule(rule));
                    this.updateRulesDisplay();
                }
            }
            
            // Дополнительно загружаем конфигурацию (но не зависим от неё для правил)
            const configResponse = await fetch(`/api/v2/link-transformation/${this.botId}/config`);
            if (configResponse.ok) {
                const configData = await configResponse.json();
                console.log('Bot config loaded:', configData.success ? 'success' : 'failed');
            }
            
        } catch (error) {
            console.error('Error loading existing rules:', error);
        }
    }

    async saveSettings() {
        // Предотвращаем повторное сохранение если уже идет процесс
        if (this.isSaving) {
            console.log('SaveSettings already in progress, skipping...');
            return;
        }
        
        this.isSaving = true;
        
        // Отменяем автосохранение, так как сохраняем вручную
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
            this.autoSaveTimeout = null;
        }
        
        const saveBtn = document.getElementById('saveSettingsBtn');
        const saveStatus = document.getElementById('saveStatus');
        const originalText = saveBtn.innerHTML;

        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Сохраняю...</span>';
        saveBtn.disabled = true;

        try {
            console.log(`Saving ${this.rules.length} rules:`, this.rules);
            
            // Просто сохраняем правила без удаления существующих
            // API сам разберется с дубликатами по ID
            for (const rule of this.rules) {
                console.log('Saving rule:', rule);
                
                // Если правило уже имеет ID, обновляем его, иначе создаем новое
                if (rule.id && rule.id.startsWith('rule_')) {
                    // Создаем новое правило
                    const response = await fetch(`/api/v2/link-transformation/${this.botId}/rules`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(rule)
                    });

                    if (!response.ok) {
                        const errorData = await response.json();
                        console.error('Failed to save rule:', rule, 'Error:', errorData);
                        throw new Error(`Failed to save rule: ${rule.name} - ${errorData.error || 'Unknown error'}`);
                    }
                    
                    const savedRuleData = await response.json();
                    console.log('Rule saved successfully:', savedRuleData);
                } else {
                    console.log('Rule already exists with server ID, skipping:', rule.id);
                }
            }

            // НЕ обновляем конфигурацию здесь - правила управляются отдельно
            // и PUT config затирает правила
            console.log('Skipping config update to prevent rule deletion');

            this.isDirty = false;
            saveStatus.textContent = '✅ Сохранено';
            saveStatus.style.color = '#28a745';
            
            this.showNotification('✅ Настройки сохранены', 'success');

        } catch (error) {
            console.error('Save error:', error);
            saveStatus.textContent = '❌ Ошибка';
            saveStatus.style.color = '#dc3545';
            this.showNotification('❌ Ошибка сохранения', 'error');
        } finally {
            this.isSaving = false;
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = false;
            
            setTimeout(() => {
                if (saveStatus) {
                    saveStatus.textContent = '';
                }
            }, 3000);
        }
    }

    scheduleAutoSave() {
        // Отключаем автосохранение, чтобы избежать race condition
        console.log('Auto-save disabled to prevent race conditions');
        return;
        
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
        }
        
        this.autoSaveTimeout = setTimeout(() => {
            if (this.isDirty) {
                this.saveSettings();
            }
        }, 2000); // Автосохранение через 2 секунды
    }

    markDirty() {
        this.isDirty = true;
        const saveBtn = document.getElementById('saveSettingsBtn');
        if (!saveBtn.classList.contains('pulse')) {
            saveBtn.style.animation = 'pulse 1s ease';
            setTimeout(() => {
                saveBtn.style.animation = '';
            }, 1000);
        }
        
        // Диспатч события отключен для предотвращения race condition
        // document.dispatchEvent(new CustomEvent('ruleChanged'));
    }

    initDragAndDrop() {
        // TODO: Implement drag and drop for rule reordering
        // This would allow users to change rule priorities by dragging
    }

    showNotification(message, type = 'info') {
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Стили для уведомления
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 12px;
            max-width: 300px;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Автоудаление через 5 секунд
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    getNotificationColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || colors.info;
    }

    closeModal() {
        const modalElement = document.getElementById('smartButtonsModal');
        if (!modalElement) return;
        
        // Анимация скрытия
        modalElement.style.opacity = '0';
        
        setTimeout(() => {
            modalElement.style.display = 'none';
            modalElement.classList.remove('show');
            document.body.style.overflow = '';
        }, 300);
    }
}

// Глобальная функция для открытия модала
function openSmartButtonsModal(botId) {
    // Создаем или получаем существующий менеджер
    if (!window.smartButtonsManagers) {
        window.smartButtonsManagers = {};
    }
    
    if (!window.smartButtonsManagers[botId]) {
        window.smartButtonsManagers[botId] = new SmartButtonsManager(botId);
    }
    
    const modalElement = document.getElementById('smartButtonsModal');
    if (!modalElement) {
        console.error('Smart buttons modal not found');
        return;
    }
    
    // Показываем модальное окно в стиле проекта
    modalElement.style.display = 'flex';
    modalElement.style.opacity = '0';
    modalElement.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Анимация появления
    setTimeout(() => {
        modalElement.style.opacity = '1';
    }, 10);
    
    // Закрытие по клику на backdrop
    const backdrop = modalElement.querySelector('.modal-backdrop');
    if (backdrop) {
        backdrop.onclick = () => {
            window.smartButtonsManagers[botId].closeModal();
        };
    }
    
    // Закрытие по Escape
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            window.smartButtonsManagers[botId].closeModal();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);
    
    // Инициализируем модальное окно (события + загрузка правил)
    window.smartButtonsManagers[botId].initModal();
}

// Экспорт для использования в других скриптах
window.SmartButtonsManager = SmartButtonsManager;
window.openSmartButtonsModal = openSmartButtonsModal;
