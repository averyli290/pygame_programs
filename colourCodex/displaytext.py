import pygame, sys

def text_objects(text, font, color, bgcolor=(30,30,30), margin=1.25, rotation=0):
    textSurface = font.render(text, True, color)
    textSurface = pygame.transform.rotate(textSurface, rotation)

    # Making the margins
    marginSurface = pygame.Surface((textSurface.get_width()*margin, textSurface.get_height()*margin))
    marginSurface.fill(bgcolor)
    marginSurface.blit(textSurface, ((marginSurface.get_width()-textSurface.get_width())/2, 
                                      (marginSurface.get_height()-textSurface.get_height())/2)) # Now blitting the text surface

    return marginSurface, textSurface, textSurface.get_rect()

def display_text(text, size, font, color, bgcolor=(30,30,30), margin=1.25, rotation=0):
    pygame.font.init()
    torender = pygame.font.Font(font, size)
    MarginSurf, TextSurf, TextRect = text_objects(text, torender, color, bgcolor, margin, rotation)
    TextRect.center = (0, 0)
    return MarginSurf, TextSurf, TextRect

def display_text_paragraph(surface, referencePoint, text, size, font, margin=1.25, centered=False, color=(0,0,0), bgcolor=(30,30,30), rotation=0):
    pygame.font.init()
    # Displays a paragraph of text
    # Reference point is the top left if text is not centered, otherwise, y and x is the centerx
    textlist = text.split("\n")
    x, y = referencePoint
    for line in textlist:
        marginSurf, textSurf, textRect = display_text(line, size, font, color, bgcolor, margin, rotation) # Now getting the y increment from this
        if centered: # Checking for centering
            x = referencePoint[0]-marginSurf.get_width()/2
        surface.blit(marginSurf, (x, y)) # Adding the text to the surface
        # Updating x and y
        y += marginSurf.get_height()

def text_objects_alpha(text, font, color, alpha=255, bgcolor=(30,30,30), margin=0.25, rotation=0):
    textSurface = font.render(text, True, color)
    textSurface = pygame.transform.rotate(textSurface, rotation)

    # Making the alpha surface
    alphaSurface = pygame.Surface((textSurface.get_width()*(1+margin), textSurface.get_height()*(1+margin)))
    alphaSurface.fill(bgcolor)
    alphaSurface.set_alpha(alpha)
    alphaSurface.blit(textSurface, (textSurface.get_width()*margin/2, textSurface.get_height()*margin/2))

    return alphaSurface, textSurface, textSurface.get_rect()

def display_text_alpha(text, size, font, color, alpha=255, bgcolor=(30,30,30), margin=0.25, rotation=0): # Margin is just multiplying the width and height by a decimal 
    pygame.font.init()
    torender = pygame.font.Font(font, size)
    AlphaSurf, TextSurf, TextRect = text_objects_alpha(text, torender, color, alpha, bgcolor, margin, rotation)
    TextRect.center = (0, 0)
    return AlphaSurf, TextSurf, TextRect


# Alpha Text has margins as x+1, Regular Text has margins as x
