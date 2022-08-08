# Generated by Django 3.2.9 on 2022-08-06 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='pseudo_name',
            field=models.CharField(help_text='Новый сток', max_length=32, verbose_name='Псевдоним'),
        ),
        migrations.AddConstraint(
            model_name='stock',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='uniq_name'),
        ),
        migrations.AddConstraint(
            model_name='stock',
            constraint=models.UniqueConstraint(fields=('user', 'pseudo_name'), name='uniq_pseudo_name'),
        ),
    ]