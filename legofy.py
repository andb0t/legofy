import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter
from sklearn.neighbors import NearestNeighbors

import utils


def load_colors():
    black_and_white = False
    print('Getting available colors ...')
    # download the color table website
    headers = {'User-Agent': "Mozilla/5.0"}
    req = requests.get("https://www.bricklink.com/catalogColors.asp", headers=headers)

    # parse the information
    tree = BeautifulSoup(req.text, "lxml")
    # select the fourth table in the HTML for solid colors
    html_table = tree.select("table")[3].select("table")[0]
    # let pandas read the table
    color_table = pd.read_html(str(html_table), header=0)[0]
    color_table = color_table.drop(["Unnamed: 1", "Unnamed: 2"], axis=1)
    # select the RGB values from the HTML background color and build three new columns with them
    rgb_table = pd.DataFrame([utils.hextoint(td.attrs["bgcolor"]) for td in html_table.select("td[bgcolor]")],
                             columns=["r", "g", "b"])
    color_table = color_table.merge(rgb_table, left_index=True, right_index=True)
    # select colors which are available in 2017 and which are not rare to find
    current_colors = color_table[color_table["Color Timeline"].str.contains("2017")]
    current_colors = current_colors[~(current_colors["Name"].str.contains("Flesh")
                                      | current_colors["Name"].str.contains("Dark Pink")
                                      | (current_colors["Name"] == "Lavender")
                                      | current_colors["Name"].str.contains("Sand Blue"))]
    if black_and_white:
        current_colors = color_table[color_table["Name"].str.contains("White")
                                     | color_table["Name"].str.contains("Black")]

    print('Available colors:')
    pd.set_option('display.expand_frame_repr', False)
    print(current_colors)
    return current_colors


def quantize_colors(picture):
    current_colours = load_colors()

    print('Quantize colors ...')
    # fit the NN to the RGB values of the colours; only one neighbour is needed
    nn = NearestNeighbors(n_neighbors=1, algorithm='brute')
    nn.fit(current_colours[["r", "g", "b"]])

    # helper function; finds the nearest colour for a given pixel
    def legofy_pixels(pixel, neighbors, colours):
        new_pixel = neighbors.kneighbors(pixel.reshape(1, -1), return_distance=False)[0][0]
        return tuple(colours.iloc[new_pixel, -3:])

    # Quantize!
    picture = np.array(picture)
    picture = np.apply_along_axis(legofy_pixels, 2, picture, nn, current_colours)
    picture = Image.fromarray(np.uint8(pixelated), mode="RGB")

    return picture


def pixelate_picture(picture):
    print('Pixelate image ...')
    picture = picture.filter(ImageFilter.MedianFilter(7)).resize((2*w10, 2*h10))
    return picture


print('Open image')
image = Image.open("heman.jpg")

print('Scale image')
# get a 10th of the image dimensions and the aspect ratio
w10 = int(image.size[0]/10)
h10 = int(image.size[1]/10)
ratio = image.size[0]/image.size[1]
# smooths the image and scales it to 20%

# pixelate
pixelated = pixelate_picture(image)

# quantize colors
pixelated = quantize_colors(pixelated)

print('Scale back')
# reduce the size of the image according to aspect ratio (32,x)
if ratio < 1:
    h = 32
    w = int(32*ratio)
else:
    w = 32
    h = int(32/ratio)

print('Get final image')
final = pixelated.resize((w, h))
final.save('lego_heman.jpg')

print('Transform to numpy array')
final_arr = np.array(final)  # image as array
