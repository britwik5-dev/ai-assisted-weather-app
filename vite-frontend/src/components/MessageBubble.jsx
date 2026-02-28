import React from 'react'
import '../styles/MessageBubble.css'

export function MessageBubble({ message, isUser, isError }) {
  return (
    <div className={`bubble-wrap ${isUser ? 'user' : 'bot'}`}>
      {!isUser && (
        <div className={`bubble-avatar ${isError ? 'error-avatar' : ''}`}>
          {isError ? '⚠' : '⛅'}
        </div>
      )}
      <div className={`bubble ${isUser ? 'bubble-user' : isError ? 'bubble-error' : 'bubble-bot'}`}>
        <p className="bubble-text">{message}</p>
      </div>
      {isUser && (
        <div className="bubble-avatar user-avatar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
          </svg>
        </div>
      )}
    </div>
  )
}

export default MessageBubble