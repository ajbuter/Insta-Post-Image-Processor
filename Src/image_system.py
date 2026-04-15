import os, sys
from PIL import Image, ImageOps

white = (255, 255, 255)

class landscape:
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
        return newIm

    def imageSystem2Pics(im1: Image.Image, im2:Image.Image, pad):
        im3 = landscape.merge(im1, im2, pad)
        im3 = landscape.resize(im3)
        im3 = landscape.border(im3)
        return im3

    def process_landscape(file1, file2=None, outFile="output_landscape.jpg"):
        im1 = Image.open(file1)

        if file2 is not None:
            im2 = Image.open(file2)
            if not landscape.size(im1, im2):
                im1, im2 = landscape.scale(im1, im2)
            im3 = landscape.imageSystem2Pics(im2, im1, 0.05)
        else:
            im3 = landscape.imageSystem1Pic(im1)
            
        im3.save(outFile)

    def imageSystem1Pic(im1: Image.Image):
        im3 = landscape.resize(im1)
        im3 = landscape.border(im3)
        return im3

class portrait:
    def size(im1: Image.Image, im2: Image.Image):
        sizeEqual = True
        print(f'im1 size: {im1.size}, im2 size: {im2.size}')
        if im1.size != im2.size:
            sizeEqual = False
        print(sizeEqual)
        return sizeEqual

    def scale(im1: Image.Image, im2: Image.Image):
        slot = (500, 680)
        im1 = ImageOps.cover(im1, slot)
        im2 = ImageOps.cover(im2, slot)
        im3 = Image.new(im2.mode,(505,685), color=(white))
        im3.paste(im2,(5,5))
        return im1, im3

    def stagger(im1: Image.Image, im2: Image.Image) -> Image.Image:
        canvas_w, canvas_h = 920, 1150
        im = Image.new(im1.mode, (canvas_w, canvas_h), color=(white))

        im.paste(im1, (0, 0))
        x2 = canvas_w - im2.size[0]
        y2 = canvas_h - im2.size[1]
        im.paste(im2, (x2, y2))

        return im

    def resize(im: Image.Image):
        small_sz = (920, 1050)
        im = ImageOps.cover(im, small_sz)
        return im

    def border(im: Image.Image):
        newIm = Image.new(im.mode, (1080, 1350), color=(white))
        print(f"Border {int((newIm.width - im.width)/2)},{int((newIm.height-im.height)/2)}")
        newIm.paste(im, (int((newIm.width - im.width)/2), int((newIm.height-im.height)/2)))
        return newIm

    def imageSystem2Pics(im1: Image.Image, im2: Image.Image):
        im3 = portrait.stagger(im1, im2)
        im3 = portrait.border(im3)
        return im3

    def imageSystem1Pic(im1: Image.Image):
        im3 = portrait.resize(im1)
        im3 = portrait.border(im3)
        return im3

    def process_portrait(file1, file2=None, outFile="output_portrait.jpg"):
        im1 = Image.open(file1)

        if file2 is not None:
            im2 = Image.open(file2)
            im1, im2 = portrait.scale(im1, im2)
            im3 = portrait.imageSystem2Pics(im1, im2)
        else:
            im3 = portrait.imageSystem1Pic(im1)

        im3.save(outFile)


if __name__ == "__main__":
    landscape.process_landscape("imageTest1.jpg", "imageTest2.jpg", "output_landscape.jpg")
    portrait.process_portrait("imageTest1.jpg", "imageTest2.jpg", "output_portrait.jpg")
    portrait.process_portrait("imageTest1.jpg", outFile="output_portrait_single.jpg")