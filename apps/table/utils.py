from pathlib import Path
from shutil import rmtree
import os

from apps.insert import models

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def delete_from(rows):
    for row in rows:
        name, study = row
        tomo = models.Tomography.objects.filter(patient__name=name, study=study)
        if tomo:
            tomo.delete()
            rmtree(os.path.join(BASE_DIR, 'media', 'files', name, study))
            rmtree(os.path.join(BASE_DIR, 'media', 'images', name, study))
            rmtree(os.path.join(BASE_DIR, 'media', 'models', name, study))
