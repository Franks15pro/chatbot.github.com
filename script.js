const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const typingIndicator = document.getElementById('typingIndicator');

// Dodaj wiadomość do chatu
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = isUser ? '👤' : '🤖';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = `<p>${text}</p>`;
    
    const time = document.createElement('span');
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

// Pokazuj "pisze..."
function showTyping() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

function hideTyping() {
    typingIndicator.style.display = 'none';
}

// Przewiń na dół
function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

// Wyślij wiadomość
async function sendMessage(event) {
    event.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Dodaj wiadomość użytkownika
    addMessage(message, true);
    messageInput.value = '';
    
    // Pokaż "pisze..."
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
        
        // Symuluj opóźnienie (bardziej naturalne)
        setTimeout(() => {
            hideTyping();
            addMessage(data.response);
        }, 500 + Math.random() * 1000);
        
    } catch (error) {
        hideTyping();
        addMessage('Przepraszam, wystąpił błąd 😔 Spróbuj ponownie!');
        console.error('Error:', error);
    }
}

// Szybkie odpowiedzi
function quickReply(text) {
    messageInput.value = text;
    messageInput.focus();
    sendMessage(new Event('submit'));
}

// Wyczyść chat
function clearChat() {
    if (confirm('Czy na pewno chcesz wyczyścić historię czatu?')) {
        chatMessages.innerHTML = '';
        addMessage('Chat został wyczyszczony! W czym mogę pomóc? 😊');
    }
}

// Auto-focus na input
messageInput.focus();

// Enter wysyła wiadomość
document.getElementById('chatForm').addEventListener('submit', sendMessage);