import cv2
import argparse
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(
        description='Script to create mask of an input image')
    parser.add_argument('image', help='imput image')
    parser.add_argument('--output', help='output mask', default=None)
    args = parser.parse_args()
    return args

drawing = False # true if mouse is pressed
ix,iy = -1,-1
radus = 25
white = (255,255,255)

# mouse callback function
def draw_circle(event,x,y,flags,param):
    global ix,iy,drawing
    mask = param["mask"]
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            cv2.circle(mask,(x,y),radus,white,-1)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.circle(mask,(x,y),radus,white,-1)
            

def mix_images(image, mask):
    m = mask==255
    mix = np.copy(image)
    mix[m] = 255
    return mix


def save_mask(mask, path):
    cv2.imwrite(path, mask)
    

if __name__ == "__main__":
    args = parse_args()
    impath = args.image
    
    if args.output:
        outpath = args.output
    else:
        l = impath.split('.')
        outpath = l[0] + "_mask." + l[1]
        
    image = cv2.imread(impath)
    name = "image"
    mask = np.zeros_like(image)
    param = {}
    param["mask"] = mask
    
    cv2.namedWindow(name)
    cv2.setMouseCallback(name, draw_circle, param)

    while(1):
        mix = mix_images(image, mask)
        cv2.imshow(name, mix)
        k = cv2.waitKey(1) & 0xFF
        # If it is escape
        if k == 27:
            break
        elif k==ord("s"):
            print(outpath)
            save_mask(mask, outpath)

            print("File saved in ", outpath)
    
    cv2.destroyAllWindows()
