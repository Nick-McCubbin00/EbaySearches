#!/usr/bin/env python3
"""
Test script to verify AI scoring works locally
"""

import os
import sys
from Complete_Ebay_AI_Analyzer import eBayConfidenceScorer

# Set environment variables for testing
os.environ['GEMINI_API_KEY'] = "AIzaSyAPIUPQ_gNZeqiLv7Q3oqPEQ98f4xU4GoY"

def test_ai_scoring():
    """Test AI scoring with mock data"""
    print("🧪 Testing AI scoring locally...")
    
    # Create mock listing data
    mock_listings = [
        {
            'itemId': '123456789',
            'title': '2004 Silver Eagle MS69 NGC',
            'soldPrice': '45.99',
            'currency': 'USD',
            'condition': 'Used',
            'itemLocation': 'US'
        },
        {
            'itemId': '987654321',
            'title': '2004 American Silver Eagle Dollar Coin',
            'soldPrice': '42.50',
            'currency': 'USD',
            'condition': 'Used',
            'itemLocation': 'US'
        }
    ]
    
    # Initialize AI scorer
    scorer = eBayConfidenceScorer()
    
    # Test single listing scoring
    print("\n📊 Testing single listing scoring...")
    try:
        result = scorer.score_listing_confidence(mock_listings[0], "2004 Silver Eagle")
        print(f"✅ Single scoring works: {result['confidence_score']}% confidence")
    except Exception as e:
        print(f"❌ Single scoring failed: {e}")
        return False
    
    # Test batch scoring
    print("\n📦 Testing batch scoring...")
    try:
        batch_results = scorer.score_listings_batch(mock_listings, "2004 Silver Eagle")
        print(f"✅ Batch scoring works: {len(batch_results)} listings processed")
        for i, result in enumerate(batch_results):
            print(f"   Listing {i+1}: {result['confidence_analysis']['confidence_score']}% confidence")
    except Exception as e:
        print(f"❌ Batch scoring failed: {e}")
        return False
    
    print("\n✅ All AI scoring tests passed!")
    return True

if __name__ == "__main__":
    success = test_ai_scoring()
    sys.exit(0 if success else 1) 