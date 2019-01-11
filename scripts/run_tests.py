import os
import os.path as osp
import argparse
import sys

import cv2

import numpy as np
from math import floor

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

        
def parse_args():
    parser = argparse.ArgumentParser(
        description='Script to create run tests on some images')
    parser.add_argument('imfolder', help='image folder')
    parser.add_argument('immask', help='mask folder')
    parser.add_argument('outfolder', help='folder where to put result')
    #parser.add_argument('mask form', help='folder where to put result')
    args = parser.parse_args()
    return args


def centered_square(photo):
    h, w  = photo.shape[:2]
    mask = np.zeros_like(photo)
    r = floor(min(h, w)/3)
    
    # fill the square
    mask[int(h/2 - r/2):int(h/2 + r/2), int(w/2 - r/2):int(w/2 + r/2)] = 255
    return mask


def create_masks(imlist, path, maskpath):
    create_dir(maskpath)
    for imname in imlist:
        image_name = ".".join(imname.split(".")[:-1])
        ext = imname.split(".")[-1]

        impath = osp.join(path, image_name + "." + ext)
        photo = cv2.imread(impath)

        mask = centered_square(photo)
        mpath = osp.join(maskpath, image_name + "_mask." + ext)

        cv2.imwrite(mpath, mask)
    

def inpaint(image, imfolder, maskfolder, layer, noise, outfolder):
    # command creator
    image_name = ".".join(image.split(".")[:-1])
    image_mask = image_name + "_mask." + image.split(".")[-1]

    impath = osp.join(imfolder, image)
    immask = osp.join(maskfolder, image_mask)
    command = "th inpaint_test.lua --input " + impath + " --mask " + immask + " --layer " + layer + " --noise " + noise

    #print(command)

    # execute inpainting
    os.system(command)

    # move files arround
    move1 = "mv input.png " + osp.join(outfolder, image_name + "_in.png")
    move2 = "mv out.png " + osp.join(outfolder, image_name + "_out.png")
    #print(move1)
    #print(move2)

    # execute moving
    #os.system(move1)
    #os.system(move2)


LAYERS = ["1", "2", "4", "5", "7", "8", "10", "11", "13", "14", "16", "17", "19", "20", "22", "23", "25", "26", "28", "29", "31", "32", "34", "35", "37", "38", "40", "41", "43", "44", "46", "47", "49"]
NOISES = ["0.00", "0.01", "0.02", "0.03", "0.04", "0.05", "0.06", "0.07", "0.08", "0.09", "0.10"]

if __name__ == "__main__":
    args = parse_args()
    impath = args.imfolder
    immask = args.immask
    outfolder = args.outfolder

    imlist = os.listdir(impath)
    number_images = len(imlist)

    create_masks(imlist, impath, immask)

    # iterate over noise and layers
    for ino, noise in enumerate(NOISES):
        for ila, layer in enumerate(LAYERS):
            layer_name = "layer_" + layer.zfill(2)
            noise_name = "noise_" + noise
            out = osp.join(outfolder, layer_name, noise_name)
            #create_dir(out)
            string = "Files in " + out + " are processed: "

            for iim, image in enumerate(imlist):
                # show computation
                all_string = "\r" + string + str(iim+1) + "/" + str(number_images)
                sys.stdout.write(all_string)
                sys.stdout.flush()

                # computation
                inpaint(image, impath, immask, layer, noise, out)
                
            # end print()
            sys.stdout.write("\n")
            #inpaint()
            
