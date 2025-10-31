#!/usr/bin/env python3
"""
Company Competitive Moat Scorer
Gets Grok to rate a company's competitive moat strength across 13 metrics (0-10 each):
- Competitive Moat
- Barriers to Entry
- Disruption Risk
- Switching Cost
- Brand Strength
- Competition Intensity
- Network Effect
- Innovativeness
- Growth Opportunity
Usage: python scorer.py
Then enter ticker symbols or company names interactively
"""

# Score weightings - adjust these to change the relative importance of each metric
# All start at 1.0 (equal weight). Increase/decrease to emphasize certain metrics.
SCORE_WEIGHTS = {
    'moat_score': 10,
    'barriers_score': 10,
    'disruption_risk': 10,
    'switching_cost': 10,
    'brand_strength': 10, 
    'competition_intensity': 10,
    'network_effect': 10,
    'product_differentiation': 10,
    'innovativeness_score': 10,
    'growth_opportunity': 10,
    'riskiness_score': 10,
    'pricing_power': 10,
    'ambition_score': 10,
}

from grok_client import GrokClient
from config import XAI_API_KEY
import sys
import json
import os
from datetime import datetime

# JSON file to store moat scores
SCORES_FILE = "scores.json"

# Stock ticker lookup file
TICKER_FILE = "stock_tickers_clean.json"

# Cache for ticker lookups
_ticker_cache = None

def load_ticker_lookup():
    """Load ticker to company name lookup."""
    global _ticker_cache
    
    if _ticker_cache is not None:
        return _ticker_cache
    
    _ticker_cache = {}
    
    try:
        if os.path.exists(TICKER_FILE):
            with open(TICKER_FILE, 'r') as f:
                data = json.load(f)
                
                for company in data.get('companies', []):
                    ticker = company.get('ticker', '').strip().upper()
                    name = company.get('name', '').strip()
                    
                    if ticker:
                        _ticker_cache[ticker] = name
        else:
            print(f"Warning: {TICKER_FILE} not found. Ticker lookups will not work.")
    except Exception as e:
        print(f"Warning: Could not load ticker file: {e}")
    
    return _ticker_cache

def resolve_to_company_name(input_str):
    """
    Resolve input to a company name.
    Returns (company_name, ticker) tuple.
    """
    input_upper = input_str.strip().upper()
    
    # Check if it's a ticker symbol (uppercase, 1-5 chars)
    if len(input_upper) >= 1 and len(input_upper) <= 5 and input_upper.isalpha():
        ticker_lookup = load_ticker_lookup()
        
        if input_upper in ticker_lookup:
            company_name = ticker_lookup[input_upper]
            return (company_name, input_upper)
    
    # Otherwise treat as company name
    return (input_str.strip(), None)

def get_ticker_from_company_name(company_name):
    """Reverse lookup: get ticker from company name."""
    ticker_lookup = load_ticker_lookup()
    
    # Known mappings for common company names
    aliases = {
        'google': 'GOOGL',
        'tsmc': 'TSM',
        'meta': 'META',
        'nvidia': 'NVDA',
        'amazon': 'AMZN',
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'tesla': 'TSLA',
        'adobe': 'ADBE',
        'salesforce': 'CRM',
        'broadcom': 'AVGO',
        'oracle': 'ORCL',
        'lululemon': 'LULU',
        'paypal': 'PYPL',
        'prologis': 'PLD',
        'dell': 'DELL',
        'micron': 'MU',
        'amd': 'AMD',
    }
    
    # Check aliases first
    company_lower = company_name.lower()
    if company_lower in aliases:
        ticker = aliases[company_lower]
        if ticker in ticker_lookup:
            return ticker
    
    # Try exact match (case insensitive)
    for ticker, name in ticker_lookup.items():
        if name.lower() == company_lower:
            return ticker
    
    # Try partial match
    for ticker, name in ticker_lookup.items():
        if company_lower in name.lower() or name.lower() in company_lower:
            return ticker
    
    return None

# Define all score metrics - add new scores here to automatically integrate them everywhere!
SCORE_DEFINITIONS = {
    'moat_score': {
        'display_name': 'Competitive Moat',
        'field_name': 'moat_score',
        'prompt': """Rate the competitive moat strength of {company_name} on a scale of 0-10, where:
- 0 = No competitive advantage, easily replaceable
- 5 = Moderate competitive advantages
- 10 = Extremely strong moat, nearly impossible to compete against

Consider factors like:
- Brand strength and customer loyalty
- Network effects
- Switching costs
- Economies of scale
- Patents/intellectual property
- Regulatory barriers
- Unique resources or capabilities

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'barriers_score': {
        'display_name': 'Barriers to Entry',
        'field_name': 'barriers_score',
        'prompt': """Rate the barriers to entry for {company_name} on a scale of 0-10, where:
- 0 = No barriers, extremely easy for competitors to enter
- 5 = Moderate barriers to entry
- 10 = Extremely high barriers, nearly impossible for new competitors to enter

Consider factors like:
- Capital requirements
- Regulatory and licensing requirements
- Technological complexity
- Distribution channel access
- Brand recognition and customer loyalty
- Network effects
- Resource advantages
- Switching costs for customers

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'disruption_risk': {
        'display_name': 'Disruption Risk',
        'field_name': 'disruption_risk',
        'prompt': """Rate the disruption risk for {company_name} on a scale of 0-10, where:
- 0 = No risk, very stable industry
- 5 = Moderate disruption risk
- 10 = Very high risk of being disrupted by new technology or competitors

Consider factors like:
- Technology disruption potential
- Regulatory risk
- Changing consumer preferences
- Emerging competitors with new business models
- Industry transformation trends
- Obsolescence risk
- Substitution threats

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': True
    },
    'switching_cost': {
        'display_name': 'Switching Cost',
        'field_name': 'switching_cost',
        'prompt': """Rate the switching costs for customers of {company_name} on a scale of 0-10, where:
- 0 = No switching costs, customers can easily leave
- 5 = Moderate switching costs
- 10 = Very high switching costs, customers are locked in

Consider factors like:
- Learning curve for new products
- Data migration complexity
- Contractual commitments
- Integration with existing systems
- Training requirements
- Financial switching costs
- Network effects making it hard to leave
- Compatibility issues

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'brand_strength': {
        'display_name': 'Brand Strength',
        'field_name': 'brand_strength',
        'prompt': """Rate the brand strength for {company_name} on a scale of 0-10, where:
- 0 = No brand recognition or loyalty
- 5 = Moderate brand strength
- 10 = Extremely strong brand with high customer loyalty and recognition

Consider factors like:
- Brand recognition and awareness
- Customer loyalty and emotional attachment
- Brand reputation and trust
- Ability to charge premium prices
- Brand value and differentiation
- Marketing effectiveness
- Brand longevity and consistency
- Global brand presence

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'competition_intensity': {
        'display_name': 'Competition Intensity',
        'field_name': 'competition_intensity',
        'prompt': """Rate the intensity of competition for {company_name} on a scale of 0-10, where:
- 0 = No competition, monopoly-like market
- 5 = Moderate competition
- 10 = Extremely intense competition with many aggressive competitors

Consider factors like:
- Number of competitors in the market
- Competitiveness of pricing strategies
- Aggressiveness of marketing and customer acquisition
- Market share fragmentation
- Barriers to market dominance
- Competitor capabilities and resources
- Frequency of competitive actions
- Market growth rate relative to competition

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': True
    },
    'network_effect': {
        'display_name': 'Network Effect',
        'field_name': 'network_effect',
        'prompt': """Rate the network effects for {company_name} on a scale of 0-10, where:
- 0 = No network effects, value doesn't increase with more users
- 5 = Moderate network effects
- 10 = Extremely strong network effects, value increases dramatically with more users

Consider factors like:
- Value increases as more users join the network
- User count creates competitive advantage
- Network density and interconnectedness
- Platform effects and ecosystem benefits
- Data network effects
- Social network effects
- Two-sided market effects
- Viral growth potential

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'product_differentiation': {
        'display_name': 'Product Differentiation',
        'field_name': 'product_differentiation',
        'prompt': """Rate the product differentiation (vs commoditization) for {company_name} on a scale of 0-10, where:
- 0 = Completely commoditized, interchangeable with competitors, price competition
- 5 = Some differentiation, moderate pricing power
- 10 = Highly differentiated, unique products/services with strong pricing power

Consider factors like:
- Product uniqueness and distinctiveness
- Ability to command premium prices
- Customer perception of differentiation
- Brand differentiation and positioning
- R&D and innovation creating uniqueness
- Proprietary features or technology
- Service or experience differentiation
- Market positioning and specialization

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'innovativeness_score': {
        'display_name': 'Innovativeness',
        'field_name': 'innovativeness_score',
        'prompt': """Rate the innovativeness of {company_name} on a scale of 0-10, where:
- 0 = Not innovative, relies on existing technologies and practices, minimal R&D
- 5 = Moderately innovative, some product improvements and incremental innovation
- 10 = Extremely innovative, breakthrough technologies, disruptive innovation, industry-leading R&D

Consider factors like:
- R&D investment and spending as percentage of revenue
- Patents, intellectual property, and technological breakthroughs
- Track record of introducing new products and services
- Innovation culture and ability to adapt to new technologies
- Leadership in developing new solutions or business models
- Speed of innovation cycles and time to market
- Investment in emerging technologies (AI, automation, etc.)
- Historical innovations and transformation initiatives

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'growth_opportunity': {
        'display_name': 'Growth Opportunity',
        'field_name': 'growth_opportunity',
        'prompt': """Rate the growth opportunity for {company_name} on a scale of 0-10, where:
- 0 = Minimal growth opportunity, mature/declining market, limited expansion potential
- 5 = Moderate growth opportunity, steady market growth, some expansion possibilities
- 10 = Exceptional growth opportunity, rapidly expanding market, multiple growth vectors, high scalability

Consider factors like:
- Market size and growth rate of industry
- Addressable market size (TAM/SAM/SOM)
- Geographic expansion opportunities
- Product/service expansion potential
- Market penetration potential in existing segments
- Adjacent market opportunities
- Demographic and macroeconomic trends favoring growth
- Ability to scale operations efficiently
- Customer acquisition and retention growth potential
- International expansion opportunities
- Pricing power and margin expansion opportunities

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'riskiness_score': {
        'display_name': 'Riskiness',
        'field_name': 'riskiness_score',
        'prompt': """Rate the overall riskiness of investing in {company_name} on a scale of 0-10, where:
- 0 = Very low risk, stable and predictable business model
- 5 = Moderate risk, some uncertainty in business outlook
- 10 = Very high risk, highly volatile or uncertain business model

Consider factors like:
- Financial risk and leverage/debt levels
- Business model stability and predictability
- Regulatory and legal risks
- Market volatility and cyclicality
- Management and execution risks
- Competitive and market position risks
- Technology and operational risks
- Macroeconomic sensitivity
- Dependency on key customers or suppliers
- Liquidity and financing risks
- Geographic and political risks
- Concentration risks

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': True
    },
    'pricing_power': {
        'display_name': 'Pricing Power',
        'field_name': 'pricing_power',
        'prompt': """Rate the pricing power of {company_name} on a scale of 0-10, where:
- 0 = No pricing power, commodity-like product with intense price competition
- 5 = Moderate pricing power, some ability to set prices above cost
- 10 = Exceptional pricing power, strong ability to raise prices without losing customers

Consider factors like:
- Ability to increase prices without significant demand loss
- Customer price sensitivity and elasticity
- Unique value proposition and differentiation
- Market position and competitive advantage
- Brand strength and customer loyalty
- Product/service necessity and switching costs
- Market concentration and competitive dynamics
- Substitution availability and alternatives
- Historical pricing power demonstrated
- Gross and operating margin trends
- Customer dependency and lock-in effects
- Regulatory or contractual pricing protections

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'ambition_score': {
        'display_name': 'Ambition',
        'field_name': 'ambition_score',
        'prompt': """Rate the company and culture ambition of {company_name} on a scale of 0-10, where:
- 0 = Low ambition, complacent, maintaining status quo, no transformative goals
- 5 = Moderate ambition, some growth and improvement goals, incremental progress
- 10 = Extremely high ambition, transformative vision, aggressive growth targets, industry-changing goals

Consider factors like:
- Vision and mission clarity and boldness
- Growth targets and expansion ambitions
- Investment in R&D and innovation initiatives
- Market leadership aspirations
- Strategic initiatives and transformation programs
- Culture of excellence and high standards
- Long-term strategic planning and vision
- Willingness to take calculated risks for growth
- Executive leadership ambition and drive
- Company culture of continuous improvement
- Market disruption and category creation goals
- Global expansion and market dominance ambitions
- Investment in talent and capability building

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    }
}


def load_scores():
    """Load existing scores from JSON file."""
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"companies": {}}
    return {"companies": {}}


def save_scores(scores_data):
    """Save scores to JSON file."""
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores_data, f, indent=2)


def calculate_total_score(scores_dict):
    """Calculate total score from a dictionary of scores.
    
    Args:
        scores_dict: Dictionary with score keys and their string values
        
    Returns:
        float: The total weighted score (handling reverse scores appropriately)
    """
    total = 0
    for score_key in SCORE_DEFINITIONS:
        score_def = SCORE_DEFINITIONS[score_key]
        weight = SCORE_WEIGHTS.get(score_key, 1.0)  # Default to 1.0 if weight not found
        try:
            score_value = float(scores_dict.get(score_key, 0))
            # For reverse scores, invert to get "goodness" value
            if score_def['is_reverse']:
                total += (10 - score_value) * weight
            else:
                total += score_value * weight
        except (ValueError, TypeError):
            pass
    return total


def calculate_percentile_rank(score, all_scores):
    """Calculate percentile rank of a score among all scores.
    
    Args:
        score: The score to calculate percentile for (float)
        all_scores: List of all scores to compare against (list of floats)
        
    Returns:
        int: Percentile rank (0-100), or None if no scores to compare
    """
    if not all_scores or len(all_scores) == 0:
        return None
    
    # Count how many scores are less than or equal to this score
    scores_less_or_equal = sum(1 for s in all_scores if s <= score)
    
    # Percentile rank = (number of scores <= this score) / total scores * 100
    percentile = int((scores_less_or_equal / len(all_scores)) * 100)
    return percentile


def get_all_total_scores():
    """Get all total scores from all companies.
    
    Returns:
        list: List of all total scores (floats)
    """
    scores_data = load_scores()
    all_totals = []
    
    for company, data in scores_data["companies"].items():
        total = calculate_total_score(data)
        all_totals.append(total)
    
    return all_totals


def format_total_score(total, percentile=None):
    """Format a total score as a percentage integer string with optional percentile.
    
    Args:
        total: The total weighted score (float)
        percentile: Optional percentile rank (int), if None will be calculated
        
    Returns:
        str: Formatted total score as percentage with percentile (e.g., "87 (75th percentile)")
    """
    # Calculate max possible score with weights
    max_score = sum(SCORE_WEIGHTS.get(key, 1.0) for key in SCORE_DEFINITIONS) * 10
    percentage = (total / max_score) * 100
    
    if percentile is not None:
        return f"{int(percentage)} ({percentile}th percentile)"
    else:
        # Calculate percentile automatically
        all_totals = get_all_total_scores()
        if len(all_totals) > 1:  # Need at least 2 scores to calculate percentile
            percentile = calculate_percentile_rank(total, all_totals)
            if percentile is not None:
                return f"{int(percentage)} ({percentile}th percentile)"
        
        return f"{int(percentage)}"


def query_score(grok, company_name, score_key):
    """Query a single score from Grok."""
    score_def = SCORE_DEFINITIONS[score_key]
    prompt = score_def['prompt'].format(company_name=company_name)
    response, _ = grok.simple_query_with_tokens(prompt, model="grok-4-fast")
    return response.strip()


def get_company_moat_score(input_str):
    """Get all scores for a company using SCORE_DEFINITIONS.
    
    Accepts either a ticker symbol or company name.
    Stores scores using ticker as key.
    """
    try:
        # Strip leading/trailing spaces only
        input_stripped = input_str.strip()
        input_upper = input_stripped.upper()
        
        ticker = None
        company_name = None
        
        # Check if the exact string (after stripping outer spaces) is in ticker database
        ticker_lookup = load_ticker_lookup()
        if input_upper in ticker_lookup:
            # Found exact match in ticker database
            ticker = input_upper
            company_name = ticker_lookup[ticker]
        else:
            # Not found in ticker database - reject it
            print(f"\nError: '{input_upper}' is not a valid ticker symbol.")
            print("Please enter a valid NYSE or NASDAQ ticker symbol.")
            return
        
        # Display format: Ticker (Company Name) or just Company Name
        if ticker:
            display_name = f"{ticker.upper()} ({company_name})"
            print(f"Company: {company_name}")
        else:
            display_name = company_name
            print(f"Company: {company_name}")
        
        scores_data = load_scores()
        
        # Try to find existing scores (by ticker, then by company name for backwards compatibility)
        existing_data = None
        storage_key = None
        
        if ticker and ticker in scores_data["companies"]:
            existing_data = scores_data["companies"][ticker]
            storage_key = ticker
        elif company_name.lower() in scores_data["companies"]:
            existing_data = scores_data["companies"][company_name.lower()]
            storage_key = company_name.lower()
        
        if existing_data:
            current_scores = {}
            for score_key in SCORE_DEFINITIONS:
                if score_key == 'moat_score':
                    current_scores[score_key] = existing_data.get(score_key, existing_data.get('score'))
                else:
                    current_scores[score_key] = existing_data.get(score_key)
            
            if all(current_scores.values()):
                if ticker:
                    print(f"\n{ticker.upper()} ({company_name}) already scored:")
                else:
                    print(f"\n{company_name} already scored:")
                
                # Create list of scores with their values for sorting
                score_list = []
                for score_key in SCORE_DEFINITIONS:
                    score_def = SCORE_DEFINITIONS[score_key]
                    try:
                        score_value = float(current_scores[score_key])
                        score_list.append((score_value, score_def['display_name'], current_scores[score_key]))
                    except (ValueError, TypeError):
                        # Skip invalid scores
                        pass
                
                # Sort by score value descending
                score_list.sort(reverse=True, key=lambda x: x[0])
                
                # Print sorted scores without /10, vertically aligned
                for score_value, display_name, score_val in score_list:
                    print(f"{display_name:25} {score_val:>8}")
                
                # Print total at the bottom
                total = calculate_total_score(current_scores)
                total_str = format_total_score(total)
                print(f"{'Total':25} {total_str:>30}")
                return
            
            grok = GrokClient(api_key=XAI_API_KEY)
            
            for score_key in SCORE_DEFINITIONS:
                if not current_scores[score_key]:
                    score_def = SCORE_DEFINITIONS[score_key]
                    print(f"Querying {score_def['display_name']}...")
                    current_scores[score_key] = query_score(grok, company_name, score_key)
                    print(f"{score_def['display_name']} Score: {current_scores[score_key]}/10")
            
            # Use ticker for storage key if available, otherwise use company name
            storage_key = ticker if ticker else company_name.lower()
            scores_data["companies"][storage_key] = current_scores
            save_scores(scores_data)
            print(f"\nScores updated in {SCORES_FILE}")
            
            # Calculate and display total
            total = calculate_total_score(current_scores)
            total_str = format_total_score(total)
            print(f"Total Score: {total_str}")
            return
        
        if ticker:
            print(f"\nAnalyzing {ticker.upper()} ({company_name})...")
        else:
            print(f"\nAnalyzing {company_name}...")
        grok = GrokClient(api_key=XAI_API_KEY)
        
        all_scores = {}
        for score_key in SCORE_DEFINITIONS:
            score_def = SCORE_DEFINITIONS[score_key]
            print(f"Querying {score_def['display_name']}...")
            all_scores[score_key] = query_score(grok, company_name, score_key)
            print(f"{score_def['display_name']} Score: {all_scores[score_key]}/10")
        
        # Use ticker for storage key if available, otherwise use company name
        storage_key = ticker if ticker else company_name.lower()
        scores_data["companies"][storage_key] = all_scores
        save_scores(scores_data)
        print(f"\nScores saved to {SCORES_FILE}")
        
        # Calculate and display total
        total = calculate_total_score(all_scores)
        total_str = format_total_score(total)
        print(f"Total Score: {total_str}")
        
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo fix this:")
        print("1. Get an API key from https://console.x.ai/")
        print("2. Set the XAI_API_KEY environment variable:")
        print("   export XAI_API_KEY='your_api_key_here'")
        
    except Exception as e:
        print(f"Error: {e}")


def migrate_scores_to_lowercase():
    """Migrate existing scores to lowercase keys and remove duplicates."""
    scores_data = load_scores()
    lowercase_companies = {}
    
    for company, data in scores_data["companies"].items():
        company_lower = company.lower()
        if company_lower not in lowercase_companies:
            lowercase_companies[company_lower] = data
        else:
            existing_date = lowercase_companies[company_lower].get('date', '1900-01-01')
            new_date = data.get('date', '1900-01-01')
            
            if 'timestamp' in lowercase_companies[company_lower] and 'timestamp' in data:
                existing_time = datetime.fromisoformat(lowercase_companies[company_lower].get('timestamp', '1900-01-01T00:00:00'))
                new_time = datetime.fromisoformat(data.get('timestamp', '1900-01-01T00:00:00'))
                if new_time > existing_time:
                    lowercase_companies[company_lower] = data
            elif new_date > existing_date:
                lowercase_companies[company_lower] = data
    
    scores_data["companies"] = lowercase_companies
    save_scores(scores_data)
    return len(scores_data["companies"])


def fill_missing_barriers_scores():
    """Fill in missing scores for all companies using SCORE_DEFINITIONS."""
    try:
        scores_data = load_scores()
        grok = GrokClient(api_key=XAI_API_KEY)
        
        companies_to_score = []
        for company_name, data in scores_data["companies"].items():
            moat_score = data.get('moat_score', data.get('score'))
            if not moat_score:
                continue
            
            missing_scores = []
            company_scores = {}
            for score_key in SCORE_DEFINITIONS:
                company_scores[score_key] = data.get(score_key)
                if not company_scores[score_key]:
                    missing_scores.append(SCORE_DEFINITIONS[score_key]['display_name'])
            
            if missing_scores:
                companies_to_score.append((company_name, company_scores))
        
        if not companies_to_score:
            print("\nAll companies already have all scores!")
            return
        
        print(f"\nFound {len(companies_to_score)} companies missing scores:")
        print("=" * 60)
        for company_name, company_scores in companies_to_score:
            moat = company_scores.get('moat_score', 'N/A')
            missing = [SCORE_DEFINITIONS[k]['display_name'] for k, v in company_scores.items() if not v]
            # Display ticker in uppercase if it looks like a ticker, otherwise capitalize
            display_name = company_name.upper() if len(company_name) <= 5 and company_name.replace(' ', '').isalpha() else company_name.capitalize()
            print(f"{display_name}: Moat {moat}/10 - Missing: {', '.join(missing)}")
        
        print(f"\nQuerying missing scores...")
        print("=" * 60)
        
        for i, (company_name, company_scores) in enumerate(companies_to_score, 1):
            # Display ticker in uppercase if it looks like a ticker, otherwise capitalize
            display_name = company_name.upper() if len(company_name) <= 5 and company_name.replace(' ', '').isalpha() else company_name.capitalize()
            print(f"\n[{i}/{len(companies_to_score)}] Processing {display_name}...")
            
            for score_key in SCORE_DEFINITIONS:
                if not company_scores[score_key]:
                    score_def = SCORE_DEFINITIONS[score_key]
                    company_scores[score_key] = query_score(grok, company_name, score_key)
                    print(f"  {score_def['display_name']}: {company_scores[score_key]}/10")
            
            scores_data["companies"][company_name] = company_scores
            save_scores(scores_data)
        
        print("\n" + "=" * 60)
        print("All missing scores have been filled!")
        
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo fix this:")
        print("1. Get an API key from https://console.x.ai/")
        print("2. Set the XAI_API_KEY environment variable:")
        print("   export XAI_API_KEY='your_api_key_here'")
        
    except Exception as e:
        print(f"Error: {e}")


def view_scores(score_type=None):
    """Display all stored moat scores using SCORE_DEFINITIONS.
    
    Args:
        score_type: Can be None (show totals), a score type name (show specific score), 
                    or a ticker/company name (show all scores for that company).
    """
    scores_data = load_scores()
    
    if not scores_data["companies"]:
        print("No scores stored yet.")
        return
    
    # Helper function to get display name
    def get_display_name(key):
        # Check if it looks like a ticker (short, alphabetic)
        if len(key) <= 5 and key.replace(' ', '').isalpha():
            return key.upper()
        
        # Try to find ticker for this company name
        ticker = get_ticker_from_company_name(key)
        if ticker:
            company_name = load_ticker_lookup().get(ticker, key)
            return f"{ticker.upper()} ({company_name})"
        return key
    
    # Check if score_type is actually a ticker or company name
    if score_type:
        # Try direct match
        if score_type in scores_data["companies"]:
            data = scores_data["companies"][score_type]
        # Try uppercase (for ticker lookup)
        elif score_type.upper() in scores_data["companies"]:
            data = scores_data["companies"][score_type.upper()]
        # Try lowercase (for company name lookup)
        elif score_type.lower() in scores_data["companies"]:
            data = scores_data["companies"][score_type.lower()]
        else:
            # Try to resolve as ticker to company name
            resolved_name, ticker = resolve_to_company_name(score_type)
            if ticker and ticker in scores_data["companies"]:
                data = scores_data["companies"][ticker]
            elif resolved_name.lower() in scores_data["companies"]:
                data = scores_data["companies"][resolved_name.lower()]
            else:
                print(f"Company '{score_type}' not found in scores.")
                return
        
        # Determine display name - capitalize if it's a ticker
        if score_type.upper() in scores_data["companies"]:
            display_name = score_type.upper()
        elif len(score_type) <= 5 and score_type.replace(' ', '').isalpha():
            # Looks like a ticker, capitalize it
            display_name = score_type.upper()
        else:
            display_name = score_type
        print(f"\n{display_name} Scores:")
        print("=" * 80)
        
        total = 0
        all_present = True
        scores_list = []
        
        for score_key in SCORE_DEFINITIONS:
            score_def = SCORE_DEFINITIONS[score_key]
            score_val = data.get(score_key, 'N/A')
            
            if score_val == 'N/A':
                score_display = 'N/A'
                all_present = False
                sort_value = 0  # Put N/A scores at the end
            else:
                try:
                    val = float(score_val)
                    weight = SCORE_WEIGHTS.get(score_key, 1.0)
                    # For reverse scores, invert to get "goodness" value
                    if score_def['is_reverse']:
                        sort_value = 10 - val
                        total += (10 - val) * weight
                    else:
                        sort_value = val
                        total += val * weight
                    score_display = score_val
                except (ValueError, TypeError):
                    score_display = 'N/A'
                    all_present = False
                    sort_value = 0
            
            scores_list.append((sort_value, score_def['display_name'], score_display))
        
        # Sort by value descending
        scores_list.sort(reverse=True, key=lambda x: x[0])
        
        # Display sorted scores
        for sort_value, display_name, score_display in scores_list:
            print(f"{display_name:25} {score_display:>8}")
        
        if all_present:
            total_str = format_total_score(total)
            print(f"{'Total':25} {total_str:>8}")
        
        return
    
    # Helper function to calculate total score
    def get_total_score(item):
        data = item[1]
        total = 0
        for score_key, score_def in SCORE_DEFINITIONS.items():
            score_val = data.get(score_key, 'N/A')
            weight = SCORE_WEIGHTS.get(score_key, 1.0)
            if score_val == 'N/A':
                if score_def['is_reverse']:
                    total += 10 * weight
                continue
            
            try:
                val = float(score_val)
                if score_def['is_reverse']:
                    total += (10 - val) * weight
                else:
                    total += val * weight
            except (ValueError, TypeError):
                    pass
        return total
    
    sorted_companies = sorted(scores_data["companies"].items(), key=get_total_score, reverse=True)
    
    # If score_type not provided, show total scores for all companies
    if not score_type:
        print("\nStored Company Scores (Total only):")
        print("=" * 80)
        print(f"Number of stocks scored: {len(sorted_companies)}")
        print()
        
        max_name_len = max([len(company.capitalize()) for company, data in sorted_companies]) if sorted_companies else 0
        
        # Calculate all totals for percentile calculation
        all_totals = []
        company_totals = {}
        for company, data in sorted_companies:
            total = 0
            all_present = True
            for score_key, score_def in SCORE_DEFINITIONS.items():
                score_val = data.get(score_key, 'N/A')
                weight = SCORE_WEIGHTS.get(score_key, 1.0)
                if score_val == 'N/A':
                    all_present = False
                    break
                try:
                    val = float(score_val)
                    if score_def['is_reverse']:
                        total += (10 - val) * weight
                    else:
                        total += val * weight
                except (ValueError, TypeError):
                    all_present = False
                    break
            
            if all_present:
                company_totals[company] = total
                all_totals.append(total)
        
        # Print column headers
        print(f"{'Company':<{min(max_name_len, 30)}} {'Score':>8} {'Percentile':>12}")
        print("-" * (min(max_name_len, 30) + 8 + 12 + 2))
        
        # Display companies with percentiles
        for company, data in sorted_companies:
            if company in company_totals:
                total = company_totals[company]
                max_score = sum(SCORE_WEIGHTS.get(key, 1.0) for key in SCORE_DEFINITIONS) * 10
                percentage = int((total / max_score) * 100)
                percentage_str = f"{percentage}"
                
                percentile = calculate_percentile_rank(total, all_totals) if len(all_totals) > 1 else None
                if percentile is not None:
                    percentile_str = f"{percentile}"
                else:
                    percentile_str = 'N/A'
            else:
                percentage_str = 'N/A'
                percentile_str = 'N/A'
            
            # Display ticker if available, otherwise company name
            display_key = get_display_name(company)
            if len(display_key) > 30:
                display_key = display_key[:30]
            print(f"{display_key:<{min(max_name_len, 30)}} {percentage_str:>8} {percentile_str:>12}")
        return
    
    # If we get here, score_type is a score type (not a company)
    score_type_lower = score_type.lower()
    
    score_map = {name.lower() or key.lower(): key for key, val in SCORE_DEFINITIONS.items() 
                for name in [val['display_name'], key] + key.split('_')}
    
    matching_key = None
    for name, key in score_map.items():
        if score_type_lower in name or name in score_type_lower:
            matching_key = key
            break
    
    if not matching_key:
        print(f"Unknown score type: {score_type}")
        print(f"Available types: {', '.join([key.split('_')[0] for key in SCORE_DEFINITIONS.keys()])}")
        return
    
    score_def = SCORE_DEFINITIONS[matching_key]
    print(f"\nStored Company Scores ({score_def['display_name']}):")
    print("=" * 80)
    
    def get_field_score(item):
        data = item[1]
        score = data.get(matching_key, 'N/A')
        try:
            return float(score) if score != 'N/A' else 0
        except (ValueError, TypeError):
            return 0
    
    sorted_by_field = sorted(scores_data["companies"].items(), key=get_field_score, reverse=True)
    max_name_len = max([len(get_display_name(company)) for company, data in sorted_by_field]) if sorted_by_field else 0
    
    for company, data in sorted_by_field:
        score = data.get(matching_key, 'N/A')
        if score != 'N/A':
            try:
                score_float = float(score)
                score = f"{int(score_float)}" if score_float == int(score_float) else f"{score_float:.1f}"
            except (ValueError, TypeError):
                pass
        
        # Display ticker if available, otherwise company name
        display_key = get_display_name(company)
        if len(display_key) > 30:
            display_key = display_key[:30]
        print(f"{display_key:<{min(max_name_len, 30)}} {score:>8}")


def delete_company(input_str):
    """Delete a company's scores from the JSON file.
    
    Args:
        input_str: Ticker symbol or company name to delete
    """
    scores_data = load_scores()
    
    if not scores_data["companies"]:
        print("No scores stored yet.")
        return
    
    # Try to find the company using the same resolution logic as view_scores
    storage_key = None
    display_name = None
    
    # Check direct match (uppercase for ticker, lowercase for company name)
    input_upper = input_str.strip().upper()
    input_lower = input_str.strip().lower()
    
    # First try as ticker (uppercase)
    if input_upper in scores_data["companies"]:
        storage_key = input_upper
        ticker_lookup = load_ticker_lookup()
        company_name = ticker_lookup.get(input_upper, input_upper)
        display_name = f"{input_upper} ({company_name})"
    # Then try as company name (lowercase)
    elif input_lower in scores_data["companies"]:
        storage_key = input_lower
        # Try to find ticker for display
        ticker = get_ticker_from_company_name(input_lower)
        if ticker:
            company_name = load_ticker_lookup().get(ticker, input_lower)
            display_name = f"{ticker.upper()} ({company_name})"
        else:
            display_name = input_lower
    else:
        # Try to resolve ticker to company name
        resolved_name, ticker = resolve_to_company_name(input_str)
        if ticker and ticker in scores_data["companies"]:
            storage_key = ticker
            company_name = load_ticker_lookup().get(ticker, resolved_name)
            display_name = f"{ticker.upper()} ({company_name})"
        elif resolved_name.lower() in scores_data["companies"]:
            storage_key = resolved_name.lower()
            display_name = resolved_name
    
    if not storage_key:
        print(f"Company '{input_str}' not found in scores.")
        print("\nAvailable companies:")
        for key in sorted(scores_data["companies"].keys()):
            # Try to format display name
            if len(key) <= 5 and key.replace(' ', '').isalpha():
                ticker_lookup = load_ticker_lookup()
                company_name = ticker_lookup.get(key.upper(), key)
                print(f"  {key.upper()} ({company_name})")
            else:
                ticker = get_ticker_from_company_name(key)
                if ticker:
                    print(f"  {ticker.upper()} ({key})")
                else:
                    print(f"  {key}")
        return
    
    # Confirm deletion
    print(f"\nFound: {display_name}")
    confirm = input("Are you sure you want to delete this company's scores? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        del scores_data["companies"][storage_key]
        save_scores(scores_data)
        print(f"\n{display_name} has been deleted from scores.")
    else:
        print("Deletion cancelled.")


def show_metrics_menu():
    """Display a numbered menu of all available metrics."""
    print("\nAvailable Metrics:")
    print("=" * 40)
    metrics_list = list(SCORE_DEFINITIONS.items())
    for i, (score_key, score_def) in enumerate(metrics_list, 1):
        print(f"{i:2}. {score_def['display_name']}")
    print()
    return metrics_list


def rank_by_metric(metric_key):
    """Display ranking of all companies for a specific metric.
    
    Args:
        metric_key: The key of the metric to rank by
    """
    scores_data = load_scores()
    
    if not scores_data["companies"]:
        print("No scores stored yet.")
        return
    
    if metric_key not in SCORE_DEFINITIONS:
        print(f"Error: Invalid metric key '{metric_key}'")
        return
    
    score_def = SCORE_DEFINITIONS[metric_key]
    is_reverse = score_def['is_reverse']
    
    # Helper function to get display name
    def get_display_name(key):
        # Check if it looks like a ticker (short, alphabetic)
        if len(key) <= 5 and key.replace(' ', '').isalpha():
            return key.upper()
        
        # Try to find ticker for this company name
        ticker = get_ticker_from_company_name(key)
        if ticker:
            company_name = load_ticker_lookup().get(ticker, key)
            return f"{ticker.upper()} ({company_name})"
        return key
    
    # Collect all scores for this metric
    rankings = []
    for company_key, data in scores_data["companies"].items():
        score_val = data.get(metric_key, 'N/A')
        if score_val != 'N/A':
            try:
                val = float(score_val)
                # For reverse scores, invert to get "goodness" value for ranking
                if is_reverse:
                    sort_value = 10 - val
                else:
                    sort_value = val
                display_name = get_display_name(company_key)
                rankings.append((sort_value, val, display_name, company_key))
            except (ValueError, TypeError):
                pass
    
    if not rankings:
        print(f"\nNo scores found for {score_def['display_name']}.")
        return
    
    # Sort by score descending
    rankings.sort(reverse=True, key=lambda x: x[0])
    
    # Display rankings
    print(f"\nRankings by {score_def['display_name']}:")
    print("=" * 80)
    print(f"{'Rank':<6} {'Company':<40} {'Score':>8}")
    print("-" * 80)
    
    for rank, (sort_value, original_val, display_name, company_key) in enumerate(rankings, 1):
        # Format the original value for display
        try:
            score_float = float(original_val)
            if score_float == int(score_float):
                score_str = str(int(score_float))
            else:
                score_str = f"{score_float:.1f}"
        except (ValueError, TypeError):
            score_str = str(original_val)
        
        # Truncate display name if too long
        if len(display_name) > 38:
            display_name = display_name[:35] + "..."
        
        print(f"{rank:<6} {display_name:<40} {score_str:>8}")


def handle_rank_command():
    """Handle the rank command - show menu and get user selection."""
    metrics_list = show_metrics_menu()
    
    try:
        selection = input("Enter metric number (or 'cancel' to go back): ").strip()
        
        if selection.lower() in ['cancel', 'c', '']:
            return
        
        metric_num = int(selection)
        if metric_num < 1 or metric_num > len(metrics_list):
            print(f"Error: Please enter a number between 1 and {len(metrics_list)}")
            return
        
        # Get the metric key from the selection
        metric_key, _ = metrics_list[metric_num - 1]
        rank_by_metric(metric_key)
        
    except ValueError:
        print("Error: Please enter a valid number.")
    except KeyboardInterrupt:
        print("\nCancelled.")


def main():
    """Main function to run the moat scorer."""
    print("Company Competitive Moat Scorer")
    print("=" * 40)
    print("Commands:")
    print("  Enter ticker symbol (e.g., AAPL) or company name to score")
    print("  Type 'view' to see total scores")
    print("  Type 'rank' to see rankings by metric")
    print("  Type 'delete' to remove a company's scores")
    print("  Type 'fill' to score companies with missing scores")
    print("  Type 'migrate' to fix duplicate entries")
    print("  Type 'quit' or 'exit' to stop")
    print()
    
    while True:
        try:
            user_input = input("Enter ticker or company name (or 'view'/'rank'/'delete'/'fill'/'quit'): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'view':
                view_scores()
                print()
            elif user_input.lower() == 'rank':
                handle_rank_command()
                print()
            elif user_input.lower() == 'delete':
                delete_input = input("Enter ticker or company name to delete: ").strip()
                if delete_input:
                    delete_company(delete_input)
                else:
                    print("Please enter a ticker symbol or company name to delete.")
                print()
            elif user_input.lower() == 'fill':
                fill_missing_barriers_scores()
                print()
            elif user_input.lower() == 'migrate':
                count = migrate_scores_to_lowercase()
                print(f"\nMigration complete! Now storing {count} unique companies.")
                print()
            elif user_input:
                get_company_moat_score(user_input)
                print()
            else:
                print("Please enter a ticker symbol or company name.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()

