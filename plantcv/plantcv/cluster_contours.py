import cv2
import numpy as np
from plantcv.plantcv import print_image
from plantcv.plantcv import plot_image
from plantcv.plantcv import color_palette


def cluster_contours(device, img, roi_objects, nrow=1, ncol=1, debug=None):

    """
    This function take a image with multiple contours and clusters them based on user input of rows and columns

    Inputs:
    img                     = An RGB image array
    roi_objects             = object contours in an image that are needed to be clustered.
    nrow                    = number of rows to cluster (this should be the approximate  number of desired rows
                              in the entire image (even if there isn't a literal row of plants)
    ncol                    = number of columns to cluster (this should be the approximate number of desired columns
                              in the entire image (even if there isn't a literal row of plants)
    file                    = output of filename from read_image function
    filenames               = input txt file with list of filenames in order from top to bottom left to right
    debug                   = print debugging images

    Returns:
    device                  = pipeline step counter
    grouped_contour_indexes = contours grouped
    contours                = All inputed contours

    :param device: int
    :param img: ndarray
    :param roi_objects: list
    :param nrow: int
    :param ncol: int
    :param debug: str
    :return device: int
    :return grouped_contour_indexes: list
    :return contours: list
    """

    device += 1

    if len(np.shape(img)) == 3:
        iy, ix, iz = np.shape(img)
    else:
        iy, ix, = np.shape(img)

    # get the break groups

    if nrow == 1:
        rbreaks = [0, iy]
    else:
        rstep = np.rint(iy / nrow)
        rstep1 = np.int(rstep)
        rbreaks = range(0, iy, rstep1)
    if ncol == 1:
        cbreaks = [0, ix]
    else:
        cstep = np.rint(ix / ncol)
        cstep1 = np.int(cstep)
        cbreaks = range(0, ix, cstep1)

    # categorize what bin the center of mass of each contour

    def digitize(a, step):
        if isinstance(step, int) == True:
            i = step
        else:
            i = len(step)
        for x in range(0, i):
            if x == 0:
                if a >= 0 and a < step[x + 1]:
                    return x + 1
            elif a >= step[x - 1] and a < step[x]:
                return x
            elif a > step[x - 1] and a > np.max(step):
                return i

    dtype = [('cx', int), ('cy', int), ('rowbin', int), ('colbin', int), ('index', int)]
    coord = []
    for i in range(0, len(roi_objects)):
        m = cv2.moments(roi_objects[i])
        if m['m00'] == 0:
            pass
        else:
            cx = int(m['m10'] / m['m00'])
            cy = int(m['m01'] / m['m00'])
            # colbin = np.digitize(cx, cbreaks)
            # rowbin = np.digitize(cy, rbreaks)
            colbin = digitize(cx, cbreaks)
            rowbin = digitize(cy, rbreaks)
            a = (cx, cy, colbin, rowbin, i)
            coord.append(a)
    coord1 = np.array(coord, dtype=dtype)
    coord2 = np.sort(coord1, order=('colbin', 'rowbin'))

    # get the list of unique coordinates and group the contours with the same bin coordinates

    groups = []
    for i, y in enumerate(coord2):
        col = y[3]
        row = y[2]
        location = str(row) + ',' + str(col)
        groups.append(location)

    unigroup = np.unique(groups)
    coordgroups = []

    for i, y in enumerate(unigroup):
        col = int(y[0])
        row = int(y[2])
        for a, b in enumerate(coord2):
            if b[2] == col and b[3] == row:
                grp = i
                contour = b[4]
                coordgroups.append((grp, contour))
            else:
                pass

    coordlist = [[y[1] for y in coordgroups if y[0] == x] for x in range(0, (len(unigroup)))]

    contours = roi_objects
    grouped_contour_indexes = coordlist

    # Debug image is rainbow printed contours

    if debug == 'print':
        if len(np.shape(img)) == 3:
            img_copy = np.copy(img)
        else:
            iy, ix = np.shape(img)
            img_copy = np.zeros((iy, ix, 3), dtype=np.uint8)

        rand_color = color_palette(len(coordlist))
        for i, x in enumerate(coordlist):
            for a in x:
                cv2.drawContours(img_copy, roi_objects, a, rand_color[i], -1, lineType=8)
        print_image(img_copy, (str(device) + '_clusters.png'))

    elif debug == 'plot':
        if len(np.shape(img)) == 3:
            img_copy = np.copy(img)
        else:
            iy, ix = np.shape(img)
            img_copy = np.zeros((iy, ix, 3), dtype=np.uint8)

        rand_color = color_palette(len(coordlist))
        for i, x in enumerate(coordlist):
            for a in x:
                cv2.drawContours(img_copy, roi_objects, a, rand_color[i], -1, lineType=8)
        plot_image(img_copy)

    return device, grouped_contour_indexes, contours
