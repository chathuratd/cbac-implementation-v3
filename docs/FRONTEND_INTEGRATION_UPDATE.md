# Frontend Integration Update Summary

## Overview
Updated the ProfileInsights and Dashboard components to integrate with the actual CBIE (Core Behavior Identification Engine) system, replacing mock data with real API calls while maintaining the existing design theme.

## Changes Made

### 1. ProfileInsights Component (`frontend/src/components/ProfileInsights.jsx`)

**Major Changes:**
- **Real API Integration**: Now fetches actual user behavior profile data from `/api/v1/get-user-profile/{userId}`
- **Cluster-Centric Display**: Displays behavior clusters (PRIMARY, SECONDARY, NOISE) as the core data structure
- **Dynamic Loading States**: Added loading, error, and empty states for better UX
- **Expandable Cluster Cards**: Users can click clusters to view wording variations
- **Real-Time Statistics**: Displays actual metrics from the analysis

**New Features:**
- `ClusterCard` component for displaying individual behavior clusters
- Cluster strength and confidence visualizations
- Temporal tracking (first seen, last seen, days active)
- Wording variations viewer (expandable)
- Tier-based color coding (PRIMARY = indigo, SECONDARY = blue, NOISE = gray)
- Refresh button to reload profile data

**Data Structure:**
```javascript
{
  user_id: "user_348",
  archetype: "Behavioral Profile Name",
  behavior_clusters: [
    {
      cluster_id: "cluster_0",
      canonical_label: "prefers visual learning",
      tier: "PRIMARY",
      cluster_strength: 0.87,
      confidence: 0.85,
      cluster_size: 3,
      wording_variations: [...],
      first_seen: 1765741962,
      last_seen: 1766000000,
      days_active: 2.99
    }
  ],
  statistics: {
    total_behaviors_analyzed: 150,
    clusters_formed: 8,
    total_prompts_analyzed: 300,
    analysis_time_span_days: 45
  }
}
```

### 2. Dashboard Component (`frontend/src/components/Dashboard.jsx`)

**Major Changes:**
- **API Integration**: Fetches profile data on component mount
- **Dynamic Statistics**: Real-time display of behavior counts and analysis metrics
- **Loading States**: Shows loading spinners while fetching data
- **Profile Summary**: Dynamic archetype display in hero section
- **Cluster Breakdown**: Shows PRIMARY/SECONDARY behavior counts with visual cards

**Updated Sections:**
- Hero profile card now displays real archetype and statistics
- Stats cards show actual observation and cluster counts
- Side statistics panel with PRIMARY, SECONDARY, and time span metrics
- Removed hardcoded "Academic Research & Deep technical" profile name

### 3. API Configuration (`frontend/src/config/api.js`)

**New File:**
- Centralized API endpoint configuration
- Environment variable support via Vite
- Endpoint helper functions for consistent API calls

```javascript
export const API_ENDPOINTS = {
  getUserProfile: (userId) => `${API_BASE_URL}${API_VERSION}/get-user-profile/${userId}`,
  listCoreBehaviors: (userId) => `${API_BASE_URL}${API_VERSION}/list-core-behaviors/${userId}`,
  analyzeFromStorage: (userId) => `${API_BASE_URL}${API_VERSION}/analyze-behaviors-from-storage?user_id=${userId}`,
  health: `${API_BASE_URL}${API_VERSION}/health`,
};
```

### 4. Environment Configuration (`frontend/.env`)

**New File:**
```env
VITE_API_URL=http://localhost:8000
```

## Design Choices

### Visual Hierarchy
- **PRIMARY behaviors**: Indigo color scheme, highest visual weight
- **SECONDARY behaviors**: Blue color scheme, medium visual weight
- **NOISE clusters**: Gray color scheme, collapsible section

### Interaction Design
- Click clusters to expand/collapse wording variations
- Hover effects on cluster cards
- Loading states with spinners
- Error states with retry buttons
- Empty states with helpful messages

### Metrics Display
- **Cluster Strength**: 0-100 scale (normalized percentage)
- **Confidence**: Progress bar with percentage
- **Temporal Info**: Human-readable dates and time ago format
- **Observation Count**: Number of behaviors in each cluster

## API Endpoints Used

1. **GET `/api/v1/get-user-profile/{userId}`**
   - Fetches complete user behavior profile
   - Returns clusters, statistics, and archetype
   - Used by both Dashboard and ProfileInsights

2. **GET `/api/v1/list-core-behaviors/{userId}`** (prepared, not yet used)
   - Returns simplified list of canonical behaviors
   - Can be used for quick summaries

3. **POST `/api/v1/analyze-behaviors-from-storage`** (prepared, not yet used)
   - Triggers re-analysis from existing data
   - Can be used for manual refresh

## User Experience Improvements

1. **Immediate Feedback**: Loading spinners during data fetch
2. **Error Handling**: Clear error messages with retry options
3. **Empty States**: Helpful guidance when no data exists
4. **Data Refresh**: Manual refresh button on ProfileInsights
5. **Interactive Exploration**: Expandable cluster cards
6. **Visual Consistency**: Maintained original design theme

## Technical Implementation

### State Management
```javascript
const [profile, setProfile] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
const [expandedClusters, setExpandedClusters] = useState(new Set());
```

### API Call Pattern
```javascript
const fetchProfile = async () => {
  try {
    setLoading(true);
    setError(null);
    const response = await fetch(API_ENDPOINTS.getUserProfile(userId));
    if (!response.ok) throw new Error('Failed to fetch profile');
    const data = await response.json();
    setProfile(data);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

## Data Flow

```
User Opens Dashboard
    ↓
Component Mounts
    ↓
fetchDashboardData() called
    ↓
API Request: GET /api/v1/get-user-profile/user_348
    ↓
Response: Profile Data (clusters, statistics, archetype)
    ↓
State Updated: setProfileData(data)
    ↓
UI Re-renders with Real Data
```

## Future Enhancements (Not Implemented Yet)

1. **User Authentication**: Replace hardcoded `user_348` with auth context
2. **Behavior Deletion**: Add delete/hide functionality for clusters
3. **Export Data**: Export profile as JSON/CSV
4. **Real-time Updates**: WebSocket for live behavior tracking
5. **Comparison View**: Compare behavior changes over time
6. **Filtering**: Filter clusters by tier, confidence, or date range
7. **Search**: Search within behaviors and clusters

## Testing Instructions

1. **Start Backend**:
   ```bash
   cd d:/Academics/implemantation-v3
   python main.py
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm install  # if not already done
   npm run dev
   ```

3. **Verify API Connection**:
   - Open browser to `http://localhost:5173`
   - Navigate to Dashboard
   - Check browser console for API requests
   - Verify data loads in ProfileInsights tab

4. **Test Data**:
   - Ensure user `user_348` has data in MongoDB
   - Run test data loader if needed: `python tests/load_data_to_databases.py`

## Breaking Changes

None. The components maintain backward compatibility with the existing UI structure. If API is unavailable, appropriate error messages are shown.

## Dependencies

No new dependencies added. Uses existing:
- React hooks (useState, useEffect, useCallback)
- lucide-react icons
- Fetch API for HTTP requests

## Browser Compatibility

- Modern browsers with ES6+ support
- Fetch API support required
- CSS Grid and Flexbox support required

## Performance Considerations

- Single API call on component mount
- Data cached in component state
- Manual refresh when needed
- Embeddings excluded from API response for performance
- Lazy expansion of wording variations

## Styling

Maintained all existing Tailwind CSS classes and design tokens:
- Color palette: indigo, blue, slate, emerald
- Border radius: rounded-2xl, rounded-3xl
- Shadows: shadow-sm, shadow-md, shadow-xl
- Typography: font-bold, font-black, tracking-tight
- Spacing: consistent padding and gaps

## Accessibility

- Semantic HTML elements
- Proper heading hierarchy
- Keyboard navigation support
- Loading states announced
- Error messages visible
- Color contrast maintained

## Known Limitations

1. **Hardcoded User ID**: Currently uses `user_348` - needs auth integration
2. **No Offline Support**: Requires active backend connection
3. **No Data Caching**: Fetches fresh data on each load
4. **No Pagination**: Loads all clusters at once (may be slow for large profiles)
5. **No Optimistic Updates**: All changes require server round-trip

## Conclusion

The frontend now fully integrates with the CBIE backend system, displaying real behavior cluster data while maintaining the existing design aesthetic. The implementation follows React best practices, handles edge cases gracefully, and provides a solid foundation for future enhancements.

---

## ✅ NEW: LLM Context API Integration (Dec 27, 2025)

### Features Added

#### 1. LLM Context Button & Modal
- **Location**: ProfileInsights component header
- **Visual**: Purple gradient button with MessageSquare icon
- **Functionality**: Opens modal dialog to view and copy LLM context

#### 2. Modal Components
- **Context Display**: Pre-formatted markdown in monospace font
- **Copy Button**: One-click clipboard copy with visual feedback
- **Metrics Cards**: 4 visual cards showing:
  - Total Clusters
  - Included Behaviors
  - Average Strength
  - Average Confidence
- **Advanced Settings**: Collapsible panel with:
  - Min Strength slider (0-100%)
  - Min Confidence slider (0-100%)
  - Max Behaviors slider (1-20)
  - Include Archetype checkbox
  - Regenerate button
- **Usage Example**: Code snippet showing integration

#### 3. API Configuration Update
Added to `frontend/src/config/api.js`:
```javascript
getLLMContext: (userId, params) => {
  const queryParams = new URLSearchParams(params).toString();
  return `${API_BASE_URL}${API_VERSION}/profile/${userId}/llm-context${queryParams ? '?' + queryParams : ''}`;
}
```

### Files Modified
1. **frontend/src/config/api.js** - Added LLM context endpoint
2. **frontend/src/components/ProfileInsights.jsx** - Added modal, button, and functionality

### New State & Functions
```javascript
// State
const [showLLMModal, setShowLLMModal] = useState(false);
const [llmContext, setLlmContext] = useState(null);
const [llmLoading, setLlmLoading] = useState(false);
const [copied, setCopied] = useState(false);
const [llmParams, setLlmParams] = useState({...});

// Functions
fetchLLMContext() - Fetches context from backend
handleCopyContext() - Copies to clipboard
openLLMModal() - Opens modal and initiates fetch
```

### Usage in Frontend
1. Click purple "LLM Context" button in profile header
2. Modal opens and automatically fetches context
3. View formatted context with metadata
4. Adjust parameters in Advanced Settings
5. Click "Regenerate" to update with new parameters
6. Click "Copy" to copy context to clipboard
7. Use context in your LLM system prompt

### Testing
- **Test User**: user_665390
- **Frontend**: http://localhost:5174
- **Backend**: http://localhost:8000/api/v1/profile/user_665390/llm-context
- **Status**: ✅ Fully functional and tested

### Backend Integration
- Endpoint: `GET /api/v1/profile/{user_id}/llm-context`
- Parameters: min_strength, min_confidence, max_behaviors, include_archetype
- Response: JSON with context string and metadata
- Documentation: [LLM_CONTEXT_INJECTION.md](./LLM_CONTEXT_INJECTION.md)
