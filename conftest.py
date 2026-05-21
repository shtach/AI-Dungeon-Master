import pytest


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="testuser",
        password="testpassword123",
    )


@pytest.fixture
def another_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="anotheruser",
        password="testpassword123",
    )


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client, user