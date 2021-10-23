from pydicom import dcmread
import numpy as np
from PIL import Image
import os

from django.core.files import File

from core.utils import unzip_file, temporary_dir
from . import models
from .image_processing import segment, volume_to_glb, create_prosthesis


def get_volume(name, study):
    images = models.Image.objects.filter(tomography__patient__name=name,
                                         tomography__study=study).order_by('slice')

    volume = np.zeros((len(images), 512, 512, 1), dtype=np.load(images[0].file.path).dtype)
    for idx, image in enumerate(images):
        volume[idx, :, :, 0] = np.load(image.file.path)

    return volume, image.tomography


def update_model(name, study, directory, pre_processing=True):
    volume, tomography = get_volume(name, study)
    if pre_processing:
        volume = segment(volume)

    meta = {'x_spacing': tomography.x_spacing, 'y_spacing': tomography.y_spacing,
            'thickness': tomography.thickness, 'name': name, 'study': study}
    model_file = volume_to_glb(volume, meta, directory)

    model_file_object = File(open(model_file, 'rb'))
    model_file_object.name = os.path.basename(model_file_object.name)

    tomography.model = model_file_object
    tomography.save()


def insert_data(zip_file):
    """
    Descompacta o arquivo zip e extrai os dados dos arquivos dicom para cadastro no banco.
    """

    with temporary_dir() as directory:
        # Extrai os arquivos dicom
        files = unzip_file(zip_file, directory)

        # Salva o arquivo dcm e a imagem
        inserts = []
        for file in files:
            # Abre o arquivo de TC
            ds = dcmread(file)

            # Cadastra o pacient
            name = str(ds.get('PatientName'))
            patient = {'name': name}
            patient = models.Patient.objects.get_or_create(**patient)[0]

            # Cadastra o estudo
            study = f"{ds.get('SeriesDescription')} {ds.get('SeriesNumber')}"
            y_spacing, x_spacing = [round(float(x), 3) for x in ds.get('PixelSpacing')]
            thickness = round(float(ds.get('SliceThickness')), 3)
            tomography = {'study': study, 'patient': patient,
                          'y_spacing': y_spacing, 'x_spacing': x_spacing,
                          'thickness': thickness}
            tomography = models.Tomography.objects.get_or_create(**tomography)[0]

            # Salva o nome e o estudo
            inserts.append((name, study))

            # Obtém os dados da camada
            slice_loc = round(float(ds.get('SliceLocation')), 3)
            shape = (ds.get('Rows'), ds.get('Columns')) == (512, 512)
            data = ds.pixel_array

            # Salva o array
            np_file = file.replace('.dcm', '.npy')
            np.save(np_file, data)

            # Salva a imagem
            img_file = file.replace('.dcm', '.jpg')
            data = np.minimum(0.0425 * (data + 2000), 255).astype(np.uint8)
            Image.fromarray(data).convert('L').save(img_file)

            # Cadastra a imagem
            np_file_object = File(open(np_file, 'rb'))
            np_file_object.name = os.path.basename(np_file_object.name)

            img_file_object = File(open(img_file, 'rb'))
            img_file_object.name = os.path.basename(img_file_object.name)

            image = {'slice': slice_loc, 'shape': shape, 'tomography': tomography}
            models.Image.objects.get_or_create(**image, file=np_file_object, image=img_file_object)

    inserts = set(inserts)
    with temporary_dir() as directory:
        # Cria o volume.
        for name, study in inserts:
            update_model(name, study, directory)


def create_data(name, study, angle, center):
    """
    Cria uma prótese com base em um estudo cadastrado.
    """
    # Obtém o volume do estudo.
    volume, tomography = get_volume(name, study)

    # Cria a prótese.
    volume = create_prosthesis(volume, angle, center)

    # Cadastra o estudo
    new_study = f'{study} prosthesis'
    tomography = {'study': new_study,
                  'y_spacing': tomography.y_spacing, 'x_spacing': tomography.x_spacing,
                  'thickness': tomography.thickness, 'patient': tomography.patient}
    tomography = models.Tomography.objects.get_or_create(**tomography)[0]

    with temporary_dir() as directory:
        for slice_loc, data in enumerate(volume):
            # Salva o array
            np_file = os.path.join(directory, f'prosthesis-{slice_loc}.npy')
            np.save(np_file, data[:,:,0])

            # Salva a imagem
            img_file = np_file.replace('.npy', '.jpg')
            data = (255 * data[:,:,0]).astype(np.uint8)
            Image.fromarray(data).convert('L').save(img_file)

            # Cadastra a imagem
            np_file_object = File(open(np_file, 'rb'))
            np_file_object.name = os.path.basename(np_file_object.name)

            img_file_object = File(open(img_file, 'rb'))
            img_file_object.name = os.path.basename(img_file_object.name)

            image = {'slice': slice_loc*tomography.thickness, 'shape': True, 'tomography': tomography}
            models.Image.objects.get_or_create(**image, file=np_file_object,
                                               image=img_file_object)

    with temporary_dir() as directory:
        update_model(name, new_study, directory, False)
