import pytest
from django.contrib.auth import get_user_model
from ai_dungeon_master.apps.characters.models import Character
from ai_dungeon_master.apps.world.models import WorldSetting, Scenario
from ai_dungeon_master.apps.game.models import GameSession, Message, DiceRoll

User = get_user_model()

@pytest.fixture
def dummy_message():
    user = User.objects.create(username="test_user")
    world = WorldSetting.objects.create(name="Test World", description="Test", ai_instructions="Test")
    scenario = Scenario.objects.create(title="Test", intro_text="Test", world=world)
    char = Character.objects.create(
        user=user, name="Hero", race="Elf", character_class="Mage",
        strength=10, dexterity=10, constitution=10, intelligence=10,
        wisdom=10, charisma=10, level=1, experience=0, max_hp=10,
        current_hp=10, armor_class=10, speed=30, background="None"
    )
    session = GameSession.objects.create(
        user=user, character=char, world=world, scenario=scenario
    )
    message = Message.objects.create(
        session=session, role="USER", content="Test roll"
    )
    return message


@pytest.mark.django_db
def test_diceroll_success_calculation(dummy_message):
    roll_success = DiceRoll.objects.create(message=dummy_message, dice_type="d20", result=15, modifier=2, dc=15)
    assert roll_success.success is True

    roll_fail = DiceRoll.objects.create(message=dummy_message, dice_type="d20", result=10, modifier=0, dc=15)
    assert roll_fail.success is False

    roll_free = DiceRoll.objects.create(message=dummy_message, dice_type="d20", result=18)
    assert roll_free.success is None