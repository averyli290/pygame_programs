import pygame, sys
import math
import time
from CellBoard import CellBoard, Cell

pygame.init()
screen_width, screen_height = size = 754, 754
screen = pygame.display.set_mode(size)

class Block(Cell):
    defaultcolor = (170,170,170) # Default color is light gray

    def __init__(self, surface, color=(255, 255, 255), topLeft=(0, 0), width=20, height=20, border=True, bordercolor=(100, 100, 100)): # Border color is light gray
        Cell.__init__(self, surface, color, topLeft, width, height, border, bordercolor)

    def get_color(self):
        return self.color
    
    def set_default_color(self):
        self.color = self.defaultcolor
        self.innercell.fill((self.color))
        self.drawCell()

    def isFilled(self): # Overriding now b.c. defualt color is (38, 38, 38)
        return self.color != self.defaultcolor
        

class MapLevel(CellBoard):
    def __init__(self, surface, startPos=(0, 0), borders=True, verts=False, cellwidth=20, cellheight=20, boardwidth=25, boardheight=25, bordercolor=(100, 100, 100), defaultBlockColor=(170, 170, 170)): # The border color is light gray

        # Needed for collision detection with blocks later
        self.defaultBlockColor = defaultBlockColor

        CellBoard.__init__(self, surface, borders, verts, cellwidth, cellheight, boardwidth, boardheight, bordercolor)
        
        self.startPos = startPos

    def initializeBoard(self): # Overriding to instead use Block class
        celllist = []

        for i in range(self.boardwidth):
            celllist.append([])
            for j in range(self.boardheight):
                x, y = i*self.cellwidth, j*self.cellheight
                # Setting it with default color
                b = Block(self.boardSurface, self.defaultBlockColor, (x, y), self.cellwidth, self.cellheight, self.borders, self.bordercolor)
                b.set_default_color()
                celllist[i].append(b)

        self.surface.blit(self.boardSurface, (0, 0))

        return celllist


class MapReader:
    def __init__(self):
        pass
    
    def readfile(filename):
        pass


class BackgroundHandler:
    # All pretty much self explanatory
    def __init__(self, surface, maplist=[]):
        
        self.maplist = maplist
        self.surface = surface
        self.currentmap = 0
        self.displayingMap = False

    def renderCurrentMap(self):
        self.maplist[self.currentmap].redraw()

    def setCurrentMap(self, index):
        self.currentmap = index

    def getCurrentMap(self):
        return self.maplist[self.currentmap]
    
    def getCurrentMapStartPos(self):
        return self.maplist[self.currentmap].startPos

    def setDisplayingMap(self, val):
        self.displayingMap = val

class Player(pygame.sprite.Sprite):

    wallcolor = (0, 0, 0) # If crashing into wall, then dead
    usualblockwidth = 25 # For scaling the speed later

    def __init__(self, screen, maplist=[], startposlist=[], rotation=0, bgcolor=(0,0,0)):
        pygame.sprite.Sprite.__init__(self)

        self.screen = screen

        # For FPS and timing updates
        self.clock = pygame.time.Clock()
        self.timediv = 4 # Dividing the tick by this val (less means increase in speed, more means decrease)

        # Player values
        self.currentbase_width = 0
        self.currentbase_height = 0 
        
        self.px = 0
        self.py = 0
        self.pwidth = 0 
        self.pheight = 0 
        self.orig_speed = self.clock.tick(60)/self.timediv
        self.current_speed = 0
        self.dx = 0 
        self.dy = 0
        self.angle = 0 # Based on unit circle (for death animation)
        self.parameters = [1, 1] # Format is [speed, size]
    
        # Image values
        self.image = pygame.Surface((0, 0))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()

        self.cx = 0
        self.cy = 0

        self.backgroundHandler = BackgroundHandler(self.screen, maplist)

        # Other values/things
        self.bgcolor = bgcolor
        self.startposlist = startposlist
        self.colordict = {"red": (255, 0, 0), # For referencing the name of the color and not have to manually punch in the rgb value
                          "pink": (255, 175, 255),
                          "purple": (185, 0, 255),
                          "orange": (255, 128, 0),
                          "black": (0, 0, 0)}

        self.maplevel = 0

        # Dictionary for applying certain effects
        # Without lambda, function always runs at beginning
        self.effectFunctions = {self.colordict["red"]: lambda: self.applySpeedUp(), # Red - Speed up
                                self.colordict["pink"]: lambda: self.applyRegulateSpeed(), # Pink - Regulate speed
                                self.colordict["purple"]: lambda: self.applyShrinkSize(), # Purple - Shrink size
                                self.colordict["orange"]: lambda: self.applyRegulateSize(), # Orange - Regulate size
                                self.colordict["black"]: lambda: [self.staticanimation(), self.initializeMap(self.maplevel)] # Black - Wall (kills you!)
                                }
    
    def initializeMap(self, index):
        currentmap = self.backgroundHandler.getCurrentMap() 

        # Getting some values
        cellwidth = currentmap.cellwidth
        cellheight = currentmap.cellheight

        # Updating player position, map, and handler values
        self.backgroundHandler.setCurrentMap(index)
        cellstartx, cellstarty = self.backgroundHandler.getCurrentMapStartPos() # The cell values
        self.px, self.py = cellstartx*cellwidth-cellwidth/2, cellstarty*cellheight-cellheight/2 # Converting to pygame coordinates
        self.backgroundHandler.setDisplayingMap(True)

        # Updating player paramaters to default
        self.setAllParamsDefault()        

        # Updating player variables
        self.current_speed = self.orig_speed*currentmap.cellwidth/self.usualblockwidth
        self.pheight = currentmap.cellwidth*1.4
        self.pwidth = currentmap.cellheight*1.4
        self.cx = self.px+self.pwidth-cellwidth
        self.cy = self.py+self.pheight-cellheight

        # Updating the blocksize values
        self.blockwidth, self.blockheight = currentmap.cellwidth, currentmap.cellheight
        self.currentbase_height = self.blockheight*1.4
        self.currentbase_width = self.blockwidth*1.4
        
        # Drawing the new things
        self.update()
        
        # Spawning player
        self.staticanimation(True)

    def get_collision(self):
        currentmap = self.backgroundHandler.getCurrentMap() 

        collisionList = [] # list of objects colliding

        for i in range(currentmap.boardheight):
            for j in range(currentmap.boardwidth):
                if self.rect.colliderect(currentmap.celllist[i][j].rect): # Checking for collision in the squares around it
                    collisionList.append(currentmap.celllist[i][j])

        return collisionList

    def handle_collision(self, block):
        # Handling colliding with blocks
        currentmap = self.backgroundHandler.getCurrentMap() 

        if block.color == currentmap.defaultBlockColor: # If NOT default color then start checking
            return None
        
        # Now checking color for different functions
        if block.color in self.effectFunctions:
            # Running function with filler
            self.effectFunctions[block.color]()

    def handle_keys(self):
        # Locking fps
        self.clock.tick(60)
        dt = self.current_speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.up(dt)
                elif event.key == pygame.K_DOWN:
                    self.down(dt)
                elif event.key == pygame.K_LEFT:
                    self.left(dt)
                elif event.key == pygame.K_RIGHT:
                    self.right(dt)
    
    # Direction change functions (modifies angle, dx, and dy) only runs when NOT in animation
    def up(self, dt):
        self.dx = 0
        self.dy = -dt
        self.angle = math.pi/2

    def down(self, dt):
        self.dx = 0
        self.dy = dt
        self.angle = 3*math.pi/2

    def left(self, dt):
        self.dx = -dt
        self.dy = 0
        self.angle = math.pi

    def right(self, dt):
        self.dx = dt
        self.dy = 0 
        self.angle = 0

    def applySpeedUp(self):
        self.parameters[0] = 1.5

    def applyRegulateSpeed(self):
        self.parameters[0] = 1

    def applyShrinkSize(self):
        self.parameters[1] = self.blockheight/self.currentbase_height # Making it so when shrunk, same size as block

    def applyRegulateSize(self):
        self.parameters[1] = 1

    def setAllParamsDefault(self):
        for i in range(len(self.parameters)):
            self.parameters[i] = 1

    def clearEventQueue(self):
        for event in pygame.event.get():
            pass

    def staticanimation(self, spawn=False):
        # Getting the original scale parameters to not rescale the player if it was previously shrunk 
        self.prev_scale = self.parameters[1]

        # Resetting dx and dy to not move after respawning
        self.dx = 0
        self.dy = 0

        # Spawn/Death animation (in 30 steps)
        for i in range(30):
            # Modifying scale (shrinking if death, growwing if spawning)
            if spawn:
                self.parameters[1] = i/30*self.prev_scale
            else:
                self.parameters[1] = (30-i)/30*self.prev_scale

            # Updating dimensions
            self.pwidth = self.currentbase_width*self.parameters[1]
            self.pheight = self.currentbase_height*self.parameters[1]
   
            # Clearing the screen
            self.screen.fill(self.bgcolor)

            # Redrawing the map
            self.backgroundHandler.getCurrentMap().redraw()
            
            # Updating the dimensions+colors
            self.image = pygame.Surface((self.pwidth, self.pheight))
            self.image.fill((255,255,255))
            self.rect = self.image.get_rect()
            
            self.rect.center = (self.px, self.py) 

            # Updating image
            self.image.fill((255,255,255))
            self.rect = self.image.get_rect()
            self.backgroundHandler.surface.blit(self.image, (self.px-self.pwidth//2, self.py-self.pheight//2))
            pygame.display.flip()

        # Clearing the event queue to prevent player from moving right after spawning
        self.clearEventQueue()

    def update(self):
        # Updating dimensions
        self.pwidth = self.currentbase_width*self.parameters[1]
        self.pheight = self.currentbase_height*self.parameters[1]

        # Clearing the screen
        self.screen.fill(self.bgcolor)

        # Redrawing the map
        self.backgroundHandler.renderCurrentMap()

        # Updating the dimensions+colors
        self.image = pygame.Surface((self.pwidth, self.pheight))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        
        # Applying multipliers for the movement speed
        self.px += self.dx * self.parameters[0]
        self.py += self.dy * self.parameters[0]
        
        self.rect.center = (self.px, self.py) 

        # Applying collision, this has to be done AFTER drawing the character, or else there will be recursion when doing collision detection into walls before player is redrawn
        blocks = p1.get_collision()
        for block in blocks:
            p1.handle_collision(block)


m = MapLevel(screen, (10, 7), True, False, 25, 25, 25, 25, (100, 100, 100), (170, 170, 170))
maplist = [m]

p1 = Player(screen, maplist, [(100, 100)], 0, (123, 123, 123))
playerSprite = pygame.sprite.Group()
playerSprite.add(p1)

m.fillCell(10, 17, p1.colordict["red"])
m.fillCell(20, 20, p1.colordict["pink"])
m.fillCell(15, 15, p1.colordict["purple"])
m.fillCell(17, 10, p1.colordict["orange"])
m.fillCell(10, 10, p1.colordict["black"])

p1.initializeMap(0)

screen.fill((0, 0, 0)) # Clearing screen completely before starting

while True:
    p1.handle_keys() # Always have to check for quitting
    if p1.backgroundHandler.displayingMap: # Making sure that they are played
        p1.update()
    playerSprite.draw(screen) # Drawing the player
    pygame.display.flip()
