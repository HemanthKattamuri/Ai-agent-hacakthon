# ⚔️ QuestFlow — RPG Gamified Task & Habit Progression Engine

> **Level up your real life.** Transform daily coding sprints, gym sessions, learning goals, and wellness habits into an immersive RPG adventure with secure authentication, animated 3D graphics, non-linear progression math, habit streaks, a virtual armory economy, and live procrastination dungeon boss battles!

---

## 🌟 Key Hackathon Submission Highlights

### 1. 🛡️ User Authentication & Security Isolation
- **Animated Auth Gateway**: Features a multi-layer 3D-tilt animated holographic neural core, interactive particle background, and real-time password strength analyzer.
- **Role & Class Selection**: Choose your starter adventurer class (*Code Mage*, *Iron Warrior*, *Cyber Rogue*, *Paladin Scholar*) with class-specific stat affinities (+15% XP on matching tasks).
- **Enterprise Security**: PBKDF2-HMAC-SHA256 password hashing with unique per-user cryptographically random salts.
- **Strict Data Isolation**: Every adventurer only views, modifies, and progresses their own tasks, inventory, and character sheet.
- **1-Click Demo Personas**: Instant one-click access for judges and evaluators (*Alex Chen - Lvl 4 Code Mage*, *Sarah Lin - Lvl 3 Paladin Scholar*, *Marcus Vance - Lvl 5 Cyber Rogue*).

### 2. ⚡ The RPG Progression Engine & Non-Linear Math
- **Exponential Leveling Formula**:
  $$\text{XP}_{\text{req}}(L) = \lfloor 100 \times L^{1.6} \rfloor$$
  - Level 1: 100 XP
  - Level 2: 303 XP
  - Level 3: 580 XP
  - Level 4: 923 XP
  - Level 5: 1,327 XP
- **Dynamic Task Difficulty Multipliers**:
  - *Trivial*: +15 XP, +5 Gold, +10 Boss DMG
  - *Easy*: +30 XP, +12 Gold, +25 Boss DMG
  - *Medium*: +60 XP, +25 Gold, +55 Boss DMG
  - *Hard*: +120 XP, +50 Gold, +120 Boss DMG
  - *Epic*: +250 XP, +110 Gold, +280 Boss DMG
- **Level Up Celebration & Fanfare**: Automatic celebratory modal with particle confetti, procedural audio fanfare, and full HP/MP restoration.

### 3. 🔥 Gamified Elements & Systems
- **Consecutive Day Streaks**: Tracks consecutive daily activity with flame badges and unlocks a **+3% bonus XP/Gold multiplier per streak day** (up to +50%).
- **5-Attribute Progression Radar**:
  - 🧠 **Intellect** (Coding, Reading, System Architecture, Problem Solving)
  - ⚔️ **Strength** (Gym, Heavy Compound Sets, Physical Grit)
  - ⚡ **Agility** (Speed tasks, PR reviews, Backlog clearing)
  - 🛡️ **Vitality** (Sleep, Hydration, Mindfulness, Nutrition)
  - 🔮 **Charisma** (Presentations, Writing, Networking, Leadership)
- **Virtual Armory & Economy**:
  - Complete quests to earn Gold ($🪙$) and Soul Gems ($💎$).
  - Shop catalogue with Weapons, Helmets/Visors, Armors, Familiar Pets, Auras, Consumables, and Realm Themes.
  - Interactive inventory equipping with direct stat boosts reflected on your 5-attribute radar.
- **🐉 Boss Battles & Dungeon Arena**:
  - Battle *The Dread Procrastination Demon* and *The Deadline Leviathan*.
  - Every task completed in your journal strikes the boss with weapon attack damage!
  - Spend Focus MP on Overclock Strikes to defeat bosses for massive bounty chests.

### 4. 🎵 Web Audio API Sound Synthesizer
- Zero-dependency in-browser synthesizer producing crisp, low-latency audio effects:
  - *Quest Complete Arpeggio*
  - *Gold Coin Ping*
  - *Level-Up Orchestral Fanfare*
  - *Boss Slash Attack*
  - *Item Equip Click*
  - Global mute toggle (`M` shortcut or HUD button).

### 5. ⌨️ Keyboard Accessibility & Responsiveness
- Full keyboard navigation across all screens:
  - `N` or `Alt+N`: Forge new quest
  - `1`: Quest Board tab
  - `2`: Character Sheet tab
  - `3`: Boss Arena tab
  - `4`: Armory Shop tab
  - `5`: Streak Matrix tab
  - `M`: Toggle audio mute
  - `Esc`: Dismiss modals
- Responsive mobile drawer and desktop layout with high-contrast readable elements and dark mode.

---

## 🚀 Quick Start Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1-Command All-in-One Launch
```bash
./run.sh
```
*Automatically sets up Python virtualenv, installs backend and frontend packages, initializes SQLite database, and runs both servers concurrently!*

- **Frontend Station**: `http://localhost:5173`
- **Backend API**: `http://127.0.0.1:8000`
- **Interactive Swagger API Docs**: `http://127.0.0.1:8000/docs`

### Manual Execution

#### Backend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/seed.py
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Test Suite

Run the full pytest suite verifying Authentication, Data Isolation, Task CRUD, Leveling Formulas, Shop Transactions, and Analytics:

```bash
./.venv/bin/pytest backend/test_questflow.py -v
```

---

## 🏛️ System Architecture

```
resolveflow/
├── backend/
│   ├── database.py         # SQLite schema & foreign key connections
│   ├── rpg_engine.py       # Non-linear leveling math, rewards, PBKDF2 hashing
│   ├── models.py           # Pydantic validation schemas
│   ├── seed.py             # Shop catalogue, demo heroes, starter quests & bosses
│   ├── main.py             # FastAPI REST endpoints with token authentication
│   └── test_questflow.py   # Full pytest verification suite
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnimatedLogo.tsx    # 3D-tilt SVG holographic animated brand icon
│   │   │   ├── AuthGateway.tsx     # Starting screen: Login/Signup/Demo & Password meter
│   │   │   ├── TopHUD.tsx          # Real-time HP/MP/XP gauges, streak flames, audio
│   │   │   ├── QuestBoard.tsx      # Task & Habit CRUD, checklist, difficulty filters
│   │   │   ├── CharacterSheet.tsx  # 5-attribute SVG radar, equipment slots
│   │   │   ├── BossArena.tsx       # Live Boss HP gauge, battle effects, raid loot
│   │   │   ├── ArmoryShop.tsx      # Virtual items shop, equipment purchasing
│   │   │   ├── AnalyticsView.tsx   # 30-day streak heat grid, attribute breakdown
│   │   │   └── LevelUpModal.tsx    # Victory fanfare modal with celebratory animation
│   │   ├── soundEngine.ts          # Web Audio API zero-dependency procedural audio
│   │   ├── api.ts                  # Fetch client with auto-token headers
│   │   ├── types.ts                # TypeScript interfaces
│   │   ├── index.css               # Realm theme variables, custom keyframe animations
│   │   └── App.tsx                 # Master state coordinator & keyboard shortcuts
│   └── package.json
└── run.sh                          # Unified execution launcher
```
