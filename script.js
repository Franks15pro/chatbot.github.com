const messagesList = document.getElementById('messagesList');
const messagesWrapper = document.getElementById('messagesWrapper');
const emptyState = document.getElementById('emptyState');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatForm = document.getElementById('chatForm');

let sessionId = generateSessionId();
let isFirstMessage = true;

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Auto-resize textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    
    // Enable/disable send button
    sendButton.disabled = !this.value.trim();
});

// Handle Enter key
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        if (messageInput.value.trim()) {
            sendMessage(event);
        }
    }
}

function addMessage(text, isUser = false, conversationId = null, confidence = null, source = null) {
    if (isFirstMessage) {
        emptyState.style.display = 'none';
        isFirstMessage = false;
    }

    const messageGroup = document.createElement('div');
    messageGroup.className = 'message-group';

    const messageRow = document.createElement('div');
    messageRow.className = `message-row ${isUser ? 'user' : 'bot'}`;

    const wrapper = document.createElement('div');
    wrapper.className = 'message-content-wrapper';

    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${isUser ? 'user' : 'bot'}`;
    avatar.textContent = isUser ? 'U' : 'AI';

    const content = document.createElement('div');
    content.className = 'message-body';

    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.textContent = text;

    content.appendChild(messageText);

    // Add ML badge
    if (source === 'learned_exact' || source === 'learned_similar') {
        const badge = document.createElement('div');
        badge.className = 'message-badge';
        badge.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/>
            </svg>
            ${source === 'learned_exact' ? 'Wyuczona odpowiedź' : 'Podobna odpowiedź'}
        `;
        content.appendChild(badge);
    }

    // Add feedback buttons for bot messages
    if (!isUser && conversationId) {
        const actions = document.createElement('div');
        actions.className = 'message-actions';
        actions.innerHTML = `
            <button class="action-btn" onclick="sendFeedback(${conversationId}, 1, this)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
                </svg>
            </button>
            <button class="action-btn" onclick="sendFeedback(${conversationId}, -1, this)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/>
                </svg>
            </button>
        `;
        
        if (confidence !== null) {
            const confidenceBtn = document.createElement('button');
            confidenceBtn.className = 'action-btn';
            confidenceBtn.textContent = `Pewność: ${Math.round(confidence * 100)}%`;
            confidenceBtn.disabled = true;
            actions.appendChild(confidenceBtn);
        }
        
        content.appendChild(actions);
    }

    wrapper.appendChild(avatar);
    wrapper.appendChild(content);
    messageRow.appendChild(wrapper);
    messageGroup.appendChild(messageRow);
    messagesList.appendChild(messageGroup);

    scrollToBottom();
}

function showTyping() {
    const typingGroup = document.createElement('div');
    typingGroup.className = 'message-group';
    typingGroup.id = 'typingIndicator';

    const typingRow = document.createElement('div');
    typingRow.className = 'message-row bot typing-indicator';

    const wrapper = document.createElement('div');
    wrapper.className = 'message-content-wrapper';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar bot';
    avatar.textContent = 'AI';

    const dots = document.createElement('div');
    dots.className = 'typing-dots';
    dots.innerHTML = '<span></span><span></span><span></span>';

    wrapper.appendChild(avatar);
    wrapper.appendChild(dots);
    typingRow.appendChild(wrapper);
    typingGroup.appendChild(typingRow);
    messagesList.appendChild(typingGroup);

    scrollToBottom();
}

function hideTyping() {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();
}

function scrollToBottom() {
    setTimeout(() => {
        messagesWrapper.scrollTop = messagesWrapper.scrollHeight;
    }, 50);
}

async function sendMessage(event) {
    event.preventDefault();

    const message = messageInput.value.trim();
    if (!message) return;

    addMessage(message, true);
    
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendButton.disabled = true;

    showTyping();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message: message,
                session_id: sessionId
            })
        });

        const data = await response.json();

        setTimeout(() => {
            hideTyping();
            addMessage(
                data.response,
                false,
                data.conversation_id,
                data.confidence,
                data.source
            );
        }, 600 + Math.random() * 400);

    } catch (error) {
        hideTyping();
        addMessage('Przepraszam, wystąpił błąd. Spróbuj ponownie.');
        console.error('Error:', error);
    }
}

async function sendFeedback(conversationId, rating, button) {
    const actionsDiv = button.parentElement;
    const buttons = actionsDiv.querySelectorAll('.action-btn');
    
    buttons.forEach(btn => {
        if (btn !== button && !btn.disabled) {
            btn.disabled = true;
            btn.style.opacity = '0.3';
        }
    });

    button.classList.add(rating > 0 ? 'active-positive' : 'active-negative');
    button.disabled = true;

    try {
        const response = await fetch('/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                conversation_id: conversationId,
                rating: rating
            })
        });

        const data = await response.json();

        if (data.success && rating > 0) {
            showToast('Dziękuję! Właśnie się nauczyłem czegoś nowego.');
        }

    } catch (error) {
        console.error('Feedback error:', error);
    }
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: var(--accent);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 1001;
        animation: slideInUp 0.3s ease;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutDown 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function quickReply(text) {
    messageInput.value = text;
    messageInput.dispatchEvent(new Event('input'));
    messageInput.focus();
    setTimeout(() => sendMessage(new Event('submit')), 100);
}

function newChat() {
    if (confirm('Czy na pewno chcesz rozpocząć nowy chat?')) {
        messagesList.innerHTML = '';
        emptyState.style.display = 'flex';
        isFirstMessage = true;
        sessionId = generateSessionId();
        closeSidebar();
    }
}

async function showStats() {
    const modal = document.getElementById('statsModal');
    const content = document.getElementById('statsContent');
    
    modal.classList.add('active');
    content.innerHTML = '<div class="loading">Ładowanie statystyk...</div>';

    try {
        const response = await fetch('/stats');
        const stats = await response.json();

        content.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${stats.total_conversations}</div>
                    <div class="stat-label">Wszystkie rozmowy</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.learned_responses}</div>
                    <div class="stat-label">Wyuczone odpowiedzi</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.positive_feedback}</div>
                    <div class="stat-label">Pozytywny feedback</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.avg_rating.toFixed(1)}</div>
                    <div class="stat-label">Średnia ocena</div>
                </div>
            </div>
            <div class="stat-description">
                Bot wykorzystuje uczenie maszynowe (TF-IDF + Cosine Similarity) do nauki z każdej rozmowy. 
                Twój feedback pomaga modelowi stawać się coraz lepszym. Im więcej pozytywnych ocen, 
                tym dokładniejsze odpowiedzi w przyszłości!
            </div>
        `;
    } catch (error) {
        content.innerHTML = '<div class="loading">Błąd podczas ładowania statystyk</div>';
        console.error('Stats error:', error);
    }

    closeSidebar();
}

function closeModal() {
    document.getElementById('statsModal').classList.remove('active');
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
}

let currentTheme = 'dark';
function toggleTheme() {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.body.classList.toggle('light-theme');
    
    const btn = event.target.closest('.sidebar-footer-btn');
    const span = btn.querySelector('span');
    span.textContent = currentTheme === 'dark' ? 'Jasny motyw' : 'Ciemny motyw';
}

// Close modal on outside click
document.getElementById('statsModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// Initial focus
messageInput.focus();

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K = Nowy chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        newChat();
    }
    
    // Escape = Zamknij modal
    if (e.key === 'Escape') {
        closeModal();
        closeSidebar();
    }
});

// Add slide animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideOutDown {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(20px);
        }
    }
`;
document.head.appendChild(style);
