# CBIE System - Complete Frontend UI Specification (User-Facing)

**Last Updated:** December 27, 2025  
**Version:** 2.1 (Cluster-Centric, User-Facing Architecture)  
**Status:** Production-Ready Design

---

## Table of Contents

1. [Overview](#overview)
2. [User-Facing Architecture](#user-facing-architecture)
3. [Design Principles](#design-principles)
4. [Screen-by-Screen Specifications](#screen-by-screen-specifications)
5. [API-to-UI Mapping](#api-to-ui-mapping)
6. [Component Library](#component-library)
7. [User Flows](#user-flows)
8. [States & Error Handling](#states--error-handling)
9. [Responsive Behavior](#responsive-behavior)

---

## Overview

This document provides a complete, technology-agnostic specification for the CBIE frontend interface. The design is centered around the **cluster-centric architecture**, where behavior clusters (not individual observations) are the primary focus of visualization and interaction.

**IMPORTANT**: This system assumes user authentication is handled externally (e.g., via SSO, session management, or existing authentication system). All screens display data specific to the current authenticated user.

### Key Concepts for UI Design

- **Behavior Clusters**: Groups of similar observations that represent a consistent pattern
- **Tiers**: PRIMARY (strength ≥ 0.80), SECONDARY (strength ≥ 0.50), NOISE (< 0.50)
- **Canonical Label**: Short, LLM-generated summary of cluster meaning
- **Cluster Name**: Descriptive 3-6 word label for cluster
- **Archetype**: Overall personality label (e.g., "Pragmatic Analytical Thinker")
- **Wording Variations**: All different phrasings of the same behavior within a cluster
- **User Control**: Users can delete incorrect behaviors, hide clusters, configure settings

---

## User-Facing Architecture

### User Roles

**End User** (Primary Role):
- View their own behavior profile only
- Delete incorrect individual behaviors
- Hide specific clusters they don't want visible
- Report incorrectly detected behaviors
- Export their data
- Configure privacy and detection settings
- Pause/resume behavior detection
- Request profile deletion (GDPR)

**System** (Background):
- Automatically analyzes user interactions
- Generates behavior clusters
- Updates profiles when new data arrives
- Respects user's deletion/hide preferences

### Privacy & Data Ownership

- **Single Profile View**: Users see only their own data
- **User Control**: Full ability to delete/hide behaviors
- **Data Export**: Users can download all their data
- **Profile Deletion**: Users can permanently delete their profile
- **Transparency**: Clear indication of what's being tracked

---

## Design Principles

1. **User-Centric**: All screens show authenticated user's own data
2. **Correction Friendly**: Easy to delete incorrect behaviors
3. **Privacy First**: Clear controls for data management
4. **Cluster-First Display**: Show aggregated patterns, not raw observations
5. **Evidence Transparency**: Allow drill-down to view all observations in a cluster
6. **Progressive Disclosure**: Summary → Details → Evidence → Settings
7. **Confidence Visualization**: Use visual indicators (colors, badges, progress bars)
8. **Temporal Awareness**: Display when behaviors were first/last seen
9. **Accessibility**: Color-blind friendly, screen reader compatible, keyboard navigable
10. **No Technical IDs**: Never show database IDs to users

---

## Screen-by-Screen Specifications

**Note**: User authentication and session management are handled externally. All screens assume user is already authenticated and display data specific to the current user.

---

### 1. My Profile Screen (User-Specific)

**Purpose**: View user's own complete behavior profile

**API Used**: GET `/api/v1/profile/me`

#### Layout Description

**Header Section**
- Breadcrumb: "My Profile" (no user ID visible)
- Profile header:
  - Avatar/icon placeholder
  - Greeting: "Your Behavioral Profile"
- Archetype display:
  - Icon: 🎭
  - Label: "Pragmatic Analytical Thinker"
  - Subtitle: "Based on 3 behavior clusters from 15 observations"
- Action buttons (right-aligned):
  - "Settings" button (⚙️)
  - "Export Data" button (⬇️)
  - "More" dropdown:
    - "View LLM Context"
    - "Pause Detection"
    - "Help & Support"

**Summary Statistics Bar**
- Four stat cards:
  1. **Observations**: "15 behaviors tracked"
  2. **Clusters**: "8 patterns detected"
  3. **Time Span**: "45 days of data"
  4. **Last Updated**: "2 hours ago"

**PRIMARY BEHAVIORS Section**
- Section heading: "Your Core Behaviors (3)"
- Information banner:
  - "These are your strongest behavioral patterns. If any seem incorrect, you can delete specific observations or hide entire clusters."
- Grid of cluster cards (see updated cluster card component below)

**SECONDARY BEHAVIORS Section**
- Section heading: "Secondary Patterns (5)"
- Similar grid of cluster cards

**NOISE/OUTLIERS Section** (collapsible, collapsed by default)
- Section heading: "Outliers (2)"
- Info tooltip: "These behaviors appear only once or inconsistently"
- When expanded: Show cluster cards with gray badges

**Empty States**
- No PRIMARY behaviors:
  - Illustration
  - Message: "You don't have any strong behavior patterns yet"
  - Subtext: "Keep using the system and we'll detect patterns over time"
- No behaviors at all:
  - Welcome message
  - "Your behavior profile is empty. Start interacting to see insights!"

**Visual Changes for User-Facing**
- Remove any admin controls
- Add user action buttons (delete, hide, report)
- Show privacy-friendly language ("Your data", "Your patterns")
- Add help tooltips throughout

---

### 3. Cluster Card Component (Updated with User Controls)

**Purpose**: Display a single cluster with user control options

#### Extended Visual Elements

All previous elements PLUS:

**User Control Menu** (top-right corner, three-dot menu icon)
- "Hide this cluster" option
- "Report incorrect detection" option
- "Help" option (explains what cluster means)

**Wording Variations List** (when expanded)
- Each variation shows:
  - Behavior text (2 lines max)
  - Timestamp (relative, e.g., "2 days ago")
  - **Delete button** (🗑️ or "×" icon) on hover
    - Appears on right side of each variation
    - Hover tooltip: "Delete this observation"
    - Click → Show confirmation modal

**Confirmation Modal** (when delete clicked)
- Heading: "Delete this behavior?"
- Behavior text displayed
- Warning: "This action cannot be undone. Your profile will be automatically recalculated."
- Buttons:
  - "Cancel" (secondary)
  - "Delete" (danger, red)

**States**
- Default: Collapsed
- Expanded: Shows variations with delete buttons
- Deleting: Loading spinner on delete button
- Deleted: Behavior fades out, toast notification "Behavior deleted"
- Hidden: Cluster removed from view (can unhide from settings)

**Interactions**
- Click three-dot menu → Show dropdown:
  - Click "Hide this cluster" → Confirm → Call hide API → Cluster disappears
  - Click "Report incorrect" → Open report modal
- Click "View Evidence" → Expand to show variations
- Hover over variation → Show delete button
- Click delete on variation → Show confirmation modal
- Confirm delete → Call DELETE `/profile/me/behaviors/{id}` → Remove from list

**Report Modal** (when "Report incorrect" clicked)
- Heading: "Report Incorrect Detection"
- Cluster name shown
- Reason dropdown:
  - "This doesn't represent my behavior"
  - "This is someone else's behavior"
  - "This is offensive or inappropriate"
  - "Other"
- Comment text area (optional)
- Submit button
- Cancel button

---

### 2. Settings Screen

**Purpose**: Manage user preferences and privacy settings

**API Used**: GET/PUT `/api/v1/profile/me/settings`

#### Layout Description

**Header**
- Page title: "Profile Settings"
- Breadcrumb: "My Profile / Settings"

**Sidebar Navigation** (left side)
- "General"
- "Privacy"
- "Data & Export"
- "Account"

**Main Content Area** (changes based on sidebar selection)

**General Tab**
- Section: Behavior Detection
  - Toggle: "Automatic behavior detection"
    - Description: "System analyzes your interactions to detect patterns"
    - Status: ON/OFF
  - Button: "Pause Detection" (if ON)
    - When paused: Shows resume button and pause start time
- Section: Notifications
  - Checkbox: "Notify when new cluster detected"
  - Checkbox: "Notify when archetype updates"
  - Dropdown: Notification method (Email/In-app/Both)

**Privacy Tab**
- Section: Data Collection
  - Radio buttons:
    - ○ Minimal (store only PRIMARY, 90 days)
    - ● Balanced (PRIMARY + SECONDARY, 1 year) [default]
    - ○ Detailed (all behaviors, indefinite)
- Section: Archetype Generation
  - Toggle: "Allow AI to generate personality archetypes"
  - Description: "Uses LLM to create labels like 'Analytical Thinker'"
- Section: Hidden Clusters
  - List of clusters user has hidden
  - Each row:
    - Cluster name
    - "Unhide" button
  - Empty state: "No hidden clusters"

**Data & Export Tab**
- Section: Export Your Data
  - Dropdown: Format (JSON/PDF/CSV)
  - Checkboxes:
    - ☑ Include all observations
    - ☑ Include clusters
    - ☑ Include settings
    - ☑ Include action history
  - "Export Data" button (primary)
  - Last export: "Dec 20, 2025"
- Section: Data Retention
  - Display: "Your data has been stored for 45 days"
  - Information: "Data older than [retention period] is automatically deleted"

**Account Tab**
- Section: Account Information
  - Email: user@example.com (read-only)
  - Account created: Dec 1, 2025
  - Button: "Change Password"
- Section: Danger Zone (red border)
  - Warning icon
  - Heading: "Delete Your Profile"
  - Description: "Permanently delete all your behavior data. This cannot be undone."
  - Button: "Delete My Profile" (danger, red)

**Delete Profile Modal** (when clicked)
- Large warning icon
- Heading: "Are you absolutely sure?"
- Text: "This will permanently delete:"
  - All your behavior observations
  - Your behavior clusters
  - Your archetype
  - Your settings
  - All associated data
- Text: "This action cannot be undone"
- Confirmation input:
  - "Type DELETE to confirm"
  - Text input (must type "DELETE" exactly)
- Buttons:
  - "Cancel" (secondary)
  - "Delete Forever" (danger, disabled until "DELETE" typed)

**Interactions**
- Toggle switches → Auto-save on change, show toast "Settings saved"
- Click "Export Data" → Call export API → Download file
- Click "Delete My Profile" → Show confirmation modal
- Confirm deletion → Call DELETE `/profile/me` → Logout → Show "Profile deleted" screen

---

### 3. LLM Context Viewer Screen (User-Specific)

**Purpose**: View token-efficient profile data (for advanced users)

**API Used**: GET `/api/v1/profile/me/llm-context`

#### Layout Description

**Header**
- Page title: "LLM Context"
- Subtitle: "Your profile optimized for AI assistants"
- Breadcrumb: "My Profile / LLM Context"
- Information banner:
  - "This is a simplified version of your profile designed for AI assistants. Copy this text to give AI tools context about your behavior patterns."
- Token count badge: "~350 tokens"
- Action buttons:
  - "Copy as JSON"
  - "Copy as Markdown"
  - "Copy as Plain Text"
  - "Back to Profile"

**Content Display**
- Same structure as admin version, but:
  - Header text: "Your Behavioral Context"
  - Language: "You exhibit..." instead of "User exhibits..."
  - Privacy note: "This data is for your use only. Share carefully."

**Visual Design**
- Clean, readable layout
- Code blocks for copyable text
- Syntax highlighting for JSON
- Copy buttons with success feedback

---

### 4. Data Export Screen

**Purpose**: Download user's complete data

**API Used**: POST `/api/v1/profile/me/export`

#### Layout Description

**Header**
- Page title: "Export Your Data"
- Subtitle: "Download a complete copy of your behavior profile"

**Export Options**
- Format selection:
  - Radio buttons: JSON / PDF / CSV
  - Each shows preview icon
- Content selection:
  - ☑ Behavior observations (15 items)
  - ☑ Behavior clusters (8 items)
  - ☑ Settings & preferences
  - ☑ Analysis history
  - ☑ Action log (deletions, hides)
- Button: "Generate Export" (primary)

**Export Status**
- Progress bar (when generating)
- Messages:
  - "Preparing your data..."
  - "Generating file..."
  - "Ready for download!"
- Download button appears when ready

**Previous Exports List**
- Table showing:
  - Date exported
  - Format
  - File size
  - "Download Again" link
- Keep last 5 exports

---

### 5. Pause Detection Screen

**Purpose**: Temporarily pause behavior tracking

**API Used**: PUT `/api/v1/profile/me/pause`

#### Layout Description

**Modal or Dedicated Page**
- Heading: "Pause Behavior Detection"
- Explanation:
  - "While paused, the system will not analyze your interactions or detect new behaviors."
  - "Your existing profile will remain intact."
- Checkbox: "I understand my profile won't be updated while paused"
- Buttons:
  - "Cancel"
  - "Pause Detection"

**Paused State Indicator**
- Banner at top of profile screen:
  - ⏸️ Icon
  - Text: "Behavior detection is currently paused"
  - Paused since: "Dec 27, 10:30 AM"
  - Button: "Resume Detection"

---

## API-to-UI Mapping (Updated for User-Facing)

### Complete API Coverage

| API Endpoint | HTTP Method | UI Location(s) | User Action | Data Displayed |
|--------------|-------------|----------------|-------------|----------------|
| **User Profile** |
| `/api/v1/profile/me` | GET | My Profile Screen | User views profile | Complete behavior profile |
| `/api/v1/profile/me/llm-context` | GET | LLM Context Viewer | User views AI context | Token-efficient profile |
| `/api/v1/profile/me/summary` | GET | Profile widget/header | Auto-refresh | Quick stats |
| **Behavior Management** |
| `/api/v1/profile/me/behaviors/{id}` | DELETE | Cluster Card > Variation | User deletes behavior | Success/re-analysis notice |
| `/api/v1/profile/me/behaviors/{id}/report` | POST | Cluster Card > Report modal | User reports incorrect | Ticket confirmation |
| `/api/v1/profile/me/clusters/{id}/hide` | PUT | Cluster Card > Hide option | User hides cluster | Confirmation, cluster hidden |
| `/api/v1/profile/me/clusters/{id}/unhide` | PUT | Settings > Hidden clusters | User unhides cluster | Cluster visible again |
| **Settings & Privacy** |
| `/api/v1/profile/me/settings` | GET | Settings Screen | User opens settings | All preferences |
| `/api/v1/profile/me/settings` | PUT | Settings Screen | User changes setting | Settings saved confirmation |
| `/api/v1/profile/me/export` | POST | Data Export Screen | User exports data | Download file |
| `/api/v1/profile/me` | DELETE | Settings > Delete Profile | User deletes account | Deletion confirmation |
| `/api/v1/profile/me/pause` | PUT | Settings / Profile header | User pauses tracking | Paused status |
| `/api/v1/profile/me/resume` | PUT | Paused banner | User resumes tracking | Active status |
| **Public** |
| `/api/v1/health` | GET | Header status indicator | Auto-poll | System status |

### User Flow Example

**Correcting Incorrect Behavior**:
1. User sees their profile (GET `/profile/me`)
2. Expands a cluster to view variations
3. Sees behavior that's wrong: "I like pineapple on pizza" 
4. Hovers over it, sees delete button
5. Clicks delete button
6. Modal asks: "Delete this behavior?"
7. User confirms
8. API called: DELETE `/profile/me/behaviors/beh_456`
9. Behavior fades out, toast: "Behavior deleted. Profile recalculating..."
10. Background re-analysis triggered
11. Profile refreshes automatically (websocket or polling)
12. Updated clusters displayed

---

## Component Library (Updated)

### 1. Cluster Card Component (with User Controls)

**Props/Data**:
- cluster_id
- canonical_label
- cluster_name
- tier
- cluster_strength
- confidence
- cluster_size
- wording_variations (array with delete capability)
- is_hidden (boolean)
- isExpanded (state)

**New UI Elements**:
- **Three-dot menu** (top-right)
  - Hide cluster
  - Report incorrect
  - Help/info
- **Delete buttons** on each wording variation
  - Appears on hover
  - Trash icon or "×"
  - Tooltip: "Delete this observation"
- **Confirmation modal** (for deletions)

**User Interactions**:
- Click three-dot menu → Show options
- Click "Hide" → Confirm → Hide cluster
- Click delete on variation → Show confirmation
- Confirm → API call → Remove from UI

---

### 2. User Control Button Component (New)

**Purpose**: Standardized button for user actions (delete, hide, report)

**Variants**:
- Delete (red, trash icon)
- Hide (gray, eye-off icon)
- Report (yellow, flag icon)
- Unhide (green, eye icon)

**Props**:
- action (delete/hide/report/unhide)
- onConfirm (callback)
- confirmationText (modal text)

**Behavior**:
- Click → Show confirmation modal (if destructive)
- Confirm → Execute action + show loading
- Success → Show toast notification

---

### 3. Privacy Control Component (New)

**Purpose**: Display privacy-related settings

**Visual**:
- Shield icon
- Setting name
- Toggle or radio buttons
- Description text
- "Saved" indicator when changed

---

### 4. Data Export Card Component

**Purpose**: Show export options and status

**Elements**:
- Format selector
- Content checkboxes
- Export button
- Progress indicator
- Download link (when ready)

---

## User Flows (Updated for User-Facing)

**Note**: User authentication is handled externally. All flows assume user is already authenticated and has an active session.

---

### Flow 1: User Deletes Incorrect Behavior

1. User logged in, viewing **My Profile Screen**
2. Sees PRIMARY cluster: "Documentation Preference"
3. Clicks "View Evidence" → Expands cluster
4. Sees 5 wording variations listed
5. Spots incorrect one: "I hate reading docs" (wrong!)
6. Hovers over it → Delete button (🗑️) appears
7. Clicks delete button
8. **Confirmation Modal** appears:
   - "Delete this behavior?"
   - Shows behavior text
   - Warning about recalculation
9. User clicks "Delete" (red button)
10. API: DELETE `/profile/me/behaviors/beh_123`
11. Modal closes, delete button shows spinner
12. Success response:
    - Behavior fades out of list
    - Toast notification: "Behavior deleted. Recalculating profile..."
13. Background: System triggers re-analysis (excludes deleted behavior)
14. Profile cluster card shows "Updating..." badge
15. After 3-5 seconds, cluster updates:
    - Cluster size: 5 → 4
    - Strength/confidence may change
    - List refreshes without deleted behavior
16. Toast: "Profile updated!"

---

### Flow 2: User Hides Entire Cluster

1. User on **My Profile Screen**
2. Sees SECONDARY cluster: "Late Night Work Patterns"
3. Thinks: "This is private, I don't want this visible"
4. Clicks three-dot menu on cluster card
5. Dropdown shows:
   - "Hide this cluster"
   - "Report incorrect detection"
   - "Help"
6. Clicks "Hide this cluster"
7. **Confirmation Modal**:
   - "Hide this cluster from your profile?"
   - "You can unhide it anytime from Settings"
8. User clicks "Hide"
9. API: PUT `/profile/me/clusters/2/hide`
10. Success response:
    - Cluster card fades out with animation
    - Toast: "Cluster hidden. View hidden clusters in Settings"
    - Profile statistics update (SECONDARY count: 5 → 4)
11. User can unhide later from **Settings Screen**

---

### Flow 3: User Exports Their Data (GDPR)

1. User on **My Profile Screen**
2. Clicks "Export Data" button in header
3. Navigates to **Data Export Screen**
4. Sees export options:
   - Format: JSON selected by default
   - All content checkboxes checked
5. Clicks "Generate Export"
6. API: POST `/profile/me/export`
7. Progress bar shows:
   - "Preparing your data..." (30%)
   - "Generating file..." (60%)
   - "Ready for download!" (100%)
8. "Download" button appears
9. User clicks download
10. Browser downloads: `user_123_profile_2024-12-27.json`
11. File contains:
    - Complete profile with all clusters
    - All observations (including deleted ones)
    - Settings
    - Action history
12. Export added to "Previous Exports" list
13. Toast: "Data exported successfully!"

---

### Flow 4: User Pauses and Resumes Detection

**Pause:**
1. User on **My Profile Screen**
2. Clicks "Settings" button
3. Navigates to **Settings Screen** → General tab
4. Sees toggle: "Automatic behavior detection" (ON)
5. Clicks "Pause Detection" button
6. **Confirmation Modal**:
   - "Pause behavior detection?"
   - "No new behaviors will be detected while paused"
7. User clicks "Pause"
8. API: PUT `/profile/me/pause`
9. Success:
   - Toggle switches to OFF
   - Button changes to "Resume Detection"
   - Toast: "Detection paused"
10. Banner appears at top of profile:
    - ⏸️ "Behavior detection is currently paused since 10:30 AM"
    - "Resume Detection" button

**Resume:**
1. User sees paused banner
2. Clicks "Resume Detection"
3. API: PUT `/profile/me/resume`
4. Success:
   - Banner disappears
   - Settings toggle: OFF → ON
   - Toast: "Detection resumed"
5. System starts analyzing new interactions again

---

### Flow 5: User Deletes Their Profile (GDPR Right to be Forgotten)

1. User on **Settings Screen**
2. Scrolls to bottom → "Danger Zone" section
3. Reads warning about permanent deletion
4. Clicks "Delete My Profile" (red button)
5. **Confirmation Modal** (large, scary):
   - Red warning icon
   - "Are you absolutely sure?"
   - Lists everything that will be deleted
   - "This cannot be undone"
   - Input field: "Type DELETE to confirm"
6. User types "DELETE" (exact match required)
7. "Delete Forever" button enables
8. User clicks "Delete Forever"
9. API: DELETE `/profile/me`
10. Response:
    - `deletion_id` provided
    - Grace period: 30 days
11. Modal shows:
    - "Profile deletion scheduled"
    - "Will be permanently deleted by: [date]"
    - "You have 30 days to cancel"
12. User automatically logged out
13. Redirected to "Profile Deleted" page:
    - Confirmation message
    - Link to cancel deletion (if within grace period)
    - Contact support link
14. Email sent to user confirming deletion request

---

## States & Error Handling

**Note**: Authentication is handled externally. This section covers application states after user is authenticated.

### Profile States

| State | Trigger | Display | User Action |
|-------|---------|---------|-------------|
| Loading | Initial page load | Skeleton loading | Wait |
| Loaded | Data fetched | Full profile | Interact |
| Empty Profile | No behaviors yet | Welcome message | Continue using system |
| Paused Detection | User paused | Banner with resume button | Resume or continue |
| Recalculating | Behavior deleted | "Updating..." badge | Wait (3-5s) |

### User Action States

| Action | In-Progress | Success | Error |
|--------|-------------|---------|-------|
| Delete Behavior | Spinner on button | Fade out + toast | Error message + retry |
| Hide Cluster | Loading overlay | Fade out animation | Error banner |
| Export Data | Progress bar | Download ready | "Export failed" + retry |
| Delete Profile | Modal spinner | Logout + confirmation | Error modal |

### Error Messages (User-Friendly)

| Error Type | Technical Message | User Message | Action |
|------------|-------------------|--------------|--------|
| Behavior Not Found | 404 Not Found | "This behavior no longer exists" | Refresh page |
| Already Deleted | 409 Conflict | "You already deleted this behavior" | Refresh |
| Rate Limited | 429 Too Many Requests | "Slow down! Try again in a minute" | Wait |
| Server Error | 500 Internal | "Something went wrong. We're fixing it!" | Retry / contact support |
| Network Error | N/A | "Check your internet connection" | Retry |

---

## Responsive Behavior

### Mobile Optimizations

**Profile View**:
- Single column layout
- Swipe to delete behaviors (like email apps)
- Bottom sheet for three-dot menus
- Floating action button for settings

**Settings**:
- Accordion-style sections (collapse/expand)
- Full-screen modals for confirmations
- Touch-optimized toggles and sliders

### Tablet Optimizations

**Profile View**:
- Two-column cluster grid
- Sidebar for quick navigation
- Split view: profile + settings

---

## Accessibility (Enhanced for Users)

### Screen Reader Support

**Important Announcements**:
- "Behavior deleted. Profile recalculating"
- "Detection paused. No new behaviors will be tracked"
- "Cluster hidden from view"
- "Settings saved successfully"

**ARIA Labels**:
- Delete buttons: "Delete [behavior text]"
- Hide buttons: "Hide [cluster name]"
- Settings toggles: "Automatic detection [ON/OFF]"

### Keyboard Navigation

**Shortcuts**:
- `Ctrl/Cmd + S`: Open settings
- `Ctrl/Cmd + E`: Export data
- `Del`: Delete focused behavior (with confirmation)
- `Esc`: Close modal
- `Enter`: Confirm action

**Focus Management**:
- Delete button appears on keyboard focus (not just hover)
- Modal focus trap (can't tab out)
- Return focus after modal close

---

## Privacy & Trust Indicators

### Visual Trust Elements

**Throughout UI**:
- 🔒 Lock icon next to "Your data is private"
- ✅ "GDPR Compliant" badge in footer
- 🛡️ Privacy-first messaging
- 📊 "You control your data" banners

**Profile Screen**:
- "Only you can see this" indicator
- "Last updated [time]" with data freshness
- "X behaviors tracked" with "Delete All" option (advanced)

**Settings Screen**:
- Privacy level clearly labeled (Minimal/Balanced/Detailed)
- Data retention period displayed
- "Export anytime" messaging
- "Delete profile" always accessible

---

## Summary of User-Facing Changes

### New Screens

1. ✅ Login Screen
2. ✅ Registration Screen
3. ✅ Welcome/Onboarding (4 steps)
4. ✅ Settings Screen (4 tabs)
5. ✅ Data Export Screen
6. ✅ Pause Detection Modal

### Updated Screens

1. ✅ My Profile (was "Profile Detail") - Now user-specific
2. ✅ LLM Context Viewer - User-scoped
3. ✅ Cluster Cards - Added delete/hide/report controls

### Removed Screens

1. ❌ User List Dashboard - Not needed (users see only their own profile)
2. ❌ Analysis Setup Screen - Happens automatically in background
3. ❌ Archetype Assignment Screen - Automated, no manual trigger needed

### Key User Features

**Behavior Correction**:
- ✅ Delete individual observations
- ✅ Hide entire clusters
- ✅ Report incorrect detections

**Privacy Controls**:
- ✅ Pause/resume detection
- ✅ Configure data retention
- ✅ Export complete data
- ✅ Delete profile (GDPR)

**Settings**:
- ✅ Privacy levels (Minimal/Balanced/Detailed)
- ✅ Notification preferences
- ✅ View hidden clusters
- ✅ Unhide clusters

---

## Implementation Priority (User-Facing)

### Phase 1: Authentication & Core Profile (Weeks 1-2)
1. ✅ Login/Registration screens
2. ✅ My Profile screen (read-only)
3. ✅ JWT authentication
4. ✅ Basic navigation

### Phase 2: User Controls (Weeks 3-4)
5. ✅ Delete behavior functionality
6. ✅ Hide cluster functionality
7. ✅ Report incorrect behavior
8. ✅ Settings screen (basic)

### Phase 3: Privacy Features (Weeks 5-6)
9. ✅ Data export
10. ✅ Pause/resume detection
11. ✅ Profile deletion
12. ✅ Privacy settings

### Phase 4: Polish & Onboarding (Weeks 7-8)
13. ✅ Welcome/onboarding flow
14. ✅ Help tooltips
15. ✅ Empty states
16. ✅ Error handling refinement

---

**End of User-Facing UI Specification**

This document provides complete specifications for building a user-facing behavior profile system where each user can view and manage their own data with full privacy controls and correction capabilities.
