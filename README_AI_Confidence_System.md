# AI-Powered eBay Coin Confidence Scoring System

## Overview

This system combines eBay API data collection with intelligent confidence scoring to provide accurate coin pricing analysis. It uses AI (Google Gemini) to analyze how well each eBay listing matches your search criteria, giving you confidence scores that help you make better pricing decisions.

## 🎯 Key Features

- **AI-Powered Confidence Scoring**: Uses Google Gemini to analyze listing relevance
- **Rule-Based Fallback**: Works without API keys using intelligent rule-based scoring
- **Weighted Price Analysis**: Calculates confidence-weighted averages and statistics
- **Comprehensive Reporting**: Provides detailed analysis with recommendations
- **Multiple Analysis Modes**: Analyze existing data or collect new data

## 📁 Files Overview

### Core Files
- **`API-Ebay.py`**: Main eBay API integration for collecting sold item data
- **`AI_Confidence_Scorer.py`**: AI-powered confidence scoring system
- **`Analyze_Existing_Data.py`**: Analyzes previously collected data files
- **`Integrated_Ebay_Analyzer.py`**: Combines API collection with confidence scoring
- **`test_confidence_scorer.py`**: Test script to demonstrate functionality

### Data Files (Generated)
- **`ebay_sold_items_*_FILTERED.json`**: Filtered eBay listings
- **`comprehensive_analysis_*.json`**: Complete analysis results with confidence scores

## 🚀 Quick Start

### 1. Basic Setup (Rule-Based Scoring)

```bash
# Test the confidence scorer with existing data
python test_confidence_scorer.py

# Analyze existing data files
python Analyze_Existing_Data.py
```

### 2. Enable AI-Powered Scoring

1. Get a Google Gemini API key from: https://makersuite.google.com/app/apikey
2. Update `AI_Confidence_Scorer.py`:
   ```python
   GEMINI_API_KEY = "your-actual-gemini-api-key-here"
   ```
3. Run the analysis again for AI-enhanced results

### 3. Collect New Data and Analyze

```bash
# First, collect new eBay data (requires valid eBay OAuth token)
python API-Ebay.py

# Then analyze with confidence scoring
python Analyze_Existing_Data.py
```

## 📊 Understanding Confidence Scores

### Score Ranges
- **90-100%**: Excellent match - highly reliable for pricing
- **80-89%**: Good match - reliable with minor variations
- **70-79%**: Fair match - usable but consider carefully
- **Below 70%**: Poor match - exclude from pricing decisions

### What the AI Analyzes
- **Year Match**: Does it match the specified year (2004)?
- **Coin Type**: Is it the right coin (Silver Eagle vs other coins)?
- **Grade Match**: Does it match specified grade (MS69, MS70, etc.)?
- **Condition**: Is it the actual coin or just accessories/boxes?
- **Red Flags**: Wrong items, damaged goods, accessories only

## 💰 Pricing Analysis Features

### Weighted Statistics
- **Weighted Average**: Prices weighted by confidence scores
- **Median Price**: Middle price when sorted
- **Percentiles**: 25th and 75th percentile prices
- **Price Range**: Minimum to maximum prices
- **Volatility Assessment**: Low/Moderate/High price variation

### Example Output
```
💰 PRICING ANALYSIS (Confidence-Weighted):
  Weighted Average: $48.09
  Median Price: $48.99
  25th Percentile: $45.95
  75th Percentile: $49.95
  Price Range: $45.00 - $50.00
  Total Range: $5.00
  Weighted Sales Count: 9
```

## 🎯 Use Cases

### 1. Graded Coin Analysis
```bash
# Search for specific graded coins
python Analyze_Existing_Data.py
# Analyzes: "2004 Silver Eagle MS69", "2004 Silver Eagle MS70"
```

### 2. Standard Coin Analysis
```bash
# Analyze standard bullion coins
python Analyze_Existing_Data.py
# Analyzes: "2004 Silver Eagle 1 Oz", "2004 American Silver Eagle 1 Oz"
```

### 3. Custom Searches
```python
# Modify search queries in the script
search_queries = [
    "2004 Silver Eagle MS69",
    "2004 Silver Eagle Proof",
    "2004 American Silver Eagle 1 Oz"
]
```

## 📈 Interpreting Results

### Data Quality Assessment
- **Excellent**: 5+ high-confidence listings
- **Good**: 3-4 high-confidence listings  
- **Fair**: 1-2 high-confidence listings
- **Poor**: No high-confidence listings

### Price Volatility
- **Low**: <$5 price range
- **Moderate**: $5-$15 price range
- **High**: >$15 price range

### Recommendations
The system provides actionable recommendations:
- Refine search terms for better matches
- Expand search to include more results
- Consider filtering by condition or seller
- Monitor prices over time for trends

## 🔧 Configuration Options

### Confidence Thresholds
```python
# In Analyze_Existing_Data.py
min_confidence = 70  # Only include listings with 70%+ confidence
```

### Search Parameters
```python
# In API-Ebay.py
max_results = 20     # Maximum listings to collect
days_back = 90       # Search period in days
```

### AI Model Settings
```python
# In AI_Confidence_Scorer.py
model = genai.GenerativeModel('gemini-pro')  # AI model to use
```

## 📊 Sample Results

### MS69 Graded Coins
```
2004 Silver Eagle MS69
- Confidence: 100.0% (9 high-confidence listings)
- Weighted Average: $48.09
- Price Range: $45.00 - $50.00
- Volatility: Low ($5.00 range)
```

### Standard Bullion Coins
```
2004 Silver Eagle 1 Oz
- Confidence: 95.0% (10 high-confidence listings)
- Weighted Average: $43.28
- Price Range: $39.99 - $46.95
- Volatility: Moderate ($6.96 range)
```

## 🛠️ Troubleshooting

### Common Issues

1. **"No Gemini API key provided"**
   - Solution: Add your API key or use rule-based scoring

2. **"Invalid access token" for eBay API**
   - Solution: Update your eBay OAuth token in `API-Ebay.py`

3. **"No data found in file"**
   - Solution: Run `API-Ebay.py` first to collect data

4. **Low confidence scores**
   - Solution: Refine search terms or lower confidence threshold

### Performance Tips

- Use filtered data files for faster analysis
- Set appropriate confidence thresholds (70%+ recommended)
- Run analyses during off-peak hours for better API performance
- Save results for historical comparison

## 🔮 Future Enhancements

### Planned Features
- **Trend Analysis**: Track price changes over time
- **Condition Filtering**: Separate analysis by coin condition
- **Seller Analysis**: Identify reliable vs unreliable sellers
- **Market Timing**: Best times to buy/sell recommendations
- **Batch Processing**: Analyze multiple coin types simultaneously

### Integration Possibilities
- **Database Storage**: Store results in SQLite/PostgreSQL
- **Web Interface**: Create a web dashboard for analysis
- **Email Alerts**: Notify when prices change significantly
- **Mobile App**: iOS/Android app for on-the-go analysis

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the sample outputs in this README
3. Test with the provided test scripts
4. Examine the generated JSON files for detailed data

## 📄 License

This system is designed for educational and business use. Please respect eBay's API terms of service and rate limits when collecting data. 