import requests
from bs4 import BeautifulSoup
import pandas as pd

import utils

print("Legofy!")

print('Getting available colors...')
# download the color table website
headers = {'User-Agent': "Mozilla/5.0"}
r = requests.get("https://www.bricklink.com/catalogColors.asp", headers=headers)

# parse the information
tree = BeautifulSoup(r.text, "lxml")
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

print('Available colors:')
pd.set_option('display.expand_frame_repr', False)
print(current_colors)
