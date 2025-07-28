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
import time
import logging

# Import our analyzer functions
from Complete_Ebay_AI_Analyzer import complete_ebay_analysis

# Set environment variables if not already set (for local development)
if not os.getenv('EBAY_ACCESS_TOKEN'):
    os.environ['EBAY_ACCESS_TOKEN'] = "v^1.1#i^1#f^0#p^1#I^3#r^0#t^H4sIAAAAAAAA/+VYbWxTVRhuu25zm0MJgoQQrBdwILm396O3vb1pa7puY43dVtZtbnMw78cpu6z3w3vuZRQEa0US8I8BI4kTJQRiSIx/8As1hA+RH2rQQELghySYKInBCH4QokTv7croJgFkjVli/zTnPe95z/M8533POffcueqax7e0brla76x27c7hOZfTSdThNVWVy2ZUuOZVOvASB+fu3KKcO19xMQQ5OaOxnQBqqgKBZ52cUSBbMIYRU1dYlYMSZBVOBpA1BDYVbUuwJIazmq4aqqBmEE+8KYwQOIFzVJom/TQnUpZNuRGxSw0jpAD8aZqhaEDzPpIhrX4ITRBXoMEphtWPkzSKB1CS6SICLO5jCQrz475+xNMDdCipiuWC4UikAJYtjNVLkN4eKAch0A0rCBKJR1tSHdF4U3N7V8hbEitSVCFlcIYJJ7Ziqgg8PVzGBLefBha82ZQpCABCxBsZm2FiUDZ6A8w9wC8IDYgAHxB9wEf6fDTPM2WRskXVZc64PQ7bIolouuDKAsWQjOydFLXU4NcAwSi22q0Q8SaP/bfC5DJSWgJ6GGlujPZFk0kk0q3ZGoIYGlMlBaLJziaUYQAjCAxBowGc4C2+YnGWsVBFjSdNE1MVUbIVg5521WgEFmQwURg/S5cIYzl1KB16NG3YcEr9gkUB6WCw317RsSU0jSHFXlQgWyp4Cs07yz8+2jB0iTcNMB5hckdBnzDCaZokIpM7C4lYzJ11MIwMGYbGer0jIyPYCIWp+movieOEt7ctkRKGgMwhN3ztWofSnQegUoGKAKyRUGKNrGZhWWclqgVAWY1EaIoIEnhR94mwIpOt/zCUcPZOLIdylQcTDAQpv0iRJOenGH+6HOURKWao18YBeC6Lypw+DAwtwwkAFaw8M2WgSyJL0WmSYtIAFf3BNOoLptMoT4t+lEgDgAPA80KQ+d9Uyd3meQoIOjDKl+jlSHI5PdTqZ+gVjfEW/5pepVlPtDUZ0VZvX6NOdbYtTyxLru8xexP9I6AtfLelcEvysYxkKdNlzV9OAexan7oIrSo0gDgleilB1UBSzUhCdnotMKWLSU43simQyViGKZGMalq8jBt1Oej9mz3i3kiX+XT670+mW7KCdr5OL1b2eGgF4DQJs88eTFBlr8pZlw7bNAjtWrdRT4m3ZF1YpxVri+QYW0kcu2liBcoYXCtgOoCqqVuXbKzDvnt1qcNAsQ4zQ1czGaD3EFMuZlk2DY7PgOlW1WVIcImbZictEaCpAEmSNDUlXkLhHB2cbltSWfdhL3QH7/o27Z34WR9xFH5E3nkUzzsPuZxOPIQvJhbij1ZVdLsr7p8HJQNgEpfGoLRasb5XdYANg6zGSbprluPkjIT4QmvitxxvfvjUr08wjvqSV4XdK/G54+8KNRVEXckjAz7/Zk8l8cDD9SSNB0iGCOA+gurHF97sdRNz3A99d+SdT/g3dhLa8X0/5gbQYP7TUAqvH3dyOisd7rzTsalhU+2O6vaXDy9Z7z6/0zzwyr7YD6ORM/tHT89bmprt2rAov/15UfhraM+bHQ/6QpWrhGbO9eeVmseeJndVr/36s9y3c775KHep7ZCZH52Lu5fP3HA8Mni97gPqzB/dYuvlBvkUu/f9C08e+Z7fuevKsesnHM+d7KRnuH6/fHagf+PKS0vyP62KB784173j2QXxgRp4ZlffgbcGLs68NszFpEUbniEWNwzu3ey/2n5w24WDO+bO2txQu2x+xavo4XPVr12AR4+podr3ti7YvlXOnpX73j09vP6l5suHq34eWLqx9/Utqz4+/eK24+e/6vvlkaQ/Ekf2Xz13YlQbOfhl3eCpWuG+tz+/tic0e2wt/wbftsIV7xEAAA=="

if not os.getenv('GEMINI_API_KEY'):
    os.environ['GEMINI_API_KEY'] = "AIzaSyAPIUPQ_gNZeqiLv7Q3oqPEQ98f4xU4GoY"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration - Always use real analysis
print(f"✅ Real eBay AI Analyzer loaded - Full functionality enabled")
print(f"✅ eBay API integration active")
print(f"✅ Google Gemini AI scoring active")


@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(open('docs/index.html', encoding='utf-8').read())

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
        
        logger.info(f"🔍 Starting analysis for: {search_query}")
        start_time = time.time()
        
        # Run the complete real analysis with timeout
        try:
            logger.info("📊 Step 1: Calling complete_ebay_analysis...")
            results = complete_ebay_analysis(
                search_query=search_query,
                max_results=8,  # Reduced for Render.com stability
                min_confidence=60,  # Reduced for more results
                days_back=90
            )
            
            analysis_time = time.time() - start_time
            logger.info(f"✅ Analysis completed in {analysis_time:.2f} seconds")
            
        except Exception as analysis_error:
            logger.error(f"❌ Analysis failed: {analysis_error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': f'Analysis failed: {str(analysis_error)}',
                'status': 'error',
                'traceback': traceback.format_exc() if app.debug else None
            }), 500
        
        # Check if results is None (no listings found)
        if results is None:
            return jsonify({
                'status': 'success',
                'data': {
                    'search_query': search_query,
                    'summary': {
                        'total_listings_found': 0,
                        'high_confidence_listings': 0,
                        'average_confidence': 0
                    },
                    'pricing_analysis': {
                        'weighted_average': 0,
                        'price_range': 0,
                        'min_price': 0,
                        'max_price': 0,
                        'median_price': 0
                    },
                    'recommendations': {
                        'data_quality': {
                            'assessment': 'No data available',
                            'reason': 'No listings found for this search query'
                        },
                        'pricing_insights': {
                            'suggested_price': 'No data available',
                            'volatility': 'Unknown',
                            'reason': 'No listings found'
                        },
                        'next_steps': [
                            'Try broadening your search terms',
                            'Check for typos in the search query',
                            'Try searching for a different year or grade'
                        ]
                    },
                    'analysis_timestamp': datetime.now().isoformat()
                }
            })
        
        # Add metadata
        results['analysis_timestamp'] = datetime.now().isoformat()
        
        print(f"✅ Analysis complete for: {search_query}")
        
        return jsonify({
            'status': 'success',
            'data': results
        })
            
    except Exception as e:
        print(f"❌ Analysis failed for '{search_query}': {e}")
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'status': 'error',
            'traceback': traceback.format_exc() if app.debug else None
        }), 500

@app.route('/api/analyze/batch', methods=['POST'])
def analyze_batch():
    """API endpoint to analyze multiple coin queries in batch"""
    try:
        data = request.get_json()
        search_queries_text = data.get('search_queries', '').strip()
        
        if not search_queries_text:
            return jsonify({
                'error': 'Search queries are required (comma-separated)',
                'status': 'error'
            }), 400
        
        # Parse comma-separated queries
        from Complete_Ebay_AI_Analyzer import parse_search_queries, batch_ebay_analysis
        
        search_queries = parse_search_queries(search_queries_text)
        
        if not search_queries:
            return jsonify({
                'error': 'No valid search queries found',
                'status': 'error'
            }), 400
        
        print(f"🚀 Starting batch analysis of {len(search_queries)} queries...")
        
        # Run batch analysis
        batch_results = batch_ebay_analysis(
            search_queries=search_queries,
            max_results=8,  # Reduced for Render.com stability
            min_confidence=60,  # Reduced for more results
            days_back=90
        )
        
        print(f"✅ Batch analysis complete: {batch_results['successful_queries']}/{batch_results['total_queries']} successful")
        
        return jsonify({
            'status': 'success',
            'data': batch_results
        })
            
    except Exception as e:
        print(f"❌ Batch analysis failed: {e}")
        return jsonify({
            'error': f'Batch analysis failed: {str(e)}',
            'status': 'error',
            'traceback': traceback.format_exc() if app.debug else None
        }), 500

@app.route('/api/status')
def api_status():
    """Check API status and configuration"""
    return jsonify({
        'status': 'online',
        'mode': 'real_analysis',
        'ebay_api': 'active',
        'gemini_ai': 'active',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Simple health check endpoint"""
    logger.info("🏥 Health check requested")
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'eBay AI Analyzer',
        'version': '1.0.0'
    })

@app.route('/api/test')
def test_endpoint():
    """Test endpoint to verify service is working"""
    logger.info("🧪 Test endpoint called")
    return jsonify({
        'message': 'Service is running!',
        'timestamp': datetime.now().isoformat(),
        'port': os.environ.get('PORT', '5000')
    })

if __name__ == '__main__':
    print("🤖 eBay AI Analyzer API Server")
    print("=" * 40)
    print("✅ Real Analysis Mode - No Demo")
    print("   - eBay API integration active")
    print("   - Google Gemini AI scoring active")
    print("   - All searches use real data")
    
    # Get port from environment variable (for Render.com) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print("\n🌐 Starting server...")
    print(f"   - Port: {port}")
    print(f"   - Local: http://localhost:{port}")
    print(f"   - API: http://localhost:{port}/api/analyze")
    print(f"   - Status: http://localhost:{port}/api/status")
    
    app.run(debug=False, host='0.0.0.0', port=port) 
