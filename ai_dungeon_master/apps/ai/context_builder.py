import logging

from .prompts import SYSTEM_PROMPT_TEMPLATE
from .summariser import should_summarise, generate_summary
from .metering import estimate_tokens

logger = logging.getLogger("ai_dungeon_master.apps.ai")

CONTEXT_WINDOW_MESSAGES = 20


def build_prompt(session, user_message, ai_client=None):
    if ai_client and should_summarise(session):
        generate_summary(session, ai_client)

    char = session.character
    world = session.world
    scenario = session.scenario

    summary_section = ""
    if session.summary and session.summary.strip():
        summary_section = f"\n{session.summary.strip()}\n\n"

    active_quests = session.quests.filter(status="ACTIVE")
    quests_section = ""
    if active_quests.exists():
        quest_lines = [f"- {q.title}" for q in active_quests]
        quests_section = "Quests: " + "; ".join(quest_lines) + "\n"

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        world_name=world.name if world else "Unknown",
        world_description=world.description if world else "No description",
        world_instructions=getattr(world, 'ai_instructions', ''),
        scenario_title=scenario.title if scenario else "Free Roam",
        scenario_intro=scenario.intro_text if scenario else "Your journey begins.",
        char_name=char.name,
        char_race=char.race,
        char_class=char.character_class,
        char_level=getattr(char, 'level', 1),
        hp_current=getattr(char, 'current_hp', 10),
        hp_max=getattr(char, 'max_hp', 10),
        armor_class=getattr(char, 'armor_class', 10),
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
        else:
            prefix = f"[{role}]"
        transcript_lines.append(f"{prefix}: {msg.content}")

    transcript = "\n".join(transcript_lines)
    if transcript:
        transcript = f"{transcript}\n"

    final_prompt = f"{system_prompt}{quests_section}\n{transcript}[Player]: {user_message}\n[DM]:"

    tokens_est = estimate_tokens(final_prompt)
    logger.info("build_prompt tokens_est=%d turn_count=%d", tokens_est, session.turn_count)

    return final_prompt