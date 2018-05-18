import pygame, sys
import math
import time
from CellBoard import CellBoard, Cell

pygame.init()
screen_width, screen_height = size = 625,625
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

    def isFilled(self): # Overriding now b.c. defualt color is (170, 170, 170)
        return self.color != self.defaultcolor
        

class MapLevel(CellBoard):
    def __init__(self, surface, startPos=(4, 22), borders=True, verts=False, cellwidth=25, cellheight=25, boardwidth=25, boardheight=25, bordercolor=(100, 100, 100), defaultBlockColor=(170, 170, 170)): # The border color is light gray

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

    def setMenu(self):
        self.displayingMap = False
        self.surface.fill((170, 170, 170))

class Player(pygame.sprite.Sprite):

    wallcolor = (0, 0, 0) # If crashing into wall, then dead
    usualblockwidth = 25 # For scaling the speed later
    scalefactor = 1.4 # The scale of player width to block width

    def __init__(self, screen, maplist=[], startposlist=[], rotation=0, bgcolor=(0,0,0)):
        pygame.sprite.Sprite.__init__(self)

        self.screen = screen

        # For FPS and timing updates
        self.clock = pygame.time.Clock()
        self.timediv = 5 # Dividing the tick by this val (less means increase in speed, more means decrease)

        # Player values
        self.currentbase_width = 0
        self.currentbase_height = 0 
        
        self.px = 0
        self.py = 0
        self.pwidth = 0 
        self.pheight = 0 
        self.orig_speed = 4 # approxiamately self.clock.tick(50)/self.timediv
        self.current_speed = 0
        self.dx = 0 
        self.dy = 0
        self.angle = 0 # Based on unit circle (for death animation)
        self.parameters = [1, 1] # Format is [speed, size]
        self.effectFunctionQueue = set() # For running functions in a queue, a set so duplicates can't be run multiple times
    
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
                          "yellow": (255, 255, 0),
                          "black": (0, 0, 0)}

        self.maplevel = 0

        # Dictionary for applying certain effects
        # Without lambda, function always runs at beginning
        self.effectFunctions = {self.colordict["red"]: lambda: self.applySpeedUp(), # Red - Speed up
                                self.colordict["pink"]: lambda: self.applyRegulateSpeed(), # Pink - Regulate speed
                                self.colordict["purple"]: lambda: self.applyShrinkSize(), # Purple - Shrink size
                                self.colordict["orange"]: lambda: self.applyRegulateSize(), # Orange - Regulate size
                                self.colordict["yellow"]: lambda: [self.staticanimation(), self.finishLevel()], # Yellow is finish
                                self.colordict["black"]: lambda: [self.staticanimation(), self.initializeMap(self.maplevel)] # Black - Wall (kills you!)
                                }

    def finishLevel(self):
        alpharectwidth = screen_width//3
        alpharectheight = screen_height//3
        alpharect = pygame.Surface((alpharectwidth, alpharectheight), pygame.SRCALPHA) # Semi transparent rectangle
        alpharect.fill((30,30,30,175)) # Dark grey color (30,30,30) + setting the alpha (transparency)
        self.screen.blit(alpharect, (screen_width//2-alpharectwidth//2, screen_height//2-alpharectheight//2))# Adding it to the screen
        pygame.display.flip() # Displaying the screen and waiting a couple seconds
        time.sleep(1)
        self.backgroundHandler.setMenu()
        pygame.display.flip()
    
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
        self.pheight = currentmap.cellwidth*self.scalefactor
        self.pwidth = currentmap.cellheight*self.scalefactor
        self.cx = self.px+self.pwidth-cellwidth
        self.cy = self.py+self.pheight-cellheight

        # Updating the blocksize values
        self.blockwidth, self.blockheight = currentmap.cellwidth, currentmap.cellheight
        self.currentbase_height = self.blockheight*self.scalefactor
        self.currentbase_width = self.blockwidth*self.scalefactor
        
        # Spawning player
        self.staticanimation(True)

    def runEffectQueue(self):
        for blockcolor in self.effectFunctionQueue:
            self.effectFunctions[blockcolor]() # Running each function in the queue
        
        self.effectFunctionQueue = set()

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
            self.effectFunctionQueue.add(block.color) # Adding the color to the queue to be run later

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

    def readfile(self, filename="levels"):
        # resetting the maps
        self.backgroundHandler.maplist = []

        lines = []

        with open(filename+".txt", "r") as f:
            for line in f:
                lines.append(line)

        colors = []
        coords = []
        
        # Splitting and adding the lines to the appropriate list
        for line in lines:
            if "SPACER" in line:
                colors.append([])
                coords.append([])
            else:
                s = line.split(";")

                # Changes string tuple into tuple
                color = eval(s[0])
                coord = eval(s[1])

                # Checking if to add new line
                if len(colors[-1]) <= coord[0]:
                    colors[-1].append([])
                    coords[-1].append([])

                colors[-1][-1].append(color)
                coords[-1][-1].append(coord)

        for m in range(len(colors)):
            toadd = MapLevel(self.screen, (4, 22), True, False, 25, 25, len(colors[m]), len(colors[m][0]))
            # Adding the colors to the map
            tempcolors = colors[m]
            tempcoords = coords[m]

            for row in range(len(tempcolors)):
                for col in range((len(tempcolors[row]))):
                    if tempcolors[row][col] == (255, 255, 255):
                        tempcolors[row][col] = (170, 170, 170)
                    toadd.fillCell(tempcoords[row][col][0], tempcoords[row][col][1], tempcolors[row][col])

            self.backgroundHandler.maplist.append(toadd)


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
        self.runEffectQueue()


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

p1.readfile()
p1.initializeMap(0)

screen.fill((0, 0, 0)) # Clearing screen completely before starting

while True:
    p1.handle_keys() # Always have to check for quitting
    if p1.backgroundHandler.displayingMap: # Making sure that they are played
        p1.update()
    playerSprite.draw(screen) # Drawing the player
    pygame.display.flip()
