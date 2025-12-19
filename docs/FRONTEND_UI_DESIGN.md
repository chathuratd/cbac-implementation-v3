# CBIE System - Frontend UI Design Specification

**Last Updated:** December 19, 2025  
**Version:** Cluster-Centric UI v1.0

---

## Overview

This document specifies the frontend UI design for the CBIE (Core Behavior Identification Engine) system. The UI is designed around the **cluster-centric architecture**, where behavior clusters are the primary visualization focus.

---

## Design Principles

1. **Cluster-First**: Display behavior clusters as primary entities, not individual behaviors
2. **Evidence Transparency**: Show all observations within each cluster
3. **Confidence Indicators**: Visual feedback on cluster reliability
4. **Progressive Disclosure**: Summary → Details → Deep dive
5. **Temporal Context**: Show behavior evolution over time
6. **Mobile-Responsive**: Works on desktop, tablet, and mobile

---

## Page Structure

### 1. Dashboard / Overview Page

**Route:** `/dashboard` or `/profile/:userId`

#### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: User Profile - user_102                          [⚙️]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  🎭 Archetype: Visual Learner                          │    │
│  │  Based on 3 behavior clusters from 10 observations     │    │
│  │  Analyzed: December 19, 2025                           │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Statistics Card ────────────────────────────────────┐      │
│  │  📊 10 Observations  │  🔗 3 Clusters  │  📅 60 Days  │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌─ PRIMARY BEHAVIORS (1) ──────────────────────────────┐      │
│  │                                                        │      │
│  │  ┌─ Cluster Card ────────────────────────────────┐   │      │
│  │  │  ★ PRIMARY                          💪 84.2%  │   │      │
│  │  │  prefers analogies and metaphors               │   │      │
│  │  │                                                 │   │      │
│  │  │  📦 4 observations  │  🎯 62.3% confidence    │   │      │
│  │  │  📅 61.8 days ago → 2 days ago                 │   │      │
│  │  │                                                 │   │      │
│  │  │  [View Details →]                              │   │      │
│  │  └────────────────────────────────────────────────┘   │      │
│  │                                                        │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌─ SECONDARY BEHAVIORS (1) ────────────────────────────┐      │
│  │                                                        │      │
│  │  ┌─ Cluster Card ────────────────────────────────┐   │      │
│  │  │  ◆ SECONDARY                        💪 77.8%  │   │      │
│  │  │  theory and concept focused                    │   │      │
│  │  │                                                 │   │      │
│  │  │  📦 2 observations  │  🎯 51.2% confidence    │   │      │
│  │  │  📅 58 days ago → 5 days ago                   │   │      │
│  │  │                                                 │   │      │
│  │  │  [View Details →]                              │   │      │
│  │  └────────────────────────────────────────────────┘   │      │
│  │                                                        │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌─ NOISE (1) ───────────────────────────────────────┐  [🔽]   │
│  │  (Collapsed by default - expandable)                │         │
│  └──────────────────────────────────────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2. Cluster Details Modal/Page

**Trigger:** Click "View Details" on any cluster card

#### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Dashboard                                      [✕]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ★ PRIMARY BEHAVIOR CLUSTER                                     │
│  prefers analogies and metaphors                                │
│                                                                  │
│  ┌─ Cluster Metrics ──────────────────────────────────────┐    │
│  │                                                          │    │
│  │  Cluster Strength    🟢🟢🟢🟢⚪ 84.2%  ━━━━━ Strong    │    │
│  │  (log(size) × ABW × recency)                            │    │
│  │                                                          │    │
│  │  Confidence          🟡🟡🟡⚪⚪ 62.3%  ━━━━━ Moderate   │    │
│  │    ├─ Consistency    🟢🟢🟢⚪⚪ 61.8%  (semantic)       │    │
│  │    ├─ Reinforcement  🟢🟢🟢🟢⚪ 69.9%  (frequency)      │    │
│  │    └─ Clarity Trend  🟡🟡⚪⚪⚪ 48.3%  (improving)      │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Temporal Timeline ────────────────────────────────────┐    │
│  │                                                          │    │
│  │  First: Dec 2, 2024  ●───────●───────●────────●  Last:  │    │
│  │                         Nov 20   Oct 15  Oct 2   Dec 17 │    │
│  │  Active for 61.8 days across 4 observations             │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ All Observations (4) ─────────────────────────────────┐    │
│  │                                                          │    │
│  │  ┌─ Observation 1 ─────────────────────────┐  ★ Canonical │
│  │  │  "prefers analogies and metaphors"       │           │    │
│  │  │  ⚡ 0.906 ABW  │  🎯 88% clarity  │  📅 Dec 17, 2024  │    │
│  │  │  💬 Prompt: "Explain HTTP lifecycle"      │           │    │
│  │  └───────────────────────────────────────────┘           │    │
│  │                                                          │    │
│  │  ┌─ Observation 2 ─────────────────────────┐            │    │
│  │  │  "uses analogies frequently"              │           │    │
│  │  │  ⚡ 0.892 ABW  │  🎯 85% clarity  │  📅 Nov 20, 2024  │    │
│  │  │  💬 Prompt: "Describe database indexing"  │           │    │
│  │  └───────────────────────────────────────────┘           │    │
│  │                                                          │    │
│  │  ┌─ Observation 3 ─────────────────────────┐            │    │
│  │  │  "likes metaphorical explanations"        │           │    │
│  │  │  ⚡ 0.878 ABW  │  🎯 82% clarity  │  📅 Oct 15, 2024  │    │
│  │  │  💬 Prompt: "What is dependency injection"│           │    │
│  │  └───────────────────────────────────────────┘           │    │
│  │                                                          │    │
│  │  ┌─ Observation 4 ─────────────────────────┐            │    │
│  │  │  "explains through analogies"             │           │    │
│  │  │  ⚡ 0.854 ABW  │  🎯 79% clarity  │  📅 Oct 2, 2024   │    │
│  │  │  💬 Prompt: "Explain garbage collection"  │           │    │
│  │  └───────────────────────────────────────────┘           │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Wording Variations ───────────────────────────────────┐    │
│  │  🔤 prefers analogies and metaphors                     │    │
│  │  🔤 uses analogies frequently                           │    │
│  │  🔤 likes metaphorical explanations                     │    │
│  │  🔤 explains through analogies                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─ Related Prompts (4) ──────────────────────────────────┐    │
│  │  💬 "Explain HTTP lifecycle"                            │    │
│  │  💬 "Describe database indexing"                        │    │
│  │  💬 "What is dependency injection"                      │    │
│  │  💬 "Explain garbage collection"                        │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  [Export Data]  [Share]  [Add Note]                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### Component 1: Cluster Card

**Purpose:** Summary view of a behavior cluster

```jsx
<ClusterCard
  tier="PRIMARY"           // PRIMARY | SECONDARY | NOISE
  label="prefers analogies and metaphors"
  strength={0.842}         // 0-2+ (displayed as percentage)
  confidence={0.623}       // 0-1
  observationCount={4}
  firstSeen={1733123456}   // Unix timestamp
  lastSeen={1734567890}
  onClick={handleViewDetails}
/>
```

**Visual Design:**

```
┌─────────────────────────────────────────────────────┐
│  ★ PRIMARY                            💪 84.2%      │  ← Tier badge + Strength bar
│  prefers analogies and metaphors                    │  ← Canonical label (large text)
│                                                      │
│  📦 4 observations  │  🎯 62.3% confidence          │  ← Quick metrics
│  📅 61.8 days ago → 2 days ago                      │  ← Time range
│                                                      │
│  [View Details →]                                   │  ← Action button
└─────────────────────────────────────────────────────┘
```

**Color Scheme:**
- PRIMARY: Gold/Yellow border (#FFD700)
- SECONDARY: Silver/Gray border (#C0C0C0)
- NOISE: Muted/Light gray (#E0E0E0)

**Strength Indicator:**
- Visual bar with gradient
- Green (>80%), Yellow (60-80%), Orange (40-60%), Red (<40%)

---

### Component 2: Confidence Breakdown

**Purpose:** Visual representation of cluster confidence components

```jsx
<ConfidenceBreakdown
  confidence={0.623}
  consistency={0.618}
  reinforcement={0.699}
  clarityTrend={0.483}
/>
```

**Visual Design:**

```
Confidence          🟡🟡🟡⚪⚪ 62.3%  ━━━━━ Moderate
  ├─ Consistency    🟢🟢🟢⚪⚪ 61.8%  (semantic similarity)
  ├─ Reinforcement  🟢🟢🟢🟢⚪ 69.9%  (multiple evidence)
  └─ Clarity Trend  🟡🟡⚪⚪⚪ 48.3%  (improving over time)
```

**Interpretation Labels:**
- 80-100%: "Strong" (green)
- 60-79%: "Moderate" (yellow)
- 40-59%: "Weak" (orange)
- 0-39%: "Very Weak" (red)

**Tooltips:**
- Consistency: "How semantically similar observations are to each other"
- Reinforcement: "Strength from having multiple observations"
- Clarity Trend: "Whether observations are getting clearer over time"

---

### Component 3: Observation Card

**Purpose:** Display individual observation within a cluster

```jsx
<ObservationCard
  text="prefers analogies and metaphors"
  abw={0.906}
  clarityScore={0.88}
  timestamp={1734567890}
  promptText="Explain HTTP lifecycle"
  promptId="prompt_950a5eb8"
  isCanonical={true}
/>
```

**Visual Design:**

```
┌───────────────────────────────────────────┐  ★ Canonical
│  "prefers analogies and metaphors"        │  ← Behavior text
│  ⚡ 0.906 ABW  │  🎯 88% clarity  │  📅 Dec 17, 2024  │
│  💬 Prompt: "Explain HTTP lifecycle"       │  ← Related prompt
└───────────────────────────────────────────┘
```

**Canonical Badge:**
- Gold star icon for the canonical observation
- Tooltip: "Selected as display label based on clarity and centrality"

---

### Component 4: Timeline Visualization

**Purpose:** Show temporal distribution of observations

```jsx
<ClusterTimeline
  observations={[
    { timestamp: 1733123456, text: "obs 1" },
    { timestamp: 1734000000, text: "obs 2" },
    // ...
  ]}
  firstSeen={1733123456}
  lastSeen={1734567890}
/>
```

**Visual Design:**

```
First: Dec 2, 2024  ●───────●───────●────────●  Last: Dec 17, 2024
                       Nov 20   Oct 15  Oct 2

Active for 61.8 days across 4 observations
```

**Interactive:**
- Hover over dots to see observation details
- Click to scroll to observation in list

---

### Component 5: Archetype Display

**Purpose:** Show LLM-generated archetype summary

```jsx
<ArchetypeCard
  archetype="Visual Learner"
  description="Prefers visual explanations and analogies. Learns best through concrete examples and metaphorical comparisons."
  basedOn={3}  // Number of clusters
/>
```

**Visual Design:**

```
┌────────────────────────────────────────────────────┐
│  🎭 Archetype: Visual Learner                      │
│                                                     │
│  Prefers visual explanations and analogies.        │
│  Learns best through concrete examples and         │
│  metaphorical comparisons.                         │
│                                                     │
│  Based on 3 behavior clusters from 10 observations │
│  Analyzed: December 19, 2025                       │
└────────────────────────────────────────────────────┘
```

---

### Component 6: Statistics Dashboard

**Purpose:** High-level metrics overview

```jsx
<StatisticsCard
  totalObservations={10}
  clustersFormed={3}
  primaryCount={1}
  secondaryCount={1}
  noiseCount={1}
  analysisTimeSpan={59.69}
  totalPrompts={250}
/>
```

**Visual Design:**

```
┌─────────────────────────────────────────────────────┐
│  📊 Statistics                                       │
│                                                      │
│  📝 10 Observations    🔗 3 Clusters   📅 60 Days  │
│  ⭐ 1 Primary          ◆ 1 Secondary   ⚪ 1 Noise   │
│  💬 250 Prompts analyzed                            │
└─────────────────────────────────────────────────────┘
```

---

## Page Flows

### Flow 1: Initial View (Dashboard)

```
User lands on dashboard
    ↓
System fetches: GET /api/v1/analyze-behaviors-from-storage?user_id=user_102
    ↓
Display archetype card (if generated)
    ↓
Render cluster cards (PRIMARY → SECONDARY → NOISE)
    ↓
Show statistics summary
```

### Flow 2: Cluster Deep Dive

```
User clicks "View Details" on cluster card
    ↓
Open modal/navigate to cluster detail page
    ↓
Display cluster metrics (strength, confidence breakdown)
    ↓
Show temporal timeline
    ↓
Render all observations in cluster
    ↓
Display wording variations
    ↓
List related prompts
```

### Flow 3: Filtering/Sorting

```
User applies filters:
  - Show only PRIMARY
  - Sort by strength (descending)
  - Date range: Last 30 days
    ↓
Re-render cluster list with filters applied
    ↓
Update statistics to match filtered data
```

---

## Data Binding Examples

### React/Vue/Angular Example

```javascript
// Fetch data
const response = await fetch(
  `/api/v1/analyze-behaviors-from-storage?user_id=${userId}`
);
const profile = await response.json();

// Bind to UI
<div>
  <ArchetypeCard archetype={profile.archetype} />
  
  <StatisticsCard stats={profile.statistics} />
  
  <ClusterSection title="PRIMARY BEHAVIORS">
    {profile.behavior_clusters
      .filter(c => c.tier === 'PRIMARY')
      .map(cluster => (
        <ClusterCard
          key={cluster.cluster_id}
          tier={cluster.tier}
          label={cluster.canonical_label}
          strength={cluster.cluster_strength}
          confidence={cluster.cluster_confidence}
          observationCount={cluster.cluster_size}
          firstSeen={cluster.first_seen}
          lastSeen={cluster.last_seen}
          onClick={() => openClusterDetails(cluster)}
        />
      ))
    }
  </ClusterSection>
  
  <ClusterSection title="SECONDARY BEHAVIORS">
    {/* Similar for SECONDARY */}
  </ClusterSection>
  
  <ClusterSection title="NOISE" collapsible defaultCollapsed>
    {/* Similar for NOISE */}
  </ClusterSection>
</div>
```

---

## Responsive Design

### Desktop (≥1024px)
- 3-column layout for cluster cards
- Side-by-side metrics in cluster details
- Full timeline visualization

### Tablet (768px - 1023px)
- 2-column layout for cluster cards
- Stacked metrics in cluster details
- Simplified timeline

### Mobile (<768px)
- Single column layout
- Collapsible sections by default
- Bottom sheet for cluster details (instead of modal)
- Swipeable timeline

---

## Accessibility

### ARIA Labels
```html
<div role="region" aria-label="Primary Behaviors">
  <article role="article" aria-labelledby="cluster-2-label">
    <h3 id="cluster-2-label">prefers analogies and metaphors</h3>
    <div role="group" aria-label="Cluster metrics">
      <span aria-label="Cluster strength">84.2%</span>
      <span aria-label="Confidence level">62.3%</span>
    </div>
  </article>
</div>
```

### Keyboard Navigation
- Tab through cluster cards
- Enter to open details
- Arrow keys to navigate observations within cluster
- Escape to close modals

### Screen Reader Support
- "PRIMARY behavior cluster with strength 84.2%"
- "Contains 4 observations with 62.3% confidence"
- "First seen 61 days ago, last seen 2 days ago"

---

## Color Palette

### Tier Colors
```css
--tier-primary: #FFD700;      /* Gold */
--tier-secondary: #C0C0C0;    /* Silver */
--tier-noise: #E0E0E0;        /* Light gray */
```

### Strength Indicators
```css
--strength-strong: #10B981;   /* Green */
--strength-moderate: #F59E0B; /* Yellow */
--strength-weak: #F97316;     /* Orange */
--strength-very-weak: #EF4444;/* Red */
```

### Background
```css
--bg-primary: #FFFFFF;        /* White */
--bg-secondary: #F9FAFB;      /* Light gray */
--bg-hover: #F3F4F6;          /* Hover state */
```

### Text
```css
--text-primary: #111827;      /* Dark gray */
--text-secondary: #6B7280;    /* Medium gray */
--text-muted: #9CA3AF;        /* Light gray */
```

---

## Interactive Elements

### 1. Hover States

**Cluster Card:**
- Background color change
- Subtle shadow elevation
- "View Details" button appears/highlights

**Observation Card:**
- Slight border emphasis
- Show full prompt text (if truncated)

### 2. Click Actions

**Cluster Card Click:**
- Open cluster details modal/page
- Animate transition (slide up or fade)

**Timeline Dot Click:**
- Scroll to corresponding observation
- Highlight observation briefly

**Prompt Click:**
- Show full prompt context
- Optionally link to conversation history

### 3. Tooltips

**Strength Bar:**
- "Cluster strength: 0.842"
- "Formula: log(size+1) × mean(ABW) × recency"

**Confidence Metrics:**
- Hover over each component for explanation

**Canonical Badge:**
- "Selected as display label based on clarity and centrality"

---

## Loading States

### Initial Load
```
┌─────────────────────────────────────┐
│  Loading profile...                 │
│  ▓▓▓▓▓▓░░░░░░░░░░░░░░░ 30%        │
│  Fetching behaviors from database   │
└─────────────────────────────────────┘
```

### Cluster Details
```
┌─────────────────────────────────────┐
│  Loading cluster details...          │
│  ⟳ Analyzing observations            │
└─────────────────────────────────────┘
```

### Skeleton Screens
- Show cluster card outlines while loading
- Animated shimmer effect
- Maintain layout structure

---

## Error States

### No Data
```
┌─────────────────────────────────────┐
│  📭 No behaviors found               │
│                                      │
│  This user has no analyzed behaviors │
│  yet. Start a conversation to build  │
│  their behavior profile.             │
│                                      │
│  [Start Analysis]                    │
└─────────────────────────────────────┘
```

### API Error
```
┌─────────────────────────────────────┐
│  ⚠️ Error loading profile            │
│                                      │
│  Unable to fetch behavior data.      │
│  Please try again.                   │
│                                      │
│  [Retry]  [Contact Support]          │
└─────────────────────────────────────┘
```

### Low Confidence Warning
```
⚠️ This cluster has low confidence (32.1%)
   Consider gathering more observations for better accuracy.
```

---

## Advanced Features (Optional)

### 1. Comparison View
- Compare current profile with historical snapshots
- Show cluster strength evolution over time
- Highlight new/disappeared clusters

### 2. Export Options
- PDF report with all clusters and metrics
- CSV of observations for analysis
- JSON for programmatic access

### 3. Collaborative Features
- Add notes/tags to clusters
- Share specific clusters with team
- Discuss observations in context

### 4. Analytics Dashboard
- Cluster strength trends over time
- Observation frequency heatmap
- Prompt correlation analysis

---

## Implementation Technologies

### Recommended Stack

**Frontend Framework:**
- React 18+ with TypeScript
- Next.js for SSR/SSG
- TailwindCSS for styling

**State Management:**
- React Query for API data
- Zustand for local state
- Context API for theme/settings

**Visualization:**
- Recharts for timeline graphs
- D3.js for advanced visualizations
- Framer Motion for animations

**UI Components:**
- Headless UI for accessible components
- Radix UI for primitives
- Custom components for cluster cards

---

## Sample Code

### Cluster Card Component (React)

```tsx
import React from 'react';
import { TierEnum } from '@/types';

interface ClusterCardProps {
  tier: TierEnum;
  label: string;
  strength: number;
  confidence: number;
  observationCount: number;
  firstSeen: number;
  lastSeen: number;
  onClick: () => void;
}

export const ClusterCard: React.FC<ClusterCardProps> = ({
  tier,
  label,
  strength,
  confidence,
  observationCount,
  firstSeen,
  lastSeen,
  onClick
}) => {
  const tierColors = {
    PRIMARY: 'border-yellow-400 bg-yellow-50',
    SECONDARY: 'border-gray-400 bg-gray-50',
    NOISE: 'border-gray-300 bg-gray-50'
  };

  const tierIcons = {
    PRIMARY: '★',
    SECONDARY: '◆',
    NOISE: '○'
  };

  const strengthPercent = Math.min(100, (strength / 2) * 100);
  const confidencePercent = confidence * 100;

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    const now = Date.now();
    const daysAgo = Math.floor((now - date.getTime()) / (1000 * 60 * 60 * 24));
    return `${daysAgo} days ago`;
  };

  return (
    <div
      className={`
        border-2 rounded-lg p-4 cursor-pointer
        transition-all duration-200
        hover:shadow-lg hover:scale-102
        ${tierColors[tier]}
      `}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{tierIcons[tier]}</span>
          <span className="font-semibold text-sm">{tier}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold">💪 {strengthPercent.toFixed(1)}%</span>
        </div>
      </div>

      {/* Canonical Label */}
      <h3 className="text-lg font-semibold mb-4 text-gray-900">
        {label}
      </h3>

      {/* Metrics */}
      <div className="flex flex-wrap gap-3 text-sm text-gray-600 mb-3">
        <span>📦 {observationCount} observations</span>
        <span>🎯 {confidencePercent.toFixed(1)}% confidence</span>
      </div>

      {/* Timeline */}
      <div className="text-sm text-gray-500 mb-4">
        📅 {formatDate(firstSeen)} → {formatDate(lastSeen)}
      </div>

      {/* Action Button */}
      <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
        View Details →
      </button>
    </div>
  );
};
```

### Confidence Breakdown Component (React)

```tsx
import React from 'react';

interface ConfidenceBreakdownProps {
  confidence: number;
  consistency: number;
  reinforcement: number;
  clarityTrend: number;
}

export const ConfidenceBreakdown: React.FC<ConfidenceBreakdownProps> = ({
  confidence,
  consistency,
  reinforcement,
  clarityTrend
}) => {
  const getLabel = (value: number) => {
    if (value >= 0.8) return { text: 'Strong', color: 'text-green-600' };
    if (value >= 0.6) return { text: 'Moderate', color: 'text-yellow-600' };
    if (value >= 0.4) return { text: 'Weak', color: 'text-orange-600' };
    return { text: 'Very Weak', color: 'text-red-600' };
  };

  const renderBar = (value: number, label: string, tooltip: string) => {
    const filled = Math.round(value * 5);
    const label_info = getLabel(value);

    return (
      <div className="flex items-center gap-3 py-2" title={tooltip}>
        <span className="text-sm w-32">{label}</span>
        <div className="flex gap-1">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className={`w-4 h-4 rounded-full ${
                i < filled ? 'bg-current' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
        <span className={`text-sm font-medium ml-2 ${label_info.color}`}>
          {(value * 100).toFixed(1)}%
        </span>
        <span className={`text-xs ml-2 ${label_info.color}`}>
          {label_info.text}
        </span>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg border p-4">
      <h4 className="font-semibold mb-4">Cluster Metrics</h4>

      {renderBar(
        confidence,
        'Confidence',
        'Overall reliability of this cluster'
      )}

      <div className="ml-6 mt-2 space-y-1">
        {renderBar(
          consistency,
          '├─ Consistency',
          'How semantically similar observations are'
        )}
        {renderBar(
          reinforcement,
          '├─ Reinforcement',
          'Strength from having multiple observations'
        )}
        {renderBar(
          clarityTrend,
          '└─ Clarity Trend',
          'Whether observations are getting clearer over time'
        )}
      </div>
    </div>
  );
};
```

---

## Wireframe Summary

### Desktop Layout
```
┌────────────────────────────────────────────────────┐
│  Header: CBIE System - User Profile                │
├────────────────────────────────────────────────────┤
│                                                     │
│  [Archetype Card - Full Width]                     │
│                                                     │
│  [Statistics Card - Full Width]                    │
│                                                     │
│  ┌─ PRIMARY (1) ─────────────────────────────┐    │
│  │  [Cluster Card]  [Cluster Card]  [...]    │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  ┌─ SECONDARY (1) ───────────────────────────┐    │
│  │  [Cluster Card]  [Cluster Card]  [...]    │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  ┌─ NOISE (1) [Collapsed] ──────────────────┐     │
│  │  [Click to expand]                        │     │
│  └────────────────────────────────────────────┘    │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Mobile Layout
```
┌───────────────────┐
│  CBIE - user_102  │
├───────────────────┤
│                   │
│  [Archetype]      │
│                   │
│  [Stats]          │
│                   │
│  PRIMARY (1) ▼    │
│  [Cluster Card]   │
│                   │
│  SECONDARY (1) ▼  │
│  [Cluster Card]   │
│                   │
│  NOISE (1) ▶      │
│  [Collapsed]      │
│                   │
└───────────────────┘
```

---

## Next Steps

1. **Design System Setup**: Create component library with reusable UI elements
2. **API Integration**: Connect to `/api/v1/analyze-behaviors-from-storage` endpoint
3. **Prototype**: Build interactive prototype in Figma/Sketch
4. **User Testing**: Validate UI/UX with target users
5. **Implementation**: Develop frontend with chosen tech stack
6. **Performance**: Optimize for large datasets (pagination, virtualization)

---

**Document Version**: 1.0  
**Last Reviewed**: December 19, 2025  
**Related Docs**: CURRENT_IMPLEMENTATION.md, API_DOCUMENTATION.md
