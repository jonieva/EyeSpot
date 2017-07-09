import SimpleITK as sitk
import os
import numpy as np
import cv2 as cv
import scipy.signal as signal
from matplotlib_util import *

import EyeSpot.logic as logic


class EyeSpot(object):
    prop1 = 1
    # Properties
    def __init__(self, training_images_path, output_files_path):
        self.training_images_path = training_images_path
        self.preprocessed_images_path = output_files_path
        logic.Util.create_directory(self.preprocessed_images_path)

    def execute_pipeline(self):
        self.preprocess_images()

    def preprocess_images(self):
        """
        :return:
        """
        for image in os.listdir(self.training_images_path):
            print("Preproccesing image " + image)
            image = sitk.ReadImage(os.path.join(self.training_images_path, image))
            # Get the Green channel
            image_array = sitk.GetArrayFromImage(image)[:,:,1]
            # Get mean and standard deviation in local patches of size s=200
            # To that end, we convolve the image with filters m (mean) and var (variance)
            s = 101
            # v = np.ones((s,s), np.double) / (s**2)
            # m2 = signal.convolve2d(image_array, v, "same")
            util = Matplotlib_Util()
            dest = np.zeros(image_array.shape)
            i = cv.integral(image_array)
            i = i[:-1, :-1]
            m = np.zeros(image_array.shape, np.int)
            m = i[s:, s:]   + i[:(i.shape[0] - s), :(i.shape[1] - s)] \
                            - i[:(i.shape[0] - s), s:] - i[s:, :(i.shape[1]-s)]
            m[:s,:s] = i[:s, :s]
            util.plota(m)
            # Variance
            #var2 = signal.convolve2d(image_array**2, v, "same")
            #var2 = var - m2**2
            # var = i[s:, s:]-m[s:, s:]**2 \
            #         + (i[:(i.shape[0] - s), :(i.shape[1] - s)] - m[:(i.shape[0] - s), :(i.shape[1] - s)]**2) \
            #         - (i[:(i.shape[0] - s), s:] - m[:(i.shape[0] - s), s:]**2) \
            #         - (i[s:, :(i.shape[1]-s)] - m[s:, :(i.shape[1]-s)]**2)
            i2 = cv.integral(image_array**2, dest)
            i2 = i2[:-1, :-1]
            var = np.zeros(image_array.shape)
            var = i2[s:, s:] + i2[:(i2.shape[0] - s), :(i2.shape[1] - s)] \
                            - i2[:(i2.shape[0] - s), s:] - i2[s:, :(i2.shape[1]-s)]
            var = var - m**2
            var[:s,:s] = i2[:s, :s]
            util.plota(var)
            # Avoid discountinuities
            var[var == 0] = 1
            # Distance for every neighbourhood
            d = np.abs((image_array-m) / var**2)
            # Bakground set to those pixels whose distance is lower than a threshold
            t = 1
            Ib = d < t

            util.plota(Ib)

            # dummy = np.zeros((200,200))
            # dummy[50:150, 50:150] = 1
            # s = 20
            # v = np.ones((s,s), np.double) / (s**2)
            # i = dummy
            # m = signal.convolve2d (i, v, mode="same")
            # util.plota(m)

if __name__ == "__main__":
    #images_folder = "/Volumes/Mac500/OneDrive/EyeSpot/diaretdb0_v_1_1/resources/images/diaretdb0_binary_masks/"
    images_folder = "/Volumes/Mac500/OneDrive/EyeSpot/diaretdb1_v_1_1/resources/images/ddb1_fundusimages/"
    output = "/Volumes/Mac500/OneDrive/EyeSpot/processed/"
    e = EyeSpot(images_folder, output)
    e.execute_pipeline()
