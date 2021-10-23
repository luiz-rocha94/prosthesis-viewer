from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=15)


def models_directory_path(instance, filename):
    return 'models/{0}/{1}/{2}'.format(instance.patient.name,
                                       instance.study,
                                       filename)


class Tomography(models.Model):
    study = models.CharField(max_length=30)
    y_spacing = models.FloatField()
    x_spacing = models.FloatField()
    thickness = models.FloatField()
    model = models.FileField(upload_to=models_directory_path, max_length=260, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)


def images_directory_path(instance, filename):
    return 'images/{0}/{1}/{2}'.format(instance.tomography.patient.name,
                                       instance.tomography.study,
                                       filename)


def files_directory_path(instance, filename):
    return 'files/{0}/{1}/{2}'.format(instance.tomography.patient.name,
                                      instance.tomography.study,
                                      filename)


class Image(models.Model):
    slice = models.FloatField()
    shape = models.BooleanField()
    image = models.FileField(upload_to=images_directory_path, max_length=260)
    file = models.FileField(upload_to=files_directory_path, max_length=260)
    tomography = models.ForeignKey(Tomography, on_delete=models.CASCADE)
