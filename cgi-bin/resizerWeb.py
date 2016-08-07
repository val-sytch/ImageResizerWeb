#!/usr/bin/env python3

import cgi
import os
import sys

try:
    from PIL import Image, ImageEnhance
except ImportError:
    exit("Please, install Pillow firstly.")


def image_resize(image_name, width, height, path_to_save):
    """Resizes the image and saves it to the path_to_save.
    Use compare_width_height() .
    If required width and height aren't equal to resized image, leave transparent spase
    around image.
    
    """    
    image = Image.open(image_name).convert('RGBA')
    image_width, image_height = image.size
    
    checked_img_size = compare_width_height(width, height, image_width, image_height)
    image_width, image_height = checked_img_size
    
    layer = Image.new('RGBA', (width, height), (0,0,0,0))
    resized_image = image.resize((int(image_width), int(image_height)))
    position = (int((width - image_width)/2), int((height - image_height)/2))
    layer.paste(resized_image, position)
    new_image_name = image_name.rsplit('.')[0]+".png"
    layer.save(os.path.join(path_to_save,new_image_name),"PNG")
    #add a name of resized file to dict. Done for communication between functions
    size_of_images[new_image_name] = checked_img_size

def compare_width_height(width, height, image_width, image_height):
    """Compare required size(width,height) of image with initial size(image_width, image_height).
    Return decreased width and height  with saved proportions.
    If initial size of image is already less than required - do nothing.
    
    """
    if (width <= image_width and height <= image_height):
        if image_width >= image_height:
            image_height = (image_height * width) / image_width
            image_width = width
        else:
            image_width = (image_width * height) / image_height
            image_height = height
    elif width < image_width and height > image_height:
        image_height = (image_height * width) / image_width
        image_width = width
    elif width > image_width and height < image_height:
        image_width = (image_width * height) / image_height
        image_height = height
    return (int(image_width),int(image_height))

def put_watermark(image_name, watermark, path_to_save, opacity):
    """Adds a watermark image to the input picture."""
    
    watermark = Image.open(watermark)
    if watermark.mode != 'RGBA':
        watermark = watermark.convert('RGBA')
    alpha = watermark.split()[3]
    #reduce the brightness or the 'alpha' band
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    watermark.putalpha(alpha)
    image = Image.open(image_name)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    # use compare_width_height() to but watermark only on image, avoiding transparent space
    checked_watermark_size = compare_width_height(size_of_images[image_name][0], size_of_images[image_name][1],\
                                                  watermark.size[0], watermark.size[1])
    watermark = watermark.resize(checked_watermark_size)
    layer = Image.new('RGBA', image.size, (0,0,0,0))
    position = (int((image.size[0]-watermark.size[0])/2),int((image.size[1]-watermark.size[1])/2))
    layer.paste(watermark, position)
    Image.composite(layer, image, layer).save(os.path.join(path_to_save, image_name),"PNG")


print("Content-type: text/html\n")
print("""<!DOCTYPE HTML>
        <html>
        <head>
           <meta charset="utf-8">
           <title>Image resizer</title>
        </head>
        <body>""")
form = cgi.FieldStorage()

path_to_get = form.getfirst("path_to_get")
path_to_save = form.getfirst("path_to_save")
width = int(form.getfirst("width"))
height = int(form.getfirst("height"))
watermark = form.getfirst("watermark_file")
opacity = float(form.getfirst("opacity","0.3"))
img_to_get = form.getfirst("img_to_get")

#check for correct input
if path_to_get is None or \
   path_to_save is None or \
   width is None or \
   height is None:
    print("""<h2>Oops! You left some required fields empty. Please try again!</h2>
            <a href="../resizer.html">Return to main page</a>
            </body>
            </html>""")
    exit()
#create empty dict for communication between functions
size_of_images = {}

#resizing images or single image    
os.chdir(path_to_get)
if img_to_get is not None:
    image_resize(img_to_get, width, height, path_to_save)
    print("<h4>Your image resized.</h4>")
else:
    for image_name in os.listdir(path_to_get):
        if image_name.lower().endswith('.png') or \
           image_name.lower().endswith('.jpg'):
            image_resize(image_name, width, height, path_to_save)
    print("<h4>Your images resized.</h4>")

# put a watermark(optional)
if watermark is not None:
    os.chdir(path_to_save)
    for key in size_of_images:
        put_watermark(key, watermark, path_to_save, opacity)
    print("<h4>Watermark added.</h4>")
        
print("""<a href="../resizer.html">Return to main page</a>
        </body>
        </html>""")

