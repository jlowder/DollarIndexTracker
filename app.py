import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="U.S. Dollar Index (DXY) Interactive Chart",
    page_icon="💲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("💲 U.S. Dollar Index (DXY) Interactive Chart")
st.markdown("""
The U.S. Dollar Index (DXY) measures the value of the United States dollar relative to a basket of foreign currencies.
This interactive chart allows you to explore historical DXY data with zoom and pan functionality.
""")

@st.cache_data
def get_presidential_data():
    """
    Get US Presidential terms data with party affiliations
    """
    presidents = [
        {"name": "Jimmy Carter", "party": "Democrat", "start": "1977-01-20", "end": "1981-01-20"},
        {"name": "Ronald Reagan", "party": "Republican", "start": "1981-01-20", "end": "1989-01-20"},
        {"name": "George H.W. Bush", "party": "Republican", "start": "1989-01-20", "end": "1993-01-20"},
        {"name": "Bill Clinton", "party": "Democrat", "start": "1993-01-20", "end": "2001-01-20"},
        {"name": "George W. Bush", "party": "Republican", "start": "2001-01-20", "end": "2009-01-20"},
        {"name": "Barack Obama", "party": "Democrat", "start": "2009-01-20", "end": "2017-01-20"},
        {"name": "Donald Trump", "party": "Republican", "start": "2017-01-20", "end": "2021-01-20"},
        {"name": "Joe Biden", "party": "Democrat", "start": "2021-01-20", "end": "2025-01-20"},
        {"name": "Donald Trump", "party": "Republican", "start": "2025-01-20", "end": "2029-01-20"},  # Second term
    ]
    
    df = pd.DataFrame(presidents)
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])
    
    return df

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_dxy_data(period="5y"):
    """
    Fetch U.S. Dollar Index data from Yahoo Finance
    """
    try:
        # DXY is the symbol for U.S. Dollar Index
        ticker = yf.Ticker("DX-Y.NYB")
        
        # Fetch historical data
        hist = ticker.history(period=period)
        
        if hist.empty:
            return None, "No data available for the selected period"
        
        # Get current info
        info = ticker.info
        
        return hist, info
    except Exception as e:
        return None, f"Error fetching data: {str(e)}"

def calculate_statistics(data):
    """
    Calculate basic statistics for the dollar index data
    """
    if data is None or data.empty:
        return None
    
    current_price = data['Close'].iloc[-1]
    previous_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
    daily_change = current_price - previous_price
    daily_change_pct = (daily_change / previous_price) * 100 if previous_price != 0 else 0
    
    stats = {
        'current_price': current_price,
        'daily_change': daily_change,
        'daily_change_pct': daily_change_pct,
        'high_52w': data['High'].max(),
        'low_52w': data['Low'].min(),
        'avg_volume': data['Volume'].mean() if 'Volume' in data.columns else 0
    }
    
    return stats

def create_interactive_chart(data, title="U.S. Dollar Index (DXY)", show_presidents=False):
    """
    Create an interactive Plotly chart with zoom and pan functionality
    """
    if data is None or data.empty:
        return None
    
    fig = go.Figure()
    
    # Add presidential background overlays if requested
    if show_presidents:
        presidents_df = get_presidential_data()
        
        # Add background shapes for each presidency within data range
        for _, president in presidents_df.iterrows():
            try:
                # Handle timezone-aware vs timezone-naive datetime comparison
                pres_start = president['start']
                pres_end = president['end']
                data_start = data.index.min()
                data_end = data.index.max()
                
                # Convert to timezone-naive if needed
                if hasattr(data_start, 'tz_localize'):
                    if data_start.tz is not None:
                        data_start = data_start.tz_localize(None)
                        data_end = data_end.tz_localize(None)
                if hasattr(pres_start, 'tz_localize'):
                    if pres_start.tz is not None:
                        pres_start = pres_start.tz_localize(None)
                        pres_end = pres_end.tz_localize(None)
                
                # Skip if president term doesn't overlap with data
                if pres_end < data_start or pres_start > data_end:
                    continue
                    
                color = 'rgba(0, 100, 200, 0.1)' if president['party'] == 'Democrat' else 'rgba(200, 50, 50, 0.1)'
                
                # Clip dates to data range
                shape_start = max(pres_start, data_start)
                shape_end = min(pres_end, data_end)
                
                fig.add_shape(
                    type="rect",
                    x0=shape_start,
                    x1=shape_end,
                    y0=0,
                    y1=1,
                    yref="paper",
                    fillcolor=color,
                    line=dict(width=0),
                    layer="below"
                )
                
                # Add annotation for president name
                duration = shape_end - shape_start
                if hasattr(duration, 'days') and duration.days > 180:
                    mid_date = shape_start + duration / 2
                    fig.add_annotation(
                        x=mid_date,
                        y=0.95,
                        yref="paper",
                        text=f"{president['name']}<br>({president['party'][0]})",
                        showarrow=False,
                        font=dict(size=10, color='black'),
                        bgcolor='rgba(255,255,255,0.8)',
                        bordercolor='black',
                        borderwidth=1
                    )
            except Exception as e:
                continue  # Skip this president if there are date comparison issues
    
    # Add the main price line
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name='DXY Close',
        line=dict(color='#2E86AB', width=2),
        hovertemplate='<b>Date:</b> %{x}<br>' +
                      '<b>Price:</b> %{y:.2f}<br>' +
                      '<extra></extra>'
    ))
    
    # Add volume as a secondary subplot if available and has meaningful data
    has_volume = 'Volume' in data.columns and data['Volume'].sum() > 0 and data['Volume'].max() > 1000
    if has_volume:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Dollar Index Price', 'Volume'),
            row_heights=[0.7, 0.3]
        )
        
        # Re-add presidential overlays for subplot
        if show_presidents:
            presidents_df = get_presidential_data()
            
            for _, president in presidents_df.iterrows():
                try:
                    # Handle timezone-aware vs timezone-naive datetime comparison
                    pres_start = president['start']
                    pres_end = president['end']
                    data_start = data.index.min()
                    data_end = data.index.max()
                    
                    # Convert to timezone-naive if needed
                    if hasattr(data_start, 'tz_localize'):
                        if data_start.tz is not None:
                            data_start = data_start.tz_localize(None)
                            data_end = data_end.tz_localize(None)
                    if hasattr(pres_start, 'tz_localize'):
                        if pres_start.tz is not None:
                            pres_start = pres_start.tz_localize(None)
                            pres_end = pres_end.tz_localize(None)
                    
                    # Skip if president term doesn't overlap with data
                    if pres_end < data_start or pres_start > data_end:
                        continue
                        
                    color = 'rgba(0, 100, 200, 0.1)' if president['party'] == 'Democrat' else 'rgba(200, 50, 50, 0.1)'
                    
                    shape_start = max(pres_start, data_start)
                    shape_end = min(pres_end, data_end)
                    
                    # Add shapes for both subplots
                    for row in [1, 2]:
                        fig.add_shape(
                            type="rect",
                            x0=shape_start,
                            x1=shape_end,
                            y0=0,
                            y1=1,
                            yref=f"y{row} domain",
                            fillcolor=color,
                            line=dict(width=0),
                            layer="below",
                            row=row, col=1
                        )
                except Exception:
                    continue  # Skip this president if there are date comparison issues
        
        # Add price trace
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='DXY Close',
            line=dict(color='#2E86AB', width=2),
            hovertemplate='<b>Date:</b> %{x}<br>' +
                          '<b>Price:</b> %{y:.2f}<br>' +
                          '<extra></extra>'
        ), row=1, col=1)
        
        # Add volume trace
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['Volume'],
            name='Volume',
            marker_color='rgba(46, 134, 171, 0.3)',
            hovertemplate='<b>Date:</b> %{x}<br>' +
                          '<b>Volume:</b> %{y:,.0f}<br>' +
                          '<extra></extra>'
        ), row=2, col=1)
    
    # Update layout for better interactivity
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=20, color='black', family='Arial Black')
        ),
        xaxis_title="Date",
        yaxis_title="Dollar Index Value",
        hovermode='x unified',
        showlegend=True,
        height=600,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black', size=12),  # Global font color and size
        legend=dict(
            font=dict(color='black', size=12),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='black',
            borderwidth=1
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            rangeslider=dict(visible=False),  # Disable range slider for cleaner look
            type='date',
            title=dict(
                text="Date",
                font=dict(color='black', size=14, family='Arial Black')
            ),
            tickfont=dict(color='black', size=12)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            title=dict(
                text="Dollar Index Value",
                font=dict(color='black', size=14, family='Arial Black')
            ),
            tickfont=dict(color='black', size=12)
        )
    )
    
    # Add range selector buttons
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=5, label="5Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ]),
                x=0,
                y=1.02,
                xanchor="left",
                yanchor="top",
                font=dict(color='black', size=12),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='black',
                borderwidth=1,
                activecolor='lightblue'
            ),
        )
    )
    
    return fig

# Sidebar for controls
st.sidebar.header("Chart Controls")

# Time period selection
period_options = {
    "1 Month": "1mo",
    "3 Months": "3mo", 
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
    "10 Years": "10y",
    "All Time": "max"
}

selected_period_label = st.sidebar.selectbox(
    "Select Time Period:",
    options=list(period_options.keys()),
    index=4  # Default to 5 Years
)

selected_period = period_options[selected_period_label]

# Presidential overlay option
show_presidential_overlay = st.sidebar.checkbox("Show Presidential Terms", value=False)
if show_presidential_overlay:
    st.sidebar.markdown("""
    **Legend:**
    - 🔵 Blue: Democrat
    - 🔴 Red: Republican
    """)

# Auto-refresh option
auto_refresh = st.sidebar.checkbox("Auto-refresh data (every 5 minutes)", value=False)

if auto_refresh:
    st.sidebar.info("Data will refresh automatically every 5 minutes")
    
# Manual refresh button
if st.sidebar.button("🔄 Refresh Data Now"):
    st.cache_data.clear()
    st.rerun()

# Main content area
col1, col2, col3, col4 = st.columns(4)

# Show loading spinner while fetching data
with st.spinner("Fetching Dollar Index data..."):
    data, info_or_error = fetch_dxy_data(selected_period)

if data is not None:
    # Calculate statistics
    stats = calculate_statistics(data)
    
    if stats:
        # Display key metrics
        with col1:
            st.metric(
                label="Current DXY",
                value=f"{stats['current_price']:.2f}",
                delta=f"{stats['daily_change']:+.2f}"
            )
        
        with col2:
            st.metric(
                label="Daily Change %",
                value=f"{stats['daily_change_pct']:+.2f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                label="52W High",
                value=f"{stats['high_52w']:.2f}",
                delta=None
            )
        
        with col4:
            st.metric(
                label="52W Low", 
                value=f"{stats['low_52w']:.2f}",
                delta=None
            )
    
    # Create and display the interactive chart
    fig = create_interactive_chart(data, f"U.S. Dollar Index (DXY) - {selected_period_label}", show_presidential_overlay)
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional information
        st.subheader("About the U.S. Dollar Index (DXY)")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("""
            **What is the Dollar Index?**
            
            The U.S. Dollar Index (DXY) is a measure of the value of the United States dollar 
            relative to a basket of foreign currencies. It was established in 1973 and is 
            maintained by ICE (Intercontinental Exchange).
            
            **Currency Basket:**
            - Euro (EUR): 57.6%
            - Japanese Yen (JPY): 13.6%
            - British Pound (GBP): 11.9%
            - Canadian Dollar (CAD): 9.1%
            - Swedish Krona (SEK): 4.2%
            - Swiss Franc (CHF): 3.6%
            """)
        
        with col_info2:
            st.markdown("""
            **Chart Features:**
            
            - **Zoom & Pan**: Click and drag to zoom into specific time periods
            - **Range Selector**: Use the buttons above the chart for quick date ranges
            - **Hover Data**: Hover over the line to see detailed price information
            - **Reset**: Double-click the chart to reset the zoom level
            
            **Data Source:** Yahoo Finance (DX-Y.NYB)
            
            **Update Frequency:** Data is cached for 5 minutes to ensure optimal performance
            """)
        
        # Data table (expandable)
        with st.expander("📊 View Raw Data"):
            # Show last 50 rows by default
            display_data = data.tail(50).copy()
            st.dataframe(
                display_data[['Open', 'High', 'Low', 'Close', 'Volume']].round(2),
                use_container_width=True
            )
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(300)  # Wait 5 minutes
        st.rerun()

else:
    # Error handling
    st.error(f"❌ Failed to fetch Dollar Index data: {info_or_error}")
    st.info("""
    **Possible solutions:**
    - Check your internet connection
    - Try refreshing the page
    - The financial markets might be closed
    - Try selecting a different time period
    """)
    
    if st.button("🔄 Try Again"):
        st.cache_data.clear()
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Data provided by Yahoo Finance | Built with Streamlit and Plotly<br>
    This application is for informational purposes only and should not be considered as financial advice.
</div>
""", unsafe_allow_html=True)
