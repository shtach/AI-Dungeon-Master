import pytest
from ai_dungeon_master.apps.game.models import DiceRoll

@pytest.mark.django_db
def test_diceroll_success_calculation():
    roll_success = DiceRoll.objects.create(dice_type="d20", result=15, modifier=2, dc=15)
    assert roll_success.success is True

    roll_fail = DiceRoll.objects.create(dice_type="d20", result=10, modifier=0, dc=15)
    assert roll_fail.success is False

    roll_free = DiceRoll.objects.create(dice_type="d20", result=18)
    assert roll_free.success is None