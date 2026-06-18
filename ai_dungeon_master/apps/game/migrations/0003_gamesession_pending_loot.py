from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0002_message_diceroll"),
    ]

    operations = [
        migrations.AddField(
            model_name="gamesession",
            name="pending_loot",
            field=models.JSONField(
                blank=True,
                help_text="Pending loot from AI",
                null=True,
            ),
        ),
    ]
