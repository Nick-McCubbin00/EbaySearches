#!/usr/bin/env python3
"""
Integrated eBay Analyzer with AI Confidence Scoring
Combines eBay API search with intelligent confidence scoring for accurate coin pricing analysis
"""

import json
import time
from typing import Dict
from datetime import datetime
# Import functions from the main eBay API file
import importlib.util
import sys

# Load the API-Ebay module
spec = importlib.util.spec_from_file_location("API_Ebay", "API-Ebay.py")
api_ebay = importlib.util.module_from_spec(spec)
sys.modules["API_Ebay"] = api_ebay
spec.loader.exec_module(api_ebay)

# Import the functions we need
search_completed_sales = api_ebay.search_completed_sales
display_completed_sales = api_ebay.display_completed_sales
from AI_Confidence_Scorer import eBayConfidenceScorer, save_analysis_results

class IntegratedEbayAnalyzer:
    """
    Integrated system that combines eBay API search with AI confidence scoring.
    Provides comprehensive coin pricing analysis with quality assessment.
    """
    
    def __init__(self, gemini_api_key: str = None):
        """Initialize the integrated analyzer."""
        self.confidence_scorer = eBayConfidenceScorer(gemini_api_key)
        print("🚀 Integrated eBay Analyzer Initialized")
        print(f"   AI Confidence Scoring: {'Enabled' if self.confidence_scorer.use_ai else 'Rule-based only'}")
    
    def analyze_coin_search(self, search_query: str, max_results: int = 20, 
                          min_confidence: int = 70, days_back: int = 90) -> Dict:
        """
        Perform comprehensive coin analysis with confidence scoring.
        
        Args:
            search_query: The search query (e.g., "2004 Silver Eagle MS69")
            max_results: Maximum number of results to analyze
            min_confidence: Minimum confidence score to include (0-100)
            days_back: Number of days back to search
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        print(f"\n{'='*60}")
        print(f"🔍 COMPREHENSIVE COIN ANALYSIS")
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
        
        # Step 2: Apply confidence scoring
        print(f"\n🤖 Step 2: Analyzing confidence scores...")
        analysis_results = self.confidence_scorer.analyze_listings(
            listings, search_query, min_confidence
        )
        
        # Step 3: Generate comprehensive report
        print(f"\n📈 Step 3: Generating comprehensive report...")
        comprehensive_results = self._generate_comprehensive_report(
            analysis_results, search_query
        )
        
        return comprehensive_results
    
    def _generate_comprehensive_report(self, analysis_results: Dict, search_query: str) -> Dict:
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
            'recommendations': self._generate_recommendations(analysis_results, weighted_stats)
        }
        
        return comprehensive_results
    
    def _generate_recommendations(self, analysis_results: Dict, weighted_stats: Dict) -> Dict:
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
    
    def display_comprehensive_results(self, results: Dict):
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
    
    def save_comprehensive_results(self, results: Dict, filename: str = None):
        """Save comprehensive results to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            query_safe = results['search_query'].replace(' ', '_').replace('/', '_')
            filename = f"comprehensive_analysis_{query_safe}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Comprehensive results saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return None

# --- Main Execution ---
if __name__ == "__main__":
    print("🚀 Integrated eBay Coin Analyzer")
    print("=" * 50)
    
    # Initialize analyzer (add your Gemini API key here if you have one)
    analyzer = IntegratedEbayAnalyzer()
    
    # Example searches - modify these based on your needs
    search_queries = [
        "2004 Silver Eagle MS69",
        "2004 American Silver Eagle 1 Oz"
    ]
    
    for search_query in search_queries:
        print(f"\n{'='*60}")
        print(f"🔍 Analyzing: {search_query}")
        print(f"{'='*60}")
        
        # Perform comprehensive analysis
        results = analyzer.analyze_coin_search(
            search_query=search_query,
            max_results=20,
            min_confidence=70,  # Only include listings with 70%+ confidence
            days_back=90
        )
        
        if results:
            # Display results
            analyzer.display_comprehensive_results(results)
            
            # Save results
            analyzer.save_comprehensive_results(results)
        
        # Add delay between searches
        time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"✅ Analysis Complete!")
    print(f"{'='*60}")
    print(f"💡 Tips for using the results:")
    print(f"  • Use confidence scores to weight your pricing decisions")
    print(f"  • Focus on high-confidence listings for most accurate data")
    print(f"  • Monitor trends over time by running regular analyses")
    print(f"  • Adjust confidence thresholds based on your needs") 