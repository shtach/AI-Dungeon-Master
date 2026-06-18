# AI Dungeon Master RPG

An immersive, text-based RPG where an AI engine powers a dynamic, responsive Dungeon Master (DM)[cite: 3]. Built on Django, this project enforces strict d20 tabletop rules, processes character attributes, calculates equipment modifications, and maps structured AI text outputs into interactive UI mechanics[cite: 1, 2, 3, 6, 7].

---

## The Player's Journey: How It Works

For anyone arriving here for the first time, this game features an automated DM that enforces world boundaries, plays NPCs, and narrates the exact consequences of your actions[cite: 3]. Here is the chronological flow of a gameplay session[cite: 4, 7]:

### Phase 1: The Multi-Step Character Creation
Players initialize their adventurer through a secure, four-step onboarding layout backed by Django sessions to prevent early database commitment[cite: 7]:

1. **Step 1: Identity (Name & Race)**
   Players give their adventurer a name and choose their heritage[cite: 1, 7], which establishes their starting narrative parameters:
   * **Human:** Versatile and ambitious, excelling in any path they choose.
   * **Elf:** Ancient and graceful, blessed with keen senses and magic affinity.
   * **Dwarf:** Stout and resilient, forged in stone and known for unbreakable will.
   * **Orc:** Fierce and powerful, driven by primal strength and raw endurance.

2. **Step 2: Choose Your Path (Class)**
   Your class choices set the baseline for your combat styles and mechanical capabilities[cite: 1]:
   * **Warrior:** Frontline fighter in heavy armor. Strength-based — absorbs punishment so allies don't have to[cite: 1].
   * **Wizard:** Ranged spellcaster with low HP but devastating intelligence-based magic. Fragile and fearsome[cite: 1].
   * **Rogue:** Agile and cunning striker. Dexterity-based — thrives on stealth, surprise attacks, and dirty tricks[cite: 1].
   * **Cleric:** Divine conduit channeling godly power. Wisdom-based — blends healing, buffs, and holy combat[cite: 1].

3. **Step 3: Attribute Allocation (Characteristics)**
   To guarantee a balanced, tactical start, players assign a fixed **Standard Array** pool of values: `[15, 14, 13, 12, 10, 8]`[cite: 7]. These values are explicitly mapped across six core attributes: *Strength, Dexterity, Constitution, Intelligence, Wisdom, and Charisma*[cite: 1, 7]. The backend strictly validates this array to prevent cheating[cite: 7].

4. **Step 4: Character Review & Background**
   The final state previews the sheet, computes derived stats (Max HP, Armor Class), and offers an optional **Background Story** text area[cite: 1, 7]. This backstory is preserved and fed directly into the initial AI state to tailor your adventure[cite: 1, 3, 7].

---

### Phase 2: Campaign Selection (Worlds & Scenarios)
After character generation, players pick a dedicated setting and a starting scenario stored securely inside database fixtures[cite: 4, 7]:

#### World 1: The Shattered Realm of Aethoria
*   **Description:** A fractured continent scarred by the Sundering — a cataclysm three centuries ago that split the sky and left raw, unstable magic bleeding through rifts in the earth[cite: 4].
*   **Scenarios Available:**
    *   **The Tomb of Silent Kings:** *You stand at the mouth of a collapsed gatehouse... The local village paid you to find out why their gravedigger stopped returning.*[cite: 4]
    *   **Whispers at the Iron Court:** *You stand in the antechamber of Casmir Vael's winter court. Your contact slipped you a note: "Do not eat the fish course, and listen for the word 'cartographer'."*[cite: 4]
    *   **The Road Through Ashen Peaks:** *A mountain pass coated in grey-white dust. Three days into a six-day crossing, the lead driver points out massive, bipedal tracks following you.*[cite: 4]

#### World 2: After the Demon King
*   **Description:** The Demon King is dead. The banners came down, the heroes went home, and a world that spent a hundred years bracing for the end now has to learn how to simply continue[cite: 4].
*   **Scenarios Available:**
    *   **The Abandoned Battlefield:** *Snow half-buries the field where the last battle was won. You came following a rumor — that something was left behind when the armies marched away.*[cite: 4]
    *   **A Town That Remembers You:** *You return to Hollowmere. The innkeeper goes pale, children stop their game, and an old woman presses something cold and heavy into your hand.*[cite: 4]
    *   **The Last Remnant:** *Deep in the marsh where the Demon King's tower fell, one light still burns. The fenfolk speak of a servant who never received the order to stop.*[cite: 4]

#### World 3: The Mages' Trial
*   **Description:** The College of Verren accepts one student in a hundred. Built into cliffs above a drowned city, its halls smell of chalk, ozone, and old fear. Magic here is discipline — measured and quietly dangerous[cite: 4].
*   **Scenarios Available:**
    *   **The Entrance Exam:** *The examination hall is ice-cold. Three proctors sit behind black glass, and before you floats a single unlit candle. "Light it. We are not grading the flame."*[cite: 4]
    *   **The Lost Grimoire:** *A book has gone missing from the Restricted Stacks. The Stacks rearrange themselves after dark, and the last student sent to find it forgot her own name.*[cite: 4]
    *   **A Duel of Mages:** *By dawn you stand in the Ring of Salt opposite a classmate you once called a friend. Word has spread that they have been practicing something forbidden.*[cite: 4]

#### World 4: The Long Road North
*   **Description:** Beyond the last waystation the maps give up. The North is a country of white silence. The cold does not hate you. It simply does not notice you at all, and somehow that is worse[cite: 4].
*   **Scenarios Available:**
    *   **The Frozen Pass:** *A knife-cut between two black peaks. Your guide turned back, leaving you with only the rope, the ice, and footprints going your way — fresh, barefoot, and set far too far apart.*[cite: 4]
    *   **The Village of Ghosts:** *Smoke rises from the chimneys of Stillwater, but not one living soul has wintered here in forty years. The dead keep the village polite, patient, and they insistently ask you to stay for supper.*[cite: 4]
    *   **The Gate at the World's End:** *A gate of black iron and older promises taller than any wall has a right to be. Tonight, for the first time in memory, it stands very slightly open...*[cite: 4]

---

### Phase 3: The Core Gameplay Loop
Once you launch an adventure, the engine initiates a loop:
1. **AI Generation:** The backend stitches world properties, scenario details, and character sheets into a systemic context prompt template[cite: 3, 4].
2. **Parsing UI Cards:** The AI generates short narrative pieces alongside option cards embedded with functional requirements (e.g., `roll=strength|dc=15`)[cite: 2].
3. **Backend Dice Mechanics:** Selecting an interactive option card prompts the backend engine to calculate modifier stack additions and run a d20 roll against the specified DC threshold[cite: 2, 6].
4. **Resolution Changes:** Structural modifications (like health points shifts, status adjustments, or item injections) resolve automatically and update the state for the next turn[cite: 1, 2].

---

## Core Technical Architecture

### 1. Advanced Character State & Dynamic Stats (`stats.py`, `models.py`)
Character statistics are computed globally dynamically by stacking active inventory items over core configurations[cite: 1, 6]:
* **Effective Stats:** Fetches a base attribute score (Strength, Dexterity, etc.) and recursively parses a character's active inventory items to aggregate any corresponding item upgrades (`stat_bonus_value`)[cite: 1, 6].
* **Ability Modifiers:** Automatically calculated using the d20 algorithm based on active effective scores[cite: 1, 6]:
    $$\text{Modifier} = \lfloor\frac{\text{Effective Stat} - 10}{2}\rfloor$$
* **Dynamic Armor Class (AC):** Combines the internal static class baseline with the fluid, gear-adjusted Dexterity modifier and any compounding item armor modifiers (`ac_bonus`)[cite: 1, 6]:
    $$\text{AC} = \text{Base AC}_{\text{Class}} + \text{Modifier}_{\text{DEX}} + \sum \text{Bonus}_{\text{Gear}}$$

### 2. Tactical Combat Resolution Engine
Weapon parameters are parsed to deliver deterministic modifications into active game states[cite: 6]:
* **To-Hit Modifiers:** Resolves automatically based on the weapon's designated structural configuration (`attack_stat`), mapping to its corresponding attribute modifier plus the item's custom `hit_bonus`[cite: 6]:
    $$\text{To-Hit} = \text{Modifier}_{\text{Attack Stat}} + \text{Bonus}_{\text{Weapon Hit}}$$
* **Damage Dictionary Generation:** Produces structural outputs pairing raw dice layouts (e.g., `"1d4"`) with calculated flat damage modifiers[cite: 6]:
    $$\text{Damage Bonus} = \text{Modifier}_{\text{Attack Stat}} + \text{Bonus}_{\text{Weapon Damage}}$$

### 3. Prompt Engineering & Context Injection (`prompts.py`)
The system orchestrates stateless LLMs into rules-conscious referees via context assembly loops inside `SYSTEM_PROMPT_TEMPLATE`[cite: 3]. Prior to each API handshake, the model receives a fully updated state snapshot[cite: 3]:
* **Isolated World Metadata:** Injects system rules, narrative boundaries (`world_description`), and global AI behavioural constraints (`ai_instructions`)[cite: 3, 4].
* **Live Character Sheet Snapshot:** Maps real-time level, dynamic HP values, AC scores, core attributes, and calculated modifiers directly into the prompt frame so the LLM remains informed of character changes[cite: 1, 3, 6].

### 4. Asynchronous Regular Expression Response Parsing Engine (`parser.py`)
To prevent raw LLM conversational text loops from breaking state boundaries, responses must comply with a rigid, regex-enforced structural tag topology[cite: 2]:

| Structural Tag | Purpose & Automated Extraction Schema |
| :--- | :--- |
| `[NARRATIVE]` | Ambient descriptions generated by the DM (safely clamped to 400 characters to optimize pacing)[cite: 2]. |
| `[CARD]` | Choice cards providing skill checks (`roll=<stat>\|dc=<n>`) or operational dependencies (`requires=<item>`). Max 4 per turn[cite: 2]. |
| `[HP_CHANGE]` | Directly parses integers to manipulate character health sheets (`hp=-4` or `hp=+10`)[cite: 2]. |
| `[QUEST_OFFER]` / `[QUEST_COMPLETE]` | Hooks structural flags for quest orchestration lifecycles[cite: 2]. |
| `[COMBAT_START]` | Shifts the UI into a combat configuration, loading enemy models: `name`, `hp`, `ac`, `atk`, and `dmg`[cite: 2]. |
| `[ENEMY_HP]` | Continually registers and monitors changes onto the active enemy's health pool[cite: 2]. |
| `[COMBAT_END]` | Concludes combat, processing evaluation parameters (`victory=True/False`)[cite: 2]. |
| `[LOOT]` | Generates item rows parsed into fields for weapon damage (`dmg`), hit modifiers (`hit`), active `bonuses`, and historical context (`lore`)[cite: 2]. |