import pygame

# This is a list of all universal functions for colour codex

def readColors(filename="colours"):
    # This returns all of the colors with their name and rgb in a dictionary
    # This also returns a dictionary with the effect that it has to the rgb

    lines = []
    colorlist = [] # For keeping track of the order of colors (dictionaries are not ordered)

    with open(filename+".txt", "r") as f:
        for line in f:
            lines.append(line)

    colorConversionRGB = {}
    colorConversionEffect = {}

    for line in lines:
        values = line.split(";")
        # Getting the values
        colorName = eval(values[0])
        colorEffect = eval(values[1])
        colorRGB = eval(values[2])
        
        # Making "None" now be None (without string)
        if colorEffect == "None": colorEffect = None

        # Adding them to the dictionaries
        colorConversionRGB[colorName] = colorRGB
        colorConversionEffect[colorRGB] = colorEffect

        # Adding the color name to the order list
        colorlist.append(colorName)

    return colorlist, colorConversionRGB, colorConversionEffect
