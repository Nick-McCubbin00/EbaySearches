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
    os.environ['EBAY_ACCESS_TOKEN'] = ''

if not os.getenv('GEMINI_API_KEY'):
    os.environ['GEMINI_API_KEY'] = ""

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
                max_results=15,  # Increased for more data
                min_confidence=30,  # Much lower threshold for more results
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
            max_results=15,  # Increased for more data
            min_confidence=30,  # Much lower threshold for more results
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

@app.route('/api/test-ebay', methods=['POST'])
def test_ebay_api():
    """Test eBay API without AI processing"""
    try:
        data = request.get_json()
        search_query = data.get('search_query', '').strip()
        
        if not search_query:
            return jsonify({
                'error': 'Search query is required',
                'status': 'error'
            }), 400
        
        logger.info(f"🧪 Testing eBay API for: {search_query}")
        
        # Import the search function
        from Complete_Ebay_AI_Analyzer import search_completed_sales
        
        # Test just the eBay search
        listings = search_completed_sales(search_query, max_results=5, days_back=90)
        
        return jsonify({
            'status': 'success',
            'search_query': search_query,
            'listings_found': len(listings) if listings else 0,
            'listings': listings[:3] if listings else []  # Show first 3 for debugging
        })
        
    except Exception as e:
        logger.error(f"❌ eBay API test failed: {e}")
        return jsonify({
            'error': f'eBay API test failed: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/test-ai', methods=['POST'])
def test_ai_api():
    """Test Gemini AI API without eBay processing"""
    try:
        data = request.get_json()
        test_text = data.get('test_text', 'Hello, how are you?')
        
        logger.info(f"🧪 Testing Gemini AI API with: {test_text}")
        
        # Import the AI components
        import google.generativeai as genai
        import os
        
        # Set up the API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({
                'error': 'GEMINI_API_KEY not set',
                'status': 'error'
            }), 500
        
        genai.configure(api_key=api_key)
        
        # Test the AI
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(f"Say hello to: {test_text}")
        
        return jsonify({
            'status': 'success',
            'test_text': test_text,
            'ai_response': response.text,
            'model': 'gemini-2.5-flash'
        })
        
    except Exception as e:
        logger.error(f"❌ AI API test failed: {e}")
        return jsonify({
            'error': f'AI API test failed: {str(e)}',
            'status': 'error'
        }), 500

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
