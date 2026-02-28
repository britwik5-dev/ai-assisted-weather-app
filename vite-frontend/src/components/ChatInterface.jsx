import React, { useState, useEffect, useRef } from 'react'
import { sendMessage, healthCheck } from '../api'
import MessageBubble from './MessageBubble'
import WeatherCard from './WeatherCard'
import '../styles/ChatInterface.css'

export function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [backendReady, setBackendReady] = useState(false)
  const [inputFocused, setInputFocused] = useState(false)

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    const checkBackend = async () => {
      try {
        await healthCheck()
        setBackendReady(true)
        setError(null)
      } catch (err) {
        setBackendReady(false)
        setError('Backend is not running. Please start the FastAPI server.')
      }
    }
    checkBackend()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!backendReady) {
      setError('Backend is not running. Please start the FastAPI server.')
      return
    }
    const trimmedInput = inputValue.trim()
    if (!trimmedInput) return

    const userMessage = { id: Date.now(), type: 'user', content: trimmedInput }
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setLoading(true)
    setError(null)

    try {
      const response = await sendMessage(trimmedInput)

      if (response.error) {
        let friendlyError = response.error
        if (response.error.includes('429') || response.error.includes('quota') || response.error.includes('RESOURCE_EXHAUSTED')) {
          friendlyError = '⏳ Too many requests! The AI is taking a breather. Please wait 1-2 minutes and try again.'
        } else if (response.error.includes('not found') || response.error.includes('404')) {
          friendlyError = '🌍 City not found. Please check the spelling and try again.'
        } else if (response.error.includes('network') || response.error.includes('connection')) {
          friendlyError = '📡 Network error. Please check your internet connection.'
        }
        setMessages((prev) => [...prev, { id: Date.now() + 1, type: 'error', content: friendlyError }])
      } else if (response.bot_type === 'weather' && response.city) {
        setMessages((prev) => [...prev, { id: Date.now() + 1, type: 'weather', content: response }])
      } else if (response.bot_type === 'chat') {
        const chatContent = response.recommendation || response.insights || 'No response received.'
        setMessages((prev) => [...prev, { id: Date.now() + 1, type: 'bot', content: chatContent }])
      }
    } catch (err) {
      const msg = err.message || ''
      let friendlyError = '❌ Something went wrong. Please try again.'
      if (msg.includes('429') || msg.includes('quota') || msg.includes('RESOURCE_EXHAUSTED')) {
        friendlyError = '⏳ Too many requests! Please wait 1-2 minutes and try again.'
      } else if (msg.includes('not running') || msg.includes('Network')) {
        friendlyError = '📡 Cannot reach the server. Is the backend running?'
      }
      setError(null)
      setMessages((prev) => [...prev, { id: Date.now() + 1, type: 'error', content: friendlyError }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const suggestions = ['New York', 'Tokyo', 'London', 'Mumbai', 'Sydney']

  return (
    <div className="app-wrapper">
      {/* Ambient background orbs */}
      <div className="bg-orb orb-1" />
      <div className="bg-orb orb-2" />
      <div className="bg-orb orb-3" />
      <div className="bg-orb orb-4" />
      <div className="bg-orb orb-5" />
      <div className="bg-orb orb-6" />
      <div className="bg-orb orb-7" />
      <div className="bg-orb orb-8" />
      <div className="bg-orb orb-9" />

      {/* Navbar */}
      <nav className="navbar">
        <div className="nav-brand">
          <span className="nav-logo">⛅</span>
          <span className="nav-title">Atmos</span>
          <span className="nav-badge">AI</span>
        </div>
        <div className="nav-center">
          {messages.length > 0 && (
            <button className="home-btn" onClick={() => setMessages([])}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M3 12L12 3L21 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M9 21V12H15V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3 12H21" stroke="currentColor" strokeWidth="0" />
              </svg>
              Home
            </button>
          )}
        </div>
        <div className="nav-status">
          <span className={`status-dot ${backendReady ? 'online' : 'offline'}`} />
          <span className="status-label">{backendReady ? 'Connected' : 'Offline'}</span>
        </div>
      </nav>

      {/* Main layout */}
      <main className="main-layout">
        {/* Hero header — shown only when no messages */}
        {messages.length === 0 && (
          <div className="hero-section">
            <div className="hero-tag">Powered by Gemini AI</div>
            <h1 className="hero-title">
              <span className="hero-title-plain">Weather Intelligence,</span>
              <span className="hero-gradient">Reimagined</span>
            </h1>
            <p className="hero-subtitle">
              Ask for any city's forecast and get AI-powered insights, recommendations, and more.
            </p>
            <div className="suggestions-row">
              {suggestions.map((city) => (
                <button
                  key={city}
                  className="suggestion-chip"
                  onClick={() => {
                    setInputValue(city)
                    inputRef.current?.focus()
                  }}
                >
                  {city}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages feed */}
        {messages.length > 0 && (
          <div className="messages-feed">
            {messages.map((message, index) => (
              <div
                key={message.id}
                className={`message-row ${message.type}`}
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                {message.type === 'user' && (
                  <MessageBubble message={message.content} isUser={true} />
                )}
                {(message.type === 'bot' || message.type === 'error') && (
                  <MessageBubble message={message.content} isUser={false} isError={message.type === 'error'} />
                )}
                {message.type === 'weather' && (
                  <WeatherCard data={message.content} />
                )}
              </div>
            ))}

            {loading && (
              <div className="message-row bot">
                <div className="typing-indicator">
                  <div className="bot-avatar">⛅</div>
                  <div className="typing-dots">
                    <span /><span /><span />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Error banner */}
        {error && !messages.find(m => m.type === 'error') && (
          <div className="error-banner">
            <span className="error-icon">⚠</span>
            <span>{error}</span>
          </div>
        )}

        {/* Floating search */}
        <div className={`input-dock ${inputFocused || inputValue ? 'expanded' : ''}`}>
          <form className="input-form" onSubmit={handleSendMessage}>
            <div className="input-wrapper">
              <svg className="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none">
                <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2"/>
                <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <input
                ref={inputRef}
                type="text"
                className="chat-input"
                placeholder="Enter a city or ask anything..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onFocus={() => setInputFocused(true)}
                onBlur={() => setInputFocused(false)}
                disabled={loading || !backendReady}
              />
              {(inputFocused || inputValue) && (
                <button
                  type="submit"
                  className={`send-btn ${loading ? 'loading' : ''}`}
                  disabled={loading || !backendReady || !inputValue.trim()}
                >
                  {loading ? (
                    <span className="btn-spinner" />
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </button>
              )}
            </div>
          </form>
          {(inputFocused || inputValue) && (
            <p className="input-hint">Try: "Weather in Paris" or "Should I carry an umbrella in Delhi?"</p>
          )}
        </div>
      </main>
    </div>
  )
}

export default ChatInterface