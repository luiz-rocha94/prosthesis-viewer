import numpy as np
from skimage import draw
from scipy import interpolate
import tensorflow as tf
from pathlib import Path
from skimage import measure
from trimesh import Trimesh, smoothing
import os

BASE_DIR = Path(__file__).resolve().parent


def segment(volume, thr=1500):
    label_segment, max_label = measure.label(volume >= thr, return_num=True)
    hist, h_edge = np.histogram(label_segment, max_label)
    best_label = np.argmax(hist[1:]) + 1
    return label_segment == best_label


def volume_to_glb(volume, meta, directory):
    vol_norm = np.zeros((512, volume.shape[0] + 2, 512), dtype=volume.dtype)
    vol_norm[:, 1:-1, :] = volume.swapaxes(0, 1).squeeze()
    verts, faces, normals, values = measure.marching_cubes(vol_norm,
                                                           spacing=(meta['x_spacing'],
                                                                    meta['thickness'],
                                                                    meta['y_spacing']))
    model = Trimesh(verts, faces)
    model = smoothing.filter_laplacian(model)
    model_file = os.path.join(directory, f'{meta["name"]} {meta["study"]}.glb').replace('\temporary\t', '\\temporary\\t')
    _ = model.export(file_obj=model_file)
    return model_file


def remove(inputs, angle, center):
    r0, c0 = center
    R = np.hypot(abs(r0 - 512), abs(c0 - 512))

    angle0, angle1 = angle
    theta0 = np.deg2rad(angle0)
    theta1 = np.deg2rad(angle0 + angle1)

    h = 2 ** 0.5 * R
    r1, c1 = int(r0 - h * np.sin(theta0)), int(c0 + h * np.cos(theta0))
    r2, c2 = int(r0 - h * np.sin(theta1)), int(c0 + h * np.cos(theta1))

    mask_poly = np.ones(inputs.shape, dtype=bool)
    rr, cc = draw.polygon([r0, r1, r2, r0],
                          [c0, c1, c2, c0], shape=mask_poly.shape)
    mask_poly[rr, cc] = 0

    aug_inputs = inputs * mask_poly
    outputs = inputs * (aug_inputs == 0)
    return aug_inputs, outputs


def create_prosthesis(volume, angle, center, slices=0, step=10):
    # Seleciona a região superior do crânio
    max_label = volume.shape[0]
    min_label = int(max_label*0.6)
    if slices:
        label_size = max_label - min_label
        slice_size = slices*step
        min_label = min_label + int(label_size/2 - slice_size/2)
        max_label = min_label + int(label_size/2 + slice_size/2)

    volume = volume[min_label:max_label]

    # Remove os objetos indesejados.
    volume = segment(volume)
    size = int(volume.shape[0] / step)

    angles = np.random.randint(-2, 2, (size, 2))
    angle0 = angle[0] + angles[:, 0]
    angle1 = angle[1] + angles[:, 1]

    crops = np.stack([angle0, angle1], axis=1)
    slices = np.linspace(0, volume.shape[0], num=size, dtype='int32')
    cs = interpolate.CubicSpline(slices, crops)
    new_slices = np.arange(0, volume.shape[0], 1)
    new_crops = cs(new_slices).astype('int32')

    vae = tf.keras.models.load_model(os.path.join(BASE_DIR, 'static/networks/vae'))

    vol_in = np.zeros(volume.shape, dtype='float32')
    vol_out = np.zeros(volume.shape, dtype='float32')
    for k in new_slices:
        vol_in[k,:,:,0], vol_out[k,:,:,0] = remove(volume[k,:,:,0], new_crops[k], center)

    vol_pred = vae.predict(vol_in)
    vol_pred = (vol_pred > 0.5).astype('float32')
    vol_pred *= vol_in == 0
    return vol_pred
