import os, sys, time
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, exposure

from skimage.morphology import disk
from skimage.filters import rank
from skimage.color import rgb2gray
from skimage.util import img_as_uint
from skimage.exposure import equalize_hist, histogram, cumulative_distribution


def get_mean_histogram(file_list):
    result_hist, result_cum = None, None
    for n,f in enumerate(file_list):
        imr = io.imread(f, as_grey=True)
        hist = exposure.histogram(imr)[0]
        cum  = exposure.cumulative_distribution(imr)[0]
        result_hist = hist if result_hist is None else result_hist + hist
        result_cum  = cum  if result_cum  is None else result_cum  + cum
    return result_hist/len(file_list), result_cum/len(file_list)


def histogram_matching(cum_hist, image_in):
    hist_in = exposure.cumulative_distribution(image_in)[0]

    m = np.zeros(256)
    for g in range(256):
        m[g] = np.argmin(np.abs(hist_in[g]-cum_hist))

    image_out = np.zeros_like(image_in)
    for h in range(image_in.shape[0]):
        for w in range(image_in.shape[1]):
            image_out[h,w] = m[image_in[h,w]*255]/255
    return image_out


def get_file_list(directory, extensions=['.jpg','.jpeg','.png','.tif'], max_files=0):
    file_list = []
    for f in os.listdir(directory):
        name, file_ext = os.path.splitext(f)
        if file_ext in extensions and name[0]!='.':
            file_list.append(os.path.join(directory, name + file_ext))
    
    file_list = sorted(file_list)
    return file_list if max_files==0 else file_list[:max_files]


if __name__ == "__main__":
    option = { "verbose" :   False }

    print "Histogram matching"
    option["verbose"] = "--verbose" in sys.argv

    if len(sys.argv)<3:
        print "usage: python",sys.argv[0],"in_dir out_dir filetype"
        print "       --verbose show detailed information"
        print "  e.g. python",sys.argv[0],"Clouds-in Clouds-out tif --verbose"
    else:
        if not os.path.exists(sys.argv[1]):
            print sys.argv[1], "does not exist, canceling."
            sys.exit(1)
        if not os.path.exists(sys.argv[2]):
            print sys.argv[2], "does not exist, canceling."
            sys.exit(1)

        np.set_printoptions(precision=4, suppress=True, linewidth=160)
        
        file_list = get_file_list(sys.argv[1], max_files=0)

        #imr = io.imread("in/Building.tif", as_grey=True)
        #histr = exposure.cumulative_distribution(imr)[0]

        ref_hist, ref_cum = get_mean_histogram(file_list)

        for n,f in enumerate(file_list):
            print "%d/%d %s" % (n+1,len(file_list),f)

            imi = io.imread(f, as_grey=True)

            imo = histogram_matching(ref_cum, imi)
            io.imsave(os.path.join(sys.argv[2], os.path.basename(f)), img_as_uint(imo))

            if option["verbose"]:
                plt.figure("image in"), plt.imshow(imi, cmap="gray")
                plt.figure("image out"), plt.imshow(imo, cmap="gray")
                plt.figure("Histogram")
                plt.plot(ref_hist, label="reference")
                plt.plot(exposure.histogram(imi)[0], label="hist in")
                plt.plot(exposure.histogram(imo)[0], label="hist out")
                plt.legend()
                plt.figure("Cumulative")
                plt.plot(ref_cum, label="reference")
                plt.plot(exposure.cumulative_distribution(imi)[0], label="cum in")
                plt.plot(exposure.cumulative_distribution(imo)[0], label="cum out")
                plt.legend()
                plt.show()
