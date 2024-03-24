// script.js

const socket = io();

socket.on('message', (message) => {
    const chatMessages = document.getElementById('chatMessages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.innerHTML = `<span class="sender">[${message.sender}]</span> ${message.content}`;
    chatMessages.appendChild(messageElement);

    // Scroll to bottom of chat box
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (message !== '') {
        socket.emit('message', message);
        messageInput.value = '';
    }
}
