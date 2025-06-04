# U.S. Dollar Index (DXY) Interactive Chart

An interactive Streamlit web application for visualizing U.S. Dollar Index data with zoom and pan functionality.

## Features

- Real-time DXY data from Yahoo Finance
- Interactive charts with zoom and pan
- Multiple time period selections (1M, 3M, 6M, 1Y, 2Y, 5Y, 10Y, All)
- Key metrics display (current price, daily change, 52W high/low)
- Range selector buttons for quick navigation
- Auto-refresh functionality
- Raw data table view

## Docker Deployment

### Prerequisites

- Docker installed on your server
- Docker Compose (optional but recommended)

### Option 1: Using Docker Compose (Recommended)

1. Clone or download all files to your server
2. Run the application:

```bash
docker-compose up -d
```

3. Access the application at `http://your-server-ip:8501`

### Option 2: Using Docker directly

1. Build the Docker image:

```bash
docker build -t dxy-chart .
```

2. Run the container:

```bash
docker run -d -p 8501:5000 --name dxy-app dxy-chart
```

3. Access the application at `http://your-server-ip:8501`

### Configuration

The application runs on port 5000 by default. To change the port, modify:

- `docker-compose.yml`: Change the port mapping (e.g., `"8080:5000"`)
- Or use Docker run with different port: `docker run -d -p 8080:5000 dxy-chart`

### Management Commands

```bash
# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Update the application
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Data Source

The application fetches real-time U.S. Dollar Index data from Yahoo Finance (DX-Y.NYB ticker).

## About the Dollar Index

The U.S. Dollar Index (DXY) measures the value of the United States dollar relative to a basket of foreign currencies:

- Euro (EUR): 57.6%
- Japanese Yen (JPY): 13.6%
- British Pound (GBP): 11.9%
- Canadian Dollar (CAD): 9.1%
- Swedish Krona (SEK): 4.2%
- Swiss Franc (CHF): 3.6%

## Technical Details

- Built with Streamlit and Plotly
- Python 3.11 runtime
- Automatic data caching (5-minute intervals)
- Health checks included for production monitoring