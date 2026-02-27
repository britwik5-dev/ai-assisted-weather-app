import React from 'react'
import '../styles/WeatherCard.css'

/**
 * WeatherCard - Displays weather data in a card format
 */
export function WeatherCard({ data }) {
  return (
    <div className="weather-card">
      <div className="weather-header">
        <h2 className="location">
          📍 {data.city}, {data.country}
        </h2>
      </div>

      <div className="weather-main">
        <div className="temperature">
          <span className="temp-value">{Math.round(data.temperature)}°</span>
          <span className="temp-unit">C</span>
        </div>
        <div className="description">
          {data.description}
        </div>
      </div>

      <div className="weather-details">
        <div className="detail-item">
          <span className="detail-icon">🌤️</span>
          <span className="detail-label">Feels Like</span>
          <span className="detail-value">{Math.round(data.feels_like)}°C</span>
        </div>

        <div className="detail-item">
          <span className="detail-icon">💧</span>
          <span className="detail-label">Humidity</span>
          <span className="detail-value">{data.humidity}%</span>
        </div>

        <div className="detail-item">
          <span className="detail-icon">💨</span>
          <span className="detail-label">Wind Speed</span>
          <span className="detail-value">{data.wind_speed} m/s</span>
        </div>
      </div>

      {data.recommendation && (
        <div className="weather-insight">
          <h3>💡 Recommendation</h3>
          <p>{data.recommendation}</p>
        </div>
      )}

      {data.insights && (
        <div className="weather-insight">
          <h3>🔍 Insights</h3>
          <p>{data.insights}</p>
        </div>
      )}
    </div>
  )
}

export default WeatherCard
