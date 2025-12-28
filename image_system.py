import os, sys
from PIL import Image, ImageOps

white = (255, 255, 255)

def size(im1: Image.Image, im2: Image.Image):
    sizeEqual = True
    print(f'im1 size: {im1.size}, im2 size: {im2.size}')
    if im1.size != im2.size:
        sizeEqual = False
    print(sizeEqual)
    return sizeEqual
    
def scale(im1: Image.Image, im2: Image.Image): 
    if im1.size[1] < im2.size[1] or im1.size[0] < im2.size[0]:
        im2 = ImageOps.cover(im2, im1.size)
    elif im1.size[1] > im2.size[1] or im1.size[0] > im2.size[0]:
        im1 = ImageOps.cover(im1, im2.size)
    else:
        None

    return im1, im2

def merge(im1: Image.Image, im2: Image.Image, pad: float=0) -> Image.Image:
    h = im1.size[1] + im2.size[1]
    pad *= (0.5 * h)
    w = max(im1.size[0], im2.size[0])
    im = Image.new(im1.mode, (w, h + int(pad)), color = (white))

    im.paste(im1)
    im.paste(im2, (0, im1.size[1] + int(pad)))

    return im

def resize(im: Image.Image):
    small_sz = (920,1050)
    im = ImageOps.cover(im, small_sz)
    return im

def border(im: Image.Image):
    newIm = Image.new(im.mode, (1080, 1350), color = (white))
    print(f"Border {int((newIm.width - im.width)/2)},{int((newIm.height-im.height)/2)}")
    newIm.paste(im, (int((newIm.width - im.width)/2),int((newIm.height-im.height)/2)))
    #newIm = ImageOps.pad(im, (1080, 1350), color = (white))
    #im3 = ImageOps.pad(im3, (1080,1350), color = (white))
    return newIm

def imageSystem2Pics(im1: Image.Image, im2:Image.Image, pad):
    im3 = merge(im1, im2, pad)
    im3 = resize(im3)
    im3 = border(im3)
    return im3

im1 = Image.open("imageTest1.jpg")
im2 = Image.open("imageTest2.jpg")

if not size(im1, im2):
    im1, im2 = scale(im1, im2)

im3 = imageSystem2Pics( im2, im1, 0.05)
 
im3.show()
im3.save("outputImage.jpg")
