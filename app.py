"""
Airline Booking Market Demand Analysis Web App
A comprehensive Flask-based web application for analyzing airline booking trends
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
import plotly.utils
from bs4 import BeautifulSoup
import time
import random
from dataclasses import dataclass
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or 'your-openai-api-key'
    AVIATIONSTACK_API_KEY = os.environ.get('AVIATIONSTACK_API_KEY') or 'your-aviationstack-api-key'

app.config.from_object(Config)

@dataclass
class FlightData:
    """Data class for flight information"""
    origin: str
    destination: str
    price: float
    date: str
    airline: str
    demand_score: float = 0.0

class DataScraper:
    """Handles data scraping and API integration"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_sample_flight_data(self) -> List[FlightData]:
        """Generate sample flight data for demonstration"""
        cities = ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Darwin']
        airlines = ['Qantas', 'Virgin Australia', 'Jetstar', 'Tiger Airways']
        
        flights = []
        for _ in range(50):
            origin = random.choice(cities)
            destination = random.choice([city for city in cities if city != origin])
            
            base_price = random.uniform(150, 800)
            date = datetime.now() + timedelta(days=random.randint(1, 90))
            
            flight = FlightData(
                origin=origin,
                destination=destination,
                price=base_price,
                date=date.strftime('%Y-%m-%d'),
                airline=random.choice(airlines),
                demand_score=random.uniform(0.3, 1.0)
            )
            flights.append(flight)
        
        return flights
    
    def get_aviation_data(self, api_key: str) -> List[Dict]:
        """Fetch data from AviationStack API (if available)"""
        if not api_key or api_key == 'your-aviationstack-api-key':
            logger.warning("AviationStack API key not configured, using sample data")
            return []
        
        try:
            url = f"http://api.aviationstack.com/v1/flights?access_key={api_key}&limit=100"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"API request failed: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching aviation data: {e}")
            return []

class DataProcessor:
    """Processes and analyzes flight data"""
    
    def __init__(self):
        self.scraper = DataScraper()
    
    def get_market_insights(self, flights: List[FlightData]) -> Dict[str, Any]:
        """Generate market insights from flight data"""
        if not flights:
            return self._get_default_insights()
        
        df = pd.DataFrame([{
            'origin': f.origin,
            'destination': f.destination,
            'price': f.price,
            'date': f.date,
            'airline': f.airline,
            'demand_score': f.demand_score
        } for f in flights])
        
        # Popular routes
        popular_routes = df.groupby(['origin', 'destination']).agg({
            'price': 'mean',
            'demand_score': 'mean'
        }).reset_index()
        popular_routes['route'] = popular_routes['origin'] + ' → ' + popular_routes['destination']
        popular_routes = popular_routes.sort_values('demand_score', ascending=False).head(10)
        
        # Price trends
        df['date'] = pd.to_datetime(df['date'])
        price_trends = df.groupby('date')['price'].mean().reset_index()
        
        # High demand periods
        demand_periods = df.groupby('date')['demand_score'].mean().reset_index()
        demand_periods = demand_periods.sort_values('demand_score', ascending=False).head(5)
        
        # Airline analysis
        airline_stats = df.groupby('airline').agg({
            'price': 'mean',
            'demand_score': 'mean'
        }).reset_index()
        
        return {
            'popular_routes': popular_routes.to_dict('records'),
            'price_trends': price_trends.to_dict('records'),
            'demand_periods': demand_periods.to_dict('records'),
            'airline_stats': airline_stats.to_dict('records'),
            'total_flights': len(flights),
            'avg_price': df['price'].mean(),
            'peak_demand_score': df['demand_score'].max()
        }
    
    def _get_default_insights(self) -> Dict[str, Any]:
        """Return default insights when no data is available"""
        return {
            'popular_routes': [],
            'price_trends': [],
            'demand_periods': [],
            'airline_stats': [],
            'total_flights': 0,
            'avg_price': 0,
            'peak_demand_score': 0
        }

class AIInsightGenerator:
    """Generates AI-powered insights using OpenAI API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def generate_insights(self, market_data: Dict[str, Any]) -> str:
        """Generate AI insights from market data"""
        if not self.api_key or self.api_key == 'your-openai-api-key':
            return self._generate_sample_insights(market_data)
        
        try:
            prompt = f"""
            Based on the following airline booking market data, provide actionable insights:
            
            Total Flights: {market_data['total_flights']}
            Average Price: ${market_data['avg_price']:.2f}
            Peak Demand Score: {market_data['peak_demand_score']:.2f}
            
            Popular Routes: {market_data['popular_routes'][:5]}
            
            Please provide:
            1. Key market trends
            2. Pricing insights
            3. Demand patterns
            4. Recommendations for hostel operators
            """
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 500,
                'temperature': 0.7
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return self._generate_sample_insights(market_data)
                
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return self._generate_sample_insights(market_data)
    
    def _generate_sample_insights(self, market_data: Dict[str, Any]) -> str:
        """Generate sample insights when AI is not available"""
        return f"""
        **Market Analysis Summary**
        
        **Key Trends:**
        - Total flights analyzed: {market_data['total_flights']}
        - Average flight price: ${market_data['avg_price']:.2f}
        - Peak demand indicator: {market_data['peak_demand_score']:.2f}
        
        **Pricing Insights:**
        - Moderate pricing variation across routes
        - Seasonal demand patterns evident
        - Competition driving competitive pricing
        
        **Demand Patterns:**
        - Major city routes show highest demand
        - Weekend and holiday periods see increased activity
        - Business travel corridors remain stable
        
        **Recommendations for Hostel Operators:**
        - Focus marketing during high-demand flight periods
        - Partner with airlines for package deals
        - Monitor route popularity for expansion opportunities
        """

# Initialize global components
data_processor = DataProcessor()
ai_generator = AIInsightGenerator(app.config['OPENAI_API_KEY'])

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """API endpoint to fetch and process flight data"""
    try:
        # Get flight data
        flights = data_processor.scraper.get_sample_flight_data()
        
        # Process data for insights
        insights = data_processor.get_market_insights(flights)
        
        # Generate AI insights
        ai_insights = ai_generator.generate_insights(insights)
        
        # Create visualizations
        charts = create_charts(insights)
        
        return jsonify({
            'success': True,
            'insights': insights,
            'ai_insights': ai_insights,
            'charts': charts
        })
        
    except Exception as e:
        logger.error(f"Error in get_data endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/filter')
def filter_data():
    """API endpoint to filter data based on user inputs"""
    try:
        # Get filter parameters
        origin = request.args.get('origin', '')
        destination = request.args.get('destination', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Get and filter flight data
        flights = data_processor.scraper.get_sample_flight_data()
        
        # Apply filters
        if origin:
            flights = [f for f in flights if f.origin.lower() == origin.lower()]
        if destination:
            flights = [f for f in flights if f.destination.lower() == destination.lower()]
        
        # Process filtered data
        insights = data_processor.get_market_insights(flights)
        charts = create_charts(insights)
        ai_insights = ai_generator.generate_insights(insights)
        
        return jsonify({
            'success': True,
            'insights': insights,
            'charts': charts,
            'ai_insights': ai_insights
        })
        
    except Exception as e:
        logger.error(f"Error in filter_data endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def create_charts(insights: Dict[str, Any]) -> Dict[str, str]:
    """Create Plotly charts from insights data"""
    charts = {}
    
    try:
        # Popular routes chart
        if insights['popular_routes']:
            routes_df = pd.DataFrame(insights['popular_routes'])
            routes_fig = go.Figure(data=[
                go.Bar(x=routes_df['route'], y=routes_df['demand_score'],
                       text=routes_df['demand_score'].round(2),
                       textposition='auto')
            ])
            routes_fig.update_layout(title='Popular Routes by Demand Score',
                                   xaxis_title='Route',
                                   yaxis_title='Demand Score')
            charts['popular_routes'] = json.dumps(routes_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Price trends chart
        if insights['price_trends']:
            price_df = pd.DataFrame(insights['price_trends'])
            price_fig = go.Figure(data=[
                go.Scatter(x=price_df['date'], y=price_df['price'],
                          mode='lines+markers', name='Average Price')
            ])
            price_fig.update_layout(title='Price Trends Over Time',
                                  xaxis_title='Date',
                                  yaxis_title='Average Price ($)')
            charts['price_trends'] = json.dumps(price_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Airline comparison chart
        if insights['airline_stats']:
            airline_df = pd.DataFrame(insights['airline_stats'])
            airline_fig = go.Figure(data=[
                go.Scatter(x=airline_df['price'], y=airline_df['demand_score'],
                          mode='markers+text', text=airline_df['airline'],
                          textposition='top center', marker=dict(size=10))
            ])
            airline_fig.update_layout(title='Airline Price vs Demand Analysis',
                                    xaxis_title='Average Price ($)',
                                    yaxis_title='Demand Score')
            charts['airline_comparison'] = json.dumps(airline_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    except Exception as e:
        logger.error(f"Error creating charts: {e}")
    
    return charts

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)