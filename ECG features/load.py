import os, glob
from scipy.io import loadmat
import numpy as np

def load_data(path):
    header_files = []
    for f in os.listdir(path):
        g = os.path.join(path, f)
        if not f.lower().startswith('.') and f.lower().endswith('hea') and os.path.isfile(g):
            header_files.append(g)

    classes = get_classes(path, header_files)
    num_classes = len(classes)
    num_files = len(header_files)
    recordings = list()
    headers = list()

    for i in range(num_files):
        recording, header = load_file(header_files[i])
        recordings.append(recording)
        headers.append(header)

    labels = list()

    for i in range(num_files):
        recording = recordings[i]
        header = headers[i]

        for l in header:
            if l.startswith('#Dx:'):
                labels_act = np.zeros(num_classes)
                arrs = l.strip().split(' ')
                for arr in arrs[1].split(','):
                    class_index = classes.index(arr.rstrip()) # Only use first positive index
                    labels_act[class_index] = 1
        labels.append(labels_act)

    labels = np.array(labels)
    return recordings, headers, labels

def get_classes(input_directory, filenames):
    classes = set()
    for filename in filenames:
        with open(filename, 'r') as f:
            for l in f:
                if l.startswith('#Dx'):
                    tmp = l.split(': ')[1].split(',')
                    for c in tmp:
                        classes.add(c.strip())
    return sorted(classes)

def load_file(header_file):
    with open(header_file, 'r') as f:
        header = f.readlines()
    mat_file = header_file.replace('.hea', '.mat')
    x = loadmat(mat_file)
    recording = np.asarray(x['val'], dtype=np.float64)
    return recording, header
