# Deadwood Tournament Leaderboard — Project Documentation

## Overview

This document describes the **Deadwood Tournament Leaderboard**, a real-time scoreboard for Sandbox VR's tournament events. The first event is scheduled for **April 24, 2026** at **The Battery, Atlanta** with a **$10,000 USD prize pool**.

The current deliverable is a **standalone HTML file** (`leaderboard.html`) that renders a fully functional leaderboard UI with mock data. The next phase is to connect it to live data from **Grafana Cloud** via a serverless backend.

---

## Tournament Format

### Qualifying Round (Daytime)
- All registered teams play **one session** of Deadwood Valley Tournament Mode
- Teams are ranked by `team[0].score` (teamScore + bonusScore)
- Top 4 teams advance to Finals

### Finals (Evening)
- Best of 4 teams play **simultaneously**
- Ranked 1st–4th on the spot
- Prize distribution: $5,000 / $2,500 / $1,500 / $1,000

### Team Composition
- 4 players per team
- Game: **Deadwood Valley** (Tournament Mode)
- Team names and player names come from the game log

---

## Current State of `leaderboard.html`

### What It Is
A **single, self-contained HTML file** with:
- All CSS inline in `<style>`
- All JS inline in `<script>`
- Deadwood Valley logo embedded as base64 data URI
- Mock data hardcoded in a `var DATA = {...}` JavaScript object
- **No external dependencies** except Google Fonts fallback (works offline)

### iOS Safari Compatibility
The file is designed to be AirDropped to iPhones and opened locally. All code follows these constraints:
- **No `const` / `let`** — all variables use `var`
- **No arrow functions** — all functions use `function()` syntax
- **No template literals** — all strings use concatenation
- **No inline `onclick`** — all events use `addEventListener`
- **`DOMContentLoaded`** wraps all init code
- **`-webkit-` prefixes** on animations and flexbox

### Design System
The UI uses **Sandbox VR's design tokens** from the private repo `github.com/SandboxVR/ui`. Key tokens applied:

#### Colors (Dark Theme)
```
Surface base:    #11161d  (--surface-base)
Surface body:    #19202a  (--surface-body)
Surface alt:     #202936  (--surface-alt)
Text full:       #ffffff  (--text-full)
Text high:       #c9d2dc  (--text-high)
Text medium:     #a9b3c1  (--text-medium)
Text low:        #8895a7  (--text-low)
Text disabled:   #4b5c71  (--text-disabled)
Brand cyan:      #03b2cb  (--brand-cyan)
Brand red:       #f4250e  (--brand-red-500)
Player red:      #e43838  (--player-red)
Player blue:     #41b5eb  (--player-blue)
Player green:    #31a868  (--player-green)
Player yellow:   #f5b31b  (--player-yellow)
Border:          #2d3846  (--border-color)
Gold:            #f5b31b  (--gold)
Silver:          #a9b3c1  (--silver)
Bronze:          #cd7f32  (--bronze)
Success green:   #2ebd37  (--qualified-green)
```

#### Typography
- Primary font: `Gordita` (Sandbox VR's custom font, licensed — not publicly available)
- Fallback: `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- Typography scale follows Sandbox VR's token system (h4, body1, body2, caption, overline)

#### Full Token Reference
The complete design token files are in the uploaded zip `ui-master.zip`:
- `packages/react/src/styles/tokens/primitive.css` — all primitive colors
- `packages/react/src/styles/tokens/semantic.css` — semantic color mapping for light/dark themes
- `packages/react/src/styles/tokens/typography.css` — font faces and typography utilities

### UI Components

#### Header
- **"Deadwood Tournament"** badge in cyan
- **Deadwood Valley logo** (base64 embedded, uses `mix-blend-mode: lighten` to blend black background with page)
- Cyan gradient line separator

#### Stats Bar
- Teams Played (count)
- High Score (top team score)
- Most Kills (top individual player name)

#### Leaderboard (Qualifying View)
Each team row shows:
- Rank number (1–3 get gold/silver/bronze colored left border + rank number)
- Team name (uppercase)
- Player names (dot-separated)
- Total score (`team.score`)
- Deaths count + result text

**Top 3 teams are expanded by default** showing details.

#### Team Details (Expandable)
Click any team row to toggle details. Contains:

**Player Cards** (4 per team, grid layout):
- Player name + weapon type
- Score, Kills, Accuracy%, Deaths
- MVP badge (star icon, gold) for the MVP player
- Colored top border matching player color (red/blue/green/yellow)

**Wave Progress Timeline**:
- 10 dots (W1–W10) connected by lines
- Each dot shows: cumulative score, wave label, per-wave score delta (+amount)
- Horizontally scrollable on mobile

#### Finals View (Currently Hidden)
- 4 cards showing rank, team name, score, prize amount
- Winner card has gold border + glow

#### Refresh Indicator
- "Auto-refresh in Xs" countdown (15-second cycle, currently cosmetic)

---

## Data Structure

### Current Mock Data Format (`var DATA`)

```javascript
var DATA = {
  qualifying: [
    {
      name: "Team Name",        // STRING — from log: team[0].name
      score: 1261552,           // INTEGER — from log: team[0].score (teamScore + bonusScore)
      result: "BothSurvived",   // STRING — from log: team[0].result
      deaths: 7,                // INTEGER — sum of all players' deaths
      waveScore: [67589, ...],  // ARRAY[10] — from log: team[0].waveScore[].Score
      players: [
        {
          name: "Player_Name",  // STRING — from log: members[].name
          score: 314929,        // INTEGER — from log: members[].score
          weapon: "Machine",    // STRING — from log: members[].weapon
          kills: 196,           // INTEGER — from log: members[].totalKills
          accuracy: 42.5,       // FLOAT — from log: members[].accuracy
          deaths: 2,            // INTEGER — from log: members[].death
          mvp: true,            // BOOLEAN — from log: members[].mvp
          color: "red"          // STRING — from log: members[].character
        },
        // ... 3 more players (4 total per team)
      ]
    },
    // ... more teams, sorted by score descending
  ],
  finals: [
    {
      name: "Team Name",       // STRING
      score: 1305200,          // INTEGER — finals round score
      prize: "$5,000"          // STRING — prize amount
    },
    // ... 3 more teams (4 total)
  ]
};
```

### Source Log Format (Unity Game Log from Grafana Cloud)

The raw log from the game contains a JSON object with `team` array and `members` array. Key field mappings:

| Leaderboard Field | Log Field | Notes |
|---|---|---|
| `name` (team) | `team[0].name` | Team name set in game |
| `score` (team) | `team[0].score` | = teamScore + bonusScore |
| `result` | `team[0].result` | "BothSurvived", "OneSurvived", "NoneSurvived" |
| `deaths` (team) | Sum of `members[].death` | NOT `team[0].death` (that field means something else) |
| `waveScore` | `team[0].waveScore[].Score` | Array of 10 integers |
| `name` (player) | `members[].name` | Player name set in game |
| `score` (player) | `members[].score` | Individual score |
| `weapon` | `members[].weapon` | "Machine", "Rifle", "Shotgun", "DesertEagle" |
| `kills` | `members[].totalKills` | Total enemy kills |
| `accuracy` | `members[].accuracy` | Float, percentage |
| `deaths` (player) | `members[].death` | Individual death count |
| `mvp` | `members[].mvp` | Boolean |
| `color` | `members[].character` | "red", "blue", "green", "yellow" |

### Data Integrity Rule
**CRITICAL: Only display data that exists in the log. Never fabricate, infer, or hardcode data that isn't present in the source.** For example:
- Don't label specific waves as "boss waves" unless the log says so
- Don't show combo data per wave if the log only has team-level combo
- Team deaths = sum of player deaths, NOT `team[0].death`

### Available but Unused Log Fields
These fields exist in the log but are not currently displayed. They can be added to the UI if needed:

**Team level:**
- `teamScore` / `bonusScore` (score breakdown)
- `rating` (1-5 star rating)
- `gameMode` (e.g. "nightmare")
- `teamCombo` / `maxTeamCombo`
- `gameTime` / `tutorialTime` (in seconds)
- `playersDiedInWave1` through `playersDiedInWave10`
- `wrathWeakpointBrokenCount`, `wrathKilledByPlayer`, `wrathKilledByFailsafe`
- Boss damage fields: `damageToBill`, `damageToJason`, `damageToRachel`, `damageToAlbert`, `damageToBeth`
- Boss saved fields: `billSaved`, `jasonSaved`, etc.

**Player level:**
- `damageDealt` / `damageTaken`
- `shots` / `shotHits` / `headshots`
- `accuracyGrade` ("A", "B", "C")
- `manualReloads` / `autoReloads`
- `kill[]` — breakdown by enemy type (enemy, vulture, leaper, zombieDog, brute, wrath)
- `damageBoss` / `damageBrute` / `damageWrath`
- `weaponRedeemedType`

---

## Architecture — Next Phase: Live Data

### Target Architecture
```
Unity Game (Store PC)
    → Game ends, log uploaded to Grafana Cloud
        → Serverless Function (Cloudflare Workers / Vercel Edge)
            → Calls Grafana Cloud API (LogQL query)
            → Parses log JSON, extracts team/player data
            → Returns sorted leaderboard JSON
                → Leaderboard Web App (polls every 10-15 seconds)
                    → Displayed on Store TV (big screen) + Player phones (QR code)
```

### Recommended Hosting
- **Frontend**: Cloudflare Pages or Vercel (free, zero maintenance, static deploy)
- **Backend**: Cloudflare Workers or Vercel Edge Function (serverless, proxies Grafana API)

### Blockers Before Going Live
1. **Grafana Cloud API key** — Need Kelvin / Hanks to provide a read-only API key
2. **Tournament mode filter** — Need Steven / Isaac to confirm how tournament mode logs are distinguished from regular game logs (is it a different `gameMode` value? A separate field?)
3. **Store identifier** — Need to filter logs to only The Battery (and later The Interlock for practice)

### Integration Steps
1. Replace `var DATA = {...}` with a `fetchData()` function that calls the backend API
2. Backend calls Grafana Cloud API with LogQL query filtering for:
   - Specific store(s)
   - Tournament mode games only
   - Date range of the event
3. Backend parses raw log JSON → transforms to the `DATA` format above → returns JSON
4. Frontend polls backend every 10-15 seconds and re-renders

---

## Practice Phase (Pre-Tournament)

Starting **April 2, 2026**, the Deadwood Valley Tournament Mode launches at:
- **The Interlock** (Atlanta)
- **The Battery** (Atlanta)

The leaderboard can be deployed early as a **practice leaderboard** to build hype and let teams see how they rank before the actual tournament.

---

## Team & Ownership

### Sandbox VR Executive Team
- **Steve Zhao** — Founder & CEO
- **Kimkind Yeung** — SVP, Product & Technology (owns this project)
- **Michael Hampden** — SVP, Content
- **Aylang Lou** — SVP, Stores
- **Elaine Kwan** — Senior Director, Finance & Accounting
- **Matthew Kellie** — SVP, Marketing
- **Adam Hilliard** — VP, People & Workplace Strategy

### Product & Technology Team (Relevant to this project)
- **Kimkind Yeung** — Team lead, project owner
- **Hanks Mak** — Senior Director, Software Engineering (Online Platform tech lead; co-maintains Grafana Cloud with Kelvin)
- **Isaac Lam** — Director, Software Engineering (Store Platform software lead; knows Unity log structure)
- **Jacky Lo** — Director, Infrastructure (Store Platform infra; IT helpdesk)
- **Eddy Chan** — Director, Project Management (Store Platform PM; handles release ops and communications)
- **Gideon Lai** — Manager, Hardware (Store Platform hardware)
- **Woody Kwong** — Senior Product Manager (Online Platform product lead)
- **Robert Stuart** — Senior UI/UX Designer (cross-platform)
- **Will Yeung** — Data & Insights Lead (business reports and analysis)

### Key Contacts for This Project
| Task | Contact | Why |
|---|---|---|
| Grafana Cloud API access | Kelvin (DevOps) / Hanks Mak | They maintain Grafana Cloud |
| Unity log format questions | Isaac Lam / Steven (CEO) | Steven provided the sample log |
| Tournament mode filter | Steven / Isaac | Need to confirm how to distinguish tournament logs |
| Store setup (TV, QR code) | Eddy Chan / Jacky Lo | Coordinate hardware at The Battery |
| Design review | Robert Stuart | UI/UX designer |

---

## File Inventory

| File | Description |
|---|---|
| `leaderboard.html` | The main leaderboard — standalone HTML with embedded CSS, JS, and base64 logo |
| `DWV_Logo.png` | Deadwood Valley logo (embedded in HTML as base64) |
| `ui-master.zip` | Sandbox VR UI component library (private repo snapshot) with design tokens |
| `LEADERBOARD_PROJECT.md` | This document |

---

## Known Issues / TODO

- [ ] **Finals view** exists in HTML but is hidden (`display:none`) — no tab to switch to it since tabs were removed. Need to decide how/when to show finals (manual toggle? auto-switch after qualifying?)
- [ ] **`showPhase()` function and finals rendering** are still in JS but unused — can be re-enabled when needed
- [ ] **Stats bar values are hardcoded** in HTML (8 teams, 1,261,552 high score, Steven_Ad most kills) — need to compute dynamically from data
- [ ] **Auto-refresh countdown** is cosmetic only — not actually fetching new data yet
- [ ] **Gordita font** will only render if the user's device has it installed; otherwise falls back to system font
- [ ] **`deaths` field** — team deaths are calculated as sum of player deaths, not from `team[0].death`. The latter appears to mean something different (possibly team wipes). Needs confirmation from game team.
- [ ] **Player `color` field mapping** — the log uses `members[].character` with values like "red", "blue", "green", "yellow". We map these to player card top border colors. Confirm this is always the character color.
