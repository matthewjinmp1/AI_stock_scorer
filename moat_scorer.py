#!/usr/bin/env python3
"""
Company Competitive Moat Scorer
Gets Grok to rate a company's competitive moat strength across 7 metrics (0-10 each):
- Competitive Moat
- Barriers to Entry
- Disruption Risk
- Switching Cost
- Brand Strength
- Competition Intensity
- Network Effect
Usage: python moat_scorer.py
Then enter company names interactively
"""

from grok_client import GrokClient
from config import XAI_API_KEY
import sys
import json
import os
from datetime import datetime

# JSON file to store moat scores
SCORES_FILE = "moat_scores.json"

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


def query_score(grok, company_name, score_key):
    """Query a single score from Grok."""
    score_def = SCORE_DEFINITIONS[score_key]
    prompt = score_def['prompt'].format(company_name=company_name)
    response, _ = grok.simple_query_with_tokens(prompt, model="grok-4-fast")
    return response.strip()


def get_company_moat_score(company_name):
    """Get all scores for a company using SCORE_DEFINITIONS."""
    try:
        company_name_lower = company_name.lower()
        scores_data = load_scores()
        
        if company_name_lower in scores_data["companies"]:
            existing_data = scores_data["companies"][company_name_lower]
            
            current_scores = {}
            for score_key in SCORE_DEFINITIONS:
                if score_key == 'moat_score':
                    current_scores[score_key] = existing_data.get(score_key, existing_data.get('score'))
                else:
                    current_scores[score_key] = existing_data.get(score_key)
            
            if all(current_scores.values()):
                print(f"\n{company_name} already scored:")
                for score_key in SCORE_DEFINITIONS:
                    score_def = SCORE_DEFINITIONS[score_key]
                    print(f"{score_def['display_name']}: {current_scores[score_key]}/10")
                return
            
            grok = GrokClient(api_key=XAI_API_KEY)
            
            for score_key in SCORE_DEFINITIONS:
                if not current_scores[score_key]:
                    score_def = SCORE_DEFINITIONS[score_key]
                    print(f"Querying {score_def['display_name']}...")
                    current_scores[score_key] = query_score(grok, company_name, score_key)
                    print(f"{score_def['display_name']} Score: {current_scores[score_key]}/10")
            
            scores_data["companies"][company_name_lower] = current_scores
            save_scores(scores_data)
            print(f"\nScores updated in {SCORES_FILE}")
            return
        
        print(f"Analyzing {company_name}...")
        grok = GrokClient(api_key=XAI_API_KEY)
        
        all_scores = {}
        for score_key in SCORE_DEFINITIONS:
            score_def = SCORE_DEFINITIONS[score_key]
            print(f"Querying {score_def['display_name']}...")
            all_scores[score_key] = query_score(grok, company_name, score_key)
            print(f"{score_def['display_name']} Score: {all_scores[score_key]}/10")
        
        scores_data["companies"][company_name_lower] = all_scores
        save_scores(scores_data)
        print(f"\nScores saved to {SCORES_FILE}")
        
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
            print(f"{company_name.capitalize()}: Moat {moat}/10 - Missing: {', '.join(missing)}")
        
        print(f"\nQuerying missing scores...")
        print("=" * 60)
        
        for i, (company_name, company_scores) in enumerate(companies_to_score, 1):
            print(f"\n[{i}/{len(companies_to_score)}] Processing {company_name.capitalize()}...")
            
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
                    or a company name (show all scores for that company).
    """
    scores_data = load_scores()
    
    if not scores_data["companies"]:
        print("No scores stored yet.")
        return
    
    # Check if score_type is actually a company name
    if score_type:
        company_lower = score_type.lower()
        if company_lower in scores_data["companies"]:
            # Display all scores for this specific company
            print(f"\n{score_type.capitalize()} Scores:")
            print("=" * 80)
            
            data = scores_data["companies"][company_lower]
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
                        # For reverse scores, invert to get "goodness" value
                        if score_def['is_reverse']:
                            sort_value = 10 - val
                            total += (10 - val)
                        else:
                            sort_value = val
                            total += val
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
                total_str = f"{int(total)}" if total == int(total) else f"{total:.1f}"
                print(f"{'Total':25} {total_str:>8}")
            
            return
    
    # Helper function to calculate total score
    def get_total_score(item):
        data = item[1]
        total = 0
        for score_key, score_def in SCORE_DEFINITIONS.items():
            score_val = data.get(score_key, 'N/A')
            if score_val == 'N/A':
                if score_def['is_reverse']:
                    total += 10
                continue
            
            try:
                val = float(score_val)
                if score_def['is_reverse']:
                    total += (10 - val)
                else:
                    total += val
            except (ValueError, TypeError):
                    pass
        return total
    
    sorted_companies = sorted(scores_data["companies"].items(), key=get_total_score, reverse=True)
    
    # If score_type not provided, show total scores for all companies
    if not score_type:
        print("\nStored Company Scores (Total only):")
        print("=" * 80)
        
        max_name_len = max([len(company.capitalize()) for company, data in sorted_companies]) if sorted_companies else 0
        
        for company, data in sorted_companies:
            total = 0
            all_present = True
            for score_key, score_def in SCORE_DEFINITIONS.items():
                score_val = data.get(score_key, 'N/A')
                if score_val == 'N/A':
                    all_present = False
                    break
                try:
                    val = float(score_val)
                    if score_def['is_reverse']:
                        total += (10 - val)
                    else:
                        total += val
                except (ValueError, TypeError):
                    all_present = False
                    break
            
            if all_present:
                total_str = f"{int(total)}" if total == int(total) else f"{total:.1f}"
            else:
                total_str = 'N/A'
            
            print(f"{company.capitalize():<{max_name_len}} {total_str:>8}")
        return
    else:
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
        max_name_len = max([len(company.capitalize()) for company, data in sorted_by_field]) if sorted_by_field else 0
        
        for company, data in sorted_by_field:
            score = data.get(matching_key, 'N/A')
            if score != 'N/A':
                try:
                    score_float = float(score)
                    score = f"{int(score_float)}" if score_float == int(score_float) else f"{score_float:.1f}"
                except (ValueError, TypeError):
                    pass
            print(f"{company.capitalize():<{max_name_len}} {score:>8}")


def main():
    """Main function to run the moat scorer."""
    print("Company Competitive Moat Scorer")
    print("=" * 40)
    print("Commands:")
    print("  Enter company name to score")
    print("  Type 'view' to see total scores")
    print("  Type 'view <type>' to see specific scores across companies")
    print("  Type 'view <company>' to see all scores for a specific company")
    print("  Type 'fill' to score companies with missing scores")
    print("  Type 'migrate' to fix duplicate entries")
    print("  Type 'quit' or 'exit' to stop")
    print()
    
    while True:
        try:
            user_input = input("Enter company name (or 'view'/'fill'/'quit'): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower().startswith('view'):
                parts = user_input.lower().split()
                if len(parts) == 1:
                    view_scores()
                else:
                    score_type = parts[1]
                    view_scores(score_type)
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
                print("Please enter a company name.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()

