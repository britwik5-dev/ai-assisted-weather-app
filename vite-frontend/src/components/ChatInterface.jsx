import React, { useState, useEffect, useRef } from 'react'
import { sendMessage, healthCheck } from '../api'
import MessageBubble from './MessageBubble'
import WeatherCard from './WeatherCard'
import '../styles/ChatInterface.css'

/**
 * ChatInterface - Main chat UI component
 */
export function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [backendReady, setBackendReady] = useState(false)
  
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Check if backend is running on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        await healthCheck()
        setBackendReady(true)
        setError(null)
      } catch (err) {
        setBackendReady(false)
        setError('❌ Backend is not running. Please start the FastAPI server.')
      }
    }
    
    checkBackend()
  }, [])

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus on input after sending
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSendMessage = async (e) => {
    e.preventDefault()

    if (!backendReady) {
      setError('❌ Backend is not running. Please start the FastAPI server.')
      return
    }

    const trimmedInput = inputValue.trim()
    if (!trimmedInput) return

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: trimmedInput,
    }
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setLoading(true)
    setError(null)

    try {
      // Send message to backend
      const response = await sendMessage(trimmedInput)

      if (response.error) {
        // Add error message
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            type: 'error',
            content: `❌ ${response.error}`,
          },
        ])
      } else if (response.bot_type === 'weather' && response.city) {
        // Add weather card
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            type: 'weather',
            content: response,
          },
        ])
      } else if (response.bot_type === 'chat' && response.insights) {
        // Add chat response
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            type: 'bot',
            content: response.insights,
          },
        ])
      }
    } catch (err) {
      // Add error message
      setError(err.message)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          type: 'error',
          content: `❌ ${err.message}`,
        },
      ])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>🌤️ Weather Assistant</h1>
        <p className="subtitle">Ask for weather or chat about anything</p>
        {!backendReady && (
          <div className="backend-warning">
            ⚠️ Backend not connected - Start the FastAPI server
          </div>
        )}
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🌍</div>
            <h2>Welcome to Weather Assistant!</h2>
            <p>Type a city name to get current weather and recommendations</p>
            <p className="hint">Example: "London", "New York", "Tokyo"</p>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message-container ${message.type}`}>
            {message.type === 'user' && (
              <MessageBubble message={message.content} isUser={true} />
            )}
            {message.type === 'bot' && (
              <MessageBubble message={message.content} isUser={false} />
            )}
            {message.type === 'error' && (
              <MessageBubble message={message.content} isUser={false} />
            )}
            {message.type === 'weather' && (
              <WeatherCard data={message.content} />
            )}
          </div>
        ))}

        {loading && (
          <div className="message-container bot">
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Thinking...</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          ref={inputRef}
          type="text"
          className="chat-input"
          placeholder="Type a city name or ask a question..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={loading || !backendReady}
          autoFocus
        />
        <button
          type="submit"
          className="send-button"
          disabled={loading || !backendReady || !inputValue.trim()}
        >
          {loading ? '⏳' : '📤'}
        </button>
      </form>
    </div>
  )
}

export default ChatInterface
