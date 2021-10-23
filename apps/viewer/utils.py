from apps.insert import models


def get_files(name, study):
    query = models.Image.objects.filter(tomography__patient__name=name,
                                        tomography__study=study).order_by('slice')
    files = [q.image.url for q in query]
    tomo = query[0].tomography
    meta = {'name': name, 'study': study, 'slices': len(files),
            'y_spacing': tomo.y_spacing, 'x_spacing': tomo.x_spacing,
            'thickness': tomo.thickness}
    model_file = tomo.model.url

    return files, model_file, meta
