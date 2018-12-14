import cv2
import argparse
import numpy as np

from enum import Enum

def parse_args():
    parser = argparse.ArgumentParser(
        description='Script to create mask of an input image')
    parser.add_argument('image', help='imput image')
    parser.add_argument('--output', help='output mask', default=None)
    args = parser.parse_args()
    return args


class Mode(Enum):
    ADD = 0
    REMOVE = 1


def toggle_mode(mode):
    if mode==Mode.ADD:
        return Mode.REMOVE
    elif mode==Mode.REMOVE:
        return Mode.ADD
    else:
        print("Cannot happend toggle_mode")
        return None
    
white = (255,255,255)
black = (0,0,0)
blue = (255,0,0)
red = (0,0,255)

colors_cursor = {}
colors_cursor[Mode.ADD] = blue
colors_cursor[Mode.REMOVE] = red

colors_action = {}
colors_action[Mode.ADD] = white
colors_action[Mode.REMOVE] = black


def circle_on_mask(mask, x, y, radus, color, fill=-1):
    cv2.circle(mask, (x,y), radus, color, fill)


# mouse callback function
def draw_circle(event, x, y, flags, param):
    mask = param["mask"]
    param["maskr"] = param["maskr"]*0
    mode = param["mode"]
    param["x"] = x
    param["y"] = y
    
    color_cursor = colors_cursor[mode]
    circle_on_mask(param["maskr"], x, y, param["radus"], color_cursor)

    if event == cv2.EVENT_LBUTTONDOWN:
        param["drawing"] = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if param["drawing"] == True:
            color_action = colors_action[mode]
            circle_on_mask(param["mask"], x, y, param["radus"], color_action)
        
    elif event == cv2.EVENT_LBUTTONUP:
        param["drawing"] = False
        color_action = colors_action[mode]
        circle_on_mask(param["mask"], x, y, param["radus"], color_action)

            

def mix_images(image, mask, maskr, mode):
    mix = np.copy(image)
    mix[mask==white] = 255
    cursor = (maskr==colors_cursor[mode]).all(axis=2)
    mix[cursor] = colors_cursor[mode]
    return mix


def save_mask(mask, path):
    cv2.imwrite(path, mask)


def print_help(impath, outpath):
    print("This is a tool to create a mask from an input image")
    print("-> To change mode (add/remove) press t")
    print("-> To save the image, press s")
    print("-> To change radus, use the trackbar")
    print("-> To quit, press ESQ or q")
    print()
    print("You are using the image \"" + impath + "\" the mask image will be saved in \"" + outpath + "\"")

if __name__ == "__main__":
    args = parse_args()
    impath = args.image
    
    if args.output:
        outpath = args.output
    else:
        l = impath.split('.')
        outpath = l[0] + "_mask." + l[1]

    print_help(impath, outpath)
    
    image = cv2.imread(impath)
    name = "image"
    
    param = {}
    param["mask"] = np.zeros_like(image)
    param["maskr"] = np.zeros_like(image)
    param["mode"] = Mode.ADD
    
    param["drawing"] = False
    param["radus"] = 20
    param["x"] = -1
    param["y"] = -1
    
    cv2.namedWindow(name)
    cv2.setMouseCallback(name, draw_circle, param)

    def trackbar_callback(radus):
        param["radus"] = radus
        
    cv2.createTrackbar('Radus',name, param["radus"], 100, trackbar_callback)


    while(1):
        mix = mix_images(image, param["mask"], param["maskr"], param["mode"])

        cv2.imshow(name, mix)
        k = cv2.waitKey(1) & 0xFF
        # If it is escape
        if k == 27 or k==ord("q"):
            break

        elif k==ord("t"):            
            param["mode"] = toggle_mode(param["mode"])
            circle_on_mask(param["maskr"], param["x"], param["y"], param["radus"], colors_cursor[param["mode"]])
        elif k==ord("s"):
            print(outpath)
            save_mask(param["mask"
            ], outpath)

            print("File saved in \"" + outpath + "\"")
    
    cv2.destroyAllWindows()
