# Fixed Syntax Errors - RAG System

## Issues Fixed

### Problem
Multiple `SyntaxError: unterminated string literal` errors in `backend/app/chatbot/chatbot.py`

### Root Cause
Unescaped quotes inside triple-quoted f-strings were causing Python parser errors:
- `"I don't have..."` inside `"""..."""` strings
- `"I'm a transit..."` inside `"""..."""` strings
- Similar issues in multiple locations

### Solution Applied
Replaced all problematic quotes with non-quoted versions:

1. **Line 95-118** - `system_prompt`:
   - Changed `"you" and "your"` → `you and your`
   - Changed `(but don't overdo it)` → `but do not overdo it`
   - Changed `"I don't have..."` → `I do not have...`
   - Changed `"I'm specialized..."` → `I am specialized...`
   - Changed `"you" and "your"` → `you and your`
   - Changed `You're a TRANSIT EXPERT` → `You are a TRANSIT EXPERT`

2. **Line 129-144** - First `friendly_template`:
   - Removed all internal quotes
   - Changed `User's Question:` → `User Question:`

3. **Line 346-361** - Second `friendly_template` (custom temperature):
   - Same fixes as above
   - Ensures consistency across both templates

4. **Line 564-590** - `intent_prompt`:
   - Removed all quotes from intent names and examples
   - Changed `"route_planning"` → `route_planning`
   - Changed `"How do I get..."` → `How do I get...`
   - Simplified all example text

## Files Modified
- `backend/app/chatbot/chatbot.py`

## Testing
Run the backend:
```bash
cd backend
python run.py
```

Should now start without syntax errors.

## Next Steps
1. Backend should start successfully
2. RAG system will enforce transit-only responses
3. Test with questions:
   - "What is react?" → Should refuse to answer
   - "What are the types of agents?" → Should retrieve from knowledge base
   - "How do I use the app?" → Should work normally
