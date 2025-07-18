import json
import re
from typing import List, Dict, Tuple
import google.generativeai as genai
from datetime import datetime

# --- Configuration ---
# Set your Google Gemini API key here
GEMINI_API_KEY = "AIzaSyAPIUPQ_gNZeqiLv7Q3oqPEQ98f4xU4GoY"  # Replace with your actual API key

# --- AI Confidence Scoring System ---

class eBayConfidenceScorer:
    """
    AI-powered system to score how well eBay listings match search criteria.
    Uses gemini's GPT models to analyze listing titles and determine relevance.
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
- Does it match the year (2004)?
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
            ai_response = response.text.strip()
            
            # Try to extract JSON from the response
            try:
                # Remove any markdown formatting
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
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
        year_match = '2004' in title_lower and '2004' in query_lower
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
        if year_match:
            score += 20
            key_factors.append("2004 year matches")
        else:
            score -= 30
            red_flags.append("Year mismatch")
        
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
    
    def display_analysis_results(self, results: Dict):
        """Display the analysis results in a formatted way."""
        print(f"\n{'='*60}")
        print(f"🤖 AI CONFIDENCE ANALYSIS RESULTS")
        print(f"{'='*60}")
        print(f"Search Query: {results['search_query']}")
        print(f"Analysis Time: {results['analysis_timestamp']}")
        print(f"\n📊 SUMMARY:")
        print(f"  Total Listings Analyzed: {results['total_listings_analyzed']}")
        print(f"  Listings Above Threshold: {results['listings_above_threshold']}")
        print(f"  High Confidence (80%+): {results['high_confidence_listings']}")
        print(f"  Average Confidence: {results['average_confidence']:.1f}%")
        print(f"  Confidence Range: {results['min_confidence']:.0f}% - {results['max_confidence']:.0f}%")
        
        print(f"\n🏆 TOP MATCHES (Confidence Score):")
        for i, listing in enumerate(results['scored_listings'][:10]):  # Show top 10
            confidence = listing['confidence_analysis']['confidence_score']
            quality = listing['confidence_analysis']['match_quality']
            title = listing.get('title', 'N/A')[:60]
            price = listing.get('soldPrice', 'N/A')
            
            print(f"  {i+1:2d}. {confidence:3.0f}% [{quality:8s}] ${price:>6} - {title}")
        
        print(f"\n🔍 DETAILED ANALYSIS:")
        for i, listing in enumerate(results['scored_listings'][:5]):  # Show detailed analysis for top 5
            confidence = listing['confidence_analysis']['confidence_score']
            reasoning = listing['confidence_analysis']['reasoning']
            title = listing.get('title', 'N/A')
            price = listing.get('soldPrice', 'N/A')
            
            print(f"\n  {i+1}. Confidence: {confidence}%")
            print(f"     Title: {title}")
            print(f"     Price: ${price}")
            print(f"     Reasoning: {reasoning}")
            
            if listing['confidence_analysis']['key_factors']:
                print(f"     ✅ Factors: {', '.join(listing['confidence_analysis']['key_factors'])}")
            if listing['confidence_analysis']['red_flags']:
                print(f"     ⚠️  Red Flags: {', '.join(listing['confidence_analysis']['red_flags'])}")

# --- Utility Functions ---

def load_ebay_data(filename: str) -> List[Dict]:
    """Load eBay data from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in file: {filename}")
        return []

def save_analysis_results(results: Dict, filename: str):
    """Save analysis results to JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ Analysis results saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    print("🤖 eBay Listing Confidence Analyzer")
    print("=" * 50)
    
    # Initialize the confidence scorer
    scorer = eBayConfidenceScorer()
    
    # Example usage - you can modify these parameters
    search_query = "2004 Silver Eagle MS69"
    input_file = "ebay_sold_items_2004_Silver_Eagle_MS69_FILTERED.json"  # Use filtered results
    min_confidence = 60  # Only show listings with 60%+ confidence
    
    print(f"Loading data from: {input_file}")
    listings = load_ebay_data(input_file)
    
    if not listings:
        print("❌ No data found. Please run the main eBay script first to generate data files.")
        exit(1)
    
    print(f"Found {len(listings)} listings to analyze")
    
    # Perform confidence analysis
    results = scorer.analyze_listings(listings, search_query, min_confidence)
    
    # Display results
    scorer.display_analysis_results(results)
    
    # Save results
    output_file = f"confidence_analysis_{search_query.replace(' ', '_')}.json"
    save_analysis_results(results, output_file)
    
    print(f"\n🎯 RECOMMENDATIONS:")
    if results['high_confidence_listings'] > 0:
        print(f"  • {results['high_confidence_listings']} listings have high confidence (80%+)")
        print(f"  • Focus on these for most accurate pricing data")
    else:
        print(f"  • No high-confidence listings found")
        print(f"  • Consider adjusting search terms or lowering confidence threshold")
    
    print(f"  • Average confidence: {results['average_confidence']:.1f}%")
    print(f"  • Use confidence scores to weight your pricing analysis") 