// Dashboard Logic

$(document).ready(function () {
    // Search Functionality
    $('#searchInput').on('keyup', function () {
        const value = $(this).val().toLowerCase();
        $('.bot-card').filter(function () {
            $(this).toggle($(this).data('name').indexOf(value) > -1)
        });
    });

    // Create Bot Form
    $('#createBotForm').on('submit', function (e) {
        e.preventDefault();
        const data = {
            bot_name: $('#bot_name').val(),
            telegram_token: $('#telegram_token').val(),
            openai_api_key: $('#openai_api_key').val(),
            assistant_id: $('#assistant_id').val(),
            enable_ai_responses: $('#enable_ai_responses').is(':checked'),
            enable_voice_responses: $('#enable_voice_responses').is(':checked')
        };

        $.ajax({
            url: '/api/bots',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function () { location.reload(); },
            error: function (xhr) {
                alert('Error creating bot: ' + (xhr.responseJSON?.error || 'Unknown error'));
            }
        });
    });

    // Auto-fill name
    $('#telegram_token').on('change', function () {
        const token = $(this).val();
        if (token && !$('#bot_name').val()) {
            $.ajax({
                url: '/api/v2/telegram/validate-token',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ token }),
                success: function (res) {
                    if (res.success && res.data.username) {
                        $('#bot_name').val(res.data.username);
                        $('#token_validation_status').html('<span style="color:var(--success)">Valid token</span>');
                    }
                }
            });
        }
    });

    // Edit Bot Form Submit
    $('#editBotForm').on('submit', function (e) {
        e.preventDefault();
        const id = $('#edit_bot_id').val();
        const data = {
            bot_name: $('#edit_bot_name').val(),
            telegram_token: $('#edit_telegram_token').val(),
            openai_api_key: $('#edit_openai_api_key').val(),
            assistant_id: $('#edit_assistant_id').val(),
            enable_ai_responses: $('#edit_enable_ai_responses').is(':checked'),
            enable_voice_responses: $('#edit_enable_voice_responses').is(':checked')
        };

        const btn = $(this).find('button[type="submit"]');
        const originalText = btn.text();
        btn.text('Saving...').prop('disabled', true);

        $.ajax({
            url: `/api/bots/${id}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function () {
                location.reload();
            },
            error: function (xhr) {
                alert('Error updating bot: ' + (xhr.responseJSON?.error || 'Unknown error'));
                btn.text(originalText).prop('disabled', false);
            }
        });
    });

    // Close modals on outside click
    $('.modal-overlay').on('click', function (e) {
        if (e.target === this) {
            $(this).removeClass('active');
        }
    });

    // Start periodic status polling
    setInterval(updateBotsStatus, 5000);
});

// Filter Functionality
function filterBots(status) {
    if (status === 'all') {
        $('.bot-card').show();
    } else if (status === 'marketplace') {
        $('.bot-card').hide();
        $('.bot-card[data-marketplace="true"]').show();
    } else {
        $('.bot-card').hide();
        $('.bot-card[data-status="' + status + '"]').show();
    }
}

// Standard Actions
function botAction(id, action, btn) {
    const $btn = $(btn);
    const originalHtml = $btn.html();
    $btn.html('<i class="fas fa-spinner fa-spin"></i>').prop('disabled', true);

    $.ajax({
        url: `/api/bots/${id}/${action}`,
        method: 'POST',
        success: function () { location.reload(); },
        error: function (xhr) {
            alert('Error: ' + (xhr.responseJSON?.error || 'Unknown error'));
            $btn.html(originalHtml).prop('disabled', false);
        }
    });
}

function deleteBot(id, btn) {
    if (!confirm('Are you sure?')) return;
    $(btn).closest('.bot-card').css('opacity', 0.5);

    $.ajax({
        url: `/api/bots/${id}`,
        method: 'DELETE',
        success: function () { location.reload(); },
        error: function (xhr) {
            alert('Error: ' + (xhr.responseJSON?.error || 'Unknown error'));
            $(btn).closest('.bot-card').css('opacity', 1);
        }
    });
}

// Modal Logic
function openCreateBotModal() {
    $('#createBotModal').addClass('active');
}

function closeCreateBotModal() {
    $('#createBotModal').removeClass('active');
}

function openEditModal(id) {
    // Fetch current bot config
    $.ajax({
        url: `/api/bots/${id}`,
        method: 'GET',
        success: function (bot) {
            $('#edit_bot_id').val(bot.id);
            $('#edit_bot_name').val(bot.config.bot_name);
            $('#edit_telegram_token').val(bot.config.telegram_token);
            $('#edit_openai_api_key').val(bot.config.openai_api_key);
            $('#edit_assistant_id').val(bot.config.assistant_id);
            $('#edit_enable_ai_responses').prop('checked', bot.config.enable_ai_responses !== false);
            $('#edit_enable_voice_responses').prop('checked', bot.config.enable_voice_responses === true);

            $('#editBotModal').addClass('active');
        },
        error: function (xhr) {
            alert('Failed to load bot details: ' + (xhr.responseJSON?.error || 'Unknown error'));
        }
    });
}

function closeEditModal() {
    $('#editBotModal').removeClass('active');
}

function updateBotsStatus() {
    $.ajax({
        url: '/api/bots',
        method: 'GET',
        success: function (bots) {
            bots.forEach(bot => {
                const card = $(`.bot-card[data-bot-id="${bot.id}"]`);
                if (card.length) {
                    const statusBadge = card.find('.status-badge');
                    const startBtn = card.find('.start-btn');
                    const stopBtn = card.find('.stop-btn');

                    if (bot.status === 'running') {
                        statusBadge.removeClass('stopped').addClass('running').html('<i class="fas fa-circle" style="font-size: 0.5rem;"></i> Running');
                        startBtn.prop('disabled', true);
                        stopBtn.prop('disabled', false);
                    } else {
                        statusBadge.removeClass('running').addClass('stopped').html('<i class="fas fa-circle" style="font-size: 0.5rem;"></i> Stopped');
                        startBtn.prop('disabled', false);
                        stopBtn.prop('disabled', true);
                    }
                }
            });
        }
    });
}
