from tempfile import TemporaryDirectory, TemporaryFile
from zipfile import ZipFile
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def temporary_dir():
    return TemporaryDirectory(dir=os.path.join(BASE_DIR, 'temporary'))


def temporary_file(suffix):
    return TemporaryFile(dir=os.path.join(BASE_DIR, 'temporary'), suffix=suffix)


def unzip_file(zip_file, directory):
    with ZipFile(zip_file, 'r') as zip_obj:
        zip_obj.extractall(directory)

    files = [os.path.join(directory, file) for file in os.listdir(directory)]
    c = 0
    while True:
        if c == len(files):
            break
        sub_path = files[c]
        if os.path.isdir(sub_path):
            files += [os.path.join(sub_path, file) for file in os.listdir(sub_path)]
        c += 1

    files = [file for file in files if os.path.splitext(file)[-1] == '.dcm']
    files.sort()
    return files
