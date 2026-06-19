from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0004_add_session_stats"),
    ]

    operations = [
        migrations.AddField(
            model_name="gamesession",
            name="current_cards",
            field=models.JSONField(blank=True, default=list, help_text="Cards from the last AI turn (for resuming a session)"),
        ),
    ]