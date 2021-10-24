from apps.insert import models

from django import template

register = template.Library()


@register.simple_tag
def list_names():
    return [patient.name for patient in models.Patient.objects.all()]


@register.simple_tag()
def list_studies():
    return [tomo.study for tomo in models.Tomography.objects.all()]

