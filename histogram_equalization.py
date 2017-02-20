import os, sys, time
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, exposure

from skimage.morphology import disk
from skimage.filters import rank
from skimage.color import rgb2gray
from skimage.util import img_as_uint
from skimage.exposure import equalize_hist
from skimage.exposure import histogram
from skimage.exposure import cumulative_distribution

def get_file_list(directory, extension, max_files=0):
    file_list = []
    for f in os.listdir(directory):
        name, file_ext = os.path.splitext(f)
        if file_ext == extension:
            file_list.append(os.path.join(directory, name + extension))
    
    file_list = sorted(file_list)
    return file_list if max_files==0 else file_list[:max_files]


if __name__ == "__main__":
    option = { "color" : False,
               "verbose" :   False }

    print "Histogram equalization"
    option["color"] = "--color" in sys.argv
    option["verbose"] = "--verbose" in sys.argv

    if len(sys.argv)<4:
        print "usage: python",sys.argv[0],"in_dir out_dir filetype"
        print "       --verbose show detailed information"
        print "       --color   to preserve color"
        print "  e.g. python",sys.argv[0],"Clouds-in Clouds-out tif --verbose"
    else:
        if not os.path.exists(sys.argv[1]):
            print sys.argv[1], "does not exist, canceling."
            sys.exit(1)
        if not os.path.exists(sys.argv[2]):
            print sys.argv[2], "does not exist, canceling."
            sys.exit(1)

        np.set_printoptions(precision=4, suppress=True, linewidth=160)
        
        file_list = get_file_list(sys.argv[1], "."+sys.argv[3], max_files=0)

        for n,f in enumerate(file_list):
            print "%d/%d %s" % (n+1,len(file_list),f)

            im = io.imread(f)
            if not option["color"] or im.ndim==2:
                if im.ndim==3:
                    im = rgb2gray(im)
                hist_before = exposure.cumulative_distribution(im)[0]
                im = exposure.equalize_hist(im)
                #im = exposure.rescale_intensity(im)
                #im = exposure.equalize_adapthist(im)
                hist_after = exposure.cumulative_distribution(im)[0]

                if option["verbose"]:
                    plt.figure("histogram")
                    plt.plot(hist_before,label='before')
                    plt.plot(hist_after,label='after')
                    plt.legend(loc=0, frameon=False)
                    #plt.figure("image"), plt.imshow(im)
                    plt.show()

                io.imsave(os.path.join(sys.argv[2], os.path.basename(f)), img_as_uint(im))
            else:
                r = np.dstack((exposure.equalize_hist(im[:,:,0]),
                               exposure.equalize_hist(im[:,:,1]),
                               exposure.equalize_hist(im[:,:,2])))

                if option["verbose"]:
                    plt.imshow(r)
                    plt.show()

                io.imsave(os.path.join(sys.argv[2], os.path.basename(f)), img_as_uint(r))
