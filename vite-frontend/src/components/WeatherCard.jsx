import React, { useState } from 'react'
import '../styles/WeatherCard.css'


const getWeatherIcon = (description) => {
  if (!description) return '🌡️'
  const d = description.toLowerCase()
  if (d.includes('clear') || d.includes('sunny')) return '☀️'
  if (d.includes('cloud')) return '☁️'
  if (d.includes('rain') || d.includes('drizzle')) return '🌧️'
  if (d.includes('thunder') || d.includes('storm')) return '⛈️'
  if (d.includes('snow')) return '❄️'
  if (d.includes('mist') || d.includes('fog') || d.includes('haze')) return '🌫️'
  if (d.includes('wind')) return '💨'
  return '🌤️'
}

const getHumidityLabel = (h) => {
  if (h < 30) return 'Dry'
  if (h < 60) return 'Comfortable'
  if (h < 80) return 'Humid'
  return 'Very Humid'
}

const getWindLabel = (w) => {
  if (w < 2) return 'Calm'
  if (w < 6) return 'Light Breeze'
  if (w < 12) return 'Moderate'
  return 'Strong'
}

export function WeatherCard({ data }) {
  const [insightsOpen, setInsightsOpen] = useState(false)
  const icon = getWeatherIcon(data.description)
  const temp = Math.round(data.temperature)
  const feelsLike = Math.round(data.feels_like)

  return (
    <div className="wcard">
      

      {/* Top header strip */}
      <div className="wcard-header">
        <div className="wcard-location">
          <span className="wcard-pin">📍</span>
          <div>
            <span className="wcard-city">{data.city}</span>
            <span className="wcard-country">{data.country}</span>
          </div>
        </div>
        <div className="wcard-icon-wrap">
          <span className="wcard-main-icon">{icon}</span>
        </div>
      </div>

      {/* Temperature hero */}
      <div className="wcard-temp-section">
        <div className="wcard-temp">
          <span className="wcard-temp-num">{temp}</span>
          <span className="wcard-temp-unit">°C</span>
        </div>
        <div className="wcard-desc-wrap">
          <span className="wcard-description">{data.description}</span>
          <span className="wcard-feels">Feels like {feelsLike}°C</span>
        </div>
      </div>

      {/* Metrics row */}
      <div className="wcard-metrics">
        <div className="wcard-metric">
          <div className="metric-icon">💧</div>
          <div className="metric-info">
            <span className="metric-value">{data.humidity}%</span>
            <span className="metric-label">Humidity</span>
            <span className="metric-sub">{getHumidityLabel(data.humidity)}</span>
          </div>
        </div>
        <div className="wcard-metric-divider" />
        <div className="wcard-metric">
          <div className="metric-icon">💨</div>
          <div className="metric-info">
            <span className="metric-value">{data.wind_speed} <small>m/s</small></span>
            <span className="metric-label">Wind</span>
            <span className="metric-sub">{getWindLabel(data.wind_speed)}</span>
          </div>
        </div>
        <div className="wcard-metric-divider" />
        <div className="wcard-metric">
          <div className="metric-icon">🌡️</div>
          <div className="metric-info">
            <span className="metric-value">{feelsLike}°C</span>
            <span className="metric-label">Feels Like</span>
            <span className="metric-sub">{temp > feelsLike ? 'Cooler than actual' : temp < feelsLike ? 'Warmer than actual' : 'Matches actual'}</span>
          </div>
        </div>
      </div>

      {/* Recommendation panel */}
      {data.recommendation && (
        <div className="wcard-recommendation">
          <div className="rec-header">
            <span className="rec-icon">💡</span>
            <span className="rec-title">AI Recommendation</span>
          </div>
          <p className="rec-text">{data.recommendation}</p>
        </div>
      )}

      {/* Insights expandable */}
      {data.insights && (
        <div className={`wcard-insights ${insightsOpen ? 'open' : ''}`}>
          <button
            className="insights-toggle"
            onClick={() => setInsightsOpen(!insightsOpen)}
          >
            <span className="insights-toggle-left">
              <span className="insights-icon">🔍</span>
              <span>Detailed Insights</span>
            </span>
            <span className={`insights-chevron ${insightsOpen ? 'rotated' : ''}`}>
              ▾
            </span>
          </button>
          <div className="insights-body">
            <p className="insights-text">{data.insights}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default WeatherCard