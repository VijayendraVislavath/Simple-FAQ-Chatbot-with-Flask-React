import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // Ref for scrolling to bottom of chat
  const messagesEndRef = useRef(null);

  // Ref for input field autofocus
  const inputRef = useRef(null);

  // Dark mode state
  const [darkMode, setDarkMode] = useState(false);

  // Toggle dark mode on/off
  const toggleDarkMode = () => setDarkMode(prev => !prev);

  // Scroll to bottom function
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Run scrollToBottom every time messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Send user message to backend and get bot response
  const sendMessage = async () => {
    if (!input) return;

    // Add user message to chat
    setMessages(prev => [...prev, { sender: 'user', text: input }]);
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
      });

      const data = await res.json();

      // Add bot's reply to chat
      setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);
    } catch (err) {
      console.error("Error calling API:", err);
      setMessages(prev => [
        ...prev,
        { sender: 'bot', text: "Sorry, the server is taking too long or is offline. Please try again later." }
      ]);
    }

    setLoading(false);
    setInput("");
    inputRef.current?.focus();  // Autofocus input after sending message
  };

  // Send message on Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className={darkMode ? 'dark-mode' : ''}>
      <div className="chat-container">
        <h2 style={{ position: 'relative' }}>
          FAQ Chatbot
          <button
            onClick={toggleDarkMode}
            style={{
              position: 'absolute',
              top: '10px',
              right: '10px',
              padding: '6px 10px',
              border: 'none',
              borderRadius: '4px',
              background: darkMode ? '#444' : '#2196F3',
              color: '#fff',
              cursor: 'pointer'
            }}
          >
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
        </h2>

        <ul className="message-list">
          {messages.map((msg, idx) => (
            <li key={idx} className={msg.sender === 'user' ? 'message user' : 'message bot'}>
              {msg.text}
            </li>
          ))}
          {/* Scroll anchor inside scrollable message list */}
          <div ref={messagesEndRef} />
        </ul>

        {loading && <div className="loading-indicator">Thinking...</div>}

        <div className="input-area">
          <input
            ref={inputRef}
            type="text"
            placeholder="Type your question..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
