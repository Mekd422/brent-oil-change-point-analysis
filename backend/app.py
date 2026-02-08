"""
Flask backend API for Brent Oil Change Point Analysis Dashboard
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Load data
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_data():
    """Load price and event data."""
    prices_df = pd.read_csv(os.path.join(DATA_DIR, 'brent_prices.csv'))
    prices_df['Date'] = pd.to_datetime(prices_df['Date'], format='%d-%b-%y')
    prices_df = prices_df.sort_values('Date').reset_index(drop=True)
    
    events_df = pd.read_csv(os.path.join(DATA_DIR, 'events.csv'))
    events_df['Date'] = pd.to_datetime(events_df['Date'])
    events_df = events_df.sort_values('Date').reset_index(drop=True)
    
    return prices_df, events_df

# Load data once at startup
prices_df, events_df = load_data()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Get historical price data with optional date filtering."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    df = prices_df.copy()
    
    if start_date:
        df = df[df['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Date'] <= pd.to_datetime(end_date)]
    
    # Convert to JSON-friendly format
    data = {
        'dates': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'prices': df['Price'].tolist()
    }
    
    return jsonify(data)

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get event data with optional filtering."""
    category = request.args.get('category')
    impact_level = request.args.get('impact_level')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    df = events_df.copy()
    
    if category:
        df = df[df['Category'] == category]
    if impact_level:
        df = df[df['Impact_Level'] == impact_level]
    if start_date:
        df = df[df['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Date'] <= pd.to_datetime(end_date)]
    
    # Convert to JSON-friendly format
    events = []
    for _, row in df.iterrows():
        events.append({
            'date': row['Date'].strftime('%Y-%m-%d'),
            'event': row['Event'],
            'description': row['Description'],
            'category': row['Category'],
            'impact_level': row['Impact_Level']
        })
    
    return jsonify({'events': events})

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get summary statistics for the price data."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    df = prices_df.copy()
    
    if start_date:
        df = df[df['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Date'] <= pd.to_datetime(end_date)]
    
    # Calculate statistics
    stats = {
        'mean': float(df['Price'].mean()),
        'median': float(df['Price'].median()),
        'std': float(df['Price'].std()),
        'min': float(df['Price'].min()),
        'max': float(df['Price'].max()),
        'count': int(len(df))
    }
    
    # Calculate log returns statistics
    df['Log_Returns'] = np.log(df['Price']).diff()
    df = df.dropna()
    
    stats['volatility'] = float(df['Log_Returns'].std() * np.sqrt(252))  # Annualized
    
    return jsonify(stats)

@app.route('/api/event-impact', methods=['GET'])
def get_event_impact():
    """Get price impact around specific events."""
    event_date_str = request.args.get('event_date')
    window_days = int(request.args.get('window_days', 30))
    
    if not event_date_str:
        return jsonify({'error': 'event_date parameter required'}), 400
    
    event_date = pd.to_datetime(event_date_str)
    
    # Find price data around the event
    start_date = event_date - pd.Timedelta(days=window_days)
    end_date = event_date + pd.Timedelta(days=window_days)
    
    df = prices_df[
        (prices_df['Date'] >= start_date) & 
        (prices_df['Date'] <= end_date)
    ].copy()
    
    # Calculate price change
    if len(df) > 0:
        price_before = df[df['Date'] < event_date]['Price'].mean() if len(df[df['Date'] < event_date]) > 0 else None
        price_after = df[df['Date'] > event_date]['Price'].mean() if len(df[df['Date'] > event_date]) > 0 else None
        
        impact = None
        if price_before and price_after:
            impact = {
                'price_before': float(price_before),
                'price_after': float(price_after),
                'absolute_change': float(price_after - price_before),
                'percentage_change': float(((price_after - price_before) / price_before) * 100)
            }
    else:
        impact = None
    
    # Convert to JSON-friendly format
    data = {
        'dates': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'prices': df['Price'].tolist(),
        'event_date': event_date.strftime('%Y-%m-%d'),
        'impact': impact
    }
    
    return jsonify(data)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get list of event categories."""
    categories = events_df['Category'].unique().tolist()
    impact_levels = events_df['Impact_Level'].unique().tolist()
    
    return jsonify({
        'categories': categories,
        'impact_levels': impact_levels
    })

@app.route('/api/date-range', methods=['GET'])
def get_date_range():
    """Get the available date range in the dataset."""
    return jsonify({
        'start_date': prices_df['Date'].min().strftime('%Y-%m-%d'),
        'end_date': prices_df['Date'].max().strftime('%Y-%m-%d')
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
