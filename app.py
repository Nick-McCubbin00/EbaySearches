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
    os.environ['EBAY_ACCESS_TOKEN'] = 'v^1.1#i^1#p^1#I^3#r^0#f^0#t^H4sIAAAAAAAA/+VYbWxTZRxvt2442JwoIkzUcogRlmvvrr32elsLfWFbSbeVtdRtyST38tx27Hp33HNlG4nabQoJQRRfMOEDTJCo+EGDEBMT34BkMUGNH4yGVyN88DVGIyEGI961ZXST8LYmLrFfmvs//+f//H6/5/9/3rBsZdXyzS2bL9ZYZ5WNZbFsmdWKz8GqKivq7ywvq6uwYEUO1rHsw1nbSPn3jZBJSyrdAaCqyBDYB9OSDOmc0Y9kNJlWGChCWmbSANI6RyeCrTGacGC0qim6wikSYo9G/IiXJ30MxrI45QWkx+MxrPKVmEnFj7gElvKY7V4Sc5ECZbRDmAFRGeqMrPsRAiNIFPOiBJXEvTTupkm3g/IR3Yg9BTQoKrLh4sCQQA4uneurFWG9PlQGQqDpRhAkEA02JdqD0ciqtmSjsyhWoKBDQmf0DJz8FVZ4YE8xUgZcfxiY86YTGY4DECLOQH6EyUHp4BUwtwE/JzXp4zg3QfA4xzJAAERJpGxStDSjXx+HaRF5VMi50kDWRX3oRooaarDrAacXvtqMENGI3fxbk2EkURCB5kdWhYJdwXgcCaxVTQ1BGA0rogzReEcEpShAcRyFk6gXw1mSZfnCKPlQBY2nDBNWZF40FYP2NkUPAQMymCoMViSM4dQut2tBQTfhFPv5rghIUd3mjOanMKP3yeakgrShgj33eWP5J3rruiayGR1MRJjakNPHjzCqKvLI1MZcIhZyZxD6kT5dV2mnc2BgwDHgcihar5PAMNzZ2RpLcH0gzSB5X7PWDX/xxh1QMUeFA0ZPKNL6kGpgGTQS1QAg9yIB0oX7cKyg+2RYganWfxmKODsnl0OpygPnPV6vi/S5vYyH9+JYKcojUMhQp4kDsMwQmma0fqCrEsMBlDPyLJMGmsjTxtJGuCgBoLzHJ6BunyCgLMl7UFwAAAOAZTkf9b+pkpvN8wTgNKCXKtFLk+Rpoa/FQ5FrQtEmz/pOeZUWa43owRZnV0hzdbQ2x+rjm1KZzlj3AGj132wpXJN8WBINZZLG+KUTwKz1UojQokAd8NOil+AUFcQVSeSGZtYEuzQ+zmj6UAJIkmGYFsmgqkZLtlCXht6trBG3R7qku9N/sTNdkxU083VmsTL7QyMAo4oOc+9xcEraqTDGocM0mbW+Lod6WrxF48A6o1gbJPNsRT5/0nTkKDvgRs6hAahkNOOQ7Wg3z15JpR/Ixmama4okAS2FT7uY0+mMzrASmGlVXYIEF5kZttMaN0KXlyAon3tavLjcPrpupi1JJV2HbQ23cJp2Tr7YByy5Hz5iPYKNWD8ss1qxRmwpvgRbXFm+1lZeXQdFHThERnBAsVc27qsacPSDIZURtbJ7LF/cGeOHW2IXsmzmvcf+WEFZaoreFcZ6sAUTLwtV5ficomcGbNHVlgq89r4agsS8BIV7cTfp7saWXG214fNt847P/uby9oVbX8kSX+2cvSzSg1+493msZsLJaq2w2EaslrLR1Ka/F/TEN1ZvO/Di+/Mu/fLc+CNHIhtqtzzRvLf9s107dp48bLtrfbJ66cq9e04fq297o638zLv7V48nak88SFZHLz/eMLZr+MS+ZOeiVIque3mD0DW8/amjB9+qGV79M+w+UfnpBXz3uK9r8POe+f2HHj1Hn+Q6+149v+/o3PC3Ox4YTSw8nf797lPcoaq1luZ50rmahlD4p++eXBGas//+NxeP/tX8ZXdg67lfK/DzqYhS/6NnWaTWsryx93DQH//k7Mb4avpA/Cj/7Evb/nx6Kzqbfu2Sf9b2r99ecv7iZl/HmQ+EZ17o2PPO7jtCdaOLTjU81DS3fukPH/+25aOVR4Jbxo8dP5uJvX7oYH4u/wGwUx188REAAA=='

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
                max_results=6,  # Reduced for faster processing
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
            max_results=6,  # Reduced for faster processing
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
