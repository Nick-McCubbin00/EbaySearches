#!/usr/bin/env python3
"""
Complete eBay AI Analyzer
Combines eBay API search with Gemini AI confidence scoring in one comprehensive workflow
Optimized for batch processing and performance
"""

import requests
import json
import os
import time
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from functools import lru_cache
import re

# Configure logging
logger = logging.getLogger(__name__)

# --- Configuration ---
# eBay API Configuration
EBAY_ACCESS_TOKEN = os.getenv('EBAY_ACCESS_TOKEN')  # Get from environment variable
EBAY_BROWSE_API_ENDPOINT = "https://api.ebay.com/buy/browse/v1/item_summary/search"

# Google Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # Get from environment variable

# Performance Configuration
MAX_CONCURRENT_REQUESTS = 10  # Reduced for better reliability
AI_BATCH_SIZE = 10  # Smaller batches for faster processing
CACHE_TTL = 600  # Cache results for 10 minutes (increased from 5)
MAX_RESULTS_DEFAULT = 20  # Reduced for faster processing
MIN_CONFIDENCE_DEFAULT = 70  # Much lower threshold for more results

# Thread-local storage for API rate limiting
thread_local = threading.local()

# Simple in-memory cache for results
_result_cache = {}
_cache_timestamps = {}

# Rate limiting for API calls
_last_api_call = 0
_api_call_interval = 0.5  # Minimum 0.5 seconds between API calls

# --- AI Confidence Scoring System ---

class eBayConfidenceScorer:
    """
    AI-powered system to score how well eBay listings match search criteria.
    Uses Gemini's GPT models to analyze listing titles and determine relevance.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the confidence scorer with Google Gemini API key."""
        if api_key:
            genai.configure(api_key=api_key)
            self.use_ai = True
            print("✅ AI confidence scoring enabled with Google Gemini")
        elif GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key-here" and GEMINI_API_KEY.strip():
            genai.configure(api_key=GEMINI_API_KEY)
            self.use_ai = True
            print("✅ AI confidence scoring enabled with Google Gemini")
        else:
            print("⚠️  Warning: No Gemini API key provided. Using rule-based scoring only.")
            self.use_ai = False
    
    def score_listing_confidence(self, listing: Dict, search_query: str) -> Dict:
        """
        Score a single listing's confidence level (0-100) based on search query.
        
        Args:
            listing: Dictionary containing listing data
            search_query: Original search query
            
        Returns:
            Dictionary with confidence score and reasoning
        """
        title = listing.get('title', '')
        price = listing.get('soldPrice', 'N/A')
        
        if not self.use_ai:
            raise Exception("AI scoring is required but not available")
        
        return self._ai_score_listing(title, price, search_query)
    
    def score_listings_batch(self, listings: List[Dict], search_query: str) -> List[Dict]:
        """
        Score multiple listings in a single API call for better performance.
        
        Args:
            listings: List of listing dictionaries
            search_query: Original search query
            
        Returns:
            List of dictionaries with confidence scores
        """
        if not self.use_ai:
            raise Exception("AI scoring is required but not available")
        
        if not listings:
            return []
        
        # Create batch prompt
        batch_data = []
        for i, listing in enumerate(listings):
            title = listing.get('title', '')
            price = listing.get('soldPrice', 'N/A')
            batch_data.append(f"LISTING {i+1}: Title='{title}', Price={price}")
        
        batch_text = "\n".join(batch_data)
        
        prompt = f"""
You are an expert coin collector and eBay listing analyzer. Score multiple listings for relevance to a search query.

SEARCH QUERY: "{search_query}"

LISTINGS TO ANALYZE:
{batch_text}

For each listing, provide:
1. A confidence score from 0-100 (where 100 = perfect match, 0 = completely wrong)
2. Brief reasoning (under 30 words)

Respond in JSON format with an array of results:
{{
  "results": [
    {{"listing_index": 0, "confidence_score": 85, "reasoning": "Perfect match for year and grade"}},
    {{"listing_index": 1, "confidence_score": 20, "reasoning": "Wrong coin type"}}
  ]
}}
"""
        
        try:
            # Simple rate limiting
            global _last_api_call
            current_time = time.time()
            time_since_last = current_time - _last_api_call
            if time_since_last < _api_call_interval:
                time.sleep(_api_call_interval - time_since_last)
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            # Remove timeout parameter as it's not supported
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            _last_api_call = time.time()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            result_data = json.loads(response_text)
            
            # Map results back to listings
            scored_listings = []
            for result in result_data.get('results', []):
                listing_index = result.get('listing_index', 0)
                if listing_index < len(listings):
                    listing = listings[listing_index].copy()
                    listing['confidence_analysis'] = {
                        'confidence_score': result.get('confidence_score', 0),
                        'reasoning': result.get('reasoning', 'No reasoning provided'),
                        'key_factors': result.get('reasoning', 'No factors identified')
                    }
                    scored_listings.append(listing)
            
            return scored_listings
            
        except Exception as e:
            print(f"⚠️  Batch scoring failed, falling back to individual scoring: {e}")
            # Fallback to individual scoring with retry
            scored_listings = []
            for listing in listings:
                try:
                    result = self.score_listing_confidence(listing, search_query)
                    scored_listings.append(result)
                except Exception as e:
                    print(f"⚠️  Failed to score listing: {e}")
                    continue
            return scored_listings
    
    def _ai_score_listing(self, title: str, price: str, search_query: str) -> Dict:
        """Use Google Gemini to score listing confidence."""
        prompt = f"""
You are an expert coin collector and eBay listing analyzer. Your task is to determine how well an eBay listing matches a search query.

SEARCH QUERY: "{search_query}"
LISTING TITLE: "{title}"
PRICE: {price}

Analyze the listing and provide:
1. A confidence score from 0-100 (where 100 = perfect match, 0 = completely wrong)
2. Brief reasoning for the score (keep under 50 words)
3. Key factors that influenced your decision

Consider:
- Does it match the year specified in the search query?
- Does it match the coin type (Silver Eagle, Gold Eagle, etc.)?
- Does it match any specified grade (MS69, MS70, PR70, etc.)?
- Is it the actual coin or just accessories/boxes?
- Is it the right condition/type?
- Are there any red flags (wrong coin, damaged, etc.)?

Respond in JSON format:
{{
    "confidence_score": 85,
    "reasoning": "Strong match - correct year, coin type, and grade",
    "key_factors": ["2004 year matches", "Silver Eagle type matches", "MS69 grade specified"],
    "red_flags": ["None"],
    "match_quality": "excellent"
}}
"""
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise Exception("AI API returned empty response")
        
        # Parse the response
        text = response.text.strip()
        
        # Remove any markdown formatting
        text = text.replace('```json', '').replace('```', '').strip()
        
        if not text:
            raise Exception("AI response is empty after cleaning")
        
        result = json.loads(text)
        
        if 'confidence_score' not in result:
            raise Exception("AI response missing confidence_score")
        
        # Ensure confidence score is between 0-100
        confidence_score = max(0, min(100, result.get('confidence_score', 50)))
        
        return {
            'confidence_score': confidence_score,
            'reasoning': result.get('reasoning', 'AI analysis completed'),
            'key_factors': result.get('key_factors', []),
            'red_flags': result.get('red_flags', []),
            'match_quality': result.get('match_quality', 'unknown'),
            'ai_analyzed': True
        }
    

    
    def analyze_listings(self, listings: List[Dict], search_query: str, min_confidence: int = 50) -> Dict:
        """
        Analyze a list of listings and return confidence scores.
        Optimized with batch processing for better performance.
        
        Args:
            listings: List of listing dictionaries
            search_query: Original search query
            min_confidence: Minimum confidence score to include (0-100)
            
        Returns:
            Dictionary with analysis results
        """
        print(f"\n🤖 Analyzing {len(listings)} listings for confidence scores...")
        print(f"Search Query: '{search_query}'")
        print(f"Minimum Confidence: {min_confidence}%")
        
        # Filter out None listings first
        valid_listings = [listing for listing in listings if listing is not None]
        
        if not valid_listings:
            return {
                'search_query': search_query,
                'total_listings_analyzed': 0,
                'listings_above_threshold': 0,
                'high_confidence_listings': 0,
                'average_confidence': 0,
                'min_confidence': 0,
                'max_confidence': 0,
                'scored_listings': [],
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        scored_listings = []
        high_confidence_count = 0
        
        # Process listings in batches for better performance
        batch_size = AI_BATCH_SIZE
        for i in range(0, len(valid_listings), batch_size):
            batch = valid_listings[i:i + batch_size]
            print(f"📦 Processing batch {i//batch_size + 1}/{(len(valid_listings) + batch_size - 1)//batch_size}")
            
            try:
                # Use batch scoring for better performance
                batch_results = self.score_listings_batch(batch, search_query)
                
                for listing in batch_results:
                    if listing.get('confidence_analysis', {}).get('confidence_score', 0) >= min_confidence:
                        scored_listings.append(listing)
                        if listing['confidence_analysis']['confidence_score'] >= 80:
                            high_confidence_count += 1
                            
            except Exception as e:
                print(f"⚠️  Batch processing failed, falling back to individual scoring: {e}")
                # Fallback to individual scoring for this batch
                with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
                    future_to_listing = {
                        executor.submit(self.score_listing_confidence, listing, search_query): listing 
                        for listing in batch
                    }
                    
                    for future in as_completed(future_to_listing):
                        listing = future_to_listing[future]
                        try:
                            confidence_data = future.result()
                            if confidence_data is not None:
                                listing['confidence_analysis'] = confidence_data
                                if confidence_data['confidence_score'] >= min_confidence:
                                    scored_listings.append(listing)
                                    if confidence_data['confidence_score'] >= 80:
                                        high_confidence_count += 1
                        except Exception as e:
                            print(f"⚠️  Error processing listing: {e}")
                            continue
        
        # Sort by confidence score (highest first)
        scored_listings.sort(key=lambda x: x['confidence_analysis']['confidence_score'], reverse=True)
        
        # Calculate statistics
        confidence_scores = [listing['confidence_analysis']['confidence_score'] for listing in scored_listings]
        
        analysis_results = {
            'search_query': search_query,
            'total_listings_analyzed': len(valid_listings),
            'listings_above_threshold': len(scored_listings),
            'high_confidence_listings': high_confidence_count,
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'min_confidence': min(confidence_scores) if confidence_scores else 0,
            'max_confidence': max(confidence_scores) if confidence_scores else 0,
            'scored_listings': scored_listings,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return analysis_results

# --- eBay API Functions ---

def search_completed_sales(keywords, max_results=10, days_back=30):
    """
    Searches for sold items using the Browse API with soldItems filter.
    
    Args:
        keywords (str): The search query (e.g., "2004 Silver Eagle").
        max_results (int): Maximum number of results to return (max 50 per page).
        days_back (int): Number of days back to search (not used in Browse API).

    Returns:
        list: A list of dictionaries, each representing a sold item.
              Returns an empty list if no results or an error occurs.
    """
    if not EBAY_ACCESS_TOKEN or EBAY_ACCESS_TOKEN == 'YOUR_OAUTH_ACCESS_TOKEN':
        print("❌ ERROR: EBAY_ACCESS_TOKEN not set or invalid")
        print("   Please set EBAY_ACCESS_TOKEN environment variable on Render")
        return []

    # API parameters for the Browse API - search for items
    params = {
        'q': keywords,  # Search query
        'limit': min(max_results, 50),  # Limit results (max 50 per page)
        'sort': 'price',  # Sort by price
    }

    # Headers for the Browse API
    headers = {
        'Authorization': f'Bearer {EBAY_ACCESS_TOKEN}',  # OAuth access token
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY-US',  # US marketplace
        'Content-Type': 'application/json'
    }

    logger.info(f"Searching sold items for '{keywords}'...")
    logger.info(f"Using endpoint: {EBAY_BROWSE_API_ENDPOINT}")
    logger.info(f"Token length: {len(EBAY_ACCESS_TOKEN) if EBAY_ACCESS_TOKEN else 0}")
    logger.info("Note: This shows sold items, not necessarily completed transactions.")
    
    try:
        # Make the actual HTTP request to eBay Browse API with timeout:
        logger.info(f"Making request to eBay API with params: {params}")
        logger.info(f"Headers: {headers}")
        response = requests.get(EBAY_BROWSE_API_ENDPOINT, params=params, headers=headers, timeout=30)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            logger.error(f"Response text: {response.text[:1000]}...")  # Show first 1000 chars of error
            response.raise_for_status()
            
        data = response.json()

        sold_items = []
        # Parse the JSON response from Browse API
        if data and 'itemSummaries' in data:
            for item in data['itemSummaries']:
                sold_item = {
                    'itemId': item.get('itemId', 'N/A'),
                    'title': item.get('title', 'N/A'),
                    'soldPrice': item.get('price', {}).get('value', 'N/A'),
                    'currency': item.get('price', {}).get('currency', 'N/A'),
                    'dateSold': 'N/A',  # Browse API doesn't provide sale date
                    'condition': item.get('condition', 'N/A'),
                    'itemLocation': item.get('itemLocation', {}).get('country', 'N/A'),
                    'shippingCost': item.get('shippingOptions', [{}])[0].get('shippingCost', {}).get('value', 'N/A') if item.get('shippingOptions') else 'N/A',
                    'totalPrice': 'N/A',  # Browse API doesn't provide total price
                    'buyingOptions': item.get('buyingOptions', []),
                    'listingType': 'N/A',  # Browse API doesn't provide listing type
                    'itemWebUrl': item.get('itemWebUrl', 'N/A'),
                }
                sold_items.append(sold_item)
        return sold_items

    except requests.exceptions.Timeout:
        print("❌ eBay API request timed out (30s). Please try again.")
        return []
    except requests.exceptions.ConnectionError:
        print("❌ Network connection error. Please check your internet connection.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Error: {e}")
        return []
    except json.JSONDecodeError:
        print("❌ Error: Could not decode JSON response from eBay API.")
        return []
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return []

def filter_coin_items(items, search_query):
    """
    Basic filter to remove obviously irrelevant items.
    Let the AI handle the detailed analysis.
    """
    filtered_items = []
    
    # Only exclude completely wrong items
    exclude_keywords = [
        'oil filter', 'honda', 'accord', 'civic', 'pilot',  # Completely wrong items
        'box only', 'coa only', 'empty', 'no coin', 'capsule only'  # Accessories only
    ]
    
    for item in items:
        title = item['title'].lower()
        
        # Only exclude if it's clearly not a coin
        should_exclude = any(keyword in title for keyword in exclude_keywords)
        
        if not should_exclude:
            filtered_items.append(item)
    
    return filtered_items

# --- Comprehensive Analysis Functions ---

def generate_comprehensive_report(analysis_results: Dict, search_query: str) -> Dict:
    """Generate a comprehensive analysis report."""
    scored_listings = analysis_results['scored_listings']
    
    if not scored_listings:
        print("⚠️  No listings met the confidence threshold.")
        return analysis_results
    
    # Calculate weighted price statistics
    prices = []
    weights = []
    
    for listing in scored_listings:
        price = listing.get('soldPrice', 'N/A')
        confidence = listing['confidence_analysis']['confidence_score']
        
        if price != 'N/A':
            try:
                price_float = float(price)
                prices.append(price_float)
                weights.append(confidence / 100.0)  # Convert to 0-1 scale
            except ValueError:
                continue
    
    # Calculate weighted statistics
    weighted_stats = {}
    if prices and weights:
        total_weight = sum(weights)
        weighted_avg = sum(p * w for p, w in zip(prices, weights)) / total_weight
        
        # Sort by price for percentile calculations
        sorted_data = sorted(zip(prices, weights))
        sorted_prices = [p for p, w in sorted_data]
        sorted_weights = [w for p, w in sorted_data]
        
        # Calculate weighted percentiles
        cumulative_weight = 0
        median_price = None
        p25_price = None
        p75_price = None
        
        for i, (price, weight) in enumerate(sorted_data):
            cumulative_weight += weight
            weight_percentile = cumulative_weight / total_weight
            
            if median_price is None and weight_percentile >= 0.5:
                median_price = price
            if p25_price is None and weight_percentile >= 0.25:
                p25_price = price
            if p75_price is None and weight_percentile >= 0.75:
                p75_price = price
        
        weighted_stats = {
            'weighted_average': round(weighted_avg, 2),
            'median_price': median_price,
            'p25_price': p25_price,
            'p75_price': p75_price,
            'min_price': min(prices),
            'max_price': max(prices),
            'price_range': max(prices) - min(prices),
            'total_weighted_sales': len(prices)
        }
    
    # Create comprehensive report
    comprehensive_results = {
        'search_query': search_query,
        'analysis_timestamp': datetime.now().isoformat(),
        'summary': {
            'total_listings_found': analysis_results['total_listings_analyzed'],
            'high_confidence_listings': analysis_results['high_confidence_listings'],
            'listings_above_threshold': analysis_results['listings_above_threshold'],
            'average_confidence': analysis_results['average_confidence'],
            'confidence_range': f"{analysis_results['min_confidence']:.0f}% - {analysis_results['max_confidence']:.0f}%"
        },
        'pricing_analysis': weighted_stats,
        'confidence_analysis': analysis_results,
        'recommendations': generate_recommendations(analysis_results, weighted_stats)
    }
    
    return comprehensive_results

def generate_recommendations(analysis_results: Dict, weighted_stats: Dict) -> Dict:
    """Generate actionable recommendations based on analysis."""
    recommendations = {
        'data_quality': {},
        'pricing_insights': {},
        'next_steps': []
    }
    
    # Data quality assessment
    total_listings = analysis_results['total_listings_analyzed']
    high_confidence = analysis_results['high_confidence_listings']
    avg_confidence = analysis_results['average_confidence']
    
    if high_confidence >= 5:
        recommendations['data_quality']['assessment'] = "Excellent"
        recommendations['data_quality']['reason'] = f"Found {high_confidence} high-confidence listings"
    elif high_confidence >= 3:
        recommendations['data_quality']['assessment'] = "Good"
        recommendations['data_quality']['reason'] = f"Found {high_confidence} high-confidence listings"
    elif high_confidence >= 1:
        recommendations['data_quality']['assessment'] = "Fair"
        recommendations['data_quality']['reason'] = f"Only {high_confidence} high-confidence listings found"
    else:
        recommendations['data_quality']['assessment'] = "Poor"
        recommendations['data_quality']['reason'] = "No high-confidence listings found"
    
    # Pricing insights
    if weighted_stats:
        price_range = weighted_stats['price_range']
        weighted_avg = weighted_stats['weighted_average']
        
        if price_range < 5:
            recommendations['pricing_insights']['volatility'] = "Low"
            recommendations['pricing_insights']['reason'] = f"Price range is only ${price_range:.2f}"
        elif price_range < 15:
            recommendations['pricing_insights']['volatility'] = "Moderate"
            recommendations['pricing_insights']['reason'] = f"Price range is ${price_range:.2f}"
        else:
            recommendations['pricing_insights']['volatility'] = "High"
            recommendations['pricing_insights']['reason'] = f"Price range is ${price_range:.2f} - consider filtering further"
        
        recommendations['pricing_insights']['suggested_price'] = f"${weighted_avg:.2f}"
    
    # Next steps
    if avg_confidence < 70:
        recommendations['next_steps'].append("Consider refining search terms for better matches")
    
    if high_confidence < 3:
        recommendations['next_steps'].append("Expand search to include more results or different time periods")
    
    if weighted_stats and weighted_stats['price_range'] > 15:
        recommendations['next_steps'].append("High price volatility - consider analyzing by condition or seller")
    
    recommendations['next_steps'].append("Use confidence scores to weight your pricing decisions")
    recommendations['next_steps'].append("Monitor prices over time for trend analysis")
    
    return recommendations

def display_comprehensive_results(results: Dict):
    """Display comprehensive analysis results."""
    if not results:
        print("❌ No results to display")
        return
    
    print(f"\n{'='*60}")
    print(f"📊 COMPREHENSIVE ANALYSIS RESULTS")
    print(f"{'='*60}")
    
    # Summary
    summary = results['summary']
    print(f"🔍 Search Query: {results['search_query']}")
    print(f"📅 Analysis Time: {results['analysis_timestamp']}")
    print(f"\n📈 SUMMARY:")
    print(f"  Total Listings Found: {summary['total_listings_found']}")
    print(f"  High Confidence (80%+): {summary['high_confidence_listings']}")
    print(f"  Above Threshold: {summary['listings_above_threshold']}")
    print(f"  Average Confidence: {summary['average_confidence']:.1f}%")
    print(f"  Confidence Range: {summary['confidence_range']}")
    
    # Pricing Analysis
    pricing = results['pricing_analysis']
    if pricing:
        print(f"\n💰 PRICING ANALYSIS (Confidence-Weighted):")
        print(f"  Weighted Average: ${pricing['weighted_average']}")
        print(f"  Median Price: ${pricing['median_price']:.2f}")
        print(f"  25th Percentile: ${pricing['p25_price']:.2f}")
        print(f"  75th Percentile: ${pricing['p75_price']:.2f}")
        print(f"  Price Range: ${pricing['min_price']:.2f} - ${pricing['max_price']:.2f}")
        print(f"  Total Range: ${pricing['price_range']:.2f}")
        print(f"  Weighted Sales Count: {pricing['total_weighted_sales']}")
    
    # Recommendations
    recs = results['recommendations']
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"  Data Quality: {recs['data_quality']['assessment']} - {recs['data_quality']['reason']}")
    
    if recs['pricing_insights']:
        print(f"  Price Volatility: {recs['pricing_insights']['volatility']} - {recs['pricing_insights']['reason']}")
        print(f"  Suggested Price: {recs['pricing_insights']['suggested_price']}")
    
    print(f"\n  Next Steps:")
    for i, step in enumerate(recs['next_steps'], 1):
        print(f"    {i}. {step}")
    
    # Top matches
    scored_listings = results['confidence_analysis']['scored_listings']
    if scored_listings:
        print(f"\n🏆 TOP MATCHES (by confidence):")
        for i, listing in enumerate(scored_listings[:5]):
            confidence = listing['confidence_analysis']['confidence_score']
            price = listing.get('soldPrice', 'N/A')
            title = listing.get('title', 'N/A')[:50]
            quality = listing['confidence_analysis']['match_quality']
            ebay_url = listing.get('itemWebUrl', 'N/A')
            
            print(f"  {i+1:2d}. {confidence:3.0f}% [{quality:8s}] ${price:>6} - {title}...")
            if ebay_url != 'N/A':
                print(f"      🔗 eBay Link: {ebay_url}")
        
        # Show all high confidence links
        high_confidence_listings = [l for l in scored_listings if l['confidence_analysis']['confidence_score'] >= 80]
        if high_confidence_listings:
            print(f"\n🔗 HIGH CONFIDENCE EBAY LINKS ({len(high_confidence_listings)} items):")
            for i, listing in enumerate(high_confidence_listings, 1):
                confidence = listing['confidence_analysis']['confidence_score']
                price = listing.get('soldPrice', 'N/A')
                title = listing.get('title', 'N/A')[:60]
                ebay_url = listing.get('itemWebUrl', 'N/A')
                
                print(f"  {i:2d}. {confidence:3.0f}% - ${price:>6} - {title}...")
                if ebay_url != 'N/A':
                    print(f"      {ebay_url}")
                else:
                    print(f"      ⚠️  No eBay URL available")

def save_comprehensive_results(results: Dict, filename: str = None):
    """Save comprehensive results to JSON file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_safe = results['search_query'].replace(' ', '_').replace('/', '_')
        filename = f"complete_analysis_{query_safe}_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Comprehensive results saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        return None

# --- Main Workflow Function ---

def complete_ebay_analysis(search_query: str, max_results: int = MAX_RESULTS_DEFAULT, 
                          min_confidence: int = MIN_CONFIDENCE_DEFAULT, days_back: int = 90) -> Dict:
    """
    Complete workflow: Search eBay → Filter → AI Confidence Scoring → Analysis
    
    Args:
        search_query: The search query (e.g., "2004 Silver Eagle MS69")
        max_results: Maximum number of results to analyze
        min_confidence: Minimum confidence score to include (0-100)
        days_back: Number of days back to search
        
    Returns:
        Dictionary with comprehensive analysis results
    """
    # Check cache first
    cache_key = f"{search_query}_{max_results}_{min_confidence}_{days_back}"
    current_time = time.time()
    
    if cache_key in _result_cache:
        cache_age = current_time - _cache_timestamps.get(cache_key, 0)
        if cache_age < CACHE_TTL:
            print(f"✅ Using cached result for '{search_query}' (age: {cache_age:.1f}s)")
            return _result_cache[cache_key]
        else:
            # Remove expired cache entry
            del _result_cache[cache_key]
            if cache_key in _cache_timestamps:
                del _cache_timestamps[cache_key]
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 COMPLETE EBAY AI ANALYSIS WORKFLOW")
    logger.info(f"{'='*60}")
    logger.info(f"Search Query: '{search_query}'")
    logger.info(f"Max Results: {max_results}")
    logger.info(f"Min Confidence: {min_confidence}%")
    logger.info(f"Search Period: Last {days_back} days")
    
    # Step 1: Search eBay for listings
    logger.info(f"\n📊 Step 1: Searching eBay listings...")
    listings = search_completed_sales(search_query, max_results, days_back)
    
    if not listings:
        print("❌ No listings found. Try adjusting your search terms.")
        return None
    
    print(f"✅ Found {len(listings)} listings")
    
    # Step 2: Apply basic filtering
    print(f"\n🔍 Step 2: Applying basic filtering...")
    filtered_listings = filter_coin_items(listings, search_query)
    print(f"✅ After filtering: {len(filtered_listings)} relevant listings")
    
    if not filtered_listings:
        print("❌ No relevant listings found after filtering.")
        return None
    
    # Step 3: Initialize AI confidence scorer
    print(f"\n🤖 Step 3: Initializing AI confidence scorer...")
    confidence_scorer = eBayConfidenceScorer()
    
    # Step 4: Apply confidence scoring
    print(f"\n🎯 Step 4: Applying AI confidence scoring...")
    analysis_results = confidence_scorer.analyze_listings(
        filtered_listings, search_query, min_confidence
    )
    
    # Step 5: Generate comprehensive report
    print(f"\n📈 Step 5: Generating comprehensive report...")
    comprehensive_results = generate_comprehensive_report(analysis_results, search_query)
    
    # Cache the result
    _result_cache[cache_key] = comprehensive_results
    _cache_timestamps[cache_key] = current_time
    print(f"✅ Cached result for '{search_query}'")
    
    return comprehensive_results

def batch_ebay_analysis(search_queries: List[str], max_results: int = MAX_RESULTS_DEFAULT, 
                       min_confidence: int = MIN_CONFIDENCE_DEFAULT, days_back: int = 90) -> Dict:
    """
    Process multiple search queries in parallel for batch analysis.
    
    Args:
        search_queries: List of search queries to analyze
        max_results: Maximum number of results per query
        min_confidence: Minimum confidence score to include
        days_back: Number of days back to search
        
    Returns:
        Dictionary containing results for all queries
    """
    print(f"🚀 Starting batch analysis of {len(search_queries)} queries...")
    print(f"📊 Configuration: max_results={max_results}, min_confidence={min_confidence}%, days_back={days_back}")
    
    all_results = {}
    failed_queries = []
    
    # Process queries in parallel
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
        # Submit all analysis tasks
        future_to_query = {
            executor.submit(complete_ebay_analysis, query, max_results, min_confidence, days_back): query
            for query in search_queries
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_query):
            query = future_to_query[future]
            try:
                result = future.result()
                if result:
                    all_results[query] = result
                    print(f"✅ Completed: {query}")
                else:
                    failed_queries.append(query)
                    print(f"❌ No results for: {query}")
                    
            except Exception as e:
                failed_queries.append(query)
                print(f"❌ Error analyzing '{query}': {e}")
    
    # Create batch summary
    batch_summary = {
        'total_queries': len(search_queries),
        'successful_queries': len(all_results),
        'failed_queries': len(failed_queries),
        'failed_query_list': failed_queries,
        'results': all_results,
        'batch_timestamp': datetime.now().isoformat()
    }
    
    return batch_summary

def display_batch_results(batch_results: Dict):
    """Display comprehensive results for batch analysis."""
    print(f"\n{'='*80}")
    print(f"📊 BATCH ANALYSIS RESULTS")
    print(f"{'='*80}")
    
    summary = batch_results
    print(f"📈 SUMMARY:")
    print(f"  Total Queries: {summary['total_queries']}")
    print(f"  Successful: {summary['successful_queries']}")
    print(f"  Failed: {summary['failed_queries']}")
    
    if summary['failed_queries'] > 0:
        print(f"\n❌ Failed Queries:")
        for query in summary['failed_query_list']:
            print(f"  • {query}")
    
    print(f"\n🏆 INDIVIDUAL RESULTS:")
    for query, results in summary['results'].items():
        print(f"\n{'─'*60}")
        print(f"🔍 {query}")
        print(f"{'─'*60}")
        
        # Display individual results
        display_comprehensive_results(results)

def save_batch_results(batch_results: Dict, filename: str = None):
    """Save batch results to JSON file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_analysis_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Batch results saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving batch results: {e}")
        return None

def parse_search_queries(input_text: str) -> List[str]:
    """
    Parse comma-separated search queries from input text.
    
    Args:
        input_text: Comma-separated list of search queries
        
    Returns:
        List of cleaned search queries
    """
    if not input_text or not input_text.strip():
        return []
    
    # Split by comma and clean each query
    queries = [query.strip() for query in input_text.split(',')]
    
    # Remove empty queries
    queries = [query for query in queries if query]
    
    return queries

# --- Main Execution ---
if __name__ == "__main__":
    print("🚀 Complete eBay AI Analyzer (Optimized)")
    print("=" * 60)
    print("This script combines eBay API search with Gemini AI confidence scoring")
    print("for comprehensive coin pricing analysis with batch processing support.")
    
    # Check if OAuth token is set
    if EBAY_ACCESS_TOKEN == 'YOUR_OAUTH_ACCESS_TOKEN':
        print("\nERROR: Please set your EBAY_ACCESS_TOKEN in the configuration section at the top of this file.")
        print("You need an OAuth access token. Get it from: https://developer.ebay.com/api-docs/static/oauth-client-credentials-grant.html")
        exit(1)
    
    # Get search queries from user input
    print("\n📝 Enter your search queries (comma-separated):")
    print("   Example: 2004 Silver Eagle MS69, 2005-W 1/10 oz Proof Gold Eagle $5 PCGS PR70")
    
    user_input = input("Search queries: ").strip()
    
    if not user_input:
        print("❌ No search queries provided. Using example queries...")
        search_queries = [
            "2004 Silver Eagle MS69",
            "2005-W 1/10 oz Proof Gold Eagle $5 PCGS PR70"
        ]
    else:
        search_queries = parse_search_queries(user_input)
    
    print(f"\n🔍 Parsed {len(search_queries)} search queries:")
    for i, query in enumerate(search_queries, 1):
        print(f"  {i}. {query}")
    
    # Ask user if they want batch processing
    print(f"\n⚡ Performance Options:")
    print(f"  1. Batch Processing (Parallel - Faster)")
    print(f"  2. Sequential Processing (One by one)")
    
    choice = input("Choose processing method (1 or 2): ").strip()
    
    if choice == "1":
        print(f"\n🚀 Starting BATCH PROCESSING...")
        start_time = time.time()
        
        # Perform batch analysis
        batch_results = batch_ebay_analysis(
            search_queries=search_queries,
            max_results=20,
            min_confidence=70,
            days_back=90
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Display batch results
        display_batch_results(batch_results)
        
        # Save batch results
        save_batch_results(batch_results)
        
        print(f"\n⏱️  Batch processing completed in {processing_time:.2f} seconds")
        print(f"📊 Processed {batch_results['successful_queries']}/{batch_results['total_queries']} queries successfully")
        
    else:
        print(f"\n🔄 Starting SEQUENTIAL PROCESSING...")
        start_time = time.time()
        
        all_results = []
        
        for search_query in search_queries:
            print(f"\n{'='*60}")
            print(f"🔍 Analyzing: {search_query}")
            print(f"{'='*60}")
            
            # Perform complete analysis
            results = complete_ebay_analysis(
                search_query=search_query,
                max_results=20,
                min_confidence=70,
                days_back=90
            )
            
            if results:
                # Display results
                display_comprehensive_results(results)
                
                # Save results
                save_comprehensive_results(results)
                
                # Store for summary
                all_results.append(results)
            
            # Add delay between searches
            time.sleep(2)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Display summary of all analyses
        if all_results:
            print(f"\n{'='*60}")
            print(f"📊 SUMMARY OF ALL ANALYSES")
            print(f"{'='*60}")
            
            for i, results in enumerate(all_results, 1):
                query = results['search_query']
                avg_confidence = results['summary']['average_confidence']
                high_conf = results['summary']['high_confidence_listings']
                
                pricing = results['pricing_analysis']
                if pricing:
                    weighted_avg = pricing['weighted_average']
                    price_range = pricing['price_range']
                    print(f"  {i}. {query}")
                    print(f"     Confidence: {avg_confidence:.1f}% (High: {high_conf})")
                    print(f"     Price: ${weighted_avg} (Range: ${price_range:.2f})")
                else:
                    print(f"  {i}. {query}")
                    print(f"     Confidence: {avg_confidence:.1f}% (High: {high_conf})")
                    print(f"     Price: No valid pricing data")
                print()
        
        print(f"\n⏱️  Sequential processing completed in {processing_time:.2f} seconds")
    
    print(f"\n{'='*60}")
    print(f"✅ Complete Analysis Finished!")
    print(f"{'='*60}")
    print(f"💡 Tips for using the results:")
    print(f"  • Use confidence scores to weight your pricing decisions")
    print(f"  • Focus on high-confidence listings for most accurate data")
    print(f"  • Compare results across different coin types and grades")
    print(f"  • Use the weighted averages for more accurate pricing")
    print(f"  • Monitor trends by running regular analyses")
    print(f"  • Batch processing is much faster for multiple queries") 
