import pygame, sys
import math
from CellBoard import CellBoard, Cell

pygame.init()
screen_width, screen_height = size = 754, 754
screen = pygame.display.set_mode(size)


class Block(Cell):
    defaultcolor = (169,169,169) # Default color is light grey

    def __init__(self, surface, color=(255, 255, 255), topLeft=(0, 0), width=20, height=20, border=True):
        Cell.__init__(self, surface, color, topLeft, width, height, border)

    def get_color(self):
        return self.color
    
    def set_default_color(self):
        self.color = self.defaultcolor
        self.image.fill((self.color))
        self.drawCell()

    def isFilled(self): # Overriding now b.c. defualt color is (38, 38, 38)
        return self.color != self.defaultcolor
        

class MapLevel(CellBoard):
    def __init__(self, surface, borders=True, verts=False, cellwidth=20, cellheight=20, boardwidth=25, boardheight=25):
        CellBoard.__init__(self, surface, borders, verts, cellwidth, cellheight, boardwidth, boardheight)

    def initializeBoard(self): # Overriding to instead use Block class
        celllist = []

        for i in range(self.boardwidth):
            celllist.append([])
            for j in range(self.boardheight):
                x, y = i*self.cellwidth, j*self.cellheight
                # Setting it with default color
                b = Block(self.boardSurface, (169, 169, 169), (x, y), self.cellwidth, self.cellheight, self.borders)
                celllist[i].append(b)
        
        self.surface.blit(self.boardSurface, (0, 0))

        return celllist


class Player(pygame.sprite.Sprite):
    orig_width = 30 
    orig_height = 30 

    image = pygame.Surface((orig_width, orig_height))
    image.fill((255, 255, 255))
    rect = image.get_rect()

    def __init__(self, screen, maplist=[], startposlist=[], rotation=0, bgcolor=(0,0,0)):
        pygame.sprite.Sprite.__init__(self)

        self.screen = screen

        # For FPS and timing updates
        self.clock = pygame.time.Clock()
        self.timediv = 4 # Dividing the tick by this val (less means increase in speed, more means decrease)

        # Player values
        self.px = 0
        self.py = 0
        self.pwidth = self.orig_width
        self.pheight = self.orig_height
        self.dx = self.clock.tick(60)/self.timediv
        self.dy = 0
        self.dir = 0 # Based on unit circle
        self.pscale = 1 # For growth
        self.statuses = [1] # For different speeds, sizes, etc
    
        # Image values
        self.cx = self.px+self.orig_width//2
        self.cy = self.py+self.orig_height//2

        # Other values
        self.bgcolor = bgcolor
        self.maplist = maplist 
        self.startposlist = startposlist
        self.currentmap = 0
    
    def initializeMap(self, mapnum):
        # Updating map index and player position
        self.currentmap = mapnum
        self.px, self.py = self.startposlist[mapnum]
        
        # Drawing the new things
        self.update()
        

    def handle_keys(self):
        # Locking fps
        dt = self.clock.tick(60)/self.timediv

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_UP:
                    self.up(dt)
                elif event.key == pygame.K_DOWN:
                    self.down(dt)
                elif event.key == pygame.K_LEFT:
                    self.left(dt)
                elif event.key == pygame.K_RIGHT:
                    self.right(dt)

    def up(self, dt):
        # Updating dimensions depending on movement direction
        self.pwidth = self.orig_height*self.pscale
        self.pheight = self.orig_width*self.pscale

        self.dx = 0
        self.dy = -dt
        self.dir = math.pi/2

    def down(self, dt):
        # Updating dimensions depending on movement direction
        self.pwidth = self.orig_height*self.pscale
        self.pheight = self.orig_width*self.pscale

        self.dx = 0
        self.dy = dt
        self.dir = 3*math.pi/2

    def left(self, dt):
        # Updating dimensions depending on movement direction
        self.pwidth = self.orig_width*self.pscale
        self.pheight = self.orig_height*self.pscale

        self.dx = -dt
        self.dy = 0
        self.dir = math.pi

    def right(self, dt):
        # Updating dimensions depending on movement direction
        self.pwidth = self.orig_width*self.pscale
        self.pheight = self.orig_height*self.pscale

        self.dx = dt
        self.dy = 0 
        self.dir = 0

    def applySpeedUp(self):
        self.statuses[0] = 1.5

    def applyRegulateSpeed(self):
        self.statuses[0] = 1

    def applyShrinkSize(self):
        self.pscale = 0.8 

    def applyRegulateSize(self):
        self.pscale = 1

    def update(self):
        # Clearing the screen
        self.screen.fill(self.bgcolor)

        # Redrawing the map
        self.maplist[self.currentmap].redraw()

        # Updating the dimensions+colors
        self.image = pygame.Surface((self.pwidth, self.pheight))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        
        # Applying multipliers
        self.px += self.dx * self.statuses[0]
        self.py += self.dy * self.statuses[0]
        
        self.rect.center = (self.px, self.py)


m = MapLevel(screen, True, False, 25, 25, 25, 25)
maplist = [m]
p1 = Player(screen, maplist, [(0, 0)], 0, (123, 123, 123))
playerSprite = pygame.sprite.Group()
playerSprite.add(p1)

p1.initializeMap(0)

while True:
    p1.handle_keys()
    p1.update()
    playerSprite.draw(screen)
    pygame.display.flip()
