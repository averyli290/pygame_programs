import pygame, sys

class Cell(pygame.sprite.Sprite):
    def __init__(self, surface, color=(255,255,255), topleft=(0, 0), width=20, height=20, border=True):

        pygame.sprite.Sprite.__init__(self)

        self.isFilled = False if color != None else True
        self.surface = surface 
        self.topleft = topleft
        self.width = width
        self.height = height
        self.color = color
        
        self.isFilled = False

        self.image = pygame.Surface([width, height])
        self.image.fill((0, 0, 0))
        
        # Creating inner cell
        # The border lines are width/10 and height/10 size
        self.wbdwidth = self.width/10
        self.hbdwidth = self.height/10
        self.cellfill = pygame.Surface((self.width-self.hbdwidth, self.height-self.wbdwidth))
        self.cellfill.fill((255, 255, 255))
        self.drawCell()

        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        # Putting the cell into the screen
        self.surface.blit(self.image, topleft)

    def fill(self, color=(0,0,0)):
        self.cellfill.fill(color) 
        self.color = color

        self.isFilled = True

        # Updating the cell
        self.drawCell()

    def clear(self):
        # Resetting the color back to white
        self.cellfill.fill((255,255,255))
        self.color = (255,255,255)
        
        self.isFilled = False

        # Updating the cell
        self.drawCell()

    def drawCell(self):
        self.image.blit(self.cellfill, (self.hbdwidth, self.wbdwidth))
        self.surface.blit(self.image, self.topleft)

class CellBoard:
    def __init__(self, surface, cellwidth=20, cellheight=20, boardwidth=25, boardheight=25, borders=True):
            
        self.surface = surface
        # Adding some amount later to compensate for the divider lines later (thickness of divider lines)
        if borders: self.boardSurface = pygame.Surface((cellwidth*boardwidth+int(cellwidth/10), cellheight*boardheight+int(cellheight/10)))
        else: self.boardSurface = pygame.Surface((cellwidth*boardwidth, cellheight*boardheight))

        self.cellwidth = cellwidth
        self.cellheight = cellheight
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.borders = borders
        self.celllist = self.initializeBoard()

    def initializeBoard(self):
        celllist = []

        # Initializing cells
        for i in range(self.boardwidth):
            celllist.append([])
            for j in range(self.boardheight):
                x, y = i*self.cellwidth, j*self.cellheight
                celllist[i].append(Cell(self.boardSurface, (255,255,255), (x, y), self.cellwidth, self.cellheight))

        if self.borders: self.initializeBorders()
        
        # Adding the board to the surface given  
        self.surface.blit(self.boardSurface, (0, 0))

        return celllist 

    def initializeBorders(self):

        # Initializing borders

        for i in range(self.boardwidth+1):
            thickness = int(self.cellwidth/10)

            pygame.draw.rect(self.boardSurface, (0, 0, 0), (i*self.cellwidth, 0, thickness, self.boardheight*self.cellheight))
                
        for j in range(self.boardheight+1):
            thickness = int(self.cellheight/10)
            
            pygame.draw.rect(self.boardSurface, (0, 0, 0), (0, j*self.cellheight, self.boardheight*self.cellwidth, thickness))

    def fillCell(self, x, y, color=(0, 0, 0)):
        if self.validCell(x, y):
            self.celllist[x][y].fill(color)
            self.surface.blit(self.boardSurface, (0, 0))
            return True
        return False

    def eraseCell(self, x, y):
        if self.validCell(x, y):
            self.celllist[x][y].fill((255,255,255))
            self.surface.blit(self.boardSurface, (0, 0))
            return True
        return False

    def validCell(self, x, y):
        return x in range(0, self.boardwidth) and y in range(0, self.boardheight)
    
    def cell_coords(self, mx, my):
        return (mx//self.cellwidth, my//self.cellheight) if self.validCell(mx//self.cellwidth, my//self.cellheight) else (-1, -1)

    def vert_coords(self, mx, my):
        # Finding the vertex selected
        # Searching for what vertex was selected
        for i in range(self.boardheight+1):
            for j in range(self.boardwidth+1):
                
                # Making a range that the point could be in
                x1, y1 = i*self.cellwidth-self.cellwidth/2, j*self.cellheight-self.cellheight/2
                x2, y2 = i*self.cellwidth+self.cellwidth/2, j*self.cellheight+self.cellheight/2
                x1, y1 = int(min(max(0, x1), self.boardwidth*self.cellwidth)), int(min(max(0, y1), self.boardheight*self.cellheight))
                x2, y2 = int(min(max(0, x2), self.boardwidth*self.cellwidth)), int(min(max(0, y2), self.boardheight*self.cellheight))
                if mx in range(x1, x2) and my in range(y1, y2): return (i, j)

        return (-1, -1)
    
    def redraw(self):
        for l in self.celllist:
            for cell in l:
                cell.drawCell()
        
        self.initializeBorders()
            

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

