import SimpleITK as sitk
import os
from util import *

class EyeSpot(object):
    prop1 = 1
    # Properties
    def __init__(self, training_images_path, output_files_path):
        self.training_images_path = training_images_path
        self.preprocessed_images_path = output_files_path
        Util.create_directory(self.preprocessed_images_path)

    def execute_pipeline(self):
        self.preprocess_images()

    def preprocess_images(self):
        """ Spencer-Frame
        :return:
        """
        for image in os.listdir(self.training_images_path):
            print("Preproccesing image " + image)



if __name__ == "__main__":
    images_folder = "/Volumes/Mac500/OneDrive/EyeSpot/diaretdb0_v_1_1/resources/images/diaretdb0_binary_masks/"
    output = "/Volumes/Mac500/OneDrive/EyeSpot/diaretdb0_v_1_1/processed/"
    e = EyeSpot(images_folder, output)
    e.execute_pipeline()
