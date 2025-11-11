const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const typingIndicator = document.getElementById('typingIndicator');
const chatForm = document.getElementById('chatForm');

let isFirstMessage = true;

function addMessage(text, isUser = false) {
    if (isFirstMessage) {
        chatMessages.innerHTML = '';
        isFirstMessage = false;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    
    if (isUser) {
        avatar.innerHTML = `
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
                <circle cx="18" cy="18" r="18" fill="url(#userGradient)"/>
                <path d="M18 18c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="white"/>
                <defs>
                    <linearGradient id="userGradient" x1="0" y1="0" x2="36" y2="36">
                        <stop offset="0%" stop-color="#667eea"/>
                        <stop offset="100%" stop-color="#764ba2"/>
                    </linearGradient>
                </defs>
            </svg>
        `;
    } else {
        avatar.innerHTML = `
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
                <circle cx="18" cy="18" r="18" fill="#f0f0f0"/>
                <path d="M18 9L22.5 13.5H20.25V18H22.5L18 22.5L13.5 18H15.75V13.5H13.5L18 9Z" fill="#667eea"/>
            </svg>
        `;
    }
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('pl-PL', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    content.appendChild(bubble);
    content.appendChild(time);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function showTyping() {
    typingIndicator.style.display = 'block';
    scrollToBottom();
}

function hideTyping() {
    typingIndicator.style.display = 'none';
}

function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

async function sendMessage(event) {
    event.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    addMessage(message, true);
    messageInput.value = '';
    
    showTyping();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        setTimeout(() => {
            hideTyping();
            addMessage(data.response);
        }, 800 + Math.random() * 700);
        
    } catch (error) {
        hideTyping();
        addMessage('Przepraszam, wystąpił błąd. Spróbuj ponownie.');
        console.error('Error:', error);
    }
}

function quickReply(text) {
    messageInput.value = text;
    messageInput.focus();
    const submitEvent = new Event('submit', { cancelable: true });
    chatForm.dispatchEvent(submitEvent);
    sendMessage(submitEvent);
}

function clearChat() {
    if (confirm('Czy na pewno chcesz wyczyścić historię czatu?')) {
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                        <rect width="64" height="64" rx="16" fill="url(#gradient2)"/>
                        <path d="M32 16L40 24H36V32H40L32 40L24 32H28V24H24L32 16Z" fill="white" opacity="0.9"/>
                        <defs>
                            <linearGradient id="gradient2" x1="0" y1="0" x2="64" y2="64">
                                <stop offset="0%" stop-color="#667eea"/>
                                <stop offset="100%" stop-color="#764ba2"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <h2>Witaj w AI Assistant</h2>
                <p>Jestem tutaj, aby Ci pomóc. Zadaj mi pytanie lub wybierz jedną z sugestii poniżej.</p>
            </div>
        `;
        isFirstMessage = true;
    }
}

function newChat() {
    clearChat();
}

function toggleSettings() {
    alert('Funkcja ustawień będzie dostępna wkrótce!');
}

messageInput.focus();

chatForm.addEventListener('submit', sendMessage);
