# Generated by Django 5.1.6 on 2025-02-15 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='controller',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='controller',
            old_name='updated',
            new_name='updated_at',
        ),
        migrations.AlterField(
            model_name='controller',
            name='image',
            field=models.ImageField(blank=True, upload_to='controllers/%Y/%m/%d'),
        ),
        migrations.AddIndex(
            model_name='controller',
            index=models.Index(fields=['id', 'slug'], name='products_co_id_31e4ab_idx'),
        ),
        migrations.AddIndex(
            model_name='controller',
            index=models.Index(fields=['name'], name='products_co_name_da63be_idx'),
        ),
        migrations.AddIndex(
            model_name='controller',
            index=models.Index(fields=['-created_at'], name='products_co_created_de0697_idx'),
        ),
    ]
