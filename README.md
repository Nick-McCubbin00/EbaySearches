# eBay AI Analyzer - Coin Pricing Intelligence

## 🎯 Overview

A comprehensive AI-powered system that combines eBay API data collection with Google Gemini AI confidence scoring to provide accurate coin pricing analysis. Perfect for coin dealers, collectors, and investors who need reliable pricing data.

## 🚀 Live Demo

Visit the live application: [https://nick-mccubbin00.github.io/EbaySearches/](https://nick-mccubbin00.github.io/EbaySearches/)

## ✨ Key Features

- **🤖 AI-Powered Confidence Scoring**: Uses Google Gemini to analyze listing relevance
- **📊 eBay API Integration**: Real-time data collection from eBay sold listings
- **🎯 Intelligent Filtering**: Automatically filters out irrelevant items
- **💰 Weighted Price Analysis**: Confidence-weighted averages and statistics
- **📈 Comprehensive Reporting**: Detailed analysis with actionable recommendations
- **🔄 Complete Workflow**: Search → Filter → AI Analysis → Report in one file

## 🛠️ Technology Stack

- **Python 3.10+**: Core application logic
- **Google Gemini AI**: Advanced confidence scoring
- **eBay Browse API**: Real-time data collection
- **GitHub Pages**: Web hosting and documentation

## 📁 Project Structure

```
EbaySearches/
├── Complete_Ebay_AI_Analyzer.py    # Main application (complete workflow)
├── API-Ebay.py                     # eBay API integration
├── AI_Confidence_Scorer.py         # AI confidence scoring system
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── docs/                           # Documentation
│   ├── index.html                  # GitHub Pages homepage
│   ├── setup.html                  # Setup instructions
│   ├── usage.html                  # Usage guide
│   └── api.html                    # API documentation
└── examples/                       # Example outputs
    ├── sample_analysis.json
    └── sample_results.txt
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Nick-Mccubbin00/EbaySearches.git
cd EbaySearches
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Edit `Complete_Ebay_AI_Analyzer.py` and add your API keys:

```python
# eBay API Configuration
EBAY_ACCESS_TOKEN = 'your-ebay-oauth-token-here'

# Google Gemini API Configuration  
GEMINI_API_KEY = 'your-gemini-api-key-here'
```

### 4. Run the Analysis

```bash
python Complete_Ebay_AI_Analyzer.py
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

## 💰 Sample Results

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

## 🎯 Use Cases

### 1. Graded Coin Analysis
```python
search_queries = [
    "2004 Silver Eagle MS69",
    "2004 Silver Eagle MS70",
    "2004 Silver Eagle Proof"
]
```

### 2. Standard Coin Analysis
```python
search_queries = [
    "2004 Silver Eagle 1 Oz",
    "2004 American Silver Eagle 1 Oz"
]
```

### 3. Custom Searches
```python
search_queries = [
    "2004 Walking Liberty Half Dollar",
    "2004 Mercury Dime",
    "2004 Buffalo Nickel"
]
```

## 🔧 Configuration Options

### Confidence Thresholds
```python
min_confidence = 70  # Only include listings with 70%+ confidence
```

### Search Parameters
```python
max_results = 20     # Maximum listings to collect
days_back = 90       # Search period in days
```

### AI Model Settings
```python
model = genai.GenerativeModel('gemini-2.5-pro')  # AI model to use
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

## 🛠️ API Setup

### eBay API Setup
1. Go to [eBay Developer Program](https://developer.ebay.com/)
2. Create a new application
3. Get your OAuth access token
4. Add it to the configuration

### Google Gemini API Setup
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to the configuration

## 🚨 Troubleshooting

### Common Issues

1. **"Invalid access token" for eBay API**
   - Solution: Update your eBay OAuth token
   - Tokens expire regularly, refresh as needed

2. **"No Gemini API key provided"**
   - Solution: Add your API key or use rule-based scoring
   - Rule-based scoring works without API keys

3. **"No listings found"**
   - Solution: Check your search terms
   - Verify your eBay API token is valid

4. **Low confidence scores**
   - Solution: Refine search terms
   - Lower confidence threshold if needed

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the sample outputs in the examples folder
3. Test with the provided test scripts
4. Open an issue on GitHub

## 🙏 Acknowledgments

- **eBay Developer Program** for providing the API
- **Google AI** for the Gemini model
- **Python Community** for the excellent libraries
- **GitHub** for hosting and Pages

---

**Made with ❤️ for the coin collecting community**

*This tool helps coin dealers and collectors make informed pricing decisions using AI-powered analysis of eBay market data.* 