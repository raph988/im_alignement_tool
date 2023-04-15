# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 11:56:37 2018

@author: raph988

The image alignement is based on the fact that both images match at least at 60%. Then the smallest image is set as template to match in the second image.
Based on template matching implemented in OpenCV.
"""


import numpy as np
import cv2
import os



    
    
def draw_missalignement(im1, im2):
    # Find size of image1
    sz = im1.shape
     
    # Define the motion model
    warp_mode = cv2.MOTION_TRANSLATION
     
    # Define 2x3 or 3x3 matrices and initialize the matrix to identity
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        warp_matrix = np.eye(3, 3, dtype=np.float32)
    else :
        warp_matrix = np.eye(2, 3, dtype=np.float32)
     
    # Specify the number of iterations.
    number_of_iterations = 5000;
     
    # Specify the threshold of the increment
    # in the correlation coefficient between two iterations
    termination_eps = 1e-10;
     
    # Define termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)
     
    # Run the ECC algorithm. The results are stored in warp_matrix.
    (cc, warp_matrix) = cv2.findTransformECC (im1, im2, warp_matrix, warp_mode, criteria)
     
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        # Use warpPerspective for Homography 
        im2_aligned = cv2.warpPerspective (im2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    else :
        # Use warpAffine for Translation, Euclidean and Affine
        im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
     
    # Show final results
    cv2.imshow("Image 1", im1)
    cv2.imshow("Image 2", im2)
    cv2.imshow("Aligned Image 2", im2_aligned)
    # cv2.waitKey(0)


def get_translation_transform(im1, im2, debug_mode=False):
    
    h2, w2 = im2.shape
    template_ratio = 1/3
    template = im2[int(h2*template_ratio):int(h2-h2*template_ratio), int(w2*template_ratio):int(w2-w2*template_ratio)]
    w, h = template.shape[::-1]
    
    img = im1.copy()
    method = cv2.TM_CCORR_NORMED

    # Apply template Matching
    res = cv2.matchTemplate(img, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    
    translation = [ int(top_left[0] - w2/3 ), int(top_left[1]-h2/3) ]
    
    if debug_mode:
        print(int(h2-template_ratio), int(h2-h2*template_ratio))
        cv2.imshow("orginal im1", im1)
        cv2.imshow("orginal im2", im2)
    
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(img, top_left, bottom_right, 255, 2)
        cv2.imshow("im1 + rect", img)
        cv2.imshow("template", template)
    
    return translation


def RealignImages(im1, im2, cut_bottom=False, debug_mode=False):
    if isinstance(im1, str) and os.path.exists(im1):
        im1 = cv2.imread(im1, 0)
    if isinstance(im2, str) and os.path.exists(im2):
        im2 = cv2.imread(im2, 0)
    
    if im1.shape != im2.shape:
        shape = ( min(im1.shape[1], im2.shape[1]), min(im1.shape[0], im2.shape[0]) )
        im1 = cv2.resize(im1, shape)
        im2 = cv2.resize(im2, shape)
    
    if cut_bottom:
        width = 50
        if isinstance(cut_bottom, int): width = cut_bottom
        im1, im2 = im1[:-width, :], im2[:-width, :]
    
    trans = get_translation_transform(im1, im2, debug_mode)
    
    new_im1_p1 = [ 0 if trans[0] < 0 else abs(trans[0]), 0 if trans[1] < 0 else abs(trans[1]) ]
    new_im1_p2 = [ im1.shape[1] + trans[0] if trans[0] < 0 else im1.shape[1] , 
                      im1.shape[0] + trans[1] if trans[1] < 0 else im1.shape[0] ]
    
    dx, dy = 0, 0
    new_im2_p1 = [ 0 if trans[0] > 0 else abs(trans[0]), 0 if trans[1] > 0 else abs(trans[1]) ]
    new_im2_p2 = [ im2.shape[1] if trans[0] < 0 else im2.shape[1] - trans[0], 
                      im2.shape[0] if trans[1] < 0 else im2.shape[0] - trans[1]]
    
    new_im2_p1[0] += dx
    new_im2_p1[1] += dy
    new_im2_p2[0] += dx
    new_im2_p2[1] += dy
    
    if debug_mode:
        tmp1 = im1.copy()
        cv2.rectangle(tmp1, tuple(new_im1_p1), tuple(new_im1_p2), 255, 2)
        cv2.imshow('tmp1', tmp1)
        
        tmp2 = im2.copy()
        cv2.rectangle(tmp2, tuple(new_im2_p1), tuple(new_im2_p2), 255, 2)
        cv2.imshow('tmp2', tmp2)
    
    
    new_im_1 = im1[ new_im1_p1[1]:new_im1_p2[1], new_im1_p1[0]:new_im1_p2[0]]
    new_im_2 = im2[ new_im2_p1[1]:new_im2_p2[1], new_im2_p1[0]:new_im2_p2[0]]
    return new_im_1, new_im_2


def gradientDiff(im1, im2, debug_mode=False):
    sobelx64f = cv2.Sobel(im1, cv2.CV_64F, 1, 0,ksize=5)
    sobel_im1 = np.absolute(sobelx64f)
    sobel_im1 = cv2.normalize(sobel_im1, None, 0, 1, cv2.NORM_MINMAX, cv2.CV_64F)
    sobel_im1 = cv2.blur(sobel_im1,(5,5))
    
    sobelx64f = cv2.Sobel(im2, cv2.CV_64F,1,0,ksize=5)
    sobel_im2 = np.absolute(sobelx64f)
    sobel_im2 = cv2.normalize(sobel_im2, None, 0, 1, cv2.NORM_MINMAX, cv2.CV_64F)
    sobel_im2 = cv2.blur(sobel_im2,(5,5))
    
    
    if debug_mode:
        cv2.imshow("sobel im1", sobel_im1)
        cv2.imshow("sobel im2", sobel_im2)
        
    sub = abs(sobel_im1 - sobel_im2)
    sub = cv2.normalize(sub*2, None, 0, 1, cv2.NORM_MINMAX, cv2.CV_64F)
    return sub


def main():
    
    im_number = 3
    im_type = ".jpg"
    global_path = "./"
    
    im_top = str(im_number)+"_top"+im_type
    im_bottom = str(im_number)+"_bottom"+im_type
    
    im1 = cv2.imread(global_path+im_top, 0)
    
    im2 = cv2.imread(global_path+im_bottom, 0)
    
    new_im_1, new_im_2 = RealignImages(im1, im2, cut_bottom=True)
    
    res = gradientDiff(new_im_1, new_im_2, True)
    
    cv2.imshow('new_im_1', new_im_1)
    cv2.imshow('new_im_2', new_im_2)
    cv2.imshow('res', res)
    
    cv2.waitKey(0), cv2.destroyAllWindows()
    
    
    
    
if __name__ == '__main__':
    main()
    
    
    
    
    