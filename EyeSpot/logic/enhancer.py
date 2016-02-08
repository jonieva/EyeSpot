import cv2
import numpy as np


class Enhancer(object):
    def __init__(self, original_image_array):
        self.original_image_array = original_image_array
        self.im_crahe = None
        self.im_out = None
        self.enhanced_image = None

    def __calculate_core_matrixes__(self):
        # green = self.original_image_array[:, :, 1]
        # mask = (green > 10).astype(np.uint8)
        # kernel = np.ones(3, np.uint8)     # Matlabaux = self.im_eq[:,:,i] - vascular_factor*128*im_out kernel
        # mask = cv2.erode(mask, kernel, iterations=5)
        # mask = cv2.dilate(mask, kernel, iterations=5)
        #
        # [fil, col] = np.where(mask == 1) # size of the image
        # rect = [np.min(fil), np.max(fil), np.min(col), np.max(col)]
        # self.image_crop = self.original_image_array[rect[0]:rect[1], rect[2]:rect[3]]
        # image_crop_green = self.image_crop[:, :, 1]
        #self.image_crop = self.original_image_array
        #image_green = self.original_image_array[:, :, 1]

        # Equalization of channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        #self.im_crahe = np.zeros(self.original_image_array.shape, np.uint8)
        self.im_crahe = np.copy(self.original_image_array)
        # self.im_crahe[:, :, 0] = self.original_image_array[:, :, 0]  # clahe.apply(self.image_crop(:,:,0))
        self.im_crahe[:, :, 1] = clahe.apply(self.original_image_array[:, :, 1])
        # self.im_crahe[:, :, 2] = self.original_image_array[:, :, 2]  # clahe.apply(self.image_crop(:,:,2))

        im_eq_green = self.im_crahe[:, :, 1].astype(np.float64)

        # FRANGI filter
        # Options = struct('FrangiScaleRange', [2 6], 'FrangiScaleRatio', 0.5, 'FrangiBetaOne', 0.5, 'FrangiBetaTwo', 15, 'verbose',true,'BlackWhite',true);
        # [outIm] = FrangiFilter2D(double(I_eq),Options);
        FrangiScaleRange = [2.0, 6.0]
        FrangiScaleRatio = 0.5
        FrangiBetaOne = 0.5
        FrangiBetaTwo = 15

        sigmas = np.arange(FrangiScaleRange[0], FrangiScaleRange[1] + FrangiScaleRatio, FrangiScaleRatio)
        beta = 2 * FrangiBetaOne ** 2
        c = 2 * FrangiBetaTwo ** 2

        all_filtered = np.zeros((im_eq_green.shape[0], im_eq_green.shape[1], sigmas.size))

        for i in range(sigmas.size):
            sigma = sigmas[i]
            # Build the gaussian 2nd derivatives filters

            ####################################################################################################################
            # Implementation of convolutions with Scipy
            # aux = np.mgrid[-np.round(3*sigma):np.round(3*sigma)+1,-np.round(3*sigma):np.round(3*sigma)+1]
            # X = aux[0].astype(np.float64)
            # Y = aux[1].astype(np.float64)
            #
            #
            # DGaussxx = 1/(2*np.pi*sigma**4) * (X**2/sigma**2 - 1) * np.exp(-(X**2 + Y**2)/(2*sigma**2))
            # DGaussxy = 1/(2*np.pi*sigma**6) * (X*Y)                 * np.exp(-(X**2 + Y**2)/(2*sigma**2))
            # DGaussyy = np.transpose(DGaussxx);
            #
            # Dxx = sc.convolve2d(im_eq_green,DGaussxx,'same')
            # Dxy = sc.convolve2d(im_eq_green,DGaussxy,'same')
            # Dyy = sc.convolve2d(im_eq_green,DGaussyy,'same')

            ####################################################################################################################
            # Implementation of convolutions with numpy along different axes
            # http://stackoverflow.com/questions/5228718/convolution-along-one-axis-only
            X = np.mgrid[-np.round(3 * sigma):np.round(3 * sigma) + 1]
            G = 1 / np.sqrt(2 * np.pi * sigma ** 2) * np.exp(-(X ** 2) / (2 * sigma ** 2))
            DGxx = (X ** 2 / sigma ** 4 - 1 / sigma ** 2) * G
            DG = (X / sigma ** 2) * G

            Dxx = np.apply_along_axis(lambda m: np.convolve(m, DGxx, mode='same'), axis=0, arr=im_eq_green)
            Dxx = np.apply_along_axis(lambda m: np.convolve(m, G.T, mode='same'), axis=1, arr=Dxx)

            Dyy = np.apply_along_axis(lambda m: np.convolve(m, DGxx.T, mode='same'), axis=1, arr=im_eq_green)
            Dyy = np.apply_along_axis(lambda m: np.convolve(m, G, mode='same'), axis=0, arr=Dyy)

            Dxy = np.apply_along_axis(lambda m: np.convolve(m, DG, mode='same'), axis=0, arr=im_eq_green)
            Dxy = np.apply_along_axis(lambda m: np.convolve(m, DG.T, mode='same'), axis=1, arr=Dxy)

            # TODO: replace Dxx2 wih Dxx from the beggining
            # Dxx = Dxx2
            # Dxy = Dxy2
            # Dyy = Dyy2

            # TESTING
            # np.abs(Dxy-Dxy2).max()
            # np.abs(Dxx-Dxx2).max()
            # np.abs(Dyy-Dyy2).max()

            # plt.figure(41)
            # plt.imshow(Dxy2)
            #
            # plt.figure(50)
            # plt.imshow(Dxx)
            # plt.figure(51)
            # plt.imshow(Dxx2)
            #
            # plt.figure(60)
            # plt.imshow(Dyy)
            # plt.figure(61)
            # plt.imshow(Dyy2)

            ####################################################################################################################

            # Correct for scale
            Dxx *= (sigma ** 2)
            Dxy *= (sigma ** 2)
            Dyy *= (sigma ** 2)

            # Eigenvalues
            tmp = np.sqrt((Dxx - Dyy) ** 2 + 4 * (Dxy ** 2))

            # Compute the eigenvalues
            mu1 = 0.5 * (Dxx + Dyy + tmp)
            mu2 = 0.5 * (Dxx + Dyy - tmp)

            # Sort eigen values by absolute value abs(Lambda1)<abs(Lambda2)
            check = np.abs(mu1) > np.abs(mu2)

            Lambda2 = np.copy(mu1)
            Lambda2[check] = mu2[check]
            Lambda1 = np.copy(mu2)
            Lambda1[check] = mu1[check]

            # Compute some similarity measures
            eps = np.finfo(float).eps
            Lambda1[Lambda1 == 0] = eps
            Rb = (Lambda2 / Lambda1) ** 2
            S2 = Lambda1 ** 2 + Lambda2 ** 2

            # Compute the output image
            Ifiltered = np.exp(-Rb / beta) * (np.ones(im_eq_green.shape) - np.exp(-S2 / c))
            Ifiltered[Lambda1 < 0] = 0

            all_filtered[:, :, i] = np.copy(Ifiltered)

        self.im_out = np.amax(all_filtered, axis=2)

    def execute_enhancement(self, vascular_factor=1, enhancement_factor=1):
        ###  Vascular enhancement
        # This vascular factor should ny go from 0 to 1
        # vascular_factor = 1
        if self.im_crahe is None or self.im_out is None:
            self.__calculate_core_matrixes__()

        im_eq2 = np.zeros(self.im_crahe.shape, self.im_crahe.dtype)

        for i in range(3):
            aux = self.im_crahe[:, :, i] - vascular_factor * 128 * self.im_out
            aux[aux < 0] = 0
            im_eq2[:, :, i] = aux[:,:]


        # This enhancement factor goes form 0 to 1 also.
        #enhancement_factor = 1

        self.enhanced_image = self.im_crahe.astype(np.float64) * (1.0 - enhancement_factor) + im_eq2.astype(
            np.float64) * enhancement_factor
        self.enhanced_image = self.enhanced_image.astype(np.uint8)
        return self.enhanced_image

        #
        # import SimpleITK as sitk
        # import matplotlib.pyplot as plt
        # import matplotlib.cm as cm
        #
        # p = "/Data/jonieva/OneDrive/EyeSpot/diaretdb0_v_1_1/resources/images/diaretdb0_fundus_images/image047.png"
        #
        # image = sitk.ReadImage(p)
        # image_array = sitk.GetArrayFromImage(image)
        # e = Enhancer(image_array)
        #
        # e.execute_enhancement()
        #
        # plt.figure(20)
        # e.execute_enhancement(0.1, 1)
        # plt.imshow(e.enhanced_image)
