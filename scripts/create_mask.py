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


class Form(Enum):
    RECT = 0
    CIRCLE = 1


def toggle_form(mode):
    Forms = list(Form)
    return Forms[(mode.value + 1) % len(Forms)]

def toggle_mode(mode):
    Modes = list(Mode)
    return Modes[(mode.value + 1) % len(Modes)]


sq2_2 = 0.707107

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


def form_on_mask(param, mask_name, fill=-1):
    mask = param[mask_name]
    x, y = param["x"], param["y"]
    radus = param["radus"]
    mode = param["mode"]
    form = param["form"]
    color = colors_action[mode] if mask_name=="mask" else colors_cursor[mode]        
        
    if form==Form.CIRCLE:
        cv2.circle(mask, (x,y), radus, color, fill)
        
    elif form==Form.RECT:
        x1, y1 = int(x - sq2_2*radus), int(y - sq2_2*radus)
        x2, y2 = int(x + sq2_2*radus), int(y + sq2_2*radus)
        cv2.rectangle(mask, (x1, y1), (x2, y2), color, fill)

# mouse callback function
def draw_form(event, x, y, flags, param):
    mode = param["mode"]
    param["x"] = x
    param["y"] = y

    # Remove old movement
    param["mask_cur"] = param["mask_cur"]*0
    
    color_cursor = colors_cursor[mode]
    form_on_mask(param, "mask_cur")

    if event == cv2.EVENT_LBUTTONDOWN:
        param["drawing"] = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if param["drawing"] == True:
            form_on_mask(param, "mask")
        
    elif event == cv2.EVENT_LBUTTONUP:
        param["drawing"] = False
        form_on_mask(param, "mask")


def mix_images(image, mask, mask_cur, mode):
    mix = np.copy(image)
    mix[mask==white] = 255
    cursor = (mask_cur==colors_cursor[mode]).all(axis=2)
    mix[cursor] = colors_cursor[mode]
    return mix


def save_mask(mask, path):
    cv2.imwrite(path, mask)


def print_help(impath, outpath):
    print("This is a tool to create a mask from an input image")
    print("-> To change mode (add/remove) press t")
    print("-> To change form (circle/rectangle) press f")
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
    param["mask_cur"] = np.zeros_like(image)
    param["mode"] = Mode.ADD
    
    param["drawing"] = False
    param["radus"] = 20
    param["x"] = -1
    param["y"] = -1

    param["form"] = Form.CIRCLE
    
    cv2.namedWindow(name)
    cv2.setMouseCallback(name, draw_form, param)

    def trackbar_callback(radus):
        param["radus"] = radus
        
    cv2.createTrackbar('Radus',name, param["radus"], 100, trackbar_callback)


    while(1):
        mix = mix_images(image, param["mask"], param["mask_cur"], param["mode"])

        cv2.imshow(name, mix)
        k = cv2.waitKey(1) & 0xFF
        # If it is escape
        if k == 27 or k==ord("q"):
            break

        elif k==ord("t"):            
            param["mode"] = toggle_mode(param["mode"])
            param["mask_cur"] = param["mask_cur"]*0
            form_on_mask(param, "mask_cur")
            
        elif k==ord("f"):
            param["form"] = toggle_form(param["form"])
            param["mask_cur"] = param["mask_cur"]*0
            form_on_mask(param, "mask_cur")
            
        elif k==ord("s"):
            print(outpath)
            save_mask(param["mask"
            ], outpath)

            print("File saved in \"" + outpath + "\"")
    
    cv2.destroyAllWindows()
