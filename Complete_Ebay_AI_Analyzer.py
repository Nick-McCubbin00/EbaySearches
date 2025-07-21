#!/usr/bin/env python3
"""
Complete eBay AI Analyzer
Combines eBay API search with Gemini AI confidence scoring in one comprehensive workflow
"""

import requests
import json
import os
import time
from typing import List, Dict
from datetime import datetime, timedelta
import google.generativeai as genai

# --- Configuration ---
# eBay API Configuration
EBAY_ACCESS_TOKEN = os.getenv('EBAY_ACCESS_TOKEN')  # Get from environment variable
EBAY_BROWSE_API_ENDPOINT = "https://api.ebay.com/buy/browse/v1/item_summary/search"

# Google Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # Get from environment variable

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
        elif GEMINI_API_KEY != "your-gemini-api-key-here":
            genai.configure(api_key=GEMINI_API_KEY)
        else:
            print("⚠️  Warning: No Gemini API key provided. Using rule-based scoring only.")
            self.use_ai = False
            return
            
        self.use_ai = True
        print("✅ AI confidence scoring enabled with Google Gemini")
    
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
        
        if self.use_ai:
            return self._ai_score_listing(title, price, search_query)
        else:
            return self._rule_based_score_listing(title, price, search_query)
    
    def _ai_score_listing(self, title: str, price: str, search_query: str) -> Dict:
        """Use Google Gemini to score listing confidence."""
        try:
            prompt = f"""
You are an expert coin collector and eBay listing analyzer. Your task is to determine how well an eBay listing matches a search query.

SEARCH QUERY: "{search_query}"
LISTING TITLE: "{title}"
PRICE: {price}

Analyze the listing and provide:
1. A confidence score from 0-100 (where 100 = perfect match, 0 = completely wrong)
2. Brief reasoning for the score
3. Key factors that influenced your decision

Consider:
- Does it match the year specified in the search query?
- Does it match the coin type (Silver Eagle)?
- Does it match any specified grade (MS69, MS70, etc.)?
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

            # Initialize Gemini model
            model = genai.GenerativeModel('gemini-2.5-pro')
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Check if response is valid
            if not response or not response.text:
                print(f"⚠️  AI response is empty, using rule-based scoring")
                return self._rule_based_score_listing(title, price, search_query)
                
            ai_response = response.text.strip()
            
            # Try to extract JSON from the response
            try:
                # Remove any markdown formatting
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
                
                # Check if response is empty after cleaning
                if not ai_response:
                    print(f"⚠️  AI response is empty after cleaning, using rule-based scoring")
                    return self._rule_based_score_listing(title, price, search_query)
                    
                result = json.loads(ai_response)
                
                return {
                    'confidence_score': result.get('confidence_score', 50),
                    'reasoning': result.get('reasoning', 'AI analysis completed'),
                    'key_factors': result.get('key_factors', []),
                    'red_flags': result.get('red_flags', []),
                    'match_quality': result.get('match_quality', 'unknown'),
                    'ai_analyzed': True
                }
                
            except json.JSONDecodeError:
                # Fallback to rule-based if AI response is malformed
                print(f"⚠️  AI response parsing failed, using rule-based scoring")
                return self._rule_based_score_listing(title, price, search_query)
                
        except Exception as e:
            print(f"⚠️  AI scoring failed: {e}, using rule-based scoring")
            return self._rule_based_score_listing(title, price, search_query)
    
    def _rule_based_score_listing(self, title: str, price: str, search_query: str) -> Dict:
        """Rule-based scoring system as fallback."""
        title_lower = title.lower()
        query_lower = search_query.lower()
        
        score = 50  # Start with neutral score
        reasoning = []
        key_factors = []
        red_flags = []
        
        # Extract search components
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', query_lower)
        target_year = year_match.group() if year_match else None
        
        year_match = target_year in title_lower if target_year else True  # If no year specified, don't penalize
        eagle_match = any(term in title_lower for term in ['silver eagle', 'ase']) and any(term in query_lower for term in ['silver eagle', 'ase'])
        
        # Grade matching
        grade_keywords = ['ms6', 'ms7', 'ms8', 'ms9', 'ms67', 'ms68', 'ms69', 'ms70', 'pf6', 'pf7', 'pf8', 'pf9', 'pf69', 'pf70', 'proof']
        search_grade = None
        listing_grade = None
        
        for grade in grade_keywords:
            if grade in query_lower:
                search_grade = grade
            if grade in title_lower:
                listing_grade = grade
        
        # Scoring logic
        if target_year:
            if year_match:
                score += 20
                key_factors.append(f"{target_year} year matches")
            else:
                score -= 30
                red_flags.append(f"Year mismatch: expected {target_year}")
        else:
            # No specific year requested, don't penalize
            score += 5
            key_factors.append("No specific year requested")
        
        if eagle_match:
            score += 25
            key_factors.append("Silver Eagle type matches")
        else:
            score -= 40
            red_flags.append("Wrong coin type")
        
        # Grade matching
        if search_grade and listing_grade:
            if search_grade == listing_grade:
                score += 20
                key_factors.append(f"Grade {search_grade.upper()} matches")
            else:
                score -= 15
                red_flags.append(f"Grade mismatch: expected {search_grade.upper()}, got {listing_grade.upper()}")
        elif search_grade and not listing_grade:
            score -= 10
            red_flags.append(f"Expected grade {search_grade.upper()} not found")
        elif not search_grade and listing_grade:
            score -= 5
            red_flags.append(f"Unexpected grade {listing_grade.upper()} in listing")
        
        # Red flag detection
        red_flag_keywords = [
            'box only', 'coa only', 'empty', 'no coin', 'capsule only',
            'oil filter', 'honda', 'accord', 'civic', 'pilot',
            'walking liberty', 'mercury', 'barber', 'seated',
            'colorized', 'color', 'colored', 'painted'
        ]
        
        for flag in red_flag_keywords:
            if flag in title_lower:
                score -= 20
                red_flags.append(f"Contains '{flag}'")
        
        # Determine match quality
        if score >= 80:
            match_quality = "excellent"
        elif score >= 60:
            match_quality = "good"
        elif score >= 40:
            match_quality = "fair"
        else:
            match_quality = "poor"
        
        # Generate reasoning
        if key_factors:
            reasoning.append(f"Positive factors: {', '.join(key_factors)}")
        if red_flags:
            reasoning.append(f"Red flags: {', '.join(red_flags)}")
        
        reasoning = " | ".join(reasoning) if reasoning else "Basic analysis completed"
        
        return {
            'confidence_score': max(0, min(100, score)),  # Clamp between 0-100
            'reasoning': reasoning,
            'key_factors': key_factors,
            'red_flags': red_flags,
            'match_quality': match_quality,
            'ai_analyzed': False
        }
    
    def analyze_listings(self, listings: List[Dict], search_query: str, min_confidence: int = 50) -> Dict:
        """
        Analyze a list of listings and return confidence scores.
        
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
        
        scored_listings = []
        high_confidence_count = 0
        
        for i, listing in enumerate(listings):
            print(f"  Analyzing listing {i+1}/{len(listings)}: {listing.get('title', 'N/A')[:50]}...")
            
            confidence_data = self.score_listing_confidence(listing, search_query)
            listing['confidence_analysis'] = confidence_data
            
            if confidence_data['confidence_score'] >= min_confidence:
                scored_listings.append(listing)
                if confidence_data['confidence_score'] >= 80:
                    high_confidence_count += 1
        
        # Sort by confidence score (highest first)
        scored_listings.sort(key=lambda x: x['confidence_analysis']['confidence_score'], reverse=True)
        
        # Calculate statistics
        confidence_scores = [listing['confidence_analysis']['confidence_score'] for listing in scored_listings]
        
        analysis_results = {
            'search_query': search_query,
            'total_listings_analyzed': len(listings),
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
    if EBAY_ACCESS_TOKEN == 'YOUR_OAUTH_ACCESS_TOKEN':
        print("ERROR: Please set your EBAY_ACCESS_TOKEN in the configuration section at the top of this file.")
        return []

    # API parameters for the Browse API with soldItems filter
    params = {
        'q': keywords,  # Search query
        'limit': min(max_results, 50),  # Limit results (max 50 per page)
        'filter': 'soldItems',  # Only show sold/completed items
        'sort': 'price',  # Sort by price
    }

    # Headers for the Browse API
    headers = {
        'Authorization': f'Bearer {EBAY_ACCESS_TOKEN}',  # OAuth access token
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY-US',  # US marketplace
        'Content-Type': 'application/json'
    }

    print(f"Searching sold items for '{keywords}'...")
    print(f"Using endpoint: {EBAY_BROWSE_API_ENDPOINT}")
    print("Note: This shows sold items, not necessarily completed transactions.")
    
    try:
        # Make the actual HTTP request to eBay Browse API:
        response = requests.get(EBAY_BROWSE_API_ENDPOINT, params=params, headers=headers)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response text: {response.text[:500]}...")  # Show first 500 chars of error
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

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return []
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from eBay API.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

def filter_silver_eagle_items(items, search_query):
    """
    Filter items to only include Silver Eagles based on search query.
    If search query includes a grade (MS69, MS70, etc.), allows graded coins.
    Otherwise, excludes graded coins and special editions.
    """
    filtered_items = []
    search_query_lower = search_query.lower()
    
    # Extract year from search query
    import re
    year_match = re.search(r'\b(19|20)\d{2}\b', search_query)
    target_year = year_match.group() if year_match else None
    
    # Keywords that indicate we want to KEEP the item
    keep_keywords = [
        'silver eagle', 'american silver eagle', 'ase', '1 oz', '1 ounce', 
        'troy oz', '.999', 'fine silver', 'bullion', 'uncirculated', 'bu', 'gem bu'
    ]
    
    # Add the target year if found
    if target_year:
        keep_keywords.append(target_year)
        print(f"🔍 Search includes year '{target_year}' - filtering for this year")
    
    # Keywords that indicate we want to EXCLUDE the item (unless specifically searched for)
    exclude_keywords = [
        'colorized', 'color', 'colored', 'painted',                   # Colorized coins
        'walking liberty', 'mercury', 'barber', 'seated',             # Wrong coin types
        'box only', 'coa only', 'empty', 'no coin', 'capsule only',   # Accessories only
        'oil filter', 'honda', 'accord', 'civic', 'pilot',           # Completely wrong items
        'littleton', 'littleton holder', 'whitman', 'folder',        # Holders/albums
        'montauk', 'lighthouse', 'special edition', 'limited',       # Special editions
        'toning', 'spot', 'damage', 'lower grade', 'worn'            # Damaged/toned
    ]
    
    # Check if search query includes a specific grade
    grade_keywords = ['ms6', 'ms7', 'ms8', 'ms9', 'ms67', 'ms68', 'ms69', 'ms70', 
                     'pf6', 'pf7', 'pf8', 'pf9', 'pf69', 'pf70', 'proof']
    search_includes_grade = any(grade in search_query_lower for grade in grade_keywords)
    
    # If searching for a specific grade, add that grade to keep keywords
    if search_includes_grade:
        # Find the specific grade in the search query
        for grade in grade_keywords:
            if grade in search_query_lower:
                keep_keywords.append(grade)
                print(f"🔍 Search includes grade '{grade.upper()}' - allowing graded coins")
                break
    
    for item in items:
        title = item['title'].lower()
        
        # Check if title contains any exclude keywords
        should_exclude = any(keyword in title for keyword in exclude_keywords)
        
        # Check if title contains enough keep keywords
        keep_count = sum(1 for keyword in keep_keywords if keyword in title)
        should_keep = keep_count >= 3  # Need at least 3 matching keywords
        
        # Additional check: must contain the target year and "silver eagle" or "ase"
        has_year = target_year in title if target_year else True  # If no year specified, don't filter by year
        has_eagle = any(eagle in title for eagle in ['silver eagle', 'ase'])
        
        # If searching for a specific grade, also check that the grade matches
        grade_matches = True
        if search_includes_grade:
            # Find the specific grade we're looking for
            target_grade = None
            for grade in grade_keywords:
                if grade in search_query_lower:
                    target_grade = grade
                    break
            
            if target_grade:
                # Check if the item title contains the target grade
                grade_matches = target_grade in title
        
        if not should_exclude and should_keep and has_year and has_eagle and grade_matches:
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
            
            print(f"  {i+1:2d}. {confidence:3.0f}% [{quality:8s}] ${price:>6} - {title}...")

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

def complete_ebay_analysis(search_query: str, max_results: int = 20, 
                          min_confidence: int = 70, days_back: int = 90) -> Dict:
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
    print(f"\n{'='*60}")
    print(f"🚀 COMPLETE EBAY AI ANALYSIS WORKFLOW")
    print(f"{'='*60}")
    print(f"Search Query: '{search_query}'")
    print(f"Max Results: {max_results}")
    print(f"Min Confidence: {min_confidence}%")
    print(f"Search Period: Last {days_back} days")
    
    # Step 1: Search eBay for listings
    print(f"\n📊 Step 1: Searching eBay listings...")
    listings = search_completed_sales(search_query, max_results, days_back)
    
    if not listings:
        print("❌ No listings found. Try adjusting your search terms.")
        return None
    
    print(f"✅ Found {len(listings)} listings")
    
    # Step 2: Apply basic filtering
    print(f"\n🔍 Step 2: Applying basic filtering...")
    filtered_listings = filter_silver_eagle_items(listings, search_query)
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
    
    return comprehensive_results

# --- Main Execution ---
if __name__ == "__main__":
    print("🚀 Complete eBay AI Analyzer")
    print("=" * 50)
    print("This script combines eBay API search with Gemini AI confidence scoring")
    print("for comprehensive coin pricing analysis.")
    
    # Check if OAuth token is set
    if EBAY_ACCESS_TOKEN == 'YOUR_OAUTH_ACCESS_TOKEN':
        print("\nERROR: Please set your EBAY_ACCESS_TOKEN in the configuration section at the top of this file.")
        print("You need an OAuth access token. Get it from: https://developer.ebay.com/api-docs/static/oauth-client-credentials-grant.html")
        exit(1)
    
    # Example searches - modify these based on your needs
    search_queries = [
        "2004 Silver Eagle MS69",
        "2004 American Silver Eagle 1 Oz"
    ]
    
    all_results = []
    
    for search_query in search_queries:
        print(f"\n{'='*60}")
        print(f"🔍 Analyzing: {search_query}")
        print(f"{'='*60}")
        
        # Perform complete analysis
        results = complete_ebay_analysis(
            search_query=search_query,
            max_results=20,
            min_confidence=70,  # Only include listings with 70%+ confidence
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
    
    print(f"\n{'='*60}")
    print(f"✅ Complete Analysis Finished!")
    print(f"{'='*60}")
    print(f"💡 Tips for using the results:")
    print(f"  • Use confidence scores to weight your pricing decisions")
    print(f"  • Focus on high-confidence listings for most accurate data")
    print(f"  • Compare results across different coin types and grades")
    print(f"  • Use the weighted averages for more accurate pricing")
    print(f"  • Monitor trends by running regular analyses") 
