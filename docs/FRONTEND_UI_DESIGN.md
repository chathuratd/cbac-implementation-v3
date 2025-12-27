# CBIE System - Complete Frontend UI Specification

**Last Updated:** December 27, 2025  
**Version:** 2.0 (Cluster-Centric Architecture)  
**Status:** Production-Ready Design

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Screen-by-Screen Specifications](#screen-by-screen-specifications)
4. [API-to-UI Mapping](#api-to-ui-mapping)
5. [Component Library](#component-library)
6. [User Flows](#user-flows)
7. [States & Error Handling](#states--error-handling)
8. [Responsive Behavior](#responsive-behavior)

---

## Overview

This document provides a complete, technology-agnostic specification for the CBIE frontend interface. The design is centered around the **cluster-centric architecture**, where behavior clusters (not individual observations) are the primary focus of visualization and interaction.

### Key Concepts for UI Design

- **Behavior Clusters**: Groups of similar observations that represent a consistent pattern
- **Tiers**: PRIMARY (strength ≥ 0.80), SECONDARY (strength ≥ 0.50), NOISE (< 0.50)
- **Canonical Label**: Short, LLM-generated summary of cluster meaning
- **Cluster Name**: Descriptive 3-6 word label for cluster
- **Archetype**: Overall personality label (e.g., "Pragmatic Analytical Thinker")
- **Wording Variations**: All different phrasings of the same behavior within a cluster

---

## Design Principles

1. **Cluster-First Display**: Show aggregated patterns, not raw observations
2. **Evidence Transparency**: Allow drill-down to view all observations in a cluster
3. **Progressive Disclosure**: Summary cards → Detail views → Evidence explorer
4. **Confidence Visualization**: Use visual indicators (colors, badges, progress bars) for strength/confidence
5. **Temporal Awareness**: Display first_seen, last_seen, days_active to show behavior evolution
6. **Action-Oriented**: Clear calls-to-action for analysis, archetype assignment, context viewing
7. **Accessibility**: Color-blind friendly, screen reader compatible, keyboard navigable
8. **No Raw IDs**: Never show database IDs, cluster_ids, or observation_ids to users

---

## Screen-by-Screen Specifications

### 1. User List / Dashboard Screen

**Purpose**: Browse all users with behavior profiles

**API Used**: GET `/api/v1/profile/{user_id}/summary` (called for each user in list)

#### Layout Description

**Top Section - Header**
- Page title: "Behavior Profiles"
- Search bar: Filter users by ID or archetype
- Button: "New Analysis" (opens analysis setup screen)

**Main Content - User Cards Grid**
- Grid layout: 3 columns on desktop, 2 on tablet, 1 on mobile
- Each card displays:
  - User identifier (e.g., "User 102")
  - Archetype badge (e.g., "Pragmatic Analytical Thinker")
  - Behavior counts:
    - "3 Primary" (green badge)
    - "5 Secondary" (blue badge)
    - "8 Total" (gray text)
  - Average confidence: Progress bar (0-100%) with percentage label
  - Last updated: Timestamp (e.g., "Updated 2 days ago")
  - Action button: "View Profile" (navigates to profile detail screen)

**Visual States**
- Default: Card with subtle shadow, white background
- Hover: Shadow deepens, slight scale increase
- Loading: Skeleton loading animation on cards
- Empty state: "No profiles found" with illustration and "Create First Analysis" button

**Interactions**
- Click card → Navigate to profile detail
- Click "View Profile" button → Navigate to profile detail
- Search box → Filter cards in real-time
- Click "New Analysis" → Open analysis setup modal

---

### 2. Profile Detail Screen

**Purpose**: View complete behavior profile for a single user

**API Used**: GET `/api/v1/profile/{user_id}` (full profile data)

#### Layout Description

**Header Section**
- Breadcrumb: "Profiles / User 102"
- User identifier: Large heading "User 102"
- Archetype display: 
  - Icon (e.g., 🎭)
  - Label: "Pragmatic Analytical Thinker"
  - Subtitle: "Based on 3 behavior clusters from 15 observations"
- Action buttons (right-aligned):
  - "Re-analyze" (triggers new analysis)
  - "Assign Archetype" (opens archetype assignment modal)
  - "View LLM Context" (opens context viewer)
  - "Settings" dropdown (export, delete options)

**Summary Statistics Bar**
- Four stat cards in horizontal row:
  1. **Total Observations**: "15 behaviors" with document icon
  2. **Active Clusters**: "8 clusters detected" with cluster icon
  3. **Time Span**: "45 days active" with calendar icon
  4. **Analysis Date**: "Analyzed Dec 27, 2025" with clock icon

**Primary Behaviors Section**
- Section heading: "PRIMARY BEHAVIORS" with count badge (e.g., "3")
- Grid of cluster cards (2 columns on desktop, 1 on mobile)
- Each cluster card shows:
  - **Tier badge**: "PRIMARY" in green with star icon
  - **Canonical label**: Bold, 2-3 lines (e.g., "Analytical Problem-Solving and Conceptual Thinking")
  - **Cluster name**: Secondary text (e.g., "Systematic Analysis and Logical Reasoning")
  - **Strength indicator**: 
    - Progress bar (0-100%, filled based on cluster_strength)
    - Label: "Strength: 85%" next to bar
  - **Confidence indicator**:
    - Progress bar (0-100%, filled based on confidence)
    - Label: "Confidence: 72%" next to bar
  - **Observation count**: Icon + text (e.g., "📊 12 observations")
  - **Temporal info**:
    - First seen: "First: Dec 1, 2025"
    - Last seen: "Last: Dec 27, 2025"
    - Days active: "Active: 27 days"
  - **Expand button**: "View Evidence ▼" (collapses/expands wording variations)

**Expanded State (when "View Evidence" clicked)**
- Same card expands vertically
- Shows list of wording variations:
  - Heading: "Wording Variations (12)"
  - Scrollable list of all behavior texts:
    - "I need to analyze the problem systematically"
    - "I prefer breaking down complex issues step by step"
    - "I approach challenges through logical reasoning"
    - ... (up to 12 variations shown, "Show more" if > 12)
  - Each variation shows timestamp as subtitle (e.g., "Dec 15, 2025")
- Collapse button: "Hide Evidence ▲"

**Secondary Behaviors Section**
- Section heading: "SECONDARY BEHAVIORS" with count badge (e.g., "5")
- Grid of cluster cards (same structure as PRIMARY but with blue badges)
- Tier badge: "SECONDARY" in blue

**Noise/Outliers Section** (collapsible by default)
- Section heading: "OUTLIERS & NOISE" with count badge (e.g., "2")
- Collapse/expand toggle
- When expanded: Show cluster cards with gray badges
- Information tooltip: "These behaviors appear inconsistently or lack sufficient evidence"

**Related Prompts Section** (optional, if prompt data available)
- Section heading: "Related Conversation Context"
- List of prompts that led to observations:
  - Prompt text (truncated to 2 lines)
  - Timestamp
  - Number of behaviors extracted
  - Click to expand full prompt

**Visual Hierarchy**
- Clear tier separation with whitespace and section dividers
- Color coding: Green (PRIMARY), Blue (SECONDARY), Gray (NOISE)
- Strength/confidence bars use gradient fills
- Cards have consistent padding and rounded corners

**Interactions**
- Click "View Evidence" → Expand card to show wording variations
- Click "Hide Evidence" → Collapse card
- Click "Re-analyze" → Open confirmation modal, then trigger POST `/analyze-and-save`
- Click "Assign Archetype" → Open archetype assignment modal
- Click "View LLM Context" → Navigate to LLM context viewer screen
- Hover over tier badges → Tooltip explaining tier meaning
- Hover over strength/confidence bars → Tooltip showing exact values

**Loading States**
- Initial load: Skeleton loading for entire page
- Re-analysis: Loading spinner overlay with "Analyzing..." message
- Expand evidence: Smooth animation, no loading (data already fetched)

**Empty States**
- No PRIMARY behaviors: Message "No strong behavior patterns detected yet"
- No SECONDARY behaviors: (Show nothing or subtle message)
- No profile data: Redirect to user list or show "Profile not found" error

---

### 3. LLM Context Viewer Screen

**Purpose**: Display token-efficient profile data for LLM system prompt injection

**API Used**: GET `/api/v1/profile/{user_id}/llm-context`

#### Layout Description

**Header Section**
- Page title: "LLM Context for User 102"
- Subtitle: "Optimized for AI assistant integration"
- Token count badge: "~350 tokens" (estimated)
- Action buttons:
  - "Copy as JSON" (copies entire context to clipboard)
  - "Copy as Markdown" (copies formatted markdown)
  - "Download" (downloads as .txt or .json)
  - "Back to Profile" (navigate back)

**Archetype Display**
- Large card at top:
  - Icon: 🎭
  - Label: "Pragmatic Analytical Thinker"
  - Subtitle: "User Personality Archetype"

**Primary Behaviors Section**
- Heading: "Primary Behaviors (3)"
- List of behavior cards (vertical stack):
  - **Label**: Bold text (e.g., "Analytical Problem-Solving")
  - **Description**: 2-3 sentences explaining the behavior
    - Example: "User consistently approaches problems through logical analysis, breaking down complex issues into manageable components."
  - **Confidence**: Badge showing percentage (e.g., "85% confidence")
  - **Observation count**: Small text (e.g., "Based on 12 observations")
  - Visual separator between cards

**Secondary Behaviors Section**
- Heading: "Secondary Behaviors (5)"
- Condensed list (more compact than PRIMARY):
  - **Label**: Bold text
  - **Confidence**: Inline percentage
  - **Observation count**: Inline text
  - No descriptions (to save tokens)
  - Example: "Documentation Preference • 65% • 5 observations"

**Summary Section**
- Heading: "Behavioral Summary"
- Text box with human-readable summary (2-3 paragraphs):
  - Example: "User exhibits strong analytical tendencies with emphasis on systematic problem-solving. Secondary traits include preference for detailed documentation and iterative refinement. Overall communication style is direct and focused on practical outcomes."
- Style: Light gray background, italic text, larger font

**Copy Preview Section**
- Heading: "Copy Preview"
- Tabs:
  - "JSON Format" (default)
  - "Markdown Format"
  - "Plain Text Format"
- Code block showing formatted output:
  - Syntax highlighting for JSON
  - Copyable text area
  - Line numbers (for JSON)

**Visual Design**
- Clean, minimal layout
- Focus on readability and scannability
- Use of whitespace to separate sections
- Monospace font for code blocks
- Color coding for confidence levels (green high, yellow medium, red low)

**Interactions**
- Click "Copy as JSON" → Copy to clipboard, show toast notification "Copied!"
- Click "Copy as Markdown" → Copy formatted markdown, show toast
- Click "Download" → Download as file with user_id in filename
- Switch tabs in Copy Preview → Show different format
- Hover over confidence badges → Tooltip explaining confidence calculation

**Token Optimization Notice**
- Information banner at top:
  - Icon: ℹ️
  - Text: "This view is optimized for LLM consumption with minimal token usage. For full details, view the complete profile."
  - Link: "View Full Profile" (navigates to profile detail screen)

---

### 4. Analysis Setup Screen

**Purpose**: Configure and trigger new behavior analysis

**API Used**: POST `/api/v1/profile/{user_id}/analyze-and-save`

#### Layout Description

**Header**
- Page title: "New Behavior Analysis"
- Breadcrumb: "Profiles / User 102 / New Analysis"

**Step 1: User Selection**
- Section heading: "1. Select User"
- User input field:
  - Label: "User ID"
  - Input: Text field or dropdown (if user list exists)
  - Placeholder: "Enter user ID or select from list"
  - Validation: Shows error if user not found

**Step 2: Data Source Selection**
- Section heading: "2. Choose Data Source"
- Radio button options:
  1. **Load from Database**
     - Description: "Analyze existing behaviors and prompts stored in database"
     - Shows count if available: "15 behaviors, 30 prompts found"
  2. **Upload New Data**
     - Description: "Upload behavior and prompt JSON files"
     - File upload fields:
       - "Behaviors JSON" (required)
       - "Prompts JSON" (optional)
     - File validation: Shows preview of uploaded data

**Step 3: Analysis Options**
- Section heading: "3. Configure Analysis"
- Checkbox options:
  - ☑ **Generate Archetype** (checked by default)
    - Description: "Use LLM to create personality archetype label"
    - Note: "May take 10-30 seconds"
  - ☑ **Save to Database** (checked by default)
    - Description: "Persist analysis results to database"
  - ☐ **Force Re-analysis**
    - Description: "Re-analyze even if recent profile exists"
    - Warning: "This will overwrite existing profile"

**Advanced Settings (collapsible)**
- Collapse/expand toggle: "Advanced Settings ▼"
- When expanded:
  - **Clustering Parameters**:
    - Min cluster size: Number input (default: 2)
    - Min samples: Number input (default: 2)
  - **Threshold Overrides**:
    - PRIMARY threshold: Slider (0-1, default: 0.80)
    - SECONDARY threshold: Slider (0-1, default: 0.50)
  - Information note: "Leave default unless you understand the impact"

**Action Buttons (bottom)**
- "Cancel" button (secondary style, left-aligned) → Navigate back
- "Start Analysis" button (primary style, right-aligned) → Trigger analysis

**Analysis Progress Modal** (appears when "Start Analysis" clicked)
- Modal overlay with progress steps:
  1. **Loading data**: Spinner + "Loading observations..."
  2. **Generating embeddings**: Spinner + "Generating embeddings..." (1/15)
  3. **Clustering**: Spinner + "Detecting behavior patterns..."
  4. **Calculating metrics**: Spinner + "Computing strength & confidence..."
  5. **Generating labels**: Spinner + "Creating LLM labels..."
  6. **Saving profile**: Spinner + "Persisting to database..."
  7. **Complete**: Checkmark + "Analysis complete!"
- Progress bar showing overall completion (0-100%)
- "Cancel" button (stops analysis if possible)

**Success Screen**
- After analysis completes, show success card:
  - Large checkmark icon: ✅
  - Heading: "Analysis Complete!"
  - Summary statistics:
    - "5 clusters detected"
    - "2 PRIMARY behaviors"
    - "3 SECONDARY behaviors"
    - "Archetype: Pragmatic Analytical Thinker"
  - Action buttons:
    - "View Profile" (primary) → Navigate to profile detail
    - "Analyze Another User" (secondary) → Reset form
    - "Close" → Navigate to user list

**Error Handling**
- If analysis fails, show error modal:
  - Red X icon: ❌
  - Heading: "Analysis Failed"
  - Error message: (specific error from API)
  - Buttons:
    - "Try Again" → Close modal, return to form
    - "Cancel" → Navigate back to user list

---

### 5. Archetype Assignment Screen

**Purpose**: Generate or update user archetype using LLM

**API Used**: POST `/api/v1/assign-archetype`

#### Layout Description

**Header**
- Page title: "Assign Behavioral Archetype"
- Subtitle: "User 102"

**Current Archetype Display** (if exists)
- Card showing:
  - Label: "Current Archetype"
  - Value: "Pragmatic Analytical Thinker"
  - Timestamp: "Assigned Dec 27, 2025"

**Behavior Selection**
- Section heading: "Select Behaviors for Archetype Generation"
- Information note: "LLM will analyze selected behaviors to generate archetype label"
- List of available clusters with checkboxes:
  - Each row shows:
    - ☑ Checkbox (PRIMARY behaviors checked by default)
    - Tier badge (PRIMARY/SECONDARY)
    - Canonical label
    - Observation count
  - "Select All" / "Deselect All" buttons above list
- Validation: At least 1 behavior must be selected

**LLM Prompt Preview** (optional, collapsible)
- Heading: "What the LLM Will See"
- Collapsible text area showing the prompt that will be sent
- Read-only, for transparency

**Action Buttons**
- "Cancel" (secondary) → Close modal/navigate back
- "Generate Archetype" (primary) → Trigger LLM call

**Loading State**
- When "Generate Archetype" clicked:
  - Loading spinner overlay
  - Message: "Generating archetype with AI..."
  - Progress: Indeterminate spinner
  - Estimated time: "This may take 10-30 seconds"

**Success State**
- Show result card:
  - Large icon: 🎭
  - New archetype: "Detail-Oriented Systematizer"
  - Comparison (if previous archetype exists):
    - "Previous: Pragmatic Analytical Thinker"
    - "New: Detail-Oriented Systematizer"
  - Action buttons:
    - "Accept and Save" → Save new archetype, navigate back
    - "Regenerate" → Try again with same inputs
    - "Cancel" → Discard, navigate back

**Error Handling**
- If LLM call fails:
  - Error message: "Failed to generate archetype: [reason]"
  - Retry button
  - Fallback option: "Enter archetype manually" (text input)

---

### 6. User Summary Screen (Minimal Dashboard)

**Purpose**: Quick overview for dashboards/widgets

**API Used**: GET `/api/v1/profile/{user_id}/summary`

#### Layout Description

**Compact Card Layout**
- Small card optimized for dashboard widgets
- Displays:
  - **User ID**: Heading "User 102"
  - **Archetype**: Subheading "Pragmatic Analytical Thinker"
  - **Behavior Counts**:
    - "3 Primary" (green chip)
    - "5 Secondary" (blue chip)
    - "8 Total" (gray text)
  - **Average Confidence**: Single progress bar (0-100%)
  - **Last Updated**: Small text "2 days ago"
  - **Quick Action**: "View Full Profile" link

**Visual Design**
- Minimal, dense layout
- Single card fits in 300x200px space
- Suitable for embedding in dashboards

**Use Cases**
- Dashboard widget
- Sidebar preview
- Quick lookup in user lists

---

### 7. Core Behaviors List Screen

**Purpose**: View simplified list of behaviors without full profile context

**API Used**: GET `/api/v1/user/{user_id}/core-behaviors`

#### Layout Description

**Header**
- Page title: "Core Behaviors"
- Subtitle: "User 102"
- Filter controls:
  - Dropdown: "Show: All / PRIMARY only / SECONDARY only"
  - Sort: "Sort by: Strength / Confidence / Observation Count"

**Behavior List**
- Table or list view:
  - Columns:
    1. **Tier**: Badge (PRIMARY/SECONDARY)
    2. **Label**: Canonical label text
    3. **Cluster Name**: Descriptive name
    4. **Strength**: Progress bar with percentage
    5. **Confidence**: Progress bar with percentage
    6. **Observations**: Count
  - Each row clickable → Expand inline to show wording variations

**Expanded Row**
- When clicked, row expands to show:
  - All wording variations in a nested list
  - Timestamps for each variation
  - "View in Full Profile" link

**Empty State**
- If no behaviors: "No core behaviors detected"
- Call-to-action: "Run Analysis" button

**Interactions**
- Click row → Expand/collapse inline
- Change filter → Reload list with filtered data
- Change sort → Re-sort list
- Click "View in Full Profile" → Navigate to profile detail

---

### 8. Health Check Indicator

**Purpose**: Show system status

**API Used**: GET `/api/v1/health`

#### Display Location

**In Main Navigation/Header**
- Small status indicator in top-right corner
- Shows:
  - 🟢 "System Healthy" (green dot)
  - 🟡 "System Degraded" (yellow dot)
  - 🔴 "System Down" (red dot)
- Tooltip on hover: "API Status: Healthy"

**Behavior**
- Poll every 30 seconds in background
- If health check fails → Show warning banner: "System may be experiencing issues"
- User can click status → Open detailed health modal (optional)

---

## API-to-UI Mapping

### Complete API Coverage

| API Endpoint | HTTP Method | UI Location(s) | Purpose | Data Displayed |
|--------------|-------------|----------------|---------|----------------|
| `/api/v1/profile/{user_id}` | GET | Profile Detail Screen | Show complete behavior profile | Archetype, behavior_clusters[], analysis_metadata, all evidence |
| `/api/v1/user/{user_id}/core-behaviors` | GET | Core Behaviors List Screen | Show simplified behavior list | Canonical labels, tier, strength, confidence, observed_count |
| `/api/v1/profile/{user_id}/llm-context` | GET | LLM Context Viewer Screen | Display token-efficient profile | Archetype, primary_behaviors[], secondary_behaviors[], summary |
| `/api/v1/profile/{user_id}/summary` | GET | User List Dashboard, Summary Widget | Show quick stats | Archetype, behavior counts, average confidence, last_updated |
| `/api/v1/profile/{user_id}/analyze-and-save` | POST | Analysis Setup Screen | Trigger new analysis and save | Returns success status, cluster counts, archetype |
| `/api/v1/assign-archetype` | POST | Archetype Assignment Screen | Generate/update archetype | Returns new archetype label |
| `/api/v1/analyze-behaviors-cluster-centric` | POST | Analysis Setup Screen (test mode) | Run analysis without saving | Returns full CoreBehaviorProfile (for preview) |
| `/api/v1/health` | GET | Navigation Header | Show system status | Health status message |

### Deprecated APIs (No UI Implementation Needed)

| API Endpoint | Status | Notes |
|--------------|--------|-------|
| `/api/v1/update-behavior` | ❌ Remove | Violates immutability |
| `/api/v1/analyze-behaviors-from-storage` | ❌ Remove | Uses old pipeline |
| `/api/v1/analyze-behaviors` | ❌ Remove | Uses old pipeline |

---

## Component Library

### 1. Cluster Card Component

**Purpose**: Display a single behavior cluster with all metadata

**Props/Data**:
- cluster_id (hidden from user)
- canonical_label (string)
- cluster_name (string)
- tier (enum: PRIMARY, SECONDARY, NOISE)
- cluster_strength (float 0-1)
- confidence (float 0-1)
- cluster_size (integer)
- wording_variations (array of strings)
- first_seen (timestamp)
- last_seen (timestamp)
- days_active (integer)
- isExpanded (boolean state)

**Visual Elements**:
- Tier badge (top-left corner)
- Canonical label (heading)
- Cluster name (subheading)
- Two progress bars (strength, confidence) with labels
- Observation count icon + text
- Temporal info row (first, last, active days)
- "View Evidence" toggle button

**States**:
- Collapsed (default): Shows summary only
- Expanded: Shows wording_variations list
- Loading: Skeleton animation
- Error: Error message in red

**Interactions**:
- Click "View Evidence" → Toggle expanded state
- Hover over tier badge → Show tooltip
- Hover over progress bars → Show exact percentages

**Color Coding**:
- PRIMARY: Green accent (#22c55e)
- SECONDARY: Blue accent (#3b82f6)
- NOISE: Gray accent (#6b7280)

---

### 2. Progress Bar Component

**Purpose**: Visualize strength/confidence values

**Props/Data**:
- value (float 0-1)
- label (string, e.g., "Strength: 85%")
- color (green/blue/gray)
- showTooltip (boolean)

**Visual Elements**:
- Background bar (light gray)
- Filled bar (colored, width = value × 100%)
- Label text (left of bar)
- Percentage text (right of bar)

**States**:
- Normal: Filled bar with color
- Low value (< 0.3): Red color
- Medium value (0.3-0.7): Yellow/orange color
- High value (> 0.7): Green color

**Interactions**:
- Hover → Show tooltip with exact value

---

### 3. Tier Badge Component

**Purpose**: Display behavior tier

**Props/Data**:
- tier (enum: PRIMARY, SECONDARY, NOISE)

**Visual Elements**:
- Pill-shaped badge
- Icon (star for PRIMARY, circle for SECONDARY, dash for NOISE)
- Text label

**Color Mapping**:
- PRIMARY: Green background (#22c55e), white text
- SECONDARY: Blue background (#3b82f6), white text
- NOISE: Gray background (#6b7280), white text

**Interactions**:
- Hover → Show tooltip explaining tier meaning

---

### 4. Archetype Display Component

**Purpose**: Show user's behavioral archetype

**Props/Data**:
- archetype (string)
- clusterCount (integer)
- observationCount (integer)

**Visual Elements**:
- Large icon (🎭)
- Archetype label (large heading)
- Subtitle with counts

**Visual Design**:
- Prominent card with subtle gradient background
- Centered text
- Rounded corners

---

### 5. Statistics Card Component

**Purpose**: Display single statistic

**Props/Data**:
- icon (emoji or icon)
- value (string/number)
- label (string)

**Visual Elements**:
- Icon (top)
- Large value (middle)
- Small label (bottom)

**Layout**:
- Vertical stack
- Centered alignment
- White background card

---

### 6. Loading State Component

**States**:
- **Skeleton Loading**: Gray animated blocks mimicking content structure
- **Spinner Loading**: Circular spinner with message
- **Progress Loading**: Progress bar for multi-step operations

**Use Cases**:
- Skeleton: Page initial load
- Spinner: Button actions, modal operations
- Progress: Analysis pipeline, file uploads

---

### 7. Empty State Component

**Props/Data**:
- message (string)
- illustration (optional image/icon)
- actionLabel (string for button)
- onAction (callback)

**Visual Elements**:
- Centered layout
- Illustration/icon
- Message text
- Call-to-action button

**Examples**:
- "No profiles found" → "Create First Analysis" button
- "No PRIMARY behaviors detected" → "Run Re-analysis" button

---

### 8. Error Banner Component

**Purpose**: Display error messages

**Props/Data**:
- message (string)
- severity (error/warning/info)
- dismissible (boolean)

**Visual Elements**:
- Horizontal banner (top of screen)
- Icon (based on severity)
- Message text
- Close button (if dismissible)

**Color Coding**:
- Error: Red background
- Warning: Yellow/orange background
- Info: Blue background

---

### 9. Toast Notification Component

**Purpose**: Show temporary success/error messages

**Props/Data**:
- message (string)
- type (success/error/info)
- duration (milliseconds)

**Visual Elements**:
- Small popup (bottom-right corner)
- Icon + message
- Auto-dismiss after duration

**Examples**:
- "Copied to clipboard!" (success)
- "Analysis failed" (error)
- "Profile updated" (success)

---

## User Flows

### Flow 1: View User Profile

1. User arrives at **User List Dashboard**
2. Sees grid of user cards (data from `/summary` API)
3. Clicks "View Profile" on a card
4. Navigates to **Profile Detail Screen**
5. System fetches full profile (GET `/profile/{user_id}`)
6. Page displays:
   - Archetype header
   - Statistics bar
   - PRIMARY behavior clusters (collapsed)
   - SECONDARY behavior clusters (collapsed)
7. User clicks "View Evidence" on a PRIMARY cluster
8. Cluster card expands, showing all wording variations
9. User scrolls through variations, seeing timestamps
10. User clicks "Hide Evidence" to collapse
11. User clicks "View LLM Context" button
12. Navigates to **LLM Context Viewer Screen**
13. System fetches context data (GET `/profile/{user_id}/llm-context`)
14. Page displays optimized context with copy buttons
15. User clicks "Copy as JSON"
16. Toast notification: "Copied to clipboard!"
17. User clicks "Back to Profile" to return

---

### Flow 2: Run New Behavior Analysis

1. User clicks "New Analysis" from **User List Dashboard**
2. Navigates to **Analysis Setup Screen**
3. Enters or selects User ID
4. Selects "Load from Database" option
5. System shows: "15 behaviors, 30 prompts found"
6. Checks "Generate Archetype" (default checked)
7. Checks "Save to Database" (default checked)
8. Clicks "Start Analysis" button
9. **Analysis Progress Modal** appears with steps:
   - Loading data ✓
   - Generating embeddings (3/15)
   - (Progress bar updates in real-time)
10. After 30-60 seconds, all steps complete ✓
11. **Success Screen** shows:
    - "5 clusters detected"
    - "2 PRIMARY, 3 SECONDARY"
    - "Archetype: Pragmatic Analytical Thinker"
12. User clicks "View Profile"
13. Navigates to **Profile Detail Screen** with new data

---

### Flow 3: Assign Archetype

1. User on **Profile Detail Screen**
2. Clicks "Assign Archetype" button
3. **Archetype Assignment Modal** opens
4. Shows current archetype: "Pragmatic Analytical Thinker"
5. Shows list of behaviors with checkboxes
6. PRIMARY behaviors are pre-checked
7. User unchecks one SECONDARY behavior
8. Clicks "Generate Archetype"
9. Loading spinner: "Generating archetype with AI..."
10. After 15 seconds, result appears:
    - "New: Detail-Oriented Systematizer"
11. User clicks "Accept and Save"
12. System calls POST `/assign-archetype`
13. Modal closes, profile refreshes with new archetype
14. Toast notification: "Archetype updated!"

---

### Flow 4: Copy LLM Context for AI Integration

1. Developer/user on **LLM Context Viewer Screen**
2. Reviews PRIMARY behaviors section
3. Reviews SECONDARY behaviors section
4. Reviews behavioral summary
5. Switches to "Markdown Format" tab in Copy Preview
6. Sees formatted markdown in code block
7. Clicks "Copy as Markdown" button
8. Toast: "Copied to clipboard!"
9. Developer pastes into AI assistant system prompt
10. AI assistant uses context to personalize responses

---

### Flow 5: Filter and Sort Behaviors

1. User on **Core Behaviors List Screen**
2. Sees table with all behaviors (PRIMARY + SECONDARY)
3. Changes filter to "PRIMARY only"
4. Table updates to show only PRIMARY tier
5. Changes sort to "Observation Count"
6. Table re-sorts with highest counts first
7. Clicks on first row
8. Row expands inline showing wording variations
9. User reviews variations
10. Clicks "View in Full Profile" link
11. Navigates to **Profile Detail Screen**, scrolls to that cluster

---

## States & Error Handling

### Global States

**1. Loading State**
- **Trigger**: Any API call in progress
- **Display**: Loading spinner or skeleton based on context
- **User Actions**: Disabled (buttons grayed out)

**2. Error State**
- **Trigger**: API call fails (4xx or 5xx response)
- **Display**: Error banner or modal with message
- **User Actions**: Retry button, back button, or close

**3. Empty State**
- **Trigger**: No data available (e.g., no profiles, no behaviors)
- **Display**: Empty state component with illustration
- **User Actions**: "Create First Analysis" or similar CTA

**4. Success State**
- **Trigger**: Action completes successfully
- **Display**: Toast notification or success screen
- **User Actions**: Continue to next screen or close

---

### Screen-Specific States

#### Profile Detail Screen

| State | Trigger | Display | Actions |
|-------|---------|---------|---------|
| Loading | Initial page load | Skeleton loading | None |
| Loaded | Data fetched | Full profile display | All interactions enabled |
| No Profile | 404 from API | "Profile not found" message | "Back to List" button |
| Re-analyzing | "Re-analyze" clicked | Loading overlay | Cancel button |
| Analysis Complete | Analysis finishes | Success modal | "View Updated Profile" |

#### Analysis Setup Screen

| State | Trigger | Display | Actions |
|-------|---------|---------|---------|
| Form Entry | Default | Input fields enabled | Fill form |
| Validating | "Start Analysis" clicked | Loading spinner | None |
| Analyzing | Validation passes | Progress modal | Cancel (if supported) |
| Success | Analysis complete | Success card | "View Profile" or "New Analysis" |
| Error | Analysis fails | Error modal | "Try Again" or "Cancel" |

#### LLM Context Viewer

| State | Trigger | Display | Actions |
|-------|---------|---------|---------|
| Loading | Initial load | Skeleton | None |
| Loaded | Data fetched | Full context display | Copy, download |
| Copied | "Copy" clicked | Toast: "Copied!" | Continue browsing |
| Error | API fails | Error message | "Retry" button |

---

### Error Messages

| Error Type | API Response | User Message | Actions |
|------------|--------------|--------------|---------|
| Profile Not Found | 404 | "No profile found for this user. Try running an analysis first." | "Run Analysis" button |
| Analysis Failed | 500 | "Analysis failed: [specific error]. Please try again." | "Retry" button |
| Network Error | N/A | "Unable to connect to server. Check your connection and try again." | "Retry" button |
| Validation Error | 400 | "Invalid input: [field] is required." | Highlight field |
| LLM Error | 500 | "AI service unavailable. Using fallback labeling." | Continue with fallback |
| Timeout | 504 | "Request timed out. The analysis may still be processing." | "Check Status" button |

---

## Responsive Behavior

### Desktop (≥ 1024px)

**Layout**:
- User list: 3-column grid
- Profile clusters: 2-column grid
- Full navigation sidebar visible
- Wide statistics bars

**Interactions**:
- Hover effects enabled
- Tooltips on hover
- Keyboard shortcuts active

---

### Tablet (768px - 1023px)

**Layout**:
- User list: 2-column grid
- Profile clusters: 1-column grid
- Collapsible navigation sidebar
- Stacked statistics bars

**Interactions**:
- Touch-optimized buttons (larger tap targets)
- Swipe gestures for navigation
- Reduced hover effects

---

### Mobile (< 768px)

**Layout**:
- User list: 1-column stack
- Profile clusters: 1-column stack
- Bottom navigation bar
- Vertical statistics stack

**Interactions**:
- Full-screen modals
- Swipe to collapse/expand sections
- Simplified navigation
- Larger font sizes

**Optimizations**:
- Lazy load data on scroll
- Simplified visualizations
- Truncate long text with "Show more"

---

## Accessibility

### Keyboard Navigation

- **Tab Order**: Logical top-to-bottom, left-to-right
- **Focus Indicators**: Visible outline on focused elements
- **Shortcuts**:
  - `Ctrl/Cmd + N`: New analysis
  - `Ctrl/Cmd + C`: Copy (when in context viewer)
  - `Esc`: Close modal
  - `Enter`: Confirm action
  - Arrow keys: Navigate lists

### Screen Readers

- **ARIA Labels**: All interactive elements labeled
- **Role Attributes**: Proper semantic HTML
- **Live Regions**: Announce loading/success/error states
- **Alt Text**: All icons/images have descriptive text

### Color Contrast

- **Minimum Ratio**: 4.5:1 for normal text, 3:1 for large text
- **Color-Blind Friendly**: Use icons + text, not color alone
- **Tier Badges**: Include icon + text (not just color)
- **Progress Bars**: Include percentage text (not just visual)

### Motion

- **Respect prefers-reduced-motion**: Disable animations if set
- **Smooth Animations**: Use ease-in-out, no jarring transitions
- **Loading Indicators**: Use animations but provide static fallback

---

## Data Display Rules

### Formatting Standards

**Timestamps**:
- Absolute: "Dec 27, 2025, 10:30 AM"
- Relative: "2 days ago" (for recent dates < 7 days)
- Format: User's locale settings

**Percentages**:
- Display: "85%" (whole numbers)
- Precision: Round to nearest integer for UI
- Tooltips: Show 2 decimal places (85.42%)

**Counts**:
- Small (< 1000): "15 observations"
- Large (≥ 1000): "1.2K observations"

**Text Truncation**:
- Canonical labels: Max 3 lines, then "..."
- Behavior variations: Max 2 lines in collapsed view
- Prompts: Max 2 lines with "Read more"

**Empty Values**:
- Missing archetype: "Not assigned"
- Zero observations: "No data" (not "0")
- Null confidence: "Unknown" (not blank)

---

### Data Refresh Strategy

**Auto-Refresh**:
- Health check: Every 30 seconds
- User list: Manual refresh only
- Profile detail: Manual refresh or after re-analysis

**Manual Refresh**:
- Refresh icon button in header
- Pull-to-refresh on mobile
- "Re-analyze" button for complete refresh

**Real-Time Updates**:
- Not implemented (future consideration)
- Show "Profile updated" toast if data changes

---

## Visual Design Guidelines

### Color Palette

**Primary Colors**:
- PRIMARY tier: Green (#22c55e)
- SECONDARY tier: Blue (#3b82f6)
- NOISE tier: Gray (#6b7280)

**Semantic Colors**:
- Success: Green (#10b981)
- Error: Red (#ef4444)
- Warning: Yellow (#f59e0b)
- Info: Blue (#3b82f6)

**Neutrals**:
- Background: White (#ffffff)
- Surface: Light gray (#f9fafb)
- Text: Dark gray (#1f2937)
- Border: Medium gray (#d1d5db)

---

### Typography

**Headings**:
- H1 (Page titles): 32px, bold
- H2 (Section headings): 24px, semibold
- H3 (Card headings): 18px, semibold

**Body Text**:
- Default: 16px, regular
- Small: 14px, regular
- Tiny: 12px, regular

**Special**:
- Code/Monospace: Consolas, Courier New
- Labels/Badges: 14px, medium, uppercase

---

### Spacing

**Padding**:
- Cards: 16px-24px
- Sections: 24px-32px
- Pages: 32px-48px

**Margins**:
- Between cards: 16px
- Between sections: 32px
- Between pages: 48px

**Grid Gaps**:
- Dense: 8px
- Normal: 16px
- Loose: 24px

---

### Shadows

**Elevation Levels**:
- Level 1 (Cards): `0 1px 3px rgba(0,0,0,0.1)`
- Level 2 (Modals): `0 4px 6px rgba(0,0,0,0.1)`
- Level 3 (Dropdowns): `0 10px 15px rgba(0,0,0,0.1)`

---

### Animation Timing

**Durations**:
- Fast: 150ms (hover effects)
- Normal: 300ms (transitions)
- Slow: 500ms (page transitions)

**Easing**:
- Default: ease-in-out
- Enter: ease-out
- Exit: ease-in

---

## Implementation Priority

### Phase 1: Core Views (MVP)
1. ✅ User List Dashboard (summary API)
2. ✅ Profile Detail Screen (full profile API)
3. ✅ Cluster Card Component
4. ✅ Basic navigation
5. ✅ Loading/error states

### Phase 2: Analysis Features
6. Analysis Setup Screen (analyze-and-save API)
7. Progress tracking modal
8. Archetype assignment (assign-archetype API)
9. Success/error handling

### Phase 3: Advanced Features
10. LLM Context Viewer (llm-context API)
11. Core Behaviors List (core-behaviors API)
12. Copy/download functionality
13. Advanced filtering/sorting

### Phase 4: Polish
14. User Summary Widget (summary API)
15. Health check indicator (health API)
16. Responsive mobile layouts
17. Accessibility enhancements
18. Animation polish

---

## Appendix: Example Screens

### Example 1: Profile Detail with PRIMARY Cluster Expanded

```
┌─────────────────────────────────────────────────────────────────┐
│  Profiles / User 102                                      [⚙️ ▼] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  🎭 Pragmatic Analytical Thinker                        │    │
│  │  Based on 3 behavior clusters from 15 observations     │    │
│  │                                                         │    │
│  │  [Re-analyze] [Assign Archetype] [View LLM Context]   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────┬──────────┬──────────┬──────────┐                 │
│  │ 📄 15    │ 🔗 8     │ 📅 45    │ 🕐 Dec   │                 │
│  │ Behaviors│ Clusters │ Days     │ 27, 2025 │                 │
│  └──────────┴──────────┴──────────┴──────────┘                 │
│                                                                  │
│  PRIMARY BEHAVIORS (3)                                          │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ [PRIMARY ⭐]                                            │    │
│  │                                                         │    │
│  │ Analytical Problem-Solving and Conceptual Thinking     │    │
│  │ Systematic Analysis and Logical Reasoning              │    │
│  │                                                         │    │
│  │ Strength: [████████████████████░░] 85%                 │    │
│  │ Confidence: [██████████████░░░░░░] 72%                 │    │
│  │                                                         │    │
│  │ 📊 12 observations • First: Dec 1 • Last: Dec 27       │    │
│  │ Active: 27 days                                        │    │
│  │                                                         │    │
│  │ ▼ Wording Variations (12)                              │    │
│  │ ┌──────────────────────────────────────────────────┐  │    │
│  │ │ • "I need to analyze the problem systematically" │  │    │
│  │ │   Dec 15, 2025                                   │  │    │
│  │ │                                                   │  │    │
│  │ │ • "I prefer breaking down complex issues step    │  │    │
│  │ │   by step"                                       │  │    │
│  │ │   Dec 18, 2025                                   │  │    │
│  │ │                                                   │  │    │
│  │ │ • "I approach challenges through logical         │  │    │
│  │ │   reasoning"                                     │  │    │
│  │ │   Dec 20, 2025                                   │  │    │
│  │ │                                                   │  │    │
│  │ │ ... (9 more) [Show All]                          │  │    │
│  │ └──────────────────────────────────────────────────┘  │    │
│  │                                                         │    │
│  │                             [Hide Evidence ▲]          │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ... (2 more PRIMARY clusters)                                  │
│                                                                  │
│  SECONDARY BEHAVIORS (5)                                        │
│  ... (collapsed cluster cards)                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Example 2: LLM Context Viewer

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Profile     LLM Context for User 102    [Copy] [⬇️]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ℹ️ This view is optimized for LLM consumption (~350 tokens)   │
│     For full details, view the complete profile.               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  🎭 Pragmatic Analytical Thinker                        │    │
│  │  User Personality Archetype                            │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  PRIMARY BEHAVIORS (3)                                          │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Analytical Problem-Solving                             │    │
│  │                                                         │    │
│  │  User consistently approaches problems through logical  │    │
│  │  analysis, breaking down complex issues into manageable │    │
│  │  components.                                            │    │
│  │                                                         │    │
│  │  [85% confidence] • 12 observations                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ... (2 more primary behaviors)                                 │
│                                                                  │
│  SECONDARY BEHAVIORS (5)                                        │
│  • Documentation Preference • 65% • 5 observations             │
│  • Iterative Refinement • 58% • 7 observations                 │
│  ... (3 more)                                                   │
│                                                                  │
│  BEHAVIORAL SUMMARY                                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  User exhibits strong analytical tendencies with        │    │
│  │  emphasis on systematic problem-solving. Secondary      │    │
│  │  traits include preference for detailed documentation   │    │
│  │  and iterative refinement. Overall communication style  │    │
│  │  is direct and focused on practical outcomes.          │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  COPY PREVIEW                                                   │
│  [JSON Format] [Markdown] [Plain Text]                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  {                                                      │    │
│  │    "user_id": "user_102",                               │    │
│  │    "archetype": "Pragmatic Analytical Thinker",         │    │
│  │    "primary_behaviors": [                               │    │
│  │      {                                                  │    │
│  │        "label": "Analytical Problem-Solving",          │    │
│  │        ...                                             │    │
│  │                                        [Copy to Clipboard]   │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary

This document provides a complete, technology-agnostic specification for the CBIE frontend UI. Every API endpoint has been mapped to specific UI locations and interactions. The design prioritizes:

- **Cluster-first visualization**: Aggregated patterns, not raw observations
- **Evidence transparency**: Drill-down capabilities for detail inspection
- **User-friendly interactions**: Clear CTAs, loading states, error handling
- **Token efficiency**: Specialized views for LLM integration
- **Accessibility**: Keyboard navigation, screen reader support, color contrast

Implementation teams can use this document as a blueprint to build the frontend interface in any technology stack.

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
