import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Send a message to the weather assistant
 * @param {string} message - The user's message (city name or question)
 * @returns {Promise<Object>} - The response from the API
 */
export const sendMessage = async (message) => {
  try {
    const response = await api.post('/chat', { message })
    return response.data
  } catch (error) {
    if (error.response) {
      // API returned an error
      throw new Error(error.response.data.detail || 'API error')
    } else if (error.request) {
      // Request was made but no response
      throw new Error('No response from server. Is the backend running?')
    } else {
      // Error in request setup
      throw new Error(error.message)
    }
  }
}

/**
 * Health check - verify backend is running
 * @returns {Promise<Object>} - Health status
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    throw new Error('Backend server is not running')
  }
}

export default api
