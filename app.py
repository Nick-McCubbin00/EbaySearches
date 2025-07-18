#!/usr/bin/env python3
"""
Flask API for eBay AI Analyzer
Provides a web API that runs the complete eBay AI analysis workflow
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
import sys
import traceback
from datetime import datetime
import threading
import queue

# Import our analyzer functions
try:
    from Complete_Ebay_AI_Analyzer import complete_ebay_analysis
except ImportError:
    print("Warning: Complete_Ebay_AI_Analyzer not found. Using demo mode.")
    complete_ebay_analysis = None

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
DEMO_MODE = complete_ebay_analysis is None
API_KEYS_CONFIGURED = False

# Check if API keys are configured
if not DEMO_MODE:
    try:
        from Complete_Ebay_AI_Analyzer import EBAY_ACCESS_TOKEN, GEMINI_API_KEY
        # Check if keys are properly configured (not placeholder values)
        if (EBAY_ACCESS_TOKEN and 
            len(EBAY_ACCESS_TOKEN) > 50 and  # Real tokens are long
            GEMINI_API_KEY and 
            len(GEMINI_API_KEY) > 30):  # Real API keys are long
            API_KEYS_CONFIGURED = True
            print(f"✅ API keys configured - Real analysis enabled")
        else:
            print(f"⚠️  API keys appear to be placeholder values - Using demo mode")
    except ImportError:
        print(f"⚠️  Could not import API keys - Using demo mode")
        pass

def generate_demo_results(search_query):
    """Generate realistic demo results for testing"""
    import random
    
    # Different results based on search query
    if 'ms69' in search_query.lower():
        return {
            "search_query": search_query,
            "summary": {
                "total_listings_found": 9,
                "high_confidence_listings": 9,
                "average_confidence": 95.5,
                "confidence_range": "90% - 100%"
            },
            "pricing_analysis": {
                "weighted_average": 48.09,
                "median_price": 48.99,
                "min_price": 45.0,
                "max_price": 50.0,
                "price_range": 5.0,
                "total_weighted_sales": 9
            },
            "recommendations": {
                "data_quality": {
                    "assessment": "Excellent",
                    "reason": "Found 9 high-confidence listings"
                },
                "pricing_insights": {
                    "volatility": "Low",
                    "reason": "Price range is only $5.00",
                    "suggested_price": "$48.09"
                },
                "next_steps": [
                    "Use confidence scores to weight your pricing decisions",
                    "Monitor prices over time for trend analysis",
                    "Consider this a reliable baseline for pricing"
                ]
            }
        }
    elif 'ms70' in search_query.lower():
        return {
            "search_query": search_query,
            "summary": {
                "total_listings_found": 7,
                "high_confidence_listings": 7,
                "average_confidence": 92.3,
                "confidence_range": "85% - 98%"
            },
            "pricing_analysis": {
                "weighted_average": 125.45,
                "median_price": 127.50,
                "min_price": 115.0,
                "max_price": 135.0,
                "price_range": 20.0,
                "total_weighted_sales": 7
            },
            "recommendations": {
                "data_quality": {
                    "assessment": "Good",
                    "reason": "Found 7 high-confidence listings"
                },
                "pricing_insights": {
                    "volatility": "Moderate",
                    "reason": "Price range is $20.00",
                    "suggested_price": "$125.45"
                },
                "next_steps": [
                    "MS70 coins show higher price volatility",
                    "Consider condition and certification details",
                    "Monitor for market trends in premium grades"
                ]
            }
        }
    else:
        # Standard bullion coins
        base_price = random.uniform(35, 45)
        return {
            "search_query": search_query,
            "summary": {
                "total_listings_found": 12,
                "high_confidence_listings": 11,
                "average_confidence": 88.7,
                "confidence_range": "75% - 95%"
            },
            "pricing_analysis": {
                "weighted_average": round(base_price, 2),
                "median_price": round(base_price + random.uniform(-1, 1), 2),
                "min_price": round(base_price - 3, 2),
                "max_price": round(base_price + 3, 2),
                "price_range": round(6, 2),
                "total_weighted_sales": 11
            },
            "recommendations": {
                "data_quality": {
                    "assessment": "Good",
                    "reason": "Found 11 high-confidence listings"
                },
                "pricing_insights": {
                    "volatility": "Low",
                    "reason": "Standard bullion shows consistent pricing",
                    "suggested_price": f"${base_price:.2f}"
                },
                "next_steps": [
                    "Standard bullion coins have predictable pricing",
                    "Consider silver spot price fluctuations",
                    "Good baseline for market value assessment"
                ]
            }
        }

@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(open('docs/index.html').read())

@app.route('/api/analyze', methods=['POST'])
def analyze_coin():
    """API endpoint to analyze coin pricing"""
    try:
        data = request.get_json()
        search_query = data.get('search_query', '').strip()
        
        if not search_query:
            return jsonify({
                'error': 'Search query is required',
                'status': 'error'
            }), 400
        
        # Check if we're in demo mode or API keys aren't configured
        if DEMO_MODE or not API_KEYS_CONFIGURED:
            # Return demo results
            import time
            time.sleep(2)  # Simulate processing time
            
            results = generate_demo_results(search_query)
            results['demo_mode'] = True
            results['message'] = 'Demo mode - using sample data. Configure API keys for real analysis.'
            
            return jsonify({
                'status': 'success',
                'data': results
            })
        
        # Real analysis mode
        try:
            # Run the complete analysis
            results = complete_ebay_analysis(
                search_query=search_query,
                max_results=20,
                min_confidence=70,
                days_back=90
            )
            
            # Add metadata
            results['demo_mode'] = False
            results['analysis_timestamp'] = datetime.now().isoformat()
            
            return jsonify({
                'status': 'success',
                'data': results
            })
            
        except Exception as e:
            # If real analysis fails, fall back to demo
            print(f"Real analysis failed: {e}")
            results = generate_demo_results(search_query)
            results['demo_mode'] = True
            results['message'] = f'Real analysis failed: {str(e)}. Using demo data.'
            
            return jsonify({
                'status': 'success',
                'data': results
            })
            
    except Exception as e:
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'status': 'error',
            'traceback': traceback.format_exc() if app.debug else None
        }), 500

@app.route('/api/status')
def api_status():
    """Check API status and configuration"""
    return jsonify({
        'status': 'online',
        'demo_mode': DEMO_MODE,
        'api_keys_configured': API_KEYS_CONFIGURED,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🤖 eBay AI Analyzer API Server")
    print("=" * 40)
    
    if DEMO_MODE:
        print("⚠️  Running in DEMO MODE")
        print("   - Complete_Ebay_AI_Analyzer.py not found")
        print("   - Using sample data for all requests")
    elif not API_KEYS_CONFIGURED:
        print("⚠️  API KEYS NOT CONFIGURED")
        print("   - Please configure EBAY_ACCESS_TOKEN and GEMINI_API_KEY")
        print("   - Running in demo mode until keys are set")
    else:
        print("✅ Full functionality enabled")
        print("   - eBay API integration active")
        print("   - Google Gemini AI scoring active")
    
    print("\n🌐 Starting server...")
    print("   - Local: http://localhost:5000")
    print("   - API: http://localhost:5000/api/analyze")
    print("   - Status: http://localhost:5000/api/status")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
