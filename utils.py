# helper function; translates hexcodes to integers
def hextoint(hexcode):
    return (int(hexcode[:2], 16), int(hexcode[2:4], 16), int(hexcode[4:], 16))
