
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('pacientes', '0001_initial')]
    operations = [migrations.AddField(model_name='paciente', name='usuarios', field=models.ManyToManyField(related_name='pacientes', to=settings.AUTH_USER_MODEL))]
