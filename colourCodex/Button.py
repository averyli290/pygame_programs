import pygame, sys
from displaytext import *

pygame.init()

class Button(pygame.sprite.Sprite):
    def __init__(self, surface, x, y, size=(50, 30), color=(100, 100, 100), alpha=255):
        pygame.sprite.Sprite.__init__(self)

        self.surface = surface

        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.alpha = alpha
        self.hovercolor = tuple([max(0, val-100) for val in self.color])

        # Image values
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.surface.blit(self.image, (self.x, self.y))
    
    def isHovered(self, mx, my):
        return self.rect.collidepoint(mx, my)

    def darken(self):
        self.image.fill(self.hovercolor)
        self.image.set_alpha(self.alpha)
        self.redraw()

    def resetColor(self):
        self.image.fill(self.color)
        self.image.set_alpha(self.alpha)
        self.redraw()

    def isClicked(self, mx, my):
        return self.rect.collidepoint((mx, my))
    
    def redraw(self):
        self.surface.blit(self.image, (self.x, self.y))
        
class TextButton(Button):
    def __init__(self, surface, x, y, text, size, color=(0,0,0), imagecolor=(200, 200, 200), alpha=185, textalpha=185, margin=2.5):
        
        self.surface = surface

        # For the text options
        self.text = text
        self.size = size
        self.color = color
        self.imagecolor = imagecolor
        self.alpha = alpha
        self.textalpha = textalpha
        self.margin = margin 
        self.hovercolor = tuple([max(0, val-100) for val in self.color])
        
        # Image values
        self.AlphaSurf, self.TextSurf, self.TextRect = display_text_alpha(text, size, pygame.font.get_default_font(), color, textalpha, self.imagecolor, 0)
        self.image = pygame.Surface((self.AlphaSurf.get_width()*self.margin, self.AlphaSurf.get_height()*self.margin)) # Image is translucent and has padding for the text(by scaling)
        self.image.fill(self.imagecolor); self.image.set_alpha(alpha) # Specs for color and transparency
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.x = x
        self.y = y

        # Drawing the number onto the padded surface, then onto the main surface
        self.image.blit(self.AlphaSurf, (self.image.get_width()//2-self.AlphaSurf.get_width()//2, self.image.get_height()//2-self.AlphaSurf.get_height()//2))
        self.surface.blit(self.image, (self.x, self.y))

    def getText(self):
        return self.text
    
    def redraw(self): # Overriding the redraw function since there are more things
        # Redrawing the color and alpha, then reblitting to the surface
        self.image.fill(self.imagecolor); self.image.set_alpha(self.alpha) # Specs for color and transparency
        self.image.blit(self.AlphaSurf, (self.image.get_width()//2-self.AlphaSurf.get_width()//2, self.image.get_height()//2-self.AlphaSurf.get_height()//2)) # Readding the numbers
        self.surface.blit(self.image, (self.x, self.y)) # Adding it to the screen

    def setCenter(self, x, y):
        # Gives an option to set a center
        self.x, self.y = x-self.image.get_width()/2, y-self.image.get_height()/2
        # Updating rect
        self.rect.center = x, y
        self.redraw()

###############
## TEST CODE ##
###############

'''

size = (600, 600)
screen = pygame.Surface(size)
screen = pygame.display.set_mode(size)

screen.fill((255, 255, 255))

b = TextButton(screen, 10, 10, "1", 30, (0, 100, 0), 200)

while True:
    for event in pygame.event.get():
        mx, my = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0] == 1:
                print(b.isClicked(mx, my))
        if b.isHovered(mx, my):
            b.darken()

    pygame.display.flip()

'''

