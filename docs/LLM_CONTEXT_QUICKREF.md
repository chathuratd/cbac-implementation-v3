# LLM Context Injection - Quick Reference

## Endpoint
```
GET /api/v1/profile/{user_id}/llm-context
```

## Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_strength` | float | 30.0 | Minimum cluster strength % (0-100) |
| `min_confidence` | float | 0.40 | Minimum confidence score (0-1) |
| `max_behaviors` | int | 5 | Maximum behaviors to include |
| `include_archetype` | bool | true | Include user archetype |

## Quick Examples

### Default Request
```bash
curl http://localhost:8000/api/v1/profile/user_665390/llm-context
```

### Custom Thresholds
```bash
curl "http://localhost:8000/api/v1/profile/user_665390/llm-context?min_strength=50&min_confidence=0.6&max_behaviors=3"
```

### Without Archetype
```bash
curl "http://localhost:8000/api/v1/profile/user_665390/llm-context?include_archetype=false"
```

### Python
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/profile/user_665390/llm-context",
    params={"min_strength": 30, "max_behaviors": 5}
)
context = response.json()['context']
```

### PowerShell
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/profile/user_665390/llm-context"
Write-Host $response.context
```

## Response Structure
```json
{
  "user_id": "string",
  "context": "markdown formatted string",
  "metadata": {
    "total_clusters": int,
    "included_behaviors": int,
    "archetype": "string" | null,
    "filters": {...},
    "summary": {...}
  }
}
```

## Context Format
```markdown
# User Behavioral Profile
Archetype: {archetype_name}

## Communication Preferences:

1. {Behavior Name} (strength: X%, confidence: Y%)
   Examples: "variation1, variation2, ..."

2. ...
```

## Common Use Cases

### System Prompt Injection
```python
system_prompt = f"""
You are a helpful AI assistant.

{llm_context['context']}

Adapt your responses to match these preferences.
"""
```

### Per-Request Injection
```python
enhanced_prompt = f"""
Context: {llm_context['context']}

Question: {user_question}
"""
```

### Conditional Injection
```python
if llm_context['metadata']['included_behaviors'] >= 3:
    # Use full context
    prompt_with_context = f"{context}\n\n{user_prompt}"
else:
    # Use without context
    prompt_with_context = user_prompt
```

## Testing
```bash
# Test script
python test_llm_context.py

# API tests
python test_api_llm_context.py

# Check users
python check_users.py
```

## Error Handling
```python
try:
    response = requests.get(f"{BASE_URL}/profile/{user_id}/llm-context")
    response.raise_for_status()
    context = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        # User profile not found
        context = None
    else:
        # Other error
        raise
```

## Status Codes
- `200` - Success
- `404` - User profile not found
- `500` - Server error

## Files
- Service: `src/services/llm_context_service.py`
- Route: `src/api/routes.py` (line ~443)
- Tests: `test_llm_context.py`, `test_api_llm_context.py`
- Docs: `docs/LLM_CONTEXT_INJECTION.md`

## Tips
1. Lower thresholds = more behaviors included
2. Higher thresholds = only strongest behaviors
3. Adjust `max_behaviors` based on LLM context window
4. Use archetype for quick personality summary
5. Check `included_behaviors` count before injecting

---
**Quick Start**: `curl http://localhost:8000/api/v1/profile/user_665390/llm-context`
