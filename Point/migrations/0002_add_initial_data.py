from django.db import migrations

def add_initial_data(apps, schema_editor):
    Point = apps.get_model('Point', 'Point')
    Point.objects.create(price='1,200원', point=10)
    Point.objects.create(price='3,600원', point=30)
    Point.objects.create(price='6,000원', point=50)
    Point.objects.create(price='12,000원', point=100)

class Migration(migrations.Migration):

    dependencies = [
        ('Point', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_data),
    ]
