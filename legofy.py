import requests
from bs4 import BeautifulSoup
import pandas as pd

print("Hello lego world")

# download the color table website
headers = {'User-Agent': "Mozilla/5.0"}

r = requests.get("https://www.bricklink.com/catalogColors.asp", headers=headers)


# parse the information

# helper function; translates hexcodes to integers
def hextoint(hexcode):
    return (int(hexcode[:2], 16), int(hexcode[2:4], 16), int(hexcode[4:], 16))

tree = BeautifulSoup(r.text, "lxml")

# select the fourth table in the HTML for solid colours
html_table = tree.select("table")[3].select("table")[0]
# let pandas read the table
colour_table = pd.read_html(str(html_table), header=0)[0]
colour_table = colour_table.drop(["Unnamed: 1", "Unnamed: 2"], axis=1)
# select the RGB values from the HTML background colour and build three new columns with them
rgb_table = pd.DataFrame([hextoint(td.attrs["bgcolor"]) for td in html_table.select("td[bgcolor]")],
                         columns=["r", "g", "b"])
colour_table = colour_table.merge(rgb_table, left_index=True, right_index=True)
# select colours which are available in 2017 and which are not rare to find
current_colours = colour_table[colour_table["Color Timeline"].str.contains("2017")]
current_colours = current_colours[~(current_colours["Name"].str.contains("Flesh")
                                    | current_colours["Name"].str.contains("Dark Pink")
                                    | (current_colours["Name"] == "Lavender")
                                    | current_colours["Name"].str.contains("Sand Blue"))]

print(current_colours)
