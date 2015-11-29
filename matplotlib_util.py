import SimpleITK as sitk
import matplotlib.pyplot as plt
import matplotlib.cm as cm

class Matplotlib_Util(object):
    def plot(self, image):
        """ Use Matplotlib to display a simpleITK image (among others)
        :param image: image to display (ex: sitkImage)
        """
        array = sitk.GetArrayFromImage(image)
        self.plota(array)


    def plota(self, array):
        """ Use Matplotlib to display a numpy array in grayscale
        :param array:
        :return:
        """
        f = plt.figure()
        plt.imshow(array, cmap=cm.Greys_r)
        #refresh()
        return f.number

    def plotBinary(self, binarySitkimage):
        """ Plot a binary simple itk image
        :param binarySitkimage:
        :return:
        """
        f = sitk.ScalarToRGBColormapImageFilter()
        f.SetColormap(f.Blue)
        i = f.Execute(binarySitkimage)
        sitk.Show(i)


    def arr(self, sitkImage):
        """ Get a numpy array from a simpleItk image
        :param imageArray:
        :return:
        """
        return sitk.GetArrayFromImage(sitkImage)

    def cl(self, id=0):
        """ Close all Matplotlib windows. If an id is passed, close just that window
        :param id: Number of window to close (0 for all the windows)
        :return:
        """
        if id == 0:
            plt.close('all')
        else:
            plt.close(id)
