import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- Configuration ---
# IMPORTANT: For the Marketplace Insights API, you need an OAuth access token.
# You can get this from your eBay Developer Program account using OAuth flow.
# Set your eBay OAuth access token here:
EBAY_ACCESS_TOKEN = 'v^1.1#i^1#f^0#I^3#p^1#r^0#t^H4sIAAAAAAAA/+VYe4wTRRjv684gHD7OyHkhWBZRkHQ7u+1ut+u10Htxld5doccBDUj2Mb1baHfL7tSj8E89AygchkeMMUByKGgIJirxwR8G42mikBiiATTBJ6CiQQOKjwRRZ9ty9E7C65p4if2nmW+++eb3+833zcwOyFWOeXBty9rfq6y32PpzIGezWqmxYExlxYzxdltthQWUOFj7c/flHL3203WGkEqm+XnQSGuqAZ0rU0nV4PPGAJHRVV4TDMXgVSEFDR5JfCzUGuFpEvBpXUOapCUJZ7gxQDA0YP1+BiS8AvQzkMZW9VLMDi1A+L0c7RUFQaRF1ktRftxvGBkYVg0kqChA0IBmXMDnorgOiuM9gAcsyVBcnHB2Qt1QNBW7kIAI5uHy+bF6CdarQxUMA+oIByGC4VBzrD0Ubmxq66hzl8QKFnWIIQFljKGtBk2Gzk4hmYFXn8bIe/OxjCRBwyDcwcIMQ4PyoUtgbgJ+XmpBknxYRUmUgchQYnmkbNb0lICujsO0KLIrkXfloYoUlL2WolgNcRmUULHVhkOEG53m39yMkFQSCtQDRFN9aFEoGiWC89OmhrDB1aApquGKzmt0cRzkJImjGJcPUCIjinJxlkKoosbDpmnQVFkxFTOcbRqqhxgyHC4MXSIMdmpX2/VQAplwSvywU0FAr98fN1e0sIQZ1K2aiwpTWAVnvnlt+QdHI6QrYgbBwQjDO/L64IVOpxWZGN6ZT8Ri7qw0AkQ3Qmne7e7p6SF7PKSmd7lpACj3wtZITOqGKYEo+Jq1jv2Vaw9wKXkqEsQjDYVH2TTGshInKgagdhFBxkP5KVDUfSis4HDrvwwlnN1Dy6Fc5UELOFkYL+MVWR8rM95ylEewmKFuEwcUhawrJejLIUonBQm6JJxnmRTUFZn3MAnawyWgS2b9CZfXn0i4REZmXVQCQgChKEp+7n9TJdeb5zEo6RCVK9HLk+SpRHcLyzFz68PN7LKFapMeaW1EoRb3onrdM691dmRGdFVnZmEk3gNbA9dbClck35BUsDIdeP7yCWDWejlEaNEMBOUR0YtJWhpGtaQiZUfXAnt0OSroKBuDySQ2jIhkKJ0Ol22jLg+9G9kjbo50WU+n/+JkuiIrw8zX0cXKHG/gAEJaIc2zh5S0lFsT8KXDNJm1vjSPekS8FXxhHVWsMckCW0Uu3DTJPGXSeFQidWhoGR1fssl28+7VoS2HKj7MkK4lk1DvpEZczKlUBgliEo62qi5DgivCKDtpKR9Dc6zHC9gR8ZLy5+jS0bYllXUfdjx0A7dp99AP+6Al/6N6rQOg13rAZrWCOjCVmgImV9rnO+zjag0FQVIREqShdKn4e1WH5HKYTQuKbqu2HB4fkR9rifyaEzNvLjg/k7NUlbwr9C8BNYMvC2Ps1NiSZwYw8XJPBXXbhCqaAT6KozgPAGwcTLnc66Dudty1ZPvJD45vZTfMTC5YvWXN3p3+w81HQdWgk9VaYXH0Wi23t6htX9bMqjzW/8aRVX/tmPTHcevAObk2vgtt/vTxz63d2zZfOPnxzk6nBU0a+NN57/71521bn9jy+prFK2py380+0Lqq9hS5YNHeWx/hxa4JFcGnT9dcdJw48Zvz+YFNx9o2PWu5c/riT95/b6/3rae+PXuouergrGUXd/8cb/rKP/nVXRf7Xvtif/TQmeo5L7/tfyE4fc7hb7YJZ32rTxylbQ800uc3T9yf+dsx8cc9XU+un/b1dmEdOHUywV54xfOR/Y76Y89NWLGhasqk6g+rv+/bRKwLzd/Ybj/44i8/3L/i4c/aQtmGuvgz498999Ka4J4dp9+xz93I/tS75UjfmY37+jqn7qufds+Z3UfmjKMKa/kPLaksrPERAAA='  # Replace with your actual OAuth access token

# eBay Browse API Endpoint (Sandbox or Production)
# For production: https://api.ebay.com/buy/browse/v1/item_summary/search
# For sandbox (testing): https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search
EBAY_BROWSE_API_ENDPOINT = "https://api.ebay.com/buy/browse/v1/item_summary/search"  # Production endpoint

# Note: Marketplace Insights API requires special access and different OAuth token
# For now, we'll use the Browse API with soldItems filter to get the best available data

# --- Functions for eBay API Interaction ---

def search_completed_sales(keywords, max_results=10, days_back=30):
    """
    Searches for sold items using the Browse API with soldItems filter.
    
    Note: This is the best available data with your current OAuth token.
    For true completed transaction data, you need Marketplace Insights API access.

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
    Filter items to only include 2004 Silver Eagles based on search query.
    If search query includes a grade (MS69, MS70, etc.), allows graded coins.
    Otherwise, excludes graded coins and special editions.
    """
    filtered_items = []
    search_query_lower = search_query.lower()
    
    # Keywords that indicate we want to KEEP the item
    keep_keywords = [
        '2004', 'silver eagle', 'american silver eagle', 'ase', '1 oz', '1 ounce', 
        'troy oz', '.999', 'fine silver', 'bullion', 'uncirculated', 'bu', 'gem bu'
    ]
    
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
        
        # Additional check: must contain "2004" and "silver eagle" or "ase"
        has_year = '2004' in title
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

def display_completed_sales(sales, search_query):
    """Display sold items results in a formatted way."""
    if sales:
        print(f"\n--- Found {len(sales)} SOLD ITEMS for '{search_query}' ---")
        
        # Filter to only show standard Silver Eagles
        filtered_sales = filter_silver_eagle_items(sales, search_query)
        print(f"--- After filtering: {len(filtered_sales)} STANDARD SILVER EAGLES ---")
        
        for i, sale in enumerate(filtered_sales):
            print(f"Standard Silver Eagle {i+1}:")
            print(f"  Title: {sale['title']}")
            print(f"  Sold Price: {sale['currency']} {sale['soldPrice']}")
            print(f"  Condition: {sale['condition']}")
            print(f"  Location: {sale['itemLocation']}")
            print(f"  Shipping Cost: {sale['currency']} {sale['shippingCost']}")
            print(f"  Buying Options: {', '.join(sale['buyingOptions']) if sale['buyingOptions'] else 'N/A'}")
            print(f"  URL: {sale['itemWebUrl']}")
            print("-" * 30)
        
        # Calculate price statistics for filtered items only
        prices = [float(sale['soldPrice']) for sale in filtered_sales if sale['soldPrice'] != 'N/A']
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            print(f"\n📊 PRICE STATISTICS (Standard Silver Eagles Only):")
            print(f"  Average Price: ${avg_price:.2f}")
            print(f"  Lowest Price: ${min_price:.2f}")
            print(f"  Highest Price: ${max_price:.2f}")
            print(f"  Number of Sales: {len(prices)}")
            
            # Show price range analysis
            if len(prices) >= 3:
                sorted_prices = sorted(prices)
                median_price = sorted_prices[len(sorted_prices)//2]
                print(f"  Median Price: ${median_price:.2f}")
                print(f"  Price Range: ${max_price - min_price:.2f}")
        else:
            print(f"\n⚠️  No valid price data found after filtering.")
        
        # Save both full and filtered data
        file_name_full = f"ebay_sold_items_{search_query.replace(' ', '_')}_FULL.json"
        file_name_filtered = f"ebay_sold_items_{search_query.replace(' ', '_')}_FILTERED.json"
        
        with open(file_name_full, "w", encoding="utf-8") as f:
            json.dump(sales, f, ensure_ascii=False, indent=4)
        with open(file_name_filtered, "w", encoding="utf-8") as f:
            json.dump(filtered_sales, f, ensure_ascii=False, indent=4)
            
        print(f"\nData saved to:")
        print(f"  Full results: {file_name_full}")
        print(f"  Filtered results: {file_name_filtered}")
    else:
        print(f"No sold items found for '{search_query}' or an error occurred.")

# --- Main Execution ---
if __name__ == "__main__":
    print("--- eBay Marketplace Insights API Script ---")
    print("This script uses the eBay Marketplace Insights API to search for COMPLETED SALES.")
    print("Make sure to replace 'YOUR_OAUTH_ACCESS_TOKEN' with your actual OAuth access token at the top of the file.")
    print("\nThis API provides actual completed transaction data, not just listings.")
    
    # Check if OAuth token is set
    if EBAY_ACCESS_TOKEN == 'YOUR_OAUTH_ACCESS_TOKEN':
        print("\nERROR: Please set your EBAY_ACCESS_TOKEN in the configuration section at the top of this file.")
        print("You need an OAuth access token. Get it from: https://developer.ebay.com/api-docs/static/oauth-client-credentials-grant.html")
        exit(1)
    
    # Example searches for 2004 Silver Eagles - modify these or add your own
    search_queries = [
        "2004 Silver Eagle 1 Oz",
        "2004 American Silver Eagle 1 Oz",
        "2004 Silver Eagle MS69"  # Test with graded coin search
    ]
    
    for search_query in search_queries:
        print(f"\n{'='*50}")
        print(f"Searching for: {search_query}")
        print(f"{'='*50}")
        
        # Search for completed sales in the last 90 days
        results = search_completed_sales(search_query, max_results=20, days_back=90)
        display_completed_sales(results, search_query)
        
        # Add a small delay between searches to be respectful to the API
        time.sleep(2)
    
    print("\n--- eBay Marketplace Insights API Script Finished ---")
