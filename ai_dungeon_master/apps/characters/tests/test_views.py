import pytest
from django.urls import reverse
from ai_dungeon_master.apps.characters.models import Character

pytestmark = pytest.mark.django_db


class TestCharacterWizard:

    def test_step1_post_saves_to_session(self, auth_client):
        client, _ = auth_client
        url = reverse("characters:create_step1")

        response = client.post(url, {"name": "Thorin", "race": "DWARF"})

        assert response.status_code == 302
        assert response.url == reverse("characters:create_step2")
        assert client.session.get("character_wizard") == {"name": "Thorin", "race": "DWARF"}

    def test_step1_race_guard_rejects_invalid(self, auth_client):
        client, _ = auth_client
        url = reverse("characters:create_step1")
        response = client.post(url, {"name": "Thorin", "race": "INVALID_RACE"})

        assert response.status_code == 302
        assert client.session.get("character_wizard") is None

    def test_step2_redirects_if_no_step1_data(self, auth_client):
        client, _ = auth_client
        url = reverse("characters:create_step2")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("characters:create_step1")

    def test_step2_rejects_invalid_class(self, auth_client):
        client, _ = auth_client
        session = client.session
        session["character_wizard"] = {"name": "Thorin", "race": "DWARF"}
        session.save()

        url = reverse("characters:create_step2")
        response = client.post(url, {"character_class": "PALADIN_INVALID"})

        assert response.status_code == 302
        assert "character_class" not in client.session.get("character_wizard", {})

    def test_step3_post_validates_standard_array(self, auth_client):
        client, _ = auth_client

        session = client.session
        session["character_wizard"] = {"name": "Thorin", "character_class": "WARRIOR"}
        session.save()

        url = reverse("characters:create_step3")

        bad_data = {
            "strength": "15", "dexterity": "15", "constitution": "13",
            "intelligence": "12", "wisdom": "10", "charisma": "8"
        }
        response = client.post(url, bad_data)

        assert response.status_code == 200
        assert "error" in response.context

        good_data = {
            "strength": "15", "dexterity": "14", "constitution": "13",
            "intelligence": "12", "wisdom": "10", "charisma": "8"
        }
        response = client.post(url, good_data)

        assert response.status_code == 302
        assert response.url == reverse("characters:create_step4")

    def test_step4_creates_character_and_clears_session(self, auth_client):
        client, user = auth_client

        session = client.session
        session["character_wizard"] = {
            "name": "Thorin",
            "race": "DWARF",
            "character_class": "WARRIOR",
            "stats": {"strength": 15, "dexterity": 14, "constitution": 13,
                      "intelligence": 12, "wisdom": 10, "charisma": 8}
        }
        session.save()

        url = reverse("characters:create_step4")

        response = client.post(url, {"background": "A brave warrior from the lonely mountain."})

        assert response.status_code == 302

        assert Character.objects.count() == 1
        char = Character.objects.first()

        assert response.url == reverse("game:create_session") + f"?character_id={char.id}"

        assert char.name == "Thorin"
        assert char.character_class == "WARRIOR"
        assert char.strength == 15
        assert char.user == user

        assert "character_wizard" not in client.session