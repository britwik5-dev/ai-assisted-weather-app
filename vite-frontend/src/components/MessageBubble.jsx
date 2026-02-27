import React from 'react'
import '../styles/MessageBubble.css'

/**
 * MessageBubble - Individual message component
 */
export function MessageBubble({ message, isUser }) {
  return (
    <div className={`message-bubble ${isUser ? 'user' : 'bot'}`}>
      <div className="message-content">
        {message}
      </div>
    </div>
  )
}

export default MessageBubble
