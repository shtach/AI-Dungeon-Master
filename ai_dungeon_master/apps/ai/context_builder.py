from .prompts import SYSTEM_PROMPT_TEMPLATE

CONTEXT_WINDOW_MESSAGES = 20

def build_prompt(session, user_message):
    char = session.character
    world = session.world
    scenario = session.scenario

    summary_section = ""
    if session.summary and session.summary.strip():
        summary_section = f"\n=== SESSION SUMMARY ===\n{session.summary.strip()}\n"

    active_quests = session.quests.filter(status="ACTIVE")
    quests_section = ""
    if active_quests.exists():
        quest_lines = [f"- {q.title}: {q.description}" for q in active_quests]
        quests_section = "\n=== ACTIVE QUESTS ===\n" + "\n".join(quest_lines) + "\n"

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        world_name=world.name if world else "Unknown",
        world_description=world.description if world else "No description",
        world_instructions=getattr(world, 'ai_instructions', 'No extra instructions'),
        scenario_title=scenario.title if scenario else "Free Roam",
        scenario_intro=scenario.intro_text if scenario else "Your journey begins.",
        char_name=char.name,
        char_race=char.race,
        char_class=char.character_class,
        char_level=getattr(char, 'level', 1),
        hp_current=getattr(char, 'current_hp', 10),   # для будущего
        hp_max=getattr(char, 'max_hp', 10),   # для будущего
        armor_class=getattr(char, 'armor_class', 10),   #для будущего
        str=char.strength,
        dex=char.dexterity,
        con=char.constitution,
        int=char.intelligence,
        wis=char.wisdom,
        cha=char.charisma,
        summary_section=summary_section
    )

    recent_msgs = list(session.messages.order_by('-created_at')[:CONTEXT_WINDOW_MESSAGES])
    recent_msgs.reverse()

    transcript_lines = []
    for msg in recent_msgs:
        role = msg.role.upper()
        if role == 'USER':
            prefix = "[Player]"
        elif role == 'ASSISTANT':
            prefix = "[DM]"
        elif role == 'SYSTEM':
            prefix = "[System]"
        else:
            prefix = f"[{role}]"

        transcript_lines.append(f"{prefix}: {msg.content}")

    transcript = "\n".join(transcript_lines)
    if transcript:
        transcript = f"{transcript}\n"

    final_prompt = f"{system_prompt}{quests_section}\n{transcript}[Player]: {user_message}\n[DM]:"
    return final_prompt