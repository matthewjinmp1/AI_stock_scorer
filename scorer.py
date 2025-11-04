#!/usr/bin/env python3
"""
Company Competitive Moat Scorer
Gets Grok to rate a company's competitive moat strength across multiple metrics (0-10 each):
- Competitive Moat
- Barriers to Entry
- Disruption Risk
- Switching Cost
- Brand Strength
- Competition Intensity
- Network Effect
- Innovativeness
- Growth Opportunity
- Product Quality
- And more...
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
    'bargaining_power_of_customers': 10,
    'bargaining_power_of_suppliers': 10,
    'product_quality_score': 10,
    'culture_employee_satisfaction_score': 10,
    'trailblazer_score': 10,
}

from grok_client import GrokClient
from config import XAI_API_KEY
import sys
import json
import os
import time
from datetime import datetime

# JSON file to store moat scores
SCORES_FILE = "scores.json"
HEAVY_SCORES_FILE = "scores_heavy.json"

# Stock ticker lookup file
TICKER_FILE = "stock_tickers_clean.json"

# Custom ticker definitions file
TICKER_DEFINITIONS_FILE = "ticker_definitions.json"

# Cache for ticker lookups
_ticker_cache = None

def load_custom_ticker_definitions():
    """Load custom ticker definitions from JSON file.
    
    Returns:
        dict: Dictionary mapping ticker (uppercase) to company name
    """
    custom_definitions = {}
    
    try:
        if os.path.exists(TICKER_DEFINITIONS_FILE):
            with open(TICKER_DEFINITIONS_FILE, 'r') as f:
                data = json.load(f)
                
                for ticker, name in data.get('definitions', {}).items():
                    ticker_upper = ticker.strip().upper()
                    name_stripped = name.strip()
                    
                    if ticker_upper and name_stripped:
                        custom_definitions[ticker_upper] = name_stripped
    except Exception as e:
        print(f"Warning: Could not load custom ticker definitions: {e}")
    
    return custom_definitions

def save_custom_ticker_definitions(definitions):
    """Save custom ticker definitions to JSON file.
    
    Args:
        definitions: Dictionary mapping ticker to company name
    """
    try:
        data = {"definitions": definitions}
        with open(TICKER_DEFINITIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error: Could not save custom ticker definitions: {e}")
        return False

def load_ticker_lookup():
    """Load ticker to company name lookup.
    Custom definitions take precedence over main ticker file.
    """
    global _ticker_cache
    
    if _ticker_cache is not None:
        return _ticker_cache
    
    _ticker_cache = {}
    
    # First load from main ticker file
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
    
    # Then load custom definitions (these override main file)
    custom_definitions = load_custom_ticker_definitions()
    _ticker_cache.update(custom_definitions)
    
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
    """Reverse lookup: get ticker from company name using ticker JSON lookup."""
    ticker_lookup = load_ticker_lookup()
    
    company_lower = company_name.lower()
    
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
    },
    'bargaining_power_of_customers': {
        'display_name': 'Bargaining Power of Customers',
        'field_name': 'bargaining_power_of_customers',
        'prompt': """Rate the bargaining power of customers for {company_name} on a scale of 0-10, where:
- 0 = Very low customer bargaining power, customers have no alternative options, company has strong pricing control
- 5 = Moderate customer bargaining power, some alternatives available, balanced negotiation power
- 10 = Very high customer bargaining power, many alternatives, customers can easily switch, strong price sensitivity

Consider factors like:
- Number of alternative suppliers and competitors available to customers
- Customer switching costs and ease of substitution
- Customer concentration and dependency on key accounts
- Product differentiation and uniqueness
- Price sensitivity and elasticity of demand
- Customer access to information and transparency
- Threat of backward integration by customers
- Importance of product/service to customer's business
- Standardization vs. customization of offerings
- Customer buying power and volume purchasing ability
- Availability of substitute products or services
- Market fragmentation vs. concentration of customers

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': True
    },
    'bargaining_power_of_suppliers': {
        'display_name': 'Bargaining Power of Suppliers',
        'field_name': 'bargaining_power_of_suppliers',
        'prompt': """Rate the bargaining power of suppliers for {company_name} on a scale of 0-10, where:
- 0 = Very low supplier bargaining power, many alternative suppliers available, company has strong negotiation control
- 5 = Moderate supplier bargaining power, some supplier concentration, balanced negotiation power
- 10 = Very high supplier bargaining power, few suppliers, suppliers have strong control, company is highly dependent

Consider factors like:
- Number of alternative suppliers and availability of substitutes
- Supplier concentration and market structure
- Switching costs to change suppliers
- Company's dependency on specific suppliers
- Supplier's control over critical inputs or resources
- Threat of forward integration by suppliers
- Uniqueness and differentiation of supplier inputs
- Importance of supplier inputs to company's operations
- Standardization vs. customization of supplier inputs
- Company's purchasing power and volume buying ability
- Availability of alternative supply sources or vertical integration options
- Market fragmentation vs. concentration of suppliers
- Supplier's ability to control prices or terms
- Criticality of supplier relationships to company's business model

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': True
    },
    'product_quality_score': {
        'display_name': 'Product Quality',
        'field_name': 'product_quality_score',
        'prompt': """Rate the product quality for {company_name} on a scale of 0-10, where:
- 0 = Poor quality, frequent defects, low reliability, high customer dissatisfaction
- 5 = Moderate quality, acceptable performance, some quality issues occasionally
- 10 = Exceptional quality, industry-leading standards, high reliability, exceptional customer satisfaction

Consider factors like:
- Product reliability and durability
- Defect rates and quality control processes
- Customer satisfaction and reviews
- Industry awards and quality certifications
- Warranty and return rates
- Quality of materials and craftsmanship
- Consistency of product quality across batches
- Quality assurance and testing procedures
- Comparison to industry standards and competitors
- Long-term product performance and reliability
- Customer complaints and support issues
- Quality metrics and KPIs
- Investment in quality improvement initiatives

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'culture_employee_satisfaction_score': {
        'display_name': 'Culture / Employee Satisfaction',
        'field_name': 'culture_employee_satisfaction_score',
        'prompt': """Rate the quality of culture and employee satisfaction for {company_name} on a scale of 0-10, where:
- 0 = Poor culture, low employee satisfaction, high turnover, toxic work environment, poor employee morale
- 5 = Moderate culture, acceptable employee satisfaction, average retention, some cultural issues
- 10 = Exceptional culture, industry-leading employee satisfaction, low turnover, great work environment, high employee engagement

Consider factors like:
- Employee satisfaction scores and surveys
- Employee retention and turnover rates
- Glassdoor and employer review ratings
- Company culture and values alignment
- Work-life balance and employee benefits
- Diversity, equity, and inclusion practices
- Employee engagement and morale
- Leadership quality and management practices
- Opportunities for career growth and development
- Workplace safety and employee well-being
- Communication and transparency
- Recognition and reward systems
- Work environment and office culture
- Employee feedback mechanisms and responsiveness

Respond with ONLY the numerical score (0-10), no explanation needed.""",
        'is_reverse': False
    },
    'trailblazer_score': {
        'display_name': 'Trailblazer',
        'field_name': 'trailblazer_score',
        'prompt': """Rate how much {company_name} challenges the status quo and pushes boundaries (trailblazer quality) on a scale of 0-10, where:
- 0 = Follows status quo, avoids risks, conventional approaches, minimal innovation, stays in established boundaries
- 5 = Some boundary-pushing, occasional calculated risks, moderate innovation beyond industry norms
- 10 = Extremely bold trailblazer, consistently challenges status quo, willing to take significant risks for big impact, pioneers new possibilities and transforms industries

Consider factors like:
- Willingness to challenge established industry norms and conventions
- Boldness in taking calculated risks for transformative impact
- Pioneering new markets, technologies, or business models
- Disruptive innovation that changes how industries operate
- Visionary leadership that pushes beyond current limitations
- Investment in moonshot projects and breakthrough initiatives
- History of breaking new ground and creating new categories
- Willingness to fail fast and learn from bold experiments
- Transformation of industries rather than incremental improvement
- Breaking conventional wisdom and traditional approaches
- Creating new paradigms and possibilities
- Revolutionary products, services, or business models
- Willingness to cannibalize existing businesses for future growth
- Aggressive pursuit of ambitious, transformative goals

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


def load_heavy_scores():
    """Load existing heavy scores from JSON file."""
    if os.path.exists(HEAVY_SCORES_FILE):
        try:
            with open(HEAVY_SCORES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"companies": {}}
    return {"companies": {}}


def save_heavy_scores(scores_data):
    """Save heavy scores to JSON file."""
    with open(HEAVY_SCORES_FILE, 'w') as f:
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


def query_score(grok, company_name, score_key, show_timing=True):
    """Query a single score from Grok.
    
    Args:
        grok: GrokClient instance
        company_name: Company name to score
        score_key: Score metric key
        show_timing: If True, print timing and token information
    """
    score_def = SCORE_DEFINITIONS[score_key]
    prompt = score_def['prompt'].format(company_name=company_name)
    start_time = time.time()
    response, token_usage = grok.simple_query_with_tokens(prompt, model="grok-4-fast")
    elapsed_time = time.time() - start_time
    total_tokens = token_usage.get('total_tokens', 0)
    if show_timing:
        print(f"  Time: {elapsed_time:.2f}s | Tokens: {total_tokens}")
    return response.strip()


def query_score_heavy(grok, company_name, score_key):
    """Query a single score from Grok using the main Grok 4 model."""
    score_def = SCORE_DEFINITIONS[score_key]
    prompt = score_def['prompt'].format(company_name=company_name)
    start_time = time.time()
    response, token_usage = grok.simple_query_with_tokens(prompt, model="grok-4-latest")
    elapsed_time = time.time() - start_time
    total_tokens = token_usage.get('total_tokens', 0)
    print(f"  Time: {elapsed_time:.2f}s | Tokens: {total_tokens}")
    return response.strip()


def score_single_ticker(input_str, silent=False, batch_mode=False):
    """Score a single ticker and return the result.
    
    Args:
        input_str: Ticker symbol or company name
        silent: If True, don't print progress messages (only errors)
        batch_mode: If True, show compact metric names during scoring (for batch processing)
        
    Returns:
        dict with keys: 'ticker', 'company_name', 'scores', 'total', 'success', 'error'
        Returns None if ticker is invalid
    """
    try:
        input_stripped = input_str.strip()
        input_upper = input_stripped.upper()
        
        ticker = None
        company_name = None
        
        ticker_lookup = load_ticker_lookup()
        if input_upper in ticker_lookup:
            ticker = input_upper
            company_name = ticker_lookup[ticker]
        else:
            if not silent:
                print(f"\nError: '{input_upper}' is not a valid ticker symbol.")
                print("Please enter a valid NYSE or NASDAQ ticker symbol.")
            return None
        
        scores_data = load_scores()
        
        # Try to find existing scores
        existing_data = None
        storage_key = None
        
        if ticker and ticker in scores_data["companies"]:
            existing_data = scores_data["companies"][ticker]
            storage_key = ticker
        elif ticker and ticker.lower() in scores_data["companies"]:
            existing_data = scores_data["companies"][ticker.lower()]
            storage_key = ticker.lower()
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
                # All scores exist
                total = calculate_total_score(current_scores)
                return {
                    'ticker': ticker,
                    'company_name': company_name,
                    'scores': current_scores,
                    'total': total,
                    'success': True,
                    'already_scored': True
                }
            
            # Some scores missing, fill them in
            if not silent:
                print(f"\nFilling missing scores for {ticker.upper()} ({company_name})...")
            grok = GrokClient(api_key=XAI_API_KEY)
            
            for score_key in SCORE_DEFINITIONS:
                if not current_scores[score_key]:
                    score_def = SCORE_DEFINITIONS[score_key]
                    if batch_mode:
                        print(f"  {score_def['display_name']}: ", end="", flush=True)
                        current_scores[score_key] = query_score(grok, company_name, score_key, show_timing=False)
                        print(f"{current_scores[score_key]}/10")
                    elif not silent:
                        print(f"Querying {score_def['display_name']}...")
                        current_scores[score_key] = query_score(grok, company_name, score_key, show_timing=True)
                        print(f"{score_def['display_name']} Score: {current_scores[score_key]}/10")
                        print()
            
            storage_key = ticker if ticker else company_name.lower()
            scores_data["companies"][storage_key] = current_scores
            save_scores(scores_data)
            if not silent:
                print(f"\nScores updated in {SCORES_FILE}")
            
            total = calculate_total_score(current_scores)
            if not silent:
                total_str = format_total_score(total)
                print(f"Total Score: {total_str}")
            return {
                'ticker': ticker,
                'company_name': company_name,
                'scores': current_scores,
                'total': total,
                'success': True,
                'already_scored': False
            }
        
        # New scoring needed
        if not silent:
            print(f"\nAnalyzing {ticker.upper()} ({company_name})...")
        grok = GrokClient(api_key=XAI_API_KEY)
        
        all_scores = {}
        for score_key in SCORE_DEFINITIONS:
            score_def = SCORE_DEFINITIONS[score_key]
            if batch_mode:
                print(f"  {score_def['display_name']}: ", end="", flush=True)
                all_scores[score_key] = query_score(grok, company_name, score_key, show_timing=False)
                print(f"{all_scores[score_key]}/10")
            elif not silent:
                print(f"Querying {score_def['display_name']}...")
                all_scores[score_key] = query_score(grok, company_name, score_key, show_timing=True)
                print(f"{score_def['display_name']} Score: {all_scores[score_key]}/10")
                print()
        
        storage_key = ticker if ticker else company_name.lower()
        scores_data["companies"][storage_key] = all_scores
        save_scores(scores_data)
        if not silent:
            print(f"\nScores saved to {SCORES_FILE}")
        
        total = calculate_total_score(all_scores)
        if not silent:
            total_str = format_total_score(total)
            print(f"Total Score: {total_str}")
        return {
            'ticker': ticker,
            'company_name': company_name,
            'scores': all_scores,
            'total': total,
            'success': True,
            'already_scored': False
        }
        
    except ValueError as e:
        error_msg = str(e)
        if not silent:
            print(f"Error: {error_msg}")
            print("\nTo fix this:")
            print("1. Get an API key from https://console.x.ai/")
            print("2. Set the XAI_API_KEY environment variable:")
            print("   export XAI_API_KEY='your_api_key_here'")
        return {
            'ticker': input_str.upper() if input_str else None,
            'company_name': None,
            'scores': None,
            'total': None,
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = str(e)
        if not silent:
            print(f"Error: {error_msg}")
        return {
            'ticker': input_str.upper() if input_str else None,
            'company_name': None,
            'scores': None,
            'total': None,
            'success': False,
            'error': error_msg
        }


def score_multiple_tickers(input_str):
    """Score multiple tickers and display results grouped together.
    
    Args:
        input_str: Space-separated ticker symbols
    """
    tickers = input_str.strip().split()
    
    if not tickers:
        print("Please provide at least one ticker symbol.")
        return
    
    print(f"\nProcessing {len(tickers)} ticker(s)...")
    print("=" * 80)
    
    results = []
    ticker_lookup = load_ticker_lookup()
    for i, ticker in enumerate(tickers, 1):
        ticker_upper = ticker.strip().upper()
        company_name = ticker_lookup.get(ticker_upper, ticker_upper)
        print(f"\n[{i}/{len(tickers)}] Processing {ticker_upper} ({company_name})...")
        result = score_single_ticker(ticker, silent=True, batch_mode=True)
        if result:
            if result['success']:
                if result.get('already_scored'):
                    print(f"  ✓ {ticker.upper()} already scored")
                else:
                    print(f"  ✓ {ticker.upper()} scored successfully")
            else:
                print(f"  ✗ Error scoring {ticker.upper()}: {result.get('error', 'Unknown error')}")
            results.append(result)
        else:
            print(f"  ✗ '{ticker}' is not a valid ticker. Skipping.")
    
    if not results:
        print("\nNo valid tickers were processed.")
        return
    
    # Display grouped results
    print("\n" + "=" * 80)
    print("Group Results")
    print("=" * 80)
    
    # Get all totals for percentile calculation
    all_totals = get_all_total_scores()
    
    # Sort results by total score (descending)
    results.sort(key=lambda x: x['total'] if x['total'] is not None else -1, reverse=True)
    
    # Calculate max score for percentage
    max_score = sum(SCORE_WEIGHTS.get(key, 1.0) for key in SCORE_DEFINITIONS) * 10
    
    # Find max name length for formatting (just ticker, no company name)
    max_name_len = max([len(r['ticker']) for r in results if r['success']], default=0)
    max_name_len = min(max(max_name_len, 6), 20)  # At least 6, cap at 20
    
    print(f"\n{'Rank':<6} {'Ticker':<{max_name_len}} {'Total Score':>15} {'Percentile':>12}")
    print("-" * (6 + max_name_len + 15 + 12 + 3))
    
    for rank, result in enumerate(results, 1):
        if not result['success']:
            display_name = result['ticker'] or 'Unknown'
            print(f"{rank:<6} {display_name:<{max_name_len}} {'ERROR':>15} {'N/A':>12}")
            if result.get('error'):
                print(f"       Error: {result['error']}")
            continue
        
        ticker = result['ticker']
        total = result['total']
        
        display_name = ticker
        
        percentage = int((total / max_score) * 100) if total is not None else 0
        percentage_str = f"{percentage}%"
        
        # Calculate percentile
        percentile = None
        if all_totals and len(all_totals) > 1 and total is not None:
            percentile = calculate_percentile_rank(total, all_totals)
        
        if percentile is not None:
            percentile_str = f"{percentile}th"
        else:
            percentile_str = 'N/A'
        
        print(f"{rank:<6} {display_name:<{max_name_len}} {percentage_str:>15} {percentile_str:>12}")
    
    print("=" * 80)


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
        
        # Try to find existing scores (by ticker, then lowercase ticker, then by company name for backwards compatibility)
        existing_data = None
        storage_key = None
        
        if ticker and ticker in scores_data["companies"]:
            existing_data = scores_data["companies"][ticker]
            storage_key = ticker
        elif ticker and ticker.lower() in scores_data["companies"]:
            # Try lowercase ticker for backwards compatibility
            existing_data = scores_data["companies"][ticker.lower()]
            storage_key = ticker.lower()
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
                # Use 35 characters for metric name to accommodate "Bargaining Power of Customers" (31 chars)
                for score_value, display_name, score_val in score_list:
                    # Truncate if longer than 35 characters
                    truncated_name = display_name[:35] if len(display_name) <= 35 else display_name[:32] + "..."
                    print(f"{truncated_name:<35} {score_val:>8}")
                
                # Print total at the bottom
                total = calculate_total_score(current_scores)
                total_str = format_total_score(total)
                print(f"{'Total':<35} {total_str:>8}")
                return
            
            grok = GrokClient(api_key=XAI_API_KEY)
            
            for score_key in SCORE_DEFINITIONS:
                if not current_scores[score_key]:
                    score_def = SCORE_DEFINITIONS[score_key]
                    print(f"Querying {score_def['display_name']}...")
                    current_scores[score_key] = query_score(grok, company_name, score_key)
                    print(f"{score_def['display_name']} Score: {current_scores[score_key]}/10")
                    print()  # Add spacing between metrics
            
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
            print()  # Add spacing between metrics
        
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


def get_company_moat_score_heavy(input_str):
    """Get all scores for a company using SCORE_DEFINITIONS with the main Grok 4 model.
    
    Accepts either a ticker symbol or company name.
    Stores scores using ticker as key in scores_heavy.json.
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
        
        # Display format: Ticker (Company Name)
        if ticker:
            display_name = f"{ticker.upper()} ({company_name})"
            print(f"Company: {company_name}")
        
        scores_data = load_heavy_scores()
        
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
                    print(f"\n{ticker.upper()} ({company_name}) already scored (heavy):")
                else:
                    print(f"\n{company_name} already scored (heavy):")
                
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
                # Use 35 characters for metric name to accommodate "Bargaining Power of Customers" (31 chars)
                for score_value, display_name, score_val in score_list:
                    # Truncate if longer than 35 characters
                    truncated_name = display_name[:35] if len(display_name) <= 35 else display_name[:32] + "..."
                    print(f"{truncated_name:<35} {score_val:>8}")
                
                # Print total at the bottom
                total = calculate_total_score(current_scores)
                total_str = format_total_score(total)
                print(f"{'Total':<35} {total_str:>8}")
                return
            
            grok = GrokClient(api_key=XAI_API_KEY)
            
            for score_key in SCORE_DEFINITIONS:
                if not current_scores[score_key]:
                    score_def = SCORE_DEFINITIONS[score_key]
                    print(f"Querying {score_def['display_name']} (heavy model)...")
                    current_scores[score_key] = query_score_heavy(grok, company_name, score_key)
                    print(f"{score_def['display_name']} Score: {current_scores[score_key]}/10")
                    print()  # Add spacing between metrics
            
            # Use ticker for storage key if available, otherwise use company name
            storage_key = ticker if ticker else company_name.lower()
            scores_data["companies"][storage_key] = current_scores
            save_heavy_scores(scores_data)
            print(f"\nScores updated in {HEAVY_SCORES_FILE}")
            
            # Calculate and display total
            total = calculate_total_score(current_scores)
            total_str = format_total_score(total)
            print(f"Total Score: {total_str}")
            return
        
        if ticker:
            print(f"\nAnalyzing {ticker.upper()} ({company_name}) with heavy model...")
        else:
            print(f"\nAnalyzing {company_name} with heavy model...")
        grok = GrokClient(api_key=XAI_API_KEY)
        
        all_scores = {}
        for score_key in SCORE_DEFINITIONS:
            score_def = SCORE_DEFINITIONS[score_key]
            print(f"Querying {score_def['display_name']} (heavy model)...")
            all_scores[score_key] = query_score_heavy(grok, company_name, score_key)
            print(f"{score_def['display_name']} Score: {all_scores[score_key]}/10")
            print()  # Add spacing between metrics
        
        # Use ticker for storage key if available, otherwise use company name
        storage_key = ticker if ticker else company_name.lower()
        scores_data["companies"][storage_key] = all_scores
        save_heavy_scores(scores_data)
        print(f"\nScores saved to {HEAVY_SCORES_FILE}")
        
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


def handle_heavy_command(tickers_input):
    """Handle the heavy command - score companies with the main Grok 4 model.
    
    Args:
        tickers_input: Space-separated ticker symbols
    """
    if not tickers_input.strip():
        print("Please provide ticker symbols. Example: heavy AAPL MSFT GOOGL")
        return
    
    tickers = tickers_input.strip().split()
    
    for ticker in tickers:
        print(f"\n{'='*60}")
        get_company_moat_score_heavy(ticker)
        print()


def calculate_correlation(light_scores, heavy_scores):
    """Calculate Pearson correlation coefficient between two lists of scores.
    
    Args:
        light_scores: List of light score values (floats)
        heavy_scores: List of heavy score values (floats)
        
    Returns:
        float: Correlation coefficient between -1 and 1, or None if insufficient data
    """
    if len(light_scores) != len(heavy_scores) or len(light_scores) < 2:
        return None
    
    # Calculate means
    light_mean = sum(light_scores) / len(light_scores)
    heavy_mean = sum(heavy_scores) / len(heavy_scores)
    
    # Calculate numerator (covariance)
    numerator = sum((light_scores[i] - light_mean) * (heavy_scores[i] - heavy_mean) 
                   for i in range(len(light_scores)))
    
    # Calculate denominators (standard deviations)
    light_std = sum((x - light_mean) ** 2 for x in light_scores) ** 0.5
    heavy_std = sum((x - heavy_mean) ** 2 for x in heavy_scores) ** 0.5
    
    # Avoid division by zero
    if light_std == 0 or heavy_std == 0:
        return None
    
    # Pearson correlation coefficient
    correlation = numerator / (light_std * heavy_std)
    return correlation


def handle_correl_command(tickers_input):
    """Handle the correl command - calculate correlation between light and heavy metric scores for each ticker.
    
    For each ticker, calculates the correlation between all its light metric scores and heavy metric scores.
    
    Args:
        tickers_input: Space-separated ticker symbols
    """
    if not tickers_input.strip():
        print("Please provide ticker symbols. Example: correl AAPL MSFT GOOGL")
        return
    
    tickers = tickers_input.strip().split()
    light_scores_data = load_scores()
    heavy_scores_data = load_heavy_scores()
    ticker_lookup = load_ticker_lookup()
    
    results = []
    
    for ticker_input in tickers:
        ticker_upper = ticker_input.strip().upper()
        
        # Validate ticker
        if ticker_upper not in ticker_lookup:
            print(f"Warning: '{ticker_upper}' is not a valid ticker symbol. Skipping.")
            continue
        
        company_name = ticker_lookup[ticker_upper]
        
        # Check if both light and heavy scores exist
        # Try uppercase ticker first, then lowercase ticker, then lowercase company name
        light_data = light_scores_data["companies"].get(ticker_upper)
        heavy_data = heavy_scores_data["companies"].get(ticker_upper)
        
        # Try lowercase ticker for backwards compatibility
        if not light_data:
            light_data = light_scores_data["companies"].get(ticker_upper.lower())
        if not heavy_data:
            heavy_data = heavy_scores_data["companies"].get(ticker_upper.lower())
        
        # Try lowercase company name for backwards compatibility
        if not light_data:
            company_name_lower = company_name.lower()
            light_data = light_scores_data["companies"].get(company_name_lower)
        if not heavy_data:
            company_name_lower = company_name.lower()
            heavy_data = heavy_scores_data["companies"].get(company_name_lower)
        
        if not light_data:
            print(f"Warning: '{ticker_upper}' has no light scores. Skipping.")
            continue
        
        if not heavy_data:
            print(f"Warning: '{ticker_upper}' has no heavy scores. Skipping.")
            continue
        
        # Collect all metric scores for this ticker
        light_metric_scores = []
        heavy_metric_scores = []
        metric_names = []
        
        try:
            for score_key in SCORE_DEFINITIONS:
                # Get light score
                light_score_str = light_data.get(score_key)
                if score_key == 'moat_score' and not light_score_str:
                    light_score_str = light_data.get('score')  # Backwards compatibility
                
                # Get heavy score
                heavy_score_str = heavy_data.get(score_key)
                if score_key == 'moat_score' and not heavy_score_str:
                    heavy_score_str = heavy_data.get('score')  # Backwards compatibility
                
                # Only include metrics that have both light and heavy scores
                if light_score_str and heavy_score_str:
                    try:
                        light_score = float(light_score_str)
                        heavy_score = float(heavy_score_str)
                        light_metric_scores.append(light_score)
                        heavy_metric_scores.append(heavy_score)
                        metric_names.append(SCORE_DEFINITIONS[score_key]['display_name'])
                    except (ValueError, TypeError):
                        continue
            
            # Need at least 2 metrics to calculate correlation
            if len(light_metric_scores) < 2:
                print(f"Warning: '{ticker_upper}' has insufficient metrics ({len(light_metric_scores)}) for correlation. Need at least 2.")
                continue
            
            # Calculate correlation for this ticker
            correlation = calculate_correlation(light_metric_scores, heavy_metric_scores)
            
            if correlation is None:
                print(f"Warning: Could not calculate correlation for '{ticker_upper}' (zero variance). Skipping.")
                continue
            
            # Calculate total scores for display - only use metrics that exist in both datasets
            # Track which score keys were actually used for comparison
            used_score_keys = []
            for score_key in SCORE_DEFINITIONS:
                light_score_str = light_data.get(score_key)
                if score_key == 'moat_score' and not light_score_str:
                    light_score_str = light_data.get('score')  # Backwards compatibility
                heavy_score_str = heavy_data.get(score_key)
                if score_key == 'moat_score' and not heavy_score_str:
                    heavy_score_str = heavy_data.get('score')  # Backwards compatibility
                if light_score_str and heavy_score_str:
                    used_score_keys.append(score_key)
            
            # Calculate totals using only the metrics that exist in both datasets
            light_total = 0
            heavy_total = 0
            for score_key in used_score_keys:
                score_def = SCORE_DEFINITIONS[score_key]
                weight = SCORE_WEIGHTS.get(score_key, 1.0)
                try:
                    light_score_str = light_data.get(score_key)
                    if score_key == 'moat_score' and not light_score_str:
                        light_score_str = light_data.get('score')
                    heavy_score_str = heavy_data.get(score_key)
                    if score_key == 'moat_score' and not heavy_score_str:
                        heavy_score_str = heavy_data.get('score')
                    
                    light_value = float(light_score_str)
                    heavy_value = float(heavy_score_str)
                    
                    if score_def['is_reverse']:
                        light_total += (10 - light_value) * weight
                        heavy_total += (10 - heavy_value) * weight
                    else:
                        light_total += light_value * weight
                        heavy_total += heavy_value * weight
                except (ValueError, TypeError):
                    pass
            
            results.append({
                'ticker': ticker_upper,
                'company_name': company_name,
                'correlation': correlation,
                'num_metrics': len(light_metric_scores),
                'light_scores': light_metric_scores,
                'heavy_scores': heavy_metric_scores,
                'metric_names': metric_names,
                'light_total': light_total,
                'heavy_total': heavy_total,
                'used_score_keys': used_score_keys  # Store for max_score calculation
            })
            
        except Exception as e:
            print(f"Warning: Error processing '{ticker_upper}': {e}. Skipping.")
            continue
    
    if not results:
        print("\nError: No tickers could be processed for correlation analysis.")
        print("Make sure all tickers have both light and heavy scores with at least 2 metrics each.")
        return
    
    # Display results
    print(f"\n{'='*80}")
    print("Correlation Analysis: Light vs Heavy Metric Scores (Per Ticker)")
    print(f"{'='*80}")
    print(f"\nTickers analyzed: {len(results)}")
    
    for result in results:
        ticker = result['ticker']
        company_name = result['company_name']
        correlation = result['correlation']
        num_metrics = result['num_metrics']
        light_scores = result['light_scores']
        heavy_scores = result['heavy_scores']
        metric_names = result['metric_names']
        
        print(f"\n{'='*80}")
        print(f"{ticker} ({company_name})")
        print(f"{'='*80}")
        print(f"Number of metrics compared: {num_metrics}")
        print(f"\n{'Metric':<35} {'Light':>10} {'Heavy':>10} {'Diff':>10}")
        print("-" * 80)
        
        for i, metric_name in enumerate(metric_names):
            light_val = light_scores[i]
            heavy_val = heavy_scores[i]
            diff = heavy_val - light_val
            diff_str = f"{diff:+.1f}" if diff != 0 else "0.0"
            
            # Truncate long metric names
            display_name = metric_name[:33] if len(metric_name) <= 33 else metric_name[:30] + "..."
            print(f"{display_name:<35} {light_val:>10.1f} {heavy_val:>10.1f} {diff_str:>10}")
        
        # Calculate and display total scores
        light_total = result['light_total']
        heavy_total = result['heavy_total']
        # Calculate max_score based only on metrics that exist in both datasets
        used_score_keys = result.get('used_score_keys', [])
        if used_score_keys:
            max_score = sum(SCORE_WEIGHTS.get(key, 1.0) for key in used_score_keys) * 10
        else:
            # Fallback: use all metrics if used_score_keys not available (shouldn't happen)
            max_score = sum(SCORE_WEIGHTS.get(key, 1.0) for key in SCORE_DEFINITIONS) * 10
        light_pct = int((light_total / max_score) * 100)
        heavy_pct = int((heavy_total / max_score) * 100)
        total_diff = heavy_total - light_total
        total_diff_pct = int((total_diff / max_score) * 100)
        total_diff_str = f"{total_diff_pct:+d}%" if total_diff != 0 else "0%"
        
        print("-" * 80)
        print(f"{'Total Score':<35} {light_pct:>9}% {heavy_pct:>9}% {total_diff_str:>10}")
        
        print(f"\nPearson Correlation Coefficient: {correlation:.4f}")
        
        # Interpret correlation
        abs_corr = abs(correlation)
        if abs_corr >= 0.9:
            strength = "very strong"
        elif abs_corr >= 0.7:
            strength = "strong"
        elif abs_corr >= 0.5:
            strength = "moderate"
        elif abs_corr >= 0.3:
            strength = "weak"
        else:
            strength = "very weak"
        
        direction = "positive" if correlation > 0 else "negative"
        print(f"Interpretation: {strength} {direction} correlation")
    
    print(f"\n{'='*80}")


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


def view_heavy_scores():
    """Display all stored heavy scores ranked by total score with percentiles."""
    scores_data = load_heavy_scores()
    
    if not scores_data["companies"]:
        print("No heavy scores stored yet.")
        return
    
    # Helper function to calculate total score
    def get_total_score(item):
        data = item[1]
        total = 0
        for score_key, score_def in SCORE_DEFINITIONS.items():
            score_val = data.get(score_key, 'N/A')
            weight = SCORE_WEIGHTS.get(score_key, 1.0)
            if score_val == 'N/A':
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
    
    # Calculate all totals for percentile calculation
    all_totals = []
    company_totals = {}
    for company, data in sorted_companies:
        total = get_total_score((company, data))
        if total > 0:  # Only include companies with valid scores
            company_totals[company] = total
            all_totals.append(total)
    
    if not company_totals:
        print("No valid heavy scores found.")
        return
    
    print("\nHeavy Scores - Total Score Rankings:")
    print("=" * 80)
    print(f"Number of stocks scored: {len(company_totals)}")
    print()
    
    max_name_len = max([len(company.upper()) for company in company_totals.keys()]) if company_totals else 0
    
    # Print column headers
    print(f"{'Rank':<6} {'Ticker':<{min(max_name_len, 30)}} {'Total Score':>15} {'Percentile':>12}")
    print("-" * (6 + min(max_name_len, 30) + 15 + 12 + 3))
    
    # Display companies with rankings and percentiles
    for rank, (company, data) in enumerate(sorted_companies, 1):
        if company in company_totals:
            total = company_totals[company]
            max_score = sum(SCORE_WEIGHTS.get(key, 1.0) for key in SCORE_DEFINITIONS) * 10
            percentage = int((total / max_score) * 100)
            percentage_str = f"{percentage}%"
            
            percentile = calculate_percentile_rank(total, all_totals) if len(all_totals) > 1 else None
            if percentile is not None:
                percentile_str = f"{percentile}th"
            else:
                percentile_str = 'N/A'
            
            # Display ticker (uppercase for consistency)
            display_key = company.upper()
            if len(display_key) > 30:
                display_key = display_key[:30]
            print(f"{rank:<6} {display_key:<{min(max_name_len, 30)}} {percentage_str:>15} {percentile_str:>12}")


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

def add_ticker_definition(ticker, company_name):
    """Add or update a custom ticker definition.
    
    Args:
        ticker: Ticker symbol (will be converted to uppercase)
        company_name: Company name to map to
        
    Returns:
        bool: True if successful, False otherwise
    """
    ticker_upper = ticker.strip().upper()
    company_name_stripped = company_name.strip()
    
    if not ticker_upper:
        print("Error: Ticker symbol cannot be empty.")
        return False
    
    if not company_name_stripped:
        print("Error: Company name cannot be empty.")
        return False
    
    # Load existing definitions
    custom_definitions = load_custom_ticker_definitions()
    
    # Check if it already exists
    if ticker_upper in custom_definitions:
        print(f"Updating existing definition: {ticker_upper} = {custom_definitions[ticker_upper]}")
    
    # Add or update
    custom_definitions[ticker_upper] = company_name_stripped
    
    # Save
    if save_custom_ticker_definitions(custom_definitions):
        print(f"✓ Added definition: {ticker_upper} = {company_name_stripped}")
        # Clear cache so it reloads with new definition
        global _ticker_cache
        _ticker_cache = None
        return True
    else:
        return False

def remove_ticker_definition(ticker):
    """Remove a custom ticker definition.
    
    Args:
        ticker: Ticker symbol to remove
        
    Returns:
        bool: True if successful, False otherwise
    """
    ticker_upper = ticker.strip().upper()
    
    # Load existing definitions
    custom_definitions = load_custom_ticker_definitions()
    
    if ticker_upper not in custom_definitions:
        print(f"Error: '{ticker_upper}' is not in custom ticker definitions.")
        return False
    
    # Remove
    company_name = custom_definitions.pop(ticker_upper)
    
    # Save
    if save_custom_ticker_definitions(custom_definitions):
        print(f"✓ Removed definition: {ticker_upper} = {company_name}")
        # Clear cache so it reloads without the removed definition
        global _ticker_cache
        _ticker_cache = None
        return True
    else:
        return False

def list_ticker_definitions():
    """List all custom ticker definitions."""
    custom_definitions = load_custom_ticker_definitions()
    
    if not custom_definitions:
        print("No custom ticker definitions found.")
        return
    
    print("\nCustom Ticker Definitions:")
    print("=" * 60)
    print(f"{'Ticker':<10} {'Company Name':<40}")
    print("-" * 60)
    
    for ticker in sorted(custom_definitions.keys()):
        company_name = custom_definitions[ticker]
        print(f"{ticker:<10} {company_name:<40}")
    
    print(f"\nTotal: {len(custom_definitions)} definition(s)")

def handle_define_command(command_input):
    """Handle the define command - add/remove/list ticker definitions.
    
    Args:
        command_input: Command input after 'define' keyword
    """
    command_input = command_input.strip()
    
    if not command_input:
        print("Usage:")
        print("  define SKH = SK Hynix          - Add/update a ticker definition")
        print("  define -r SKH                  - Remove a ticker definition")
        print("  define -l                      - List all custom ticker definitions")
        return
    
    # List command
    if command_input.lower() in ['-l', '--list', 'list']:
        list_ticker_definitions()
        return
    
    # Remove command
    if command_input.lower().startswith('-r ') or command_input.lower().startswith('--remove '):
        ticker = command_input[3:].strip() if command_input.lower().startswith('-r ') else command_input[9:].strip()
        if ticker:
            remove_ticker_definition(ticker)
        else:
            print("Error: Please provide a ticker symbol to remove.")
        return
    
    # Add/update command - look for "=" separator
    if '=' in command_input:
        parts = command_input.split('=', 1)
        if len(parts) == 2:
            ticker = parts[0].strip()
            company_name = parts[1].strip()
            
            if ticker and company_name:
                add_ticker_definition(ticker, company_name)
            else:
                print("Error: Both ticker and company name are required.")
                print("Usage: define SKH = SK Hynix")
        else:
            print("Error: Invalid format. Use: define SKH = SK Hynix")
    else:
        print("Error: Invalid command. Use:")
        print("  define SKH = SK Hynix          - Add/update a ticker definition")
        print("  define -r SKH                  - Remove a ticker definition")
        print("  define -l                      - List all custom ticker definitions")


def main():
    """Main function to run the moat scorer."""
    print("Company Competitive Moat Scorer")
    print("=" * 40)
    print("Commands:")
    print("  Enter ticker symbol (e.g., AAPL) or multiple tickers (e.g., AAPL MSFT GOOGL) to score")
    print("  Type 'view' to see total scores")
    print("  Type 'view heavy' to see heavy model scores ranked with percentiles")
    print("  Type 'rank' to see rankings by metric")
    print("  Type 'delete' to remove a company's scores")
    print("  Type 'fill' to score companies with missing scores")
    print("  Type 'migrate' to fix duplicate entries")
    print("  Type 'heavy TICKER1 TICKER2 ...' to score with main Grok 4 model")
    print("  Type 'correl TICKER1 TICKER2 ...' to see correlation between light and heavy metric scores per ticker")
    print("  Type 'define TICKER = Company Name' to add custom ticker definition")
    print("  Type 'define -r TICKER' to remove a custom ticker definition")
    print("  Type 'define -l' to list all custom ticker definitions")
    print("  Type 'quit' or 'exit' to stop")
    print()
    
    while True:
        try:
            user_input = input("Enter ticker or company name (or 'view'/'view heavy'/'rank'/'delete'/'fill'/'heavy'/'correl'/'define'/'quit'): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'view heavy':
                view_heavy_scores()
                print()
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
            elif user_input.lower() == 'heavy':
                print("Please provide ticker symbols. Example: heavy AAPL MSFT GOOGL")
                print()
            elif user_input.lower().startswith('heavy '):
                tickers = user_input[6:].strip()  # Remove 'heavy ' prefix
                handle_heavy_command(tickers)
            elif user_input.lower() == 'correl':
                print("Please provide ticker symbols. Example: correl AAPL MSFT GOOGL")
                print()
            elif user_input.lower().startswith('correl '):
                tickers = user_input[7:].strip()  # Remove 'correl ' prefix
                handle_correl_command(tickers)
                print()
            elif user_input.lower() == 'define':
                print("Usage:")
                print("  define SKH = SK Hynix          - Add/update a ticker definition")
                print("  define -r SKH                  - Remove a ticker definition")
                print("  define -l                      - List all custom ticker definitions")
                print()
            elif user_input.lower().startswith('define '):
                command_input = user_input[7:].strip()  # Remove 'define ' prefix
                handle_define_command(command_input)
                print()
            elif user_input:
                # Check if input contains multiple space-separated tickers
                tickers = user_input.strip().split()
                if len(tickers) > 1:
                    # Multiple tickers - use the batch scoring function
                    score_multiple_tickers(user_input)
                    print()
                else:
                    # Single ticker - use the original function
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

