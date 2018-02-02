'''
Script to read image files and crop them according to specified dimensions.

@author: Joao Hatum
@date: 26Nov2017
'''

import glob
from PIL import Image

def loadImages(root_path):
    return glob.glob(root_path + '**/*.png', recursive=True)

def cropImages(images_array):
    print('Cropping files...')
    for img_path in images_array:
        img = Image.open(img_path)
        width = img.size[0]
        height = img.size[1]

        print(img.filename + '...')

        img_crop = img.crop((300, 140, width-300, height))
        img_crop.save(img.filename)

    print('Operation successfully completed!')

# Testing before using it!
#test_files_path_root = ''
#test_images = loadImages(test_files_path_root)

files_path_root = '' # Set path
images = loadImages(files_path_root)

# Loop images to crop them
cropImages(images)
