import logging

logger = logging.getLogger("ai_dungeon_master.apps.ai")

SUMMARY_PROMPT = (
    "Summarise the following RPG session turns into a short prose paragraph "
    "(3-5 sentences). Keep character names, key events, decisions, and quest "
    "progress. Be concise.\n\nTURNS:\n{turns}"
)

SUMMARISE_EVERY_N = 10


def _build_turns_text(messages):
    lines = []
    for msg in messages:
        role = msg.role.upper()
        if role == "USER":
            prefix = "[Player]"
        elif role == "ASSISTANT":
            prefix = "[DM]"
        else:
            prefix = f"[{role}]"
        lines.append(f"{prefix}: {msg.content}")
    return "\n".join(lines)


def should_summarise(session):
    return session.turn_count > 0 and session.turn_count % SUMMARISE_EVERY_N == 0


def generate_summary(session, ai_client):
    old_count = max(0, session.messages.count() - 20)
    if old_count == 0:
        return

    old_msgs = list(session.messages.order_by("created_at")[:old_count])
    if not old_msgs:
        return

    turns_text = _build_turns_text(old_msgs)
    prompt = SUMMARY_PROMPT.format(turns=turns_text)

    try:
        new_summary = ai_client.generate(prompt)
    except Exception:
        logger.exception("Failed to generate session summary")
        return

    existing = (session.summary or "").strip()
    if existing:
        new_summary = f"{existing}\n\n{new_summary.strip()}"

    session.summary = new_summary.strip()
    session.save(update_fields=["summary"])
    logger.info(
        "Session %s summary updated (%d chars)",
        session.pk,
        len(session.summary),
    )
