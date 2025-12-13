#!/usr/bin/env python3
"""
Company Keywords Generator
Uses Grok 4.1 Fast via OpenRouter to generate 100 keywords/phrases about what a company does.

Example: If you input "Google", it will return keywords like:
- Search
- Cloud
- AI
- Information Technology
- Software
- etc.
"""

import os
import sys
import json
from typing import List, Optional

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.clients.openrouter_client import OpenRouterClient
    from config import OPENROUTER_KEY
    OPENROUTER_AVAILABLE = True
except ImportError:
    OPENROUTER_AVAILABLE = False
    print("Error: Could not import OpenRouterClient. Make sure dependencies are installed.")
    sys.exit(1)

# Import ticker lookup functionality
try:
    from src.scoring.scorer import load_ticker_lookup, resolve_to_company_name
except ImportError:
    print("Error: Could not import scorer module.")
    sys.exit(1)


def generate_company_keywords(company_name: str, ticker: Optional[str] = None) -> tuple[List[str], dict]:
    """
    Generate 100 keywords/phrases about what a company does using Grok 4.1 Fast.
    
    Args:
        company_name: Name of the company
        ticker: Optional ticker symbol (for context)
        
    Returns:
        Tuple of (keywords_list, token_usage_dict)
    """
    if not OPENROUTER_AVAILABLE:
        raise Exception("OpenRouterClient not available.")
    
    if not OPENROUTER_KEY:
        raise Exception("OPENROUTER_KEY not configured. Please set it in config.py or as an environment variable.")
    
    # Initialize OpenRouter client
    client = OpenRouterClient(api_key=OPENROUTER_KEY)
    
    # Create prompt
    ticker_context = f" (stock ticker: {ticker})" if ticker else ""
    prompt = f"""Generate exactly 100 general keywords and phrases that describe what {company_name}{ticker_context} does.

IMPORTANT: These must be GENERAL business keywords/phrases, NOT company-specific product names or brand names.
- Use generic terms like "Email Services" NOT "Gmail"
- Use "Navigation Services" or "Maps" NOT "Google Maps"
- Use "Mobile Operating System" NOT "Android Operating System"
- Use "Video Platform" or "Video Streaming" NOT "YouTube Platform"
- Use "Productivity Suite" NOT "Google Workspace"
- Use "Cloud Platform" NOT "Google Cloud Platform"
- Use "Cloud Storage" NOT "Google Drive"

These should be general keywords/phrases about the company's business, products, services, industry, and operations.
Include:
- Industry sectors (e.g., "Information Technology", "Software", "Cloud Computing")
- Product categories (e.g., "Search Engine", "Web Browser", "Operating System")
- Services offered (e.g., "Cloud Services", "Advertising", "E-commerce")
- Technologies used (e.g., "Artificial Intelligence", "Machine Learning", "Data Analytics")
- Business models (e.g., "SaaS", "B2B", "Consumer Products")
- Market segments (e.g., "Enterprise Software", "Consumer Electronics")
- And any other relevant keywords that describe the company's activities

DO NOT include:
- Company-specific product names (e.g., "Gmail", "Google Maps", "Android")
- Brand names or proprietary terms
- Company-specific service names

Return ONLY a comma-separated list of exactly 100 general keywords/phrases. Do not include numbers, bullets, or any other formatting.
Just the keywords separated by commas.

Example format:
Search, Cloud Computing, Artificial Intelligence, Information Technology, Software, Web Services, Advertising, Data Analytics, Machine Learning, Mobile Apps, Operating Systems, Enterprise Software, Consumer Products, E-commerce, Digital Services, Internet Services, Cloud Storage, Email Services, Maps, Video Streaming, Productivity Software, Developer Tools, Cloud Infrastructure, AI Research, Search Engine, Web Browser, Mobile Operating System, Cloud Platform, Digital Advertising, Analytics, Software Development, Cloud Services, Data Centers, Network Infrastructure, Information Retrieval, Natural Language Processing, Computer Vision, Autonomous Vehicles, Smart Home, IoT, Wearables, Health Technology, Financial Services, Payment Processing, Cloud Security, Enterprise Solutions, Collaboration Tools, Communication Platforms, Content Delivery, Media Services, Entertainment, Gaming, Social Media, Messaging, Video Conferencing, Project Management, Customer Relationship Management, Supply Chain Management, Human Resources, Accounting Software, Business Intelligence, Data Warehousing, Database Management, Server Infrastructure, Virtualization, Containerization, DevOps Tools, API Management, Integration Platforms, Workflow Automation, Document Management, File Sharing, Backup Solutions, Disaster Recovery, Network Security, Identity Management, Access Control, Compliance, Regulatory Technology, Risk Management, Fraud Detection, Cybersecurity, Threat Intelligence, Incident Response, Security Operations, Vulnerability Assessment, Penetration Testing, Security Consulting, Managed Security Services, Cloud Migration, Digital Transformation, IT Consulting, System Integration, Application Development, Custom Software, Software Maintenance, Technical Support, Training Services, Professional Services, Outsourcing, Managed Services, Infrastructure as a Service, Platform as a Service, Software as a Service"""

    print(f"Querying Grok 4.1 Fast to generate keywords for {company_name}...")
    
    # Call Grok 4.1 Fast
    response_text, token_usage = client.chat_completion_with_tokens(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates comprehensive keyword lists about companies. Always use GENERAL business terms, NOT company-specific product names or brand names. For example, use 'Email Services' not 'Gmail', 'Navigation Services' not 'Google Maps', 'Mobile Operating System' not 'Android'. Always return exactly the requested number of keywords in a clean, comma-separated format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="grok-4-1-fast-reasoning",
        temperature=0.7,
        max_tokens=2000  # Enough for 100 keywords
    )
    
    # Parse the response - extract keywords from comma-separated list
    keywords = []
    response_clean = response_text.strip()
    
    # Remove any leading/trailing text that might not be keywords
    # Look for the actual list (might have some intro text)
    lines = response_clean.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove common prefixes like "Keywords:", "Here are:", etc.
        for prefix in ["Keywords:", "Here are", "The keywords", "Keywords for", "1.", "-"]:
            if line.lower().startswith(prefix.lower()):
                line = line[len(prefix):].strip()
                # Remove leading colon if present
                if line.startswith(':'):
                    line = line[1:].strip()
                break
        
        # Split by comma and clean each keyword
        for keyword in line.split(','):
            keyword = keyword.strip()
            # Remove quotes if present
            if keyword.startswith('"') and keyword.endswith('"'):
                keyword = keyword[1:-1]
            if keyword.startswith("'") and keyword.endswith("'"):
                keyword = keyword[1:-1]
            # Remove trailing periods, colons, etc.
            keyword = keyword.rstrip('.;:')
            if keyword:
                keywords.append(keyword)
    
    # If we got fewer than 100, try to split more aggressively
    if len(keywords) < 50:
        # Maybe the response is all on one line with commas
        all_text = response_clean.replace('\n', ' ')
        keywords = [k.strip().rstrip('.;:') for k in all_text.split(',') if k.strip()]
    
    # Limit to 100 if we got more
    keywords = keywords[:100]
    
    return keywords, token_usage


def format_keywords_output(keywords: List[str], format_type: str = "list") -> str:
    """
    Format keywords for output.
    
    Args:
        keywords: List of keywords
        format_type: "list" (one per line), "comma" (comma-separated), or "json" (JSON array)
        
    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(keywords, indent=2)
    elif format_type == "comma":
        return ", ".join(keywords)
    else:  # list
        return "\n".join(keywords)


def main():
    """Main function to generate company keywords."""
    print("=" * 80)
    print("Company Keywords Generator")
    print("Uses Grok 4.1 Fast via OpenRouter")
    print("=" * 80)
    print()
    
    if not OPENROUTER_AVAILABLE:
        print("Error: OpenRouterClient not available.")
        sys.exit(1)
    
    if not OPENROUTER_KEY:
        print("Error: OPENROUTER_KEY not configured.")
        print("Please set it in config.py or as an environment variable.")
        sys.exit(1)
    
    # Get input from command line or prompt
    if len(sys.argv) > 1:
        input_str = " ".join(sys.argv[1:])
    else:
        input_str = input("Enter company name or ticker: ").strip()
    
    if not input_str:
        print("Error: No input provided.")
        sys.exit(1)
    
    # Try to resolve to company name and ticker
    input_upper = input_str.strip().upper()
    ticker_lookup = load_ticker_lookup()
    
    ticker = None
    company_name = input_str
    
    # Check if it's a ticker
    if input_upper in ticker_lookup:
        ticker = input_upper
        company_name = ticker_lookup[ticker]
        print(f"Found ticker: {ticker} = {company_name}")
    else:
        # Try to resolve it
        resolved_name, resolved_ticker = resolve_to_company_name(input_str)
        if resolved_ticker:
            ticker = resolved_ticker
            company_name = resolved_name
            print(f"Resolved: {ticker} = {company_name}")
        else:
            company_name = resolved_name
            print(f"Using company name: {company_name}")
    
    print()
    
    try:
        # Generate keywords
        keywords, token_usage = generate_company_keywords(company_name, ticker)
        
        print(f"\nGenerated {len(keywords)} keywords for {company_name}")
        print("=" * 80)
        print()
        
        # Display keywords
        print("Keywords:")
        print("-" * 80)
        for i, keyword in enumerate(keywords, 1):
            print(f"{i:3d}. {keyword}")
        
        print()
        print("=" * 80)
        print("Token Usage:")
        print(f"  Input tokens:  {token_usage.get('prompt_tokens', 0):,}")
        print(f"  Output tokens: {token_usage.get('completion_tokens', 0):,}")
        print(f"  Total tokens:  {token_usage.get('total_tokens', 0):,}")
        if 'cached_tokens' in token_usage:
            print(f"  Cached tokens: {token_usage['cached_tokens']:,}")
        
        # Option to save to file
        save_option = input("\nSave to file? (y/n): ").strip().lower()
        if save_option == 'y':
            output_format = input("Format (json/comma/list) [list]: ").strip().lower() or "list"
            filename = input(f"Filename [keywords_{company_name.replace(' ', '_')}.txt]: ").strip()
            if not filename:
                filename = f"keywords_{company_name.replace(' ', '_').replace('/', '_')}.txt"
            
            output = format_keywords_output(keywords, output_format)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output)
            
            print(f"\nSaved {len(keywords)} keywords to {filename}")
        
        # Also print comma-separated version for easy copying
        print("\n" + "=" * 80)
        print("Comma-separated (for easy copying):")
        print("-" * 80)
        print(", ".join(keywords))
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
