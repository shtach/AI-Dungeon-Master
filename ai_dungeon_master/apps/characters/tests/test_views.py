import pytest
from django.urls import reverse
from ai_dungeon_master.apps.characters.models import Character

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_logged_in(client, django_user_model):
    user = django_user_model.objects.create_user(username="testuser", password="testpass123")
    client.force_login(user)
    return client, user


class TestCharacterWizard:

    def test_step1_post_saves_to_session(self, client_logged_in):
        client, _ = client_logged_in
        url = reverse("characters:create_step1")

        response = client.post(url, {"name": "Thorin", "race": "Dwarf"})

        assert response.status_code == 302
        assert response.url == reverse("characters:create_step2")
        assert client.session.get("character_wizard") == {"name": "Thorin", "race": "Dwarf"}

    def test_step2_redirects_if_no_step1_data(self, client_logged_in):
        client, _ = client_logged_in
        url = reverse("characters:create_step2")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("characters:create_step1")

    def test_step3_post_validates_standard_array(self, client_logged_in):
        client, _ = client_logged_in

        session = client.session
        session["character_wizard"] = {"name": "Thorin", "character_class": "Warrior"}
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

    def test_step4_creates_character_and_clears_session(self, client_logged_in):
        client, user = client_logged_in

        session = client.session
        session["character_wizard"] = {
            "name": "Thorin",
            "race": "Dwarf",
            "character_class": "Warrior",
            "stats": {"strength": 15, "dexterity": 14, "constitution": 13,
                      "intelligence": 12, "wisdom": 10, "charisma": 8}
        }
        session.save()

        url = reverse("characters:create_step4")

        response = client.post(url, {"background": "A brave warrior from the lonely mountain."})

        assert response.status_code == 302
        assert response.url == reverse("game:dashboard")

        assert Character.objects.count() == 1
        char = Character.objects.first()
        assert char.name == "Thorin"
        assert char.character_class == "Warrior"
        assert char.strength == 15
        assert char.user == user

        assert "character_wizard" not in client.session