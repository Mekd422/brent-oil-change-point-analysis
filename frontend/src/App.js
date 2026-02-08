import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function App() {
  const [prices, setPrices] = useState([]);
  const [events, setEvents] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [eventImpact, setEventImpact] = useState(null);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    category: '',
    impactLevel: ''
  });
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [categories, setCategories] = useState({ categories: [], impact_levels: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDateRange();
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchDateRange = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/date-range`);
      setDateRange({
        start: response.data.start_date,
        end: response.data.end_date
      });
      setFilters(prev => ({
        ...prev,
        startDate: prev.startDate || response.data.start_date,
        endDate: prev.endDate || response.data.end_date
      }));
    } catch (error) {
      console.error('Error fetching date range:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [pricesRes, eventsRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/prices`, {
          params: {
            start_date: filters.startDate,
            end_date: filters.endDate
          }
        }),
        axios.get(`${API_BASE_URL}/events`, {
          params: {
            category: filters.category || undefined,
            impact_level: filters.impactLevel || undefined,
            start_date: filters.startDate,
            end_date: filters.endDate
          }
        }),
        axios.get(`${API_BASE_URL}/statistics`, {
          params: {
            start_date: filters.startDate,
            end_date: filters.endDate
          }
        })
      ]);

      // Combine prices and dates
      const priceData = pricesRes.data.dates.map((date, idx) => ({
        date,
        price: pricesRes.data.prices[idx]
      }));

      setPrices(priceData);
      setEvents(eventsRes.data.events);
      setStatistics(statsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEventClick = async (event) => {
    setSelectedEvent(event);
    try {
      const response = await axios.get(`${API_BASE_URL}/event-impact`, {
        params: {
          event_date: event.date,
          window_days: 30
        }
      });
      setEventImpact(response.data);
    } catch (error) {
      console.error('Error fetching event impact:', error);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // Prepare chart data with event markers
  const chartData = prices.map(pricePoint => {
    const pointEvents = events.filter(e => e.date === pricePoint.date);
    return {
      ...pricePoint,
      events: pointEvents.length > 0 ? pointEvents.map(e => e.event).join(', ') : null
    };
  });

  return (
    <div className="App">
      <header className="App-header">
        <h1>Brent Oil Price Change Point Analysis</h1>
        <p>Analyzing the impact of geopolitical and economic events on oil prices</p>
      </header>

      <div className="container">
        {/* Filters Section */}
        <div className="filters-section">
          <h2>Filters</h2>
          <div className="filters-grid">
            <div className="filter-group">
              <label>Start Date:</label>
              <input
                type="date"
                value={filters.startDate}
                onChange={(e) => handleFilterChange('startDate', e.target.value)}
                min={dateRange.start}
                max={dateRange.end}
              />
            </div>
            <div className="filter-group">
              <label>End Date:</label>
              <input
                type="date"
                value={filters.endDate}
                onChange={(e) => handleFilterChange('endDate', e.target.value)}
                min={dateRange.start}
                max={dateRange.end}
              />
            </div>
            <div className="filter-group">
              <label>Category:</label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
              >
                <option value="">All Categories</option>
                {categories.categories?.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            <div className="filter-group">
              <label>Impact Level:</label>
              <select
                value={filters.impactLevel}
                onChange={(e) => handleFilterChange('impactLevel', e.target.value)}
              >
                <option value="">All Levels</option>
                {categories.impact_levels?.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Statistics Section */}
        {statistics && (
          <div className="statistics-section">
            <h2>Statistics</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">Mean Price</div>
                <div className="stat-value">${statistics.mean.toFixed(2)}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Median Price</div>
                <div className="stat-value">${statistics.median.toFixed(2)}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Volatility (Annualized)</div>
                <div className="stat-value">{(statistics.volatility * 100).toFixed(2)}%</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Min Price</div>
                <div className="stat-value">${statistics.min.toFixed(2)}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Max Price</div>
                <div className="stat-value">${statistics.max.toFixed(2)}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Data Points</div>
                <div className="stat-value">{statistics.count.toLocaleString()}</div>
              </div>
            </div>
          </div>
        )}

        {/* Main Chart */}
        <div className="chart-section">
          <h2>Historical Brent Oil Prices</h2>
          {loading ? (
            <div className="loading">Loading data...</div>
          ) : (
            <ResponsiveContainer width="100%" height={500}>
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis
                  label={{ value: 'Price (USD/barrel)', angle: -90, position: 'insideLeft' }}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                  formatter={(value) => [`$${value.toFixed(2)}`, 'Price']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#8884d8"
                  strokeWidth={2}
                  dot={false}
                  name="Brent Oil Price"
                />
                {events.map((event, idx) => (
                  <ReferenceLine
                    key={idx}
                    x={event.date}
                    stroke="#ff7300"
                    strokeDasharray="3 3"
                    label={{ value: event.event, position: 'top', angle: -90 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Events List */}
        <div className="events-section">
          <h2>Key Events ({events.length})</h2>
          <div className="events-list">
            {events.map((event, idx) => (
              <div
                key={idx}
                className={`event-card ${selectedEvent?.date === event.date ? 'selected' : ''}`}
                onClick={() => handleEventClick(event)}
              >
                <div className="event-header">
                  <span className="event-date">{event.date}</span>
                  <span className={`event-category ${event.category.toLowerCase()}`}>
                    {event.category}
                  </span>
                  <span className={`event-impact ${event.impact_level.toLowerCase()}`}>
                    {event.impact_level}
                  </span>
                </div>
                <div className="event-title">{event.event}</div>
                <div className="event-description">{event.description}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Event Impact Analysis */}
        {selectedEvent && eventImpact && (
          <div className="impact-section">
            <h2>Impact Analysis: {selectedEvent.event}</h2>
            {eventImpact.impact ? (
              <div>
                <div className="impact-stats">
                  <div className="impact-stat">
                    <div className="impact-label">Price Before</div>
                    <div className="impact-value">${eventImpact.impact.price_before.toFixed(2)}</div>
                  </div>
                  <div className="impact-stat">
                    <div className="impact-label">Price After</div>
                    <div className="impact-value">${eventImpact.impact.price_after.toFixed(2)}</div>
                  </div>
                  <div className="impact-stat">
                    <div className="impact-label">Absolute Change</div>
                    <div className={`impact-value ${eventImpact.impact.absolute_change >= 0 ? 'positive' : 'negative'}`}>
                      ${eventImpact.impact.absolute_change.toFixed(2)}
                    </div>
                  </div>
                  <div className="impact-stat">
                    <div className="impact-label">Percentage Change</div>
                    <div className={`impact-value ${eventImpact.impact.percentage_change >= 0 ? 'positive' : 'negative'}`}>
                      {eventImpact.impact.percentage_change.toFixed(2)}%
                    </div>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={eventImpact.prices.map((p, i) => ({ date: eventImpact.dates[i], price: p }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="price" stroke="#8884d8" name="Price" />
                    <ReferenceLine
                      x={eventImpact.event_date}
                      stroke="red"
                      strokeDasharray="3 3"
                      label={{ value: 'Event Date', position: 'top' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div>Insufficient data to calculate impact for this event.</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
