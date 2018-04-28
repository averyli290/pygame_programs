import pygame, sys

class Cell(pygame.sprite.Sprite):
    def __init__(self, surface, color=(255,255,255), topleft=(0, 0), width=20, height=20):

        pygame.sprite.Sprite.__init__(self)

        self.isFilled = False if color != None else True
        self.surface = surface 
        self.topleft = topleft
        self.width = width
        self.height = height
        self.color = color

        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        # Putting the cell into the screen
        self.surface.blit(self.image, topleft)

    def fill(self, color=(0,0,0)):
        self.image.fill(color)
        self.color = color

        # Updating the cell
        self.surface.blit(self.image, self.topleft)

    def clear(self):
        # Resetting the color back to white
        self.image.fill((255,255,255))
        self.color = (255,255,255)

        # Updating the cell
        self.surface.blit(self.image, self.topleft)

class CellBoard:
    def __init__(self, surface, cellwidth=20, cellheight=20, boardwidth=25, boardheight=25, borders=True):
            
        self.surface = surface
        # Adding some amount later to compensate for the divider lines later (thickness of divider lines)
        if borders: self.boardSurface = pygame.Surface((cellwidth*boardwidth+int(cellwidth/10), cellheight*boardheight+int(cellheight/10)))

        self.cellwidth = cellwidth
        self.cellheight = cellheight
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.celllist = []
        self.borders = borders
            
        self.initializeBoard()

        # Adding the board to the screen
        self.surface.blit(self.boardSurface, (0, 0))

    def initializeBoard(self):

        # Initializing cells
        for i in range(self.boardwidth):
            for j in range(self.boardheight):
                x, y = i*self.cellwidth, j*self.cellheight
                c = Cell(self.boardSurface, (255,255,255), (x, y), self.cellwidth, self.cellheight)
                self.celllist += [c]
            

        # Initializing borders
        if self.borders:
            for i in range(self.boardwidth+1):
                thickness = int(self.cellwidth/10)
                pygame.draw.rect(self.boardSurface, (0, 0, 0), (i*self.cellwidth, 0, thickness, self.boardheight*self.cellheight))

            for j in range(self.boardheight+1):
                thickness = int(self.cellheight/10)
                pygame.draw.rect(self.boardSurface , (0, 0, 0), (0, j*self.cellheight, self.boardheight*self.cellwidth, thickness))

#############
# TEST CODE #
#############

'''

size = width, height = 1440, 900
screen = pygame.display.set_mode((size))
screen.fill((255,255,255))


b = CellBoard(screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    pygame.display.flip()
'''
