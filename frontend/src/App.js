// frontend/src/App.js
import React, { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);   // Chat history
  const [input, setInput] = useState("");         // Current user input

  // Send message to backend when user hits Send or Enter
  const sendMessage = async () => {
    if (!input) return;
    // Add user's message to chat
    setMessages(prev => [...prev, { sender: 'user', text: input }]);
    try {
      // Call backend /chat endpoint
      const res = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      // Append bot's reply
      setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);
    } catch (err) {
      console.error("Error calling API:", err);
      setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, an error occurred." }]);
    }
    setInput(""); // clear input field
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="chat-container">
      <h2>FAQ Chatbot</h2>
      <ul className="message-list">
        {messages.map((msg, idx) => (
          <li key={idx} className={msg.sender === 'user' ? 'message user' : 'message bot'}>
            {msg.text}
          </li>
        ))}
      </ul>
      <div className="input-area">
        <input
          type="text"
          placeholder="Type your question..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;

