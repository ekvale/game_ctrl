from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0003_alter_controller_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='controller',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
    ] 