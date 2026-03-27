# Deadwood Valley Tournament Leaderboard

A static HTML leaderboard for tracking internal playtesting scores of **Deadwood Valley** — a VR zombie survival game by Sandbox VR.

🔗 **Live:** https://yeungkimkind.github.io/dwt-leaderboard/leaderboard.html

---

## How It Works

1. After each test session, copy the game's `output_log_*.txt` file into the `session-log/` folder
2. Ask Claude to extract the score and update the leaderboard
3. Claude parses the JSON after `"Experience Stats Uploaded"` in the log, adds it to `leaderboard.html`, and pushes to GitHub
4. The page auto-refreshes every 15 seconds — ideal for displaying on a TV screen

The leaderboard is a fully self-contained HTML file (no server, no build step). Data is hardcoded directly in the file.

---

## Session ID Format

```
sbvrdev-YYMMDD-T{roomNumber}-HHmmss
```

Example: `sbvrdev-260327-T4-142545` = March 27, 2026, Room 4, started at 14:25:45

---

## Score Record JSON Structure

Each session log contains a JSON block after `"Experience Stats Uploaded"`. Below is the full reference of fields used by the leaderboard.

### `stats.experience` — Game metadata

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Experience ID (e.g. `"deadwoodv"`) |
| `language` | string | Language code (e.g. `"EN"`) |
| `version` | string | Game build version |
| `vrpreview` | string | VR preview skin active during session |

---

### `stats.team[0]` — Team-level result

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Team name entered at kiosk |
| `numOfPlayers` | int | Number of players (usually 4) |
| `teamScore` | int | Raw score before bonus |
| `bonusScore` | int | Bonus points added on top |
| `score` | int | **Final total score** (`teamScore + bonusScore`) |
| `rating` | int | Star rating (1–5) |
| `death` | int | Total team deaths across all waves |
| `result` | string | Game outcome — see Result Values below |
| `gameMode` | string | Difficulty (`"nightmare"`, etc.) |
| `gameTime` | int | Total gameplay time in seconds |
| `tutorialTime` | int | Tutorial time in seconds |
| `teamCombo` | int | Final combo count |
| `maxTeamCombo` | int | Highest combo reached during the session |
| `wrathWeakpointBrokenCount` | int | Number of Wrath weakpoints broken |
| `wrathKilledByPlayer` | bool | Whether Wrath was killed by players |
| `wrathKilledByFailsafe` | bool | Whether Wrath was killed by failsafe mechanism |
| `billSaved` / `jasonSaved` / `rachelSaved` / `albertSaved` / `bethSaved` | bool | Whether each NPC survived |
| `damageToBill` / `damageToJason` / `damageToRachel` / `damageToAlbert` / `damageToBeth` | int | Friendly fire damage dealt to each NPC |
| `playersDiedInWave1`–`playersDiedInWave10` | int | Number of player deaths per wave |
| `waveScore` | array | Score earned in each wave — see Wave Score below |

#### Result Values

| Value | Meaning |
|-------|---------|
| `BothSurvived` | Both boss waves survived |
| `BethSurvived` | Beth the NPC survived |
| `BillSurvived` | Bill the NPC survived |
| `Timesup` | Game ended due to time limit |

#### `waveScore[]` — Per-wave breakdown

| Field | Type | Description |
|-------|------|-------------|
| `WaveName` | string | Wave identifier (e.g. `"Wave7"`) |
| `Score` | int | Score earned in that wave |

---

### `stats.members[]` — Per-player stats

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Player's in-game name |
| `score` | int | Individual score |
| `weapon` | string | Weapon used (`"Rifle"`, `"Shotgun"`, `"Machine"`, `"DesertEagle"`, `"Pistol"`) |
| `character` | string | Character colour slot (`"red"`, `"blue"`, `"green"`, `"yellow"`) |
| `mvp` | bool | Whether this player was MVP |
| `totalKills` | int | Total enemy kills |
| `death` | int | Number of times this player died |
| `accuracy` | float | Shot accuracy percentage |
| `accuracyGrade` | string | Grade for accuracy (`"S"`, `"A"`, `"B"`, `"C"`, `"D"`) |
| `shots` | int | Total shots fired |
| `shotHits` | int | Total shots that connected |
| `headshots` | int | Number of headshots |
| `damageDealt` | int | Total damage dealt to enemies |
| `damageTaken` | int | Total damage received |
| `damageBoss` | int | Damage dealt to boss enemies |
| `damageBrute` | int | Damage dealt to brute enemies |
| `damageWrath` | int | Damage dealt to the Wrath boss |
| `manualReloads` | int | Number of manual reloads performed |
| `autoReloads` | int | Number of auto-reloads triggered |
| `kill[]` | array | Kill breakdown by enemy type (enemy, vulture, leaper, zombieDog, brute, wrath) |

---

## Filtering Rules

Sessions are excluded from the leaderboard if:
- The team name suggests an internal test (e.g. contains `"test"`, `"T1"` prefix, or similar patterns)
- The score is abnormally low (likely an incomplete/aborted run)
- The session was played under an old score formula (currently: sessions before the formula update are excluded)
