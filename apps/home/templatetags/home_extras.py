from apps.insert import models

from django import template
from django.db.models import Count

register = template.Library()


@register.simple_tag
def list_names():
    return [patient.name for patient in models.Patient.objects.all()]


@register.simple_tag()
def list_studies():
    return [tomo.study for tomo in models.Tomography.objects.all()]


@register.simple_tag()
def list_all():
    return [(tomo.patient.name, tomo.study, tomo.num_images)
            for tomo in models.Tomography.objects.annotate(num_images=Count('image'))]
