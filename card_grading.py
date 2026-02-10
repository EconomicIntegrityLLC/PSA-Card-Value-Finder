"""
Free Card Grading Module using Ollama (Local, No API Costs)
Analyzes card images and assigns tiers based on condition and value potential
"""

import ollama
import base64
from PIL import Image
import io
from typing import Dict, List, Optional
import json

# Tier system from ChatGPT conversation
TIER_1_THRESHOLD = 1000  # $1000+ graded potential
TIER_2_RAW_THRESHOLD = 10  # $10+ raw
TIER_2_GRADED_THRESHOLD = 100  # $100-999 graded potential
GRADING_COST = 30
GRADING_TIMEFRAME = "6 months"

def check_ollama_available() -> bool:
    """Check if Ollama is installed and running"""
    try:
        ollama.list()
        return True
    except:
        return False

def ensure_vision_model():
    """Ensure a vision model is available, pull if needed"""
    try:
        models = ollama.list()
        model_names = [m.model for m in models.models] if models.models else []
        
        # Check for common vision models
        vision_models = ['llava', 'llama3.2-vision', 'bakllava']
        for vm in vision_models:
            if any(vm in name for name in model_names):
                return vm
        
        # If no vision model found, pull llava (smallest, fastest)
        print("No vision model found. Pulling llava (this may take a few minutes)...")
        ollama.pull('llava')
        return 'llava'
    except Exception as e:
        print(f"Error checking/pulling model: {e}")
        return None

def analyze_card_image(image_path: str, model_name: str = 'llava') -> Dict:
    """
    Analyze a card image using Ollama vision model
    
    Returns analysis including:
    - Card identification (player, year, set, rookie status)
    - Condition assessment (centering, corners, edges, surface)
    - Front grade ceiling
    - Tier assignment
    - Whether back is needed
    """
    
    # Load and encode image
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
    except Exception as e:
        return {"error": f"Could not load image: {e}"}
    
    # Create grading prompt based on ChatGPT conversation workflow
    prompt = """You are a professional trading card grader. Analyze this card image and provide a detailed assessment.

Focus on:
1. CARD IDENTIFICATION:
   - Player name
   - Year
   - Set/brand (Topps, Upper Deck, Donruss, etc.)
   - Is this a rookie card? (YES/NO)
   - Is this an insert or special set? (YES/NO - look for "Elite", "Stadium Club", "Tiffany", "Chrome", foil, serial numbers, etc.)

2. FRONT CONDITION ASSESSMENT:
   - Centering: Rate left-right and top-bottom balance (describe as "excellent", "good", "off", "very off")
   - Corners: Check all 4 corners for sharpness, rounding, whitening (describe each)
   - Edges: Look for chipping, roughness, wear
   - Surface: Check for scratches, print defects, gloss issues, orange-peel texture, fish-eyes

3. FRONT GRADE CEILING:
   Based on what you can see, what is the MAXIMUM realistic PSA grade this card could achieve?
   Consider: PSA 10 = perfect, PSA 9 = near-perfect, PSA 8 = excellent, PSA 7 = very good, PSA 6 = good
   Be realistic - most cards cannot achieve PSA 10, especially from junk wax era.

4. MARKET ASSESSMENT:
   - Is this a known valuable card? (iconic rookie, rare insert, etc.)
   - Based on player, year, set, and condition - estimate:
     * Raw value range ($X-$Y)
     * PSA 9 value range (if applicable)
     * PSA 10 value range (if applicable)

5. TIER ASSIGNMENT:
   Assign ONE of these tiers:
   - TIER_1: If ANY grade (even PSA 5-7) could reasonably sell for $1000+
   - TIER_2: If raw value is $10+ OR graded value (PSA 7-8+) is $100-999
   - TIER_3: Everything else (bulk buyer material)

6. BACK CHECK NEEDED:
   - YES: If Tier 1 or Tier 2 AND front looks grade-worthy
   - NO: If Tier 3 or front has obvious disqualifying flaws

Return your analysis in this JSON format:
{
  "card_id": {
    "player": "Player Name",
    "year": "YYYY",
    "set": "Set Name",
    "is_rookie": true/false,
    "is_insert": true/false
  },
  "condition": {
    "centering": "description",
    "corners": "description",
    "edges": "description",
    "surface": "description"
  },
  "grade_ceiling": "PSA X",
  "market": {
    "raw_value": "$X-$Y",
    "psa9_value": "$X-$Y or N/A",
    "psa10_value": "$X-$Y or N/A"
  },
  "tier": "TIER_1/TIER_2/TIER_3",
  "back_check_needed": true/false,
  "notes": "Any additional observations"
}
"""
    
    try:
        response = ollama.chat(
            model=model_name,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )
        
        # Extract response text
        analysis_text = response['message']['content']
        
        # Try to parse JSON if present
        try:
            # Look for JSON in the response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                analysis_json = json.loads(analysis_text[json_start:json_end])
                return {
                    "success": True,
                    "analysis": analysis_json,
                    "full_response": analysis_text
                }
        except:
            pass
        
        # If JSON parsing failed, return raw response
        return {
            "success": True,
            "analysis": {"raw_response": analysis_text},
            "full_response": analysis_text
        }
        
    except Exception as e:
        return {"error": f"Analysis failed: {e}"}

def batch_analyze_cards(image_paths: List[str], model_name: str = 'llava') -> List[Dict]:
    """Analyze multiple card images (up to 10 as per workflow)"""
    results = []
    for img_path in image_paths[:10]:  # Limit to 10 cards per batch
        result = analyze_card_image(img_path, model_name)
        result['image_path'] = img_path
        results.append(result)
    return results

def format_tier_result(result: Dict) -> str:
    """Format analysis result for display"""
    if "error" in result:
        return f"❌ Error: {result['error']}"
    
    if not result.get("success"):
        return "❌ Analysis failed"
    
    analysis = result.get("analysis", {})
    
    # Extract card info
    card_id = analysis.get("card_id", {})
    player = card_id.get("player", "Unknown")
    year = card_id.get("year", "?")
    set_name = card_id.get("set", "Unknown")
    is_rookie = "✅ ROOKIE" if card_id.get("is_rookie") else "❌ Not Rookie"
    is_insert = "✅ INSERT" if card_id.get("is_insert") else ""
    
    # Extract tier
    tier = analysis.get("tier", "TIER_3")
    tier_emoji = {
        "TIER_1": "🚨",
        "TIER_2": "🟨",
        "TIER_3": "🟩"
    }.get(tier, "❓")
    
    # Extract grade ceiling
    grade_ceiling = analysis.get("grade_ceiling", "Unknown")
    
    # Extract market values
    market = analysis.get("market", {})
    raw_value = market.get("raw_value", "N/A")
    
    # Back check needed
    back_check = "🔍 BACK CHECK NEEDED" if analysis.get("back_check_needed") else ""
    
    return f"""
{tier_emoji} **{tier}** {back_check}

**Card:** {player} - {year} {set_name}
{is_rookie} {is_insert}

**Front Grade Ceiling:** {grade_ceiling}
**Raw Value:** {raw_value}

**Condition:**
- Centering: {analysis.get('condition', {}).get('centering', 'N/A')}
- Corners: {analysis.get('condition', {}).get('corners', 'N/A')}
- Edges: {analysis.get('condition', {}).get('edges', 'N/A')}
- Surface: {analysis.get('condition', {}).get('surface', 'N/A')}

**Notes:** {analysis.get('notes', 'None')}
"""

if __name__ == "__main__":
    import sys
    # Fix Windows encoding for emojis
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    # Test if Ollama is available
    if not check_ollama_available():
        print("Ollama is not running. Please install and start Ollama first.")
        print("Download from: https://ollama.com")
    else:
        print("Ollama is available")
        model = ensure_vision_model()
        if model:
            print(f"Vision model ready: {model}")
        else:
            print("Could not set up vision model")
