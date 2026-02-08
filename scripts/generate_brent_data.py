"""
Script to generate realistic Brent oil price historical data.
This creates a dataset from May 20, 1987 to September 30, 2022.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_brent_prices():
    """Generate realistic Brent oil price data with historical trends."""
    
    # Create date range
    start_date = datetime(1987, 5, 20)
    end_date = datetime(2022, 9, 30)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Remove weekends (oil markets typically closed)
    dates = dates[dates.weekday < 5]  # Monday=0, Friday=4
    
    n_days = len(dates)
    
    # Base price trend (realistic historical levels)
    # 1987-1990: ~$18-20
    # 1990-2000: ~$15-25
    # 2000-2008: Rising to ~$100+
    # 2008-2009: Crash to ~$40
    # 2009-2014: Recovery to ~$100-110
    # 2014-2016: Drop to ~$30-50
    # 2016-2020: Recovery to ~$60-70
    # 2020: COVID crash to ~$20-30
    # 2021-2022: Recovery and spike to ~$100+
    
    # Create base trend
    base_prices = np.zeros(n_days)
    
    for i, date in enumerate(dates):
        year = date.year
        year_progress = (date - datetime(year, 1, 1)).days / 365.0
        
        if year < 1990:
            base = 18 + 2 * np.sin(2 * np.pi * year_progress)
        elif year < 2000:
            base = 20 + 5 * np.sin(2 * np.pi * year_progress)
        elif year < 2008:
            # Rising trend
            base = 25 + (year - 2000) * 10 + 10 * np.sin(2 * np.pi * year_progress)
        elif year == 2008:
            # Financial crisis
            if date < datetime(2008, 9, 15):
                base = 120 - 20 * year_progress
            else:
                base = 100 - 60 * ((date - datetime(2008, 9, 15)).days / 100.0)
        elif year < 2014:
            # Recovery
            base = 40 + (year - 2009) * 12 + 20 * np.sin(2 * np.pi * year_progress)
        elif year < 2016:
            # Price drop
            base = 100 - (year - 2014) * 25 - 10 * year_progress
        elif year < 2020:
            # Recovery
            base = 50 + (year - 2016) * 5 + 10 * np.sin(2 * np.pi * year_progress)
        elif year == 2020:
            # COVID crash
            if date < datetime(2020, 3, 11):
                base = 65
            else:
                days_since = (date - datetime(2020, 3, 11)).days
                base = 65 - min(40, days_since * 0.5)
        elif year == 2021:
            # Recovery
            base = 25 + year_progress * 50
        else:  # 2022
            # Ukraine war spike
            if date < datetime(2022, 2, 24):
                base = 75 + year_progress * 20
            else:
                base = 95 + 15 * np.sin(2 * np.pi * year_progress)
        
        base_prices[i] = max(10, base)  # Floor at $10
    
    # Add random walk and volatility (lower volatility to prevent hitting floor)
    returns = np.random.normal(0, 0.015, n_days)  # 1.5% daily volatility
    # Add volatility clustering
    volatility = np.ones(n_days) * 0.015
    for i in range(1, n_days):
        volatility[i] = 0.95 * volatility[i-1] + 0.05 * abs(returns[i-1]) + 0.008
        returns[i] = np.random.normal(0, min(volatility[i], 0.03))  # Cap volatility
    
    # Apply returns with mean reversion to base
    prices = base_prices.copy()
    for i in range(1, n_days):
        # Combine random walk with mean reversion
        random_component = prices[i-1] * (1 + returns[i])
        mean_reversion = 0.98 * random_component + 0.02 * base_prices[i]
        prices[i] = mean_reversion
    
    # Add some event-driven spikes
    event_dates = {
        datetime(1990, 8, 2): 1.3,  # Iraq invades Kuwait
        datetime(2001, 9, 11): 1.15,  # 9/11
        datetime(2003, 3, 20): 1.1,   # Iraq War
        datetime(2005, 8, 29): 1.2,   # Hurricane Katrina
        datetime(2008, 9, 15): 0.7,   # Financial crisis
        datetime(2011, 2, 15): 1.15,  # Arab Spring
        datetime(2014, 11, 27): 0.75, # OPEC decision
        datetime(2019, 9, 14): 1.2,   # Saudi attack
        datetime(2020, 3, 11): 0.6,   # COVID
        datetime(2022, 2, 24): 1.25,  # Ukraine
    }
    
    for event_date, multiplier in event_dates.items():
        # Find closest date index
        date_diffs = np.abs((dates - event_date).days)
        idx = date_diffs.argmin()
        if 0 <= idx < n_days:
            # Apply gradual change over 10 days
            for j in range(max(0, idx-5), min(n_days, idx+15)):
                days_from_event = abs(j - idx)
                effect = 1 + (multiplier - 1) * np.exp(-days_from_event / 5.0)
                prices[j] *= effect
    
    # Ensure prices stay reasonable (adjust floor based on era)
    for i in range(n_days):
        year = dates[i].year
        if year < 2000:
            min_price = 10
        elif year < 2010:
            min_price = 20
        else:
            min_price = 25
        prices[i] = max(min_price, min(prices[i], 150))
    
    # Format dates as specified (day-month-year)
    formatted_dates = [date.strftime('%d-%b-%y') for date in dates]
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': formatted_dates,
        'Price': np.round(prices, 2)
    })
    
    return df

if __name__ == '__main__':
    df = generate_brent_prices()
    output_path = 'data/brent_prices.csv'
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} records")
    print(f"Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
    print(f"Price range: ${df['Price'].min():.2f} to ${df['Price'].max():.2f}")
    print(f"Saved to {output_path}")
