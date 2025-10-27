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


def get_company_moat_score(company_name):
    """Get competitive moat, barriers to entry, disruption risk, and switching costs scores for a company from Grok."""
    try:
        # Convert company name to lowercase for storage consistency
        company_name_lower = company_name.lower()
        
        # Load existing scores to check if company already exists
        scores_data = load_scores()
        
        # Check if company already exists
        if company_name_lower in scores_data["companies"]:
            existing_data = scores_data["companies"][company_name_lower]
            moat_score = existing_data.get('moat_score', existing_data.get('score'))
            barriers_score = existing_data.get('barriers_score')
            disruption_score = existing_data.get('disruption_risk')
            switching_cost = existing_data.get('switching_cost')
            brand_strength = existing_data.get('brand_strength')
            competition_intensity = existing_data.get('competition_intensity')
            network_effect = existing_data.get('network_effect')
            
            # If company already has all seven scores, just display them
            if moat_score and barriers_score and disruption_score and switching_cost and brand_strength and competition_intensity and network_effect:
                print(f"\n{company_name} already scored:")
                print(f"Competitive Moat: {moat_score}/10")
                print(f"Barriers to Entry: {barriers_score}/10")
                print(f"Disruption Risk: {disruption_score}/10")
                print(f"Switching Cost: {switching_cost}/10")
                print(f"Brand Strength: {brand_strength}/10")
                print(f"Competition Intensity: {competition_intensity}/10")
                print(f"Network Effect: {network_effect}/10")
                return
            
            # Company exists but missing some scores - need to query for them
            grok = GrokClient(api_key=XAI_API_KEY)
            
            # Query for missing scores
            if not brand_strength:
                print(f"Querying brand strength...")
                brand_prompt = f"""Rate the brand strength for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                brand_response, _ = grok.simple_query_with_tokens(brand_prompt, model="grok-4-fast")
                brand_strength = brand_response.strip()
                print(f"Brand Strength Score: {brand_strength}/10")
            else:
                brand_strength = brand_strength
            
            if not competition_intensity:
                print(f"Querying competition intensity...")
                competition_prompt = f"""Rate the intensity of competition for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                competition_response, _ = grok.simple_query_with_tokens(competition_prompt, model="grok-4-fast")
                competition_intensity = competition_response.strip()
                print(f"Competition Intensity Score: {competition_intensity}/10")
            else:
                competition_intensity = competition_intensity
            
            if not network_effect:
                print(f"Querying network effect...")
                network_prompt = f"""Rate the network effects for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                network_response, _ = grok.simple_query_with_tokens(network_prompt, model="grok-4-fast")
                network_effect = network_response.strip()
                print(f"Network Effect Score: {network_effect}/10")
            else:
                network_effect = network_effect
            
            if not barriers_score:
                print(f"{company_name} already has a moat score ({moat_score}/10). Querying barriers to entry...")
                barriers_prompt = f"""Rate the barriers to entry for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                barriers_response, _ = grok.simple_query_with_tokens(barriers_prompt, model="grok-4-fast")
                barriers_score = barriers_response.strip()
                print(f"Barriers to Entry Score: {barriers_score}/10")
            else:
                barriers_score = barriers_score
            
            if not disruption_score:
                print(f"Querying disruption risk...")
                disruption_prompt = f"""Rate the disruption risk for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                disruption_response, _ = grok.simple_query_with_tokens(disruption_prompt, model="grok-4-fast")
                disruption_score = disruption_response.strip()
                print(f"Disruption Risk Score: {disruption_score}/10")
            else:
                disruption_score = disruption_score
            
            if not switching_cost:
                print(f"Querying switching costs...")
                switching_prompt = f"""Rate the switching costs for customers of {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                switching_response, _ = grok.simple_query_with_tokens(switching_prompt, model="grok-4-fast")
                switching_cost = switching_response.strip()
                print(f"Switching Cost Score: {switching_cost}/10")
            else:
                switching_cost = switching_cost
            
            # Update existing entry with missing scores
            scores_data["companies"][company_name_lower] = {
                "moat_score": moat_score,
                "barriers_score": barriers_score,
                "disruption_risk": disruption_score,
                "switching_cost": switching_cost,
                "brand_strength": brand_strength,
                "competition_intensity": competition_intensity,
                "network_effect": network_effect
            }
            
            save_scores(scores_data)
            print(f"\nScores updated in {SCORES_FILE}")
            return
        
        # Company doesn't exist, need to query for all four scores
        print(f"Analyzing {company_name}...")
        
        # Initialize the Grok client with API key
        grok = GrokClient(api_key=XAI_API_KEY)
        
        # Query 1: Competitive Moat Score
        moat_prompt = f"""Rate the competitive moat strength of {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

        moat_response, moat_token_usage = grok.simple_query_with_tokens(moat_prompt, model="grok-4-fast")
        moat_score = moat_response.strip()
        
        print(f"Competitive Moat Score: {moat_score}/10")
        
        # Query 2: Barriers to Entry Score
        barriers_prompt = f"""Rate the barriers to entry for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

        barriers_response, barriers_token_usage = grok.simple_query_with_tokens(barriers_prompt, model="grok-4-fast")
        barriers_score = barriers_response.strip()
        
        print(f"Barriers to Entry Score: {barriers_score}/10")
        
        # Query 3: Disruption Risk Score
        disruption_prompt = f"""Rate the disruption risk for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

        disruption_response, disruption_token_usage = grok.simple_query_with_tokens(disruption_prompt, model="grok-4-fast")
        disruption_score = disruption_response.strip()
        
        print(f"Disruption Risk Score: {disruption_score}/10")
        
        # Query 4: Switching Cost Score
        switching_prompt = f"""Rate the switching costs for customers of {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

        switching_response, switching_token_usage = grok.simple_query_with_tokens(switching_prompt, model="grok-4-fast")
        switching_cost = switching_response.strip()
        
        print(f"Switching Cost Score: {switching_cost}/10")
        
        # Query 5: Brand Strength Score
        brand_prompt = f"""Rate the brand strength for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

        brand_response, brand_token_usage = grok.simple_query_with_tokens(brand_prompt, model="grok-4-fast")
        brand_strength = brand_response.strip()
        
        print(f"Brand Strength Score: {brand_strength}/10")
        
        # Query 6: Competition Intensity Score
        competition_prompt = f"""Rate the intensity of competition for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

        competition_response, competition_token_usage = grok.simple_query_with_tokens(competition_prompt, model="grok-4-fast")
        competition_intensity = competition_response.strip()
        
        print(f"Competition Intensity Score: {competition_intensity}/10")
        
        # Query 7: Network Effect Score
        network_prompt = f"""Rate the network effects for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

        network_response, network_token_usage = grok.simple_query_with_tokens(network_prompt, model="grok-4-fast")
        network_effect = network_response.strip()
        
        print(f"Network Effect Score: {network_effect}/10")
        
        # Save all seven scores to JSON file
        scores_data["companies"][company_name_lower] = {
            "moat_score": moat_score,
            "barriers_score": barriers_score,
            "disruption_risk": disruption_score,
            "switching_cost": switching_cost,
            "brand_strength": brand_strength,
            "competition_intensity": competition_intensity,
            "network_effect": network_effect
        }
        
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
        # Keep the most recent entry if duplicates exist
        if company_lower not in lowercase_companies:
            lowercase_companies[company_lower] = data
        else:
            # Compare dates to keep the most recent (fallback to timestamp if exists)
            existing_date = lowercase_companies[company_lower].get('date', '1900-01-01')
            new_date = data.get('date', '1900-01-01')
            
            # If timestamps exist, use them for more precise comparison
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
    """Fill in missing barriers, disruption risk, switching cost, brand strength, competition intensity, and network effect scores for all companies."""
    try:
        scores_data = load_scores()
        grok = GrokClient(api_key=XAI_API_KEY)
        
        # Find companies missing barriers_score, disruption_risk, switching_cost, brand_strength, competition_intensity, or network_effect
        companies_to_score = []
        for company_name, data in scores_data["companies"].items():
            moat_score = data.get('moat_score', data.get('score'))
            barriers_score = data.get('barriers_score')
            disruption_risk = data.get('disruption_risk')
            switching_cost = data.get('switching_cost')
            brand_strength = data.get('brand_strength')
            competition_intensity = data.get('competition_intensity')
            network_effect = data.get('network_effect')
            
            if moat_score and (not barriers_score or not disruption_risk or not switching_cost or not brand_strength or not competition_intensity or not network_effect):
                companies_to_score.append((company_name, moat_score, barriers_score, disruption_risk, switching_cost, brand_strength, competition_intensity, network_effect))
        
        if not companies_to_score:
            print("\nAll companies already have all scores!")
            return
        
        print(f"\nFound {len(companies_to_score)} companies missing scores:")
        print("=" * 60)
        for company_name, moat, barriers, disruption, switching, brand, competition, network in companies_to_score:
            missing = []
            if not barriers:
                missing.append("barriers")
            if not disruption:
                missing.append("disruption risk")
            if not switching:
                missing.append("switching cost")
            if not brand:
                missing.append("brand strength")
            if not competition:
                missing.append("competition intensity")
            if not network:
                missing.append("network effect")
            print(f"{company_name.capitalize()}: Moat {moat}/10 - Missing: {', '.join(missing)}")
        
        print(f"\nQuerying missing scores...")
        print("=" * 60)
        
        for i, (company_name, moat_score, barriers_score, disruption_risk, switching_cost, brand_strength, competition_intensity, network_effect) in enumerate(companies_to_score, 1):
            print(f"\n[{i}/{len(companies_to_score)}] Processing {company_name.capitalize()}...")
            
            if not brand_strength:
                brand_prompt = f"""Rate the brand strength for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                brand_response, _ = grok.simple_query_with_tokens(brand_prompt, model="grok-4-fast")
                brand_strength = brand_response.strip()
                print(f"  Brand Strength Score: {brand_strength}/10")
            
            if not competition_intensity:
                competition_prompt = f"""Rate the intensity of competition for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                competition_response, _ = grok.simple_query_with_tokens(competition_prompt, model="grok-4-fast")
                competition_intensity = competition_response.strip()
                print(f"  Competition Intensity Score: {competition_intensity}/10")
            
            if not network_effect:
                network_prompt = f"""Rate the network effects for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                network_response, _ = grok.simple_query_with_tokens(network_prompt, model="grok-4-fast")
                network_effect = network_response.strip()
                print(f"  Network Effect Score: {network_effect}/10")
            
            if not barriers_score:
                barriers_prompt = f"""Rate the barriers to entry for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                barriers_response, _ = grok.simple_query_with_tokens(barriers_prompt, model="grok-4-fast")
                barriers_score = barriers_response.strip()
                print(f"  Barriers to Entry Score: {barriers_score}/10")
            
            if not disruption_risk:
                disruption_prompt = f"""Rate the disruption risk for {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                disruption_response, _ = grok.simple_query_with_tokens(disruption_prompt, model="grok-4-fast")
                disruption_risk = disruption_response.strip()
                print(f"  Disruption Risk Score: {disruption_risk}/10")
            
            if not switching_cost:
                switching_prompt = f"""Rate the switching costs for customers of {company_name} on a scale of 0-10, where:
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

Respond with ONLY the numerical score (0-10), no explanation needed."""

                switching_response, _ = grok.simple_query_with_tokens(switching_prompt, model="grok-4-fast")
                switching_cost = switching_response.strip()
                print(f"  Switching Cost Score: {switching_cost}/10")
            
            # Update the entry
            scores_data["companies"][company_name]["moat_score"] = moat_score
            if barriers_score:
                scores_data["companies"][company_name]["barriers_score"] = barriers_score
            if disruption_risk:
                scores_data["companies"][company_name]["disruption_risk"] = disruption_risk
            if switching_cost:
                scores_data["companies"][company_name]["switching_cost"] = switching_cost
            if brand_strength:
                scores_data["companies"][company_name]["brand_strength"] = brand_strength
            if competition_intensity:
                scores_data["companies"][company_name]["competition_intensity"] = competition_intensity
            if network_effect:
                scores_data["companies"][company_name]["network_effect"] = network_effect
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
    """Display all stored moat scores.
    
    Args:
        score_type: Optional score type to filter ('moat', 'barriers', 'disrupt', 'switching', 'brand', 'competition', etc.)
    """
    scores_data = load_scores()
    
    if not scores_data["companies"]:
        print("No scores stored yet.")
        return
    
    # Sort companies by total score in descending order
    def get_total_score(item):
        data = item[1]
        moat = data.get('moat_score', data.get('score', '0'))
        barriers = data.get('barriers_score', '0')
        disruption = data.get('disruption_risk', '10')
        switching = data.get('switching_cost', '0')
        brand = data.get('brand_strength', '0')
        competition = data.get('competition_intensity', '10')
        network = data.get('network_effect', '0')
        
        try:
            moat_val = float(moat)
            barriers_val = float(barriers) if barriers != 'N/A' else 0
            disruption_val = float(disruption) if disruption != 'N/A' else 10
            switching_val = float(switching) if switching != 'N/A' else 0
            brand_val = float(brand) if brand != 'N/A' else 0
            competition_val = float(competition) if competition != 'N/A' else 10
            network_val = float(network) if network != 'N/A' else 0
            # Total = moat + barriers + switching_cost + brand_strength + network_effect + (10 - disruption_risk) + (10 - competition_intensity)
            return moat_val + barriers_val + switching_val + brand_val + network_val + (10 - disruption_val) + (10 - competition_val)
        except (ValueError, TypeError):
            return 0
    
    sorted_companies = sorted(
        scores_data["companies"].items(),
        key=get_total_score,
        reverse=True
    )
    
    # If no specific score type requested, show only totals
    if not score_type:
        print("\nStored Company Scores (Total only):")
        print("=" * 80)
        
        # Find longest company name for alignment
        max_name_len = max([len(company.capitalize()) for company, data in sorted_companies]) if sorted_companies else 0
        
        for company, data in sorted_companies:
            moat = data.get('moat_score', data.get('score', 'N/A'))
            barriers = data.get('barriers_score', 'N/A')
            disruption = data.get('disruption_risk', 'N/A')
            switching = data.get('switching_cost', 'N/A')
            brand = data.get('brand_strength', 'N/A')
            competition = data.get('competition_intensity', 'N/A')
            network = data.get('network_effect', 'N/A')
            
            # Calculate total score
            total = 'N/A'
            if moat != 'N/A' and barriers != 'N/A' and disruption != 'N/A' and switching != 'N/A' and brand != 'N/A' and competition != 'N/A' and network != 'N/A':
                try:
                    moat_val = float(moat)
                    barriers_val = float(barriers)
                    disruption_val = float(disruption)
                    switching_val = float(switching)
                    brand_val = float(brand)
                    competition_val = float(competition)
                    network_val = float(network)
                    total_val = moat_val + barriers_val + switching_val + brand_val + network_val + (10 - disruption_val) + (10 - competition_val)
                    # Format as integer if whole number, otherwise 1 decimal place
                    total = f"{int(total_val)}" if total_val == int(total_val) else f"{total_val:.1f}"
                except (ValueError, TypeError):
                    pass
            
            print(f"{company.capitalize():<{max_name_len}} {total:>8}")
    else:
        # Show specific score type
        score_type_lower = score_type.lower()
        score_map = {
            'moat': ('moat_score', 'Moat'),
            'barriers': ('barriers_score', 'Barriers'),
            'disrupt': ('disruption_risk', 'Disruption Risk'),
            'disruption': ('disruption_risk', 'Disruption Risk'),
            'switching': ('switching_cost', 'Switching Cost'),
            'switch': ('switching_cost', 'Switching Cost'),
            'brand': ('brand_strength', 'Brand Strength'),
            'competition': ('competition_intensity', 'Competition Intensity'),
            'comp': ('competition_intensity', 'Competition Intensity'),
            'network': ('network_effect', 'Network Effect')
        }
        
        if score_type_lower not in score_map:
            print(f"Unknown score type: {score_type}")
            print(f"Available types: moat, barriers, disrupt, switching, brand, competition, network")
            return
        
        field_name, display_name = score_map[score_type_lower]
        print(f"\nStored Company Scores ({display_name}):")
        print("=" * 80)
        
        def get_field_score(item):
            data = item[1]
            score = data.get(field_name, 'N/A')
            try:
                return float(score) if score != 'N/A' else 0
            except (ValueError, TypeError):
                return 0
        
        sorted_by_field = sorted(
            scores_data["companies"].items(),
            key=get_field_score,
            reverse=True
        )
        
        # Find longest company name for alignment
        max_name_len = max([len(company.capitalize()) for company, data in sorted_by_field]) if sorted_by_field else 0
        
        for company, data in sorted_by_field:
            score = data.get(field_name, 'N/A')
            # Format score to remove .0
            if score != 'N/A':
                try:
                    score_float = float(score)
                    score_formatted = f"{int(score_float)}" if score_float == int(score_float) else f"{score_float:.1f}"
                    score = score_formatted
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
    print("  Type 'view <type>' to see specific scores (moat, barriers, disrupt, switching, brand, competition, network)")
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
                # Parse "view" or "view <score_type>"
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