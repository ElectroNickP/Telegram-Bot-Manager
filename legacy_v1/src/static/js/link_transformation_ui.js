/**
 * Link Transformation UI Integration
 * 
 * This module adds Link Transformation configuration button to bot management interfaces.
 * Can be included in any bot management page to provide link transformation functionality.
 */

(function() {
    'use strict';

    // Global Link Transformation managers
    window.LinkTransformationManagers = window.LinkTransformationManagers || {};

    /**
     * Add Link Transformation button to a bot management interface
     * @param {number} botId - Bot ID
     * @param {string} containerId - Container element ID where to add the button
     * @param {Object} options - Configuration options
     */
    function addLinkTransformationButton(botId, containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn('Link Transformation: Container not found:', containerId);
            return;
        }

        // Default options  
        const config = {
            buttonText: options.buttonText || 'Умные кнопки',
            buttonClass: options.buttonClass || 'bot-btn secondary',
            position: options.position || 'append', // 'append', 'prepend', 'before', 'after'
            ...options
        };

        // Create button element
        const button = document.createElement('button');
        button.type = 'button';
        button.className = config.buttonClass;
        // Показываем только иконку (как у других кнопок в ряду)
        button.innerHTML = `<i class="fas fa-magic"></i>`;
        button.title = config.buttonText;
        button.onclick = () => openSmartButtonsModal(botId);

        // Add button to container at correct position (after edit button, before dialogs)
        const editBtn = container.querySelector('.edit-btn');
        const dialogsLink = container.querySelector('a[href*="/dialogs/"]');
        
        if (editBtn && dialogsLink) {
            // Insert after edit button, before dialogs
            container.insertBefore(button, dialogsLink);
        } else if (editBtn) {
            // Insert after edit button
            editBtn.insertAdjacentElement('afterend', button);
        } else {
            // Fallback to append
            container.appendChild(button);
        }

        console.log(`Link Transformation button added for bot ${botId}`);
        return button;
    }

    /**
     * Initialize and show modal for specific bot
     * @param {number} botId - Bot ID
     */
    function initializeModalForBot(botId) {
        if (!botId) {
            alert('Ошибка: ID бота не указан');
            return;
        }
        
        // Initialize Link Transformation Manager for this bot if not already done
        if (!window.LinkTransformationManagers[botId]) {
            if (typeof window.LinkTransformationManager === 'function') {
                window.LinkTransformationManagers[botId] = new window.LinkTransformationManager(botId);
            } else {
                console.error('LinkTransformationManager not available');
                alert('Ошибка: Модуль управления не загружен');
                return;
            }
        }

        // Show the modal
        const modal = document.getElementById('linkTransformationModal');
        if (modal) {
            // Set bot ID in modal
            modal.setAttribute('data-bot-id', botId);
            
            // Show modal using Bootstrap or custom modal system
            if (modal.classList) {
                modal.classList.add('show');
                modal.style.display = 'block';
            }
            
            // Load existing configuration for this bot
            window.LinkTransformationManagers[botId].loadConfiguration();
            
            console.log(`Link Transformation modal opened for bot ${botId}`);
        } else {
            alert('Ошибка: Модальное окно не найдено');
        }
    }

    /**
     * Open Link Transformation modal for a specific bot
     * @param {number} botId - Bot ID
     */
    function openLinkTransformationModal(botId) {
        // Check if modal exists in DOM (already embedded)
        if (document.getElementById('linkTransformationModal')) {
            initializeModalForBot(botId);
        } else {
            // Try to load modal dynamically
            loadLinkTransformationModal().then(() => {
                initializeModalForBot(botId);
            }).catch(error => {
                console.error('Failed to load Link Transformation modal:', error);
                alert('Ошибка загрузки интерфейса настройки ссылок. Модальное окно не найдено в DOM.');
            });
        }
    }

    /**
     * Load Link Transformation modal HTML
     * @returns {Promise}
     */
    async function loadLinkTransformationModal() {
        try {
            const response = await fetch('/templates/link_transformation_modal.html');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const modalHtml = await response.text();
            
            // Create container and insert modal HTML
            const modalContainer = document.createElement('div');
            modalContainer.innerHTML = modalHtml;
            document.body.appendChild(modalContainer);

            // Load JavaScript for modal functionality
            if (!window.LinkTransformationManager) {
                await loadScript('/static/js/link_transformation.js');
            }

            console.log('Link Transformation modal loaded successfully');
        } catch (error) {
            console.error('Error loading Link Transformation modal:', error);
            throw error;
        }
    }

    /**
     * Initialize modal for specific bot
     * @param {number} botId - Bot ID
     */
    function initializeModalForBot(botId) {
        try {
            // Initialize or get existing manager
            if (!window.LinkTransformationManagers[botId]) {
                if (typeof LinkTransformationManager === 'undefined') {
                    throw new Error('LinkTransformationManager class not loaded');
                }
                window.LinkTransformationManagers[botId] = new LinkTransformationManager(botId);
            }

            // Show modal
            const modal = document.getElementById('linkTransformationModal');
            if (modal) {
                // For Bootstrap modals
                if (window.bootstrap && bootstrap.Modal) {
                    const modalInstance = bootstrap.Modal.getOrCreateInstance(modal);
                    modalInstance.show();
                } else {
                    // Fallback for custom modal implementation
                    modal.style.display = 'block';
                    modal.classList.add('show');
                }
            }
        } catch (error) {
            console.error('Error initializing Link Transformation modal:', error);
            alert('Ошибка инициализации настроек ссылок: ' + error.message);
        }
    }

    /**
     * Dynamically load a JavaScript file
     * @param {string} src - Script source URL
     * @returns {Promise}
     */
    function loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if script is already loaded
            const existing = document.querySelector(`script[src="${src}"]`);
            if (existing) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * Auto-detect and add Link Transformation buttons to common bot management interfaces
     */
    function autoInitialize() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', autoInitialize);
            return;
        }

        console.log('Auto-initializing Link Transformation UI...');

        // Strategy 1: Look for bot cards with data attributes
        const botCards = document.querySelectorAll('[data-bot-id]');
        botCards.forEach(card => {
            const botId = parseInt(card.dataset.botId);
            if (botId) {
                // Look for action buttons container
                const actionsContainer = card.querySelector('.bot-actions, .card-actions, .btn-group, .actions');
                if (actionsContainer) {
                    // Ensure container has an ID
                    if (!actionsContainer.id) {
                        actionsContainer.id = generateId();
                    }
                    addLinkTransformationButton(botId, actionsContainer.id, {
                        buttonClass: 'btn btn-outline-primary btn-sm'
                    });
                }
            }
        });

        // Strategy 2: Look for edit bot forms/modals
        const editForms = document.querySelectorAll('form[data-bot-id], .bot-edit-form');
        editForms.forEach(form => {
            const botId = parseInt(form.dataset.botId) || parseInt(form.querySelector('#edit_bot_id, #bot_id')?.value);
            if (botId) {
                // Look for form actions or tab navigation
                const tabNav = form.querySelector('.nav-tabs, .tab-buttons');
                if (tabNav) {
                    // Add as tab
                    const tabButton = document.createElement('button');
                    tabButton.type = 'button';
                    tabButton.className = 'nav-link btn btn-link';
                    tabButton.innerHTML = '<i class="fas fa-link"></i> Ссылки';
                    tabButton.onclick = () => openLinkTransformationModal(botId);
                    
                    const listItem = document.createElement('li');
                    listItem.className = 'nav-item';
                    listItem.appendChild(tabButton);
                    tabNav.appendChild(listItem);
                }
            }
        });

        console.log(`Link Transformation UI auto-initialized for ${botCards.length} bot cards and ${editForms.length} edit forms`);
    }

    /**
     * Generate unique ID for elements
     * @returns {string}
     */
    function generateId() {
        return 'lt-container-' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * API for manual integration
     */
    window.LinkTransformationUI = {
        addButton: addLinkTransformationButton,
        openModal: openLinkTransformationModal,
        autoInit: autoInitialize,
        
        // Convenience method for quick integration
        init: function(config = {}) {
            if (config.auto !== false) {
                autoInitialize();
            }
            
            // Allow manual button additions
            if (config.buttons) {
                config.buttons.forEach(buttonConfig => {
                    addLinkTransformationButton(
                        buttonConfig.botId,
                        buttonConfig.containerId,
                        buttonConfig.options
                    );
                });
            }
        }
    };

    // Auto-initialize when script loads (can be disabled by setting window.LinkTransformationUI_NoAutoInit = true)
    if (!window.LinkTransformationUI_NoAutoInit) {
        autoInitialize();
    }

    // Export functions to global scope for external access
    window.addLinkTransformationButton = addLinkTransformationButton;
    window.openLinkTransformationModal = openLinkTransformationModal;

})();

// CSS styles for the Link Transformation button
const linkTransformationStyles = `
    .link-transformation-btn {
        position: relative;
        overflow: hidden;
    }
    
    .link-transformation-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .link-transformation-btn:active {
        transform: translateY(0);
    }
    
    .link-transformation-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .link-transformation-btn:hover::before {
        left: 100%;
    }
    
    .link-transformation-tooltip {
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s, visibility 0.3s;
        z-index: 1000;
    }
    
    .link-transformation-btn:hover .link-transformation-tooltip {
        opacity: 1;
        visibility: visible;
    }
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = linkTransformationStyles;
document.head.appendChild(styleSheet);



