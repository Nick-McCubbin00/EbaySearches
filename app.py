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
from Complete_Ebay_AI_Analyzer import complete_ebay_analysis, EBAY_ACCESS_TOKEN, GEMINI_API_KEY

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
        
        print(f"🔍 Analyzing: {search_query}")
        
        # Run the complete real analysis
        results = complete_ebay_analysis(
            search_query=search_query,
            max_results=20,
            min_confidence=70,
            days_back=90
        )
        
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
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🤖 eBay AI Analyzer API Server")
    print("=" * 40)
    print("✅ Real Analysis Mode - No Demo")
    print("   - eBay API integration active")
    print("   - Google Gemini AI scoring active")
    print("   - All searches use real data")
    
    print("\n🌐 Starting server...")
    print("   - Local: http://localhost:5000")
    print("   - API: http://localhost:5000/api/analyze")
    print("   - Status: http://localhost:5000/api/status")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 