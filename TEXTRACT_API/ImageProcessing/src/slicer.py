import cv2
import numpy as np
# from pathlib import Path
import os


def threshold_and_invert_img(img):
    # Thresholding the image
    thresh, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # Invert the image
    img_bin = 255 - img_bin
    return img_bin


# Weighting parameters, this will decide the quantity of an image to be added to make a new image.
def merge_two_images(verticle_lines_img, horizontal_lines_img):
    alpha = 0.5
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return img_final_bin


def vertical_horizontal_lines_extractor(img_bin):
    x = 50
    # Defining a kernel length
    global horizontal_lines_img, verticle_lines_img, kernel
    kernel_length = np.array(img_bin).shape[1] // x

    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # Morphological operation to detect vertical lines from an image
    img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
    verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=3)
    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)
    return verticle_lines_img, horizontal_lines_img


def sort_contours(cnts, method="left-to-right"):
    # initialize the reverse flag and sort index
    reverse = False
    i = 0

    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True

    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1

    # construct the list of bounding boxes and sort them from top to
    # bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))

    # return the list of sorted contours and bounding boxes
    return cnts, boundingBoxes


def image_slicer(main_image, user_dir_bin):
    # Read the image
    img = cv2.imread(main_image, 0)

    # Apply Thresholding on image to make it look clear
    img_bin = threshold_and_invert_img(img)

    # Extract Vertical and Horizontal lines from the image
    vertical_line_image, horizontal_line_image = vertical_horizontal_lines_extractor(img_bin)

    # Merge vertical_line and horizontal_line image to make one image
    merged_image = merge_two_images(vertical_line_image, horizontal_line_image)
    # temp = cv2.resize(merged_image, (600, 800))
    # cv2.imshow('image', temp)
    # cv2.waitKey(0)

    # print(type(merged_image))

    # Find contours on the image
    contours, hierarchy = cv2.findContours(merged_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort all the contours by top to bottom.
    contours, boundingBoxes = sort_contours(contours, method="top-to-bottom")

    idx = 0
    for c in contours:
        # Returns the location and width,height for every contour
        x, y, w, h = cv2.boundingRect(c)
        print(w, h)
        # If the box height is greater then 20, width is >80, then only save it as a box in "cropped/" folder.
        if 1000 > w > 400 and 700 > h > 400:
            # print(w,h)
            idx += 1
            new_img = img[y:y + h, x:x + w]

            # plt.subplot(10,1, idx)
            final_crop_output = user_dir_bin + str(idx) + ".png"
            cv2.imwrite(final_crop_output, new_img)
            # plt.axis('off')
    os.remove(main_image)