from django.apps import AppConfig


class MedicosConfig(AppConfig):
    name = 'medicos'

    def ready(self):
        import medicos.signals
