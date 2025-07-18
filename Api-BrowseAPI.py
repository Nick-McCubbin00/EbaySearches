import requests
import json
import os
import time

# --- Configuration ---
# IMPORTANT: For the Browse API, you need an OAuth access token, not just the App ID.
# You can get this from your eBay Developer Program account using OAuth flow.
# Set your eBay OAuth access token here:
EBAY_ACCESS_TOKEN = 'v^1.1#i^1#f^0#I^3#p^1#r^0#t^H4sIAAAAAAAA/+VYe4wTRRjv684gHD7OyHkhWBZRkHQ7u+1ut+u10Htxld5doccBDUj2Mb1baHfL7tSj8E89AygchkeMMUByKGgIJirxwR8G42mikBiiATTBJ6CiQQOKjwRRZ9ty9E7C65p4if2nmW+++eb3+833zcwOyFWOeXBty9rfq6y32PpzIGezWqmxYExlxYzxdltthQWUOFj7c/flHL3203WGkEqm+XnQSGuqAZ0rU0nV4PPGAJHRVV4TDMXgVSEFDR5JfCzUGuFpEvBpXUOapCUJZ7gxQDA0YP1+BiS8AvQzkMZW9VLMDi1A+L0c7RUFQaRF1ktRftxvGBkYVg0kqChA0IBmXMDnorgOiuM9gAcsyVBcnHB2Qt1QNBW7kIAI5uHy+bF6CdarQxUMA+oIByGC4VBzrD0Ubmxq66hzl8QKFnWIIQFljKGtBk2Gzk4hmYFXn8bIe/OxjCRBwyDcwcIMQ4PyoUtgbgJ+XmpBknxYRUmUgchQYnmkbNb0lICujsO0KLIrkXfloYoUlL2WolgNcRmUULHVhkOEG53m39yMkFQSCtQDRFN9aFEoGiWC89OmhrDB1aApquGKzmt0cRzkJImjGJcPUCIjinJxlkKoosbDpmnQVFkxFTOcbRqqhxgyHC4MXSIMdmpX2/VQAplwSvywU0FAr98fN1e0sIQZ1K2aiwpTWAVnvnlt+QdHI6QrYgbBwQjDO/L64IVOpxWZGN6ZT8Ri7qw0AkQ3Qmne7e7p6SF7PKSmd7lpACj3wtZITOqGKYEo+Jq1jv2Vaw9wKXkqEsQjDYVH2TTGshInKgagdhFBxkP5KVDUfSis4HDrvwwlnN1Dy6Fc5UELOFkYL+MVWR8rM95ylEewmKFuEwcUhawrJejLIUonBQm6JJxnmRTUFZn3MAnawyWgS2b9CZfXn0i4REZmXVQCQgChKEp+7n9TJdeb5zEo6RCVK9HLk+SpRHcLyzFz68PN7LKFapMeaW1EoRb3onrdM691dmRGdFVnZmEk3gNbA9dbClck35BUsDIdeP7yCWDWejlEaNEMBOUR0YtJWhpGtaQiZUfXAnt0OSroKBuDySQ2jIhkKJ0Ol22jLg+9G9kjbo50WU+n/+JkuiIrw8zX0cXKHG/gAEJaIc2zh5S0lFsT8KXDNJm1vjSPekS8FXxhHVWsMckCW0Uu3DTJPGXSeFQidWhoGR1fssl28+7VoS2HKj7MkK4lk1DvpEZczKlUBgliEo62qi5DgivCKDtpKR9Dc6zHC9gR8ZLy5+jS0bYllXUfdjx0A7dp99AP+6Al/6N6rQOg13rAZrWCOjCVmgImV9rnO+zjag0FQVIREqShdKn4e1WH5HKYTQuKbqu2HB4fkR9rifyaEzNvLjg/k7NUlbwr9C8BNYMvC2Ps1NiSZwYw8XJPBXXbhCqaAT6KozgPAGwcTLnc66Dudty1ZPvJD45vZTfMTC5YvWXN3p3+w81HQdWgk9VaYXH0Wi23t6htX9bMqjzW/8aRVX/tmPTHcevAObk2vgtt/vTxz63d2zZfOPnxzk6nBU0a+NN57/71521bn9jy+prFK2py380+0Lqq9hS5YNHeWx/hxa4JFcGnT9dcdJw48Zvz+YFNx9o2PWu5c/riT95/b6/3rae+PXuouergrGUXd/8cb/rKP/nVXRf7Xvtif/TQmeo5L7/tfyE4fc7hb7YJZ32rTxylbQ800uc3T9yf+dsx8cc9XU+un/b1dmEdOHUywV54xfOR/Y76Y89NWLGhasqk6g+rv+/bRKwLzd/Ybj/44i8/3L/i4c/aQtmGuvgz498999Ka4J4dp9+xz93I/tS75UjfmY37+jqn7qufds+Z3UfmjKMKa/kPLaksrPERAAA='  # Replace with your actual OAuth access token

# eBay Browse API Endpoint (Sandbox or Production)
# For production: https://api.ebay.com/buy/browse/v1/item_summary/search
# For sandbox (testing): https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search
EBAY_BROWSE_API_ENDPOINT = "https://api.ebay.com/buy/browse/v1/item_summary/search"  # Production endpoint

# --- Functions for eBay API Interaction ---

def search_ebay_listings(keywords, max_results=10):
    """
    Searches eBay listings using the Browse API's search endpoint.

    Args:
        keywords (str): The search query (e.g., "laptop", "vintage camera").
        max_results (int): Maximum number of results to return (eBay has limits, typically 50 per page).

    Returns:
        list: A list of dictionaries, each representing an eBay listing.
              Returns an empty list if no results or an error occurs.
    """
    if EBAY_ACCESS_TOKEN == 'YOUR_OAUTH_ACCESS_TOKEN':
        print("ERROR: Please set your EBAY_ACCESS_TOKEN in the configuration section at the top of this file.")
        return []

    # API parameters for the Browse API's search endpoint
    params = {
        'q': keywords,  # Search query
        'limit': min(max_results, 50),  # Limit results (max 50 per page)
        'sort': 'price',  # Sort by price
        'filter': 'soldItems',  # Only show sold/completed items
    }

    # Headers for the Browse API
    headers = {
        'Authorization': f'Bearer {EBAY_ACCESS_TOKEN}',  # OAuth access token
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY-US',  # US marketplace
        'Content-Type': 'application/json'
    }

    print(f"Searching eBay for '{keywords}'...")
    print(f"Using endpoint: {EBAY_BROWSE_API_ENDPOINT}")
    try:
        # Make the actual HTTP request to eBay Browse API:
        response = requests.get(EBAY_BROWSE_API_ENDPOINT, params=params, headers=headers)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response text: {response.text[:500]}...")  # Show first 500 chars of error
            response.raise_for_status()
            
        data = response.json()

        listings = []
        # Parse the JSON response from Browse API
        if data and 'itemSummaries' in data:
            for item in data['itemSummaries']:
                listing = {
                    'itemId': item.get('itemId', 'N/A'),
                    'title': item.get('title', 'N/A'),
                    'price': item.get('price', {}).get('value', 'N/A'),
                    'currency': item.get('price', {}).get('currency', 'N/A'),
                    'itemWebUrl': item.get('itemWebUrl', 'N/A'),
                    'image': item.get('image', {}).get('imageUrl', 'N/A'),
                    'condition': item.get('condition', 'N/A'),
                    'itemLocation': item.get('itemLocation', {}).get('country', 'N/A'),
                    'shippingOptions': item.get('shippingOptions', []),
                    'buyingOptions': item.get('buyingOptions', []),
                }
                listings.append(listing)
        return listings

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return []
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from eBay API.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

def display_listings(listings, search_query):
    """Display search results in a formatted way."""
    if listings:
        print(f"\n--- Found {len(listings)} SOLD Listings for '{search_query}' ---")
        for i, listing in enumerate(listings):
            print(f"Sold Item {i+1}:")
            print(f"  Title: {listing['title']}")
            print(f"  Sold Price: {listing['currency']} {listing['price']}")
            print(f"  URL: {listing['itemWebUrl']}")
            print(f"  Condition: {listing['condition']}")
            print(f"  Location: {listing['itemLocation']}")
            print(f"  Buying Options: {', '.join(listing['buyingOptions']) if listing['buyingOptions'] else 'N/A'}")
            print("-" * 30)
        
        # Save to JSON file
        file_name = f"ebay_sold_listings_{search_query.replace(' ', '_')}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(listings, f, ensure_ascii=False, indent=4)
        print(f"\nData saved to {file_name}")
    else:
        print(f"No sold listings found for '{search_query}' or an error occurred.")

# --- Main Execution ---
if __name__ == "__main__":
    print("--- eBay API Search Script ---")
    print("This script uses the eBay Browse API to search for listings.")
    print("Make sure to replace 'YOUR_OAUTH_ACCESS_TOKEN' with your actual OAuth access token at the top of the file.")
    
    # Check if OAuth token is set
    if EBAY_ACCESS_TOKEN == 'YOUR_OAUTH_ACCESS_TOKEN':
        print("\nERROR: Please set your EBAY_ACCESS_TOKEN in the configuration section at the top of this file.")
        print("You need an OAuth access token, not just an App ID. Get it from: https://developer.ebay.com/api-docs/static/oauth-client-credentials-grant.html")
        exit(1)
    
    # Example searches - modify these or add your own
    search_queries = [
        "2004 Silver Eagle 1 oz",
        "2004 American Silver Eagle",
        "2004 ASE 1 oz"
    ]
    
    for search_query in search_queries:
        print(f"\n{'='*50}")
        print(f"Searching for: {search_query}")
        print(f"{'='*50}")
        
        results = search_ebay_listings(search_query, max_results=5)
        display_listings(results, search_query)
        
        # Add a small delay between searches to be respectful to the API
        time.sleep(2)
    
    print("\n--- eBay API Search Script Finished ---")
