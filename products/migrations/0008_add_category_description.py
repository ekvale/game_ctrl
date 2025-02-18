from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_add_category_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ] 