# CBIE Dataset Generator v2.0

## Overview

Improved behavior dataset generator that creates realistic test data for various CBIE analysis scenarios. The generator now produces behaviors that correctly map to PRIMARY, SECONDARY, and NOISE tiers based on the CBIE calculation formulas.

## Key Improvements

### ✅ Realistic Tier Distribution
- **PRIMARY behaviors**: High credibility (0.88-0.95), high reinforcement (15-30% of prompts), low decay
- **SECONDARY behaviors**: Medium credibility (0.70-0.88), moderate reinforcement (8-15% of prompts), medium decay
- **NOISE behaviors**: Low credibility (0.45-0.70), low reinforcement (2-7% of prompts), high decay

### ✅ Profile Types

**1. Balanced** (default)
- PRIMARY: 2-3 behaviors
- SECONDARY: 3-5 behaviors
- NOISE: Remaining behaviors
- Use case: General testing, realistic user profiles

**2. Focused**
- PRIMARY: 1-2 behaviors (heavily weighted)
- SECONDARY: 2-3 behaviors
- NOISE: Remaining behaviors
- Use case: Expert users with clear preferences

**3. Exploratory**
- PRIMARY: 1 behavior
- SECONDARY: 4-5 behaviors
- NOISE: 3-4 behaviors
- Use case: Learning users exploring different approaches

**4. Noisy**
- PRIMARY: 0 behaviors
- SECONDARY: 1-2 behaviors
- NOISE: Most behaviors
- Use case: Edge cases, inconsistent users

### ✅ Score Calculation Preview

The generator now calculates and displays expected BW (Behavior Weight) and ABW (Adjusted Behavior Weight) scores, showing which tier each behavior should fall into before you even run the analysis pipeline.

**Formulas Used:**
- BW = credibility^0.35 × clarity^0.40 × confidence^0.25
- ABW = BW × (1 + count × 0.01) × e^(-decay × days)

**Tier Thresholds:**
- PRIMARY: ABW ≥ 1.0
- SECONDARY: 0.7 ≤ ABW < 1.0
- NOISE: ABW < 0.7

## Usage

```bash
cd test-data
python behavior_gen_v2.py
```

### Interactive Prompts

1. **Number of prompts**: Total prompts to generate (e.g., 150-300)
2. **Profile type**: Select 1-4 for different behavior distributions
3. **Number of behaviors**: How many distinct behaviors (5-12 recommended)

### Example Session

```
Enter number of prompts to generate: 150
Select profile type (1-4) [default: 1]: 2
Number of behaviors to use (5-12) [default: 12]: 10

📊 Target Profile: FOCUSED
  PRIMARY: 2 behaviors
  SECONDARY: 3 behaviors
  NOISE: 5 behaviors

✓ Target/Actual Match: 10/10 (100%)

📋 Behavior Details (sorted by ABW):
  🟢→🟢 prefers comparative analysis    | Count: 43 | ABW: 1.2838
  🟢→🟢 prefers detailed documentation   | Count: 37 | ABW: 1.2070
  🟡→🟡 theory and concept focused       | Count: 14 | ABW: 0.8596
  ...
```

## Output Files

Generated in `./behavior_dataset/`:
- `prompts_user_XXX_timestamp.json` - All prompts with timestamps
- `behaviors_user_XXX_timestamp.json` - All behaviors with metadata

## Statistics Display

### Target vs Actual
- **Target**: Designed tier assignment
- **Actual**: Calculated tier based on ABW formula
- **Match %**: How well the generated data matches intended distribution

### Behavior Details
- 🟢 = PRIMARY (ABW ≥ 1.0)
- 🟡 = SECONDARY (0.7 ≤ ABW < 1.0)
- 🔴 = NOISE (ABW < 0.7)

Format: `🟢→🟢` = Target→Actual (green = match, different color = mismatch)

## Testing Scenarios

### Test Primary Behavior Detection
```bash
# Generate focused profile with strong primary behaviors
Profile type: 2 (focused)
Number of behaviors: 8
```

### Test Secondary Behavior Detection
```bash
# Generate exploratory profile with many secondaries
Profile type: 3 (exploratory)
Number of behaviors: 10
```

### Test Noise Filtering
```bash
# Generate noisy profile
Profile type: 4 (noisy)
Number of behaviors: 12
```

### Test Balanced Analysis
```bash
# Generate balanced profile
Profile type: 1 (balanced)
Number of behaviors: 12
```

## Integration

After generating data:

```bash
# Load into databases
python load_data_to_databases.py

# Verify in Qdrant
python verify_qdrant_data.py

# Run analysis via API
curl -X POST "http://localhost:8000/api/v1/analyze-behaviors-from-storage?user_id=user_XXX"
```

## Key Metrics

- **Reinforcement Count**: Higher for PRIMARY (15-50), moderate for SECONDARY (8-20), low for NOISE (2-8)
- **Credibility**: Higher for PRIMARY (0.88-0.95), moderate for SECONDARY (0.70-0.88), lower for NOISE (0.45-0.70)
- **Decay Rate**: Lower for PRIMARY (0.01-0.015), moderate for SECONDARY (0.015-0.022), higher for NOISE (0.020-0.030)
- **Time Span**: ~60 days with temporal clustering

## Validation

The generator performs self-validation:
1. Calculates expected BW/ABW for each behavior
2. Determines actual tier based on thresholds
3. Compares with target tier assignment
4. Reports match percentage (aim for 90-100%)

## Tips

1. **Start with focused profile** to ensure PRIMARY detection works
2. **Use 10-12 behaviors** for comprehensive testing
3. **Generate 150-300 prompts** for realistic data volume
4. **Check match percentage** - should be 90%+ for good data
5. **Compare ABW values** with thresholds to verify tier assignment

## Troubleshooting

**Low match percentage (<80%)**
- Try adjusting number of prompts (more prompts = better reinforcement)
- Check if behaviors have enough variation in target distribution

**No PRIMARY behaviors detected**
- Increase number of prompts to boost reinforcement counts
- Use focused or balanced profile types

**Too many NOISE behaviors**
- Use focused or balanced profile
- Increase number of prompts to improve ABW scores

---

**Version**: 2.0  
**Last Updated**: 2025-12-19  
**Compatibility**: CBIE MVP v1.0
