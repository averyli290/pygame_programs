import pygame, sys

pygame.init()

def text_objects(text, font, color, alpha=255, bgcolor=(30,30,30), rotation=0):
    textSurface = font.render(text, True, color)
    textSurface = pygame.transform.rotate(textSurface, rotation)

    # Making the alpha surface
    alphaSurface = pygame.Surface(textSurface.get_size())
    alphaSurface.fill(bgcolor)
    alphaSurface.set_alpha(alpha)
    alphaSurface.blit(textSurface, (0, 0))

    return alphaSurface, textSurface, textSurface.get_rect()

def display_text(text, size, font, color, alpha=255, bgcolor=(30,30,30), rotation=0):
    pygame.font.init()
    torender = pygame.font.Font(font, size)
    AlphaSurf, TextSurf, TextRect = text_objects(text, torender, color, alpha, bgcolor, rotation)
    TextRect.center = (0, 0)
    return AlphaSurf, TextSurf, TextRect

class Button(pygame.sprite.Sprite):
    def __init__(self, surface, x, y, size=(50, 30), color=(100, 100, 100), alpha=255):
        pygame.sprite.Sprite.__init__(self)

        self.surface = surface

        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.alpha = alpha

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
        hovercolor = tuple([max(0, val-100) for val in self.color]) # If hovered over, should darken button
        self.image.fill(hovercolor)

    def isClicked(self, mx, my):
        return self.rect.collidepoint((mx, my))
    
    def redraw(self):
        self.surface.blit(self.image, (self.x, self.y))
        
class TextButton(Button):
    imagecolor = (200,200,200) # For the bgcolor on the number
    def __init__(self, surface, x, y, text, size, color=(0,0,0), alpha=185):
        
        self.surface = surface

        # For the text options
        self.text = text
        self.size = size
        self.color = color
        self.alpha = alpha
        
        # Image values
        self.AlphaSurf, self.TextSurf, self.TextRect = display_text(text, size, pygame.font.get_default_font(), color, alpha, self.imagecolor)
        self.image = pygame.Surface((self.AlphaSurf.get_width()*2.5, self.AlphaSurf.get_height()*2.5)) # Image is translucent and has padding for the text(by scaling)
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

