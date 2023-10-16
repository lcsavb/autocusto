
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('medicos', '0001_initial'), ('clinicas', '0001_initial')]
    operations = [migrations.AddField(model_name='emissor', name='medico', field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medicos.Medico'))]
