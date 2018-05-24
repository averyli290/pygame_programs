import pygame, sys
import math
import time
import random
import re
from CellBoard import CellBoard, Cell
from Button import *

pygame.init()
screen_width, screen_height = size = 625,625
screen = pygame.display.set_mode(size)

# MAKE ESCAPE/QUIT BUTTON FOR THE LOWEST GUI LEVEL


# GENERAL FUNCTIONS

def surface_fade_out(screen, alphacap=60, iterspeed=2, color=(0,0,0)): # Default color to fade out to is black, 60 is good alpha
    # Iterspeed is how fast it fades 
    for alpha in range(0, alphacap, iterspeed):
        check_quit() # To check whether any quitting has happened
        time.sleep(0.01)
        # Covering with darkening rectangle to make it fade out
        bgAlpha = pygame.Surface(screen.get_size())
        bgAlpha.fill(color)
        bgAlpha.set_alpha(alpha)
        # Adding the overlay to the screen
        screen.blit(bgAlpha, (0,0))
        # Updating screen
        pygame.display.flip()

def surface_fade_in(screen, alphafloor=60, iterspeed=2, color=(0,0,0)): # Default color to fade in from is black, 60 is good alpha
    # Iterspeed is how fast it fades 
    screencopy = screen.copy() # Copying the screen because the alpha wont go away, need to blit this every single time to the screen (only a problem if fading in)
    temprange = list(range(0, 255-alphafloor, (255-alphafloor)//alphafloor*iterspeed))
    # To go backwards, we need to take 255-alphacap, but we need to skip some numbers in order to make the transition the same amount of time as fading in
    temprange = temprange[::-1] # Now backwards

    for alpha in temprange:
        check_quit() # To check whether any quitting has happened
        time.sleep(0.01)
        # Covering with rectangle to make it fade in 
        bgAlpha = pygame.Surface(screen.get_size())
        bgAlpha.fill(color)
        bgAlpha.set_alpha(alpha)
        # Adding the overlay and copy to the screen
        screen.blit(screencopy, (0,0))
        screen.blit(bgAlpha, (0,0))
        # Updating screen
        pygame.display.flip()


def check_quit():
    # Checking to see whether the program is to quit or not
    # This returns a list of all of the events if there is no quitting
    event_list = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        event_list.append(event) # Adding to list to return
    
    return event_list


class Block(Cell): # A block on the playing area
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
        
        # Variables
        self.levelpacks = {} # "Pack Name: [maplist]" 
        self.currentPack = None # The map pack being used
        self.maplist = maplist # Will be dependent on the current Pack being used
        self.surface = surface
        self.currentmapnum = 0
        self.displayingLevel = False
        self.currentbuttons = []
        
        # Initializing the buttons
        self.guiLevelInitializeFunctions = {0.0: lambda: self.initializeMainMenuButtons(),
                                            1.0: lambda: self.initializeLevelPackButtons(),
                                            2.0: lambda: self.initializeLevelButtons(), 
                                            1.1: lambda: self.initialzeInfoButtons()}
        # redrawing the buttons for the menus
        self.guiLevelDrawFunctions = {0.0: lambda: self.drawMainMenu(),
                                      1.0: lambda: self.drawLevelPackMenu(),
                                      2.0: lambda: self.drawLevelMenu(), 
                                      1.1: lambda: self.drawInfoMenu()}
        
        # Just for readability
        self.guiLevelNamesConversion = {"Main Menu": 0.0,
                                  "Level Packs": 1.0,
                                  "Levels": 2.0,
                                  "Info": 1.1}

        self.guiLevel = 0.0 # 0.0 is main menu,
                            # 1.0 is level pack menu,
                            # 1.1 is info,
                            # 2.0 is level menu

        # Initializing the numbers to choose the map
        self.initializeLevelButtons()
       
        # Effects of buttons clicked (changes level, starts level, uses clamping to keep in range)
        self.buttonEffectsDict = { # Level Screen
                                  "<": lambda: [self.setPrevMap(), self.drawLevelMenu()],
                                  ">": lambda: [self.setNextMap(), self.drawLevelMenu()],
                                  "|<": lambda: [self.setCurrentMap(0), self.drawLevelMenu()],
                                  ">|": lambda: [self.setCurrentMap(len(self.maplist)-1), self.drawLevelMenu()],
                                  "Start": lambda: self.setDisplayingMap(True),
                                   # Main Menu
                                   "Level Packs": lambda: [self.setGUILevel(self.guiLevelNamesConversion["Level Packs"]),
                                                           self.drawCurrentMenu()],
                                   # Level Packs Menu
                                   "Levels": lambda: [self.setGUILevel(self.guiLevelNamesConversion["Levels"]),
                                                      self.drawCurrentMenu()]
                                  }


    # Simple getter and helper functions
    def renderCurrentMap(self):
        self.maplist[self.currentmapnum].redraw()

    def setCurrentMap(self, index):
        self.currentmapnum = max(0, min(len(self.maplist)-1, index)) # Clamping

    def getCurrentMap(self):
        return self.maplist[self.currentmapnum]
    
    def setNextMap(self):
        self.currentmapnum = max(0, min(len(self.maplist)-1, self.getCurrentMapNum()+1)) # Clamping

    def setPrevMap(self):
        self.currentmapnum = max(0, min(len(self.maplist)-1, self.getCurrentMapNum()-1)) # Clamping

    def getCurrentMapNum(self):
        return self.currentmapnum

    def getCurrentMapStartPos(self):
        return self.maplist[self.currentmapnum].startPos

    def setDisplayingMap(self, val):
        self.displayingLevel = val

    def isDisplayingLevel(self):
        return self.displayingLevel

    def setGUILevel(self, level):
        self.guiLevel = level

    def initializeLevelButtons(self):
        # Creates buttons for the level screen

        self.currentbuttons = []

        buttonQueue = ["|<", "<", "Start", ">", ">|"] # Buttons to make
        
        # Constructing the parameters
        fontsize = 35 
        color = (0, 0, 0)
        alpha = 175 

        frameButtons = [TextButton(self.surface, 0, 0, text, fontsize, color, alpha) for text in buttonQueue] # For getting width and height

        xmargin = (self.surface.get_width()-sum([frameButton.image.get_width() for frameButton in frameButtons]))/(len(buttonQueue)+1)
        
        # Starting coordinates
        x = 0 
        y = (self.surface.get_height() - frameButtons[0].image.get_height())/2

        for text in buttonQueue:
            # Making margin and distance adjustments
            if len(self.currentbuttons) > 0: x += self.currentbuttons[-1].image.get_width()
            x += xmargin

            self.currentbuttons.append(TextButton(self.surface, x, y, text, fontsize, color, alpha))

    def initializeMainMenuButtons(self):
        # Creates buttons for the main menu

        self.currentbuttons = []

        buttonQueue = ["Level Packs"] # Buttons to make 
        
        # Constructing the parameters
        fontsize = 35 
        color = (0, 0, 0)
        alpha = 175 

        frameButtons = [TextButton(self.surface, 0, 0, text, fontsize, color, alpha) for text in buttonQueue] # For getting width and height

        x = self.surface.get_width()//2
        y = (self.surface.get_height() - frameButtons[0].image.get_height())/2

        for text in buttonQueue:
            frameButton = TextButton(self.surface, 0, 0, text, fontsize, color, alpha) # For getting the width and height
            # Making margin and distance adjustments
            if len(self.currentbuttons) > 0: y += self.currentbuttons[-1].image.get_height()
            x = (self.surface.get_width()-frameButton.image.get_width())//2
            self.currentbuttons.append(TextButton(self.surface, x, y, text, fontsize, color, alpha))

    def initializeLevelPackButtons(self):
        # Creates buttons for the main menu

        self.currentbuttons = []

        buttonQueue = ["Levels"] # Buttons to make 
        
        # Constructing the parameters
        fontsize = 35 
        color = (0, 0, 0)
        alpha = 175 

        frameButtons = [TextButton(self.surface, 0, 0, text, fontsize, color, alpha) for text in buttonQueue] # For getting width and height

        x = self.surface.get_width()//2
        y = (self.surface.get_height() - frameButtons[0].image.get_height())/2

        for text in buttonQueue:
            frameButton = TextButton(self.surface, 0, 0, text, fontsize, color, alpha) # For getting the width and height
            # Making margin and distance adjustments
            if len(self.currentbuttons) > 0: y += self.currentbuttons[-1].image.get_height()
            x = (self.surface.get_width()-frameButton.image.get_width())//2
            self.currentbuttons.append(TextButton(self.surface, x, y, text, fontsize, color, alpha))

    def initialzeInfoButtons(self):
        pass

    def drawLevelMenu(self):
        # Initializing the buttons
        self.initializeLevelButtons()

        # Setting values and clearing 
        self.displayingLevel = False
        self.surface.fill((0, 0, 0))

        # Choosing the map to display in the background
        toshow = self.getCurrentMap()
        toshow.redraw()

        # Setting an alpha rectangle over it to tint it darker
        bgAlphaRect = pygame.Surface(self.surface.get_size())
        bgAlphaRect.fill((30, 30, 30))
        bgAlphaRect.set_alpha(175)
        self.surface.blit(bgAlphaRect, (0, 0))

        # Drawing the level number
        text = "Level " + str(self.getCurrentMapNum())
        fontsize = 30 
        color = (255,255,255)
        alpha = 150 
        levelNumberFrame = TextButton(self.surface, 0, 0, text, fontsize, color, 0)
        x, y = (self.surface.get_width()-levelNumberFrame.image.get_width())/2, levelNumberFrame.image.get_height()
        levelNumber = TextButton(self.surface, x, y, text, fontsize, (0, 0, 0), alpha)
        
        # redrawing buttons 
        self.redrawButtons()

        surface_fade_in(self.surface, 30) # Fade effect

    def drawLevelPackMenu(self):
        # Initializing the buttons
        self.initializeLevelPackButtons()

        # Setting values and clearing 
        self.displayingLevel = False
        self.surface.fill((0, 0, 0))

        # redrawing buttons
        self.redrawButtons()

    def drawMainMenu(self):
        # Initializing the buttons
        self.initializeMainMenuButtons()

        # Setting values and clearing 
        self.displayingLevel = False
        self.surface.fill((0, 0, 0))

        # redrawing buttons
        self.redrawButtons()
    
    def initializeCurrentMenu(self):
        # Initializes the menu
        self.guiLevelInitializeFunctions[self.guiLevel]()

    def drawCurrentMenu(self):
        # Draws the menu
        self.guiLevelDrawFunctions[self.guiLevel]()

    def redrawButtons(self):
        # Redraws start, next, and back buttons
        for button in self.currentbuttons:
            button.redraw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse(event) # Handing to another funciton handler
            elif event.type == pygame.KEYDOWN:
                self.handle_key(event)# Handing to another funciton handler

    def handle_mouse(self, event):
        # Mouse inputs
        mx, my = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Checking to see if a level has been selected
                val = self.checkButtonClicked(mx, my) 
                if val != None: self.buttonEffectsDict[val]()

    def handle_key(self, event):
        # Takes a key input and applies something with it
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                maxIntGuiLevel = max([int(guiLevel) for guiLevel in self.guiLevelInitializeFunctions]) # Stripping off the decimals to get the max of the guilevel
                self.guiLevel = float(max(0, min(int(self.guiLevel)-1, maxIntGuiLevel))) # Sets the guiLevel to a lower base(int)level
                # Drawing the menu
                self.drawCurrentMenu()
        
    def checkButtonClicked(self, mx, my):
        # Checking to see if any button has been clicked
        for button in self.currentbuttons:
            if button.isClicked(mx, my):
                return button.getText()

        return None

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
        self.hasKey = False # For getting through brown
    
        # Image values
        self.color = (255, 255, 255)
        self.playerAlpha = 255 
        self.image = pygame.Surface((0, 0))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()

        self.cx = 0
        self.cy = 0

        self.backgroundHandler = BackgroundHandler(self.screen, maplist)

        # Other values/things
        self.bgcolor = bgcolor
        self.startposlist = startposlist
        self.colordict = {"startcolor": (128, 128, 128), # THIS IS THE START COLOR
                          "red": (255, 0, 0), # For referencing the name of the color and not have to manually punch in the rgb value
                          "pink": (255, 175, 255),
                          "purple": (185, 0, 255),
                          "lightpurple": (185, 125, 255),
                          "orange": (255, 128, 0),
                          "yellow": (255, 255, 0),
                          "green": (0, 255, 0),
                          "brown": (78, 46, 40),
                          "black": (0, 0, 0)}

        self.maplevel = 0

        # Dictionary for applying certain effects
        # Without lambda, function always runs at beginning
        self.effectFunctions = {self.colordict["red"]: lambda: self.applySpeedUp(), # Red - Speed up
                                self.colordict["pink"]: lambda: self.applyRegulateSpeed(), # Pink - Regulate speed
                                self.colordict["purple"]: lambda: self.applyShrinkSize(), # Purple - Shrink size
                                self.colordict["lightpurple"]: lambda: self.applySuperShrinkSize(), # Light Purple - Shrink size
                                self.colordict["orange"]: lambda: self.applyRegulateSize(), # Orange - Regulate size
                                self.colordict["yellow"]: lambda: [self.staticanimation(), self.finishLevel()], # Yellow - Finish
                                self.colordict["green"]: lambda: self.gainKey(), # Green - Key to go through brown
                                self.colordict["brown"]: lambda: self.checkKey(), # Brown - Door that requires green
                                self.colordict["black"]: lambda: [self.staticanimation(), self.initializeMap(self.backgroundHandler.getCurrentMapNum())] # Black - Wall (kills you!)
                                }

    
    def finishLevel(self):
        # a fading rectangle into screen with text inside of it

        for f in range(0, 25): # The alpha only goes up to 25
            # Displaying text with 3 times the alpha of the rectangle so it can be seen, size 27
            alphaSurf, textSurf, textRect = display_text("Level Finished!", 27, pygame.font.get_default_font(), (255, 255, 255))
            
            # Making paddings for the text in the translucent rectangle
            alpharectwidth = textSurf.get_width()*1.5
            alpharectheight = textSurf.get_height()*2 

            alpharect = pygame.Surface((alpharectwidth, alpharectheight)) # Semi transparent rectangle
            alpharect.fill((30,30,30,f)) # Dark grey color (30,30,30)
            cx, cy = ((alpharect.get_width()-textSurf.get_width())/2, (alpharect.get_height()-textSurf.get_height())/2) # Calculating where the top left of the rectangle should be
            alpharect.blit(textSurf, (cx, cy)) # Adding the text to the surface to be added to the screen
            alpharect.set_alpha(f) # Setting the alpha (transparency)

            self.screen.blit(alpharect, (self.screen.get_width()//2-alpharect.get_width()//2, self.screen.get_height()//2-alpharect.get_height()//2))# Adding it to the screen and cetnering using math

            pygame.display.flip() # Displaying the screen 

            # Sleeping for emphasizing fade effect
            time.sleep(0.02)

        # Waiting a few seconds
        time.sleep(1)

        # Fading out
        surface_fade_out(self.screen, 60)
        
        # Automatically progresses to next map and then draws menu
        self.backgroundHandler.drawLevelMenu()

    def initializeMap(self, index):
        currentmap = self.backgroundHandler.getCurrentMap() 

        # Getting some values
        cellwidth = currentmap.cellwidth
        cellheight = currentmap.cellheight

        # Updating player values, map, and handler values
        self.backgroundHandler.setCurrentMap(index)
        cellstartx, cellstarty = self.backgroundHandler.getCurrentMapStartPos() # The cell values
        self.px, self.py = cellstartx*cellwidth+cellwidth/2, cellstarty*cellheight+cellheight/2 # Converting to pygame coordinates
        self.hasKey = False # Resetting key value
        self.backgroundHandler.setDisplayingMap(True)

        # Updating player paramaters to default
        self.resetPlayerParams()        

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

    def exitLevel(self):
        # For exiting the level
        self.staticanimation()
        # Fade effect
        surface_fade_out(self.screen, 50)
        # Initializing menu
        self.backgroundHandler.drawLevelMenu()

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
        self.clock.tick(50)
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
                
                elif event.key == pygame.K_ESCAPE:
                    self.exitLevel()

    def check_new_level(self):
        if self.backgroundHandler.isDisplayingLevel(): # Checking to see if displaying a level, in other words to see if to display level
            self.initializeMap(self.backgroundHandler.getCurrentMapNum()) # Getting the index of the map and initalizing map
    
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
        self.parameters[1] = self.blockheight/self.currentbase_height # Making it so when shrunk,

    def applySuperShrinkSize(self):
        self.parameters[1] = (self.blockheight/self.currentbase_height) / 1.25 # Making it so shrunk smaller than block

    def applyRegulateSize(self):
        self.parameters[1] = 1
    
    def gainKey(self):
        self.hasKey = True # Player gains passage through brown doors
        self.image.fill((0, 255, 0)) # Green tint effect
        self.image.set_alpha(175)

    def checkKey(self):
        # If no key and brown collision, then player dies
        if self.hasKey == False:
            self.effectFunctions[self.colordict["black"]]() # Running death function 
        # Otherwise, nothing happens
    
    def resetPlayerParams(self):
        # Resets all params, dx, and dy
        for i in range(len(self.parameters)):
            self.parameters[i] = 1

        self.dx = 0
        self.dy = 0

    def clearEventQueue(self):
        # Clearing all events
        for event in pygame.event.get():
            pass

    def staticanimation(self, spawn=False, animationLength=45):
        # Getting the original scale parameters to not rescale the player if it was previously shrunk 
        self.prev_scale = self.parameters[1]

        # Resetting dx and dy to not move after respawning
        self.dx = 0
        self.dy = 0

        # Spawn/Death animation (in animationLength steps)
        for i in range(animationLength):
            check_quit() # To check whether any quitting has happened

            time.sleep(0.01) # for shrink and grow effect
            # Modifying scale (shrinking if death, growwing if spawning)
            if spawn:
                self.parameters[1] = i/animationLength*self.prev_scale
            else:
                self.parameters[1] = (animationLength-i)/animationLength*self.prev_scale

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

            # Updating image + screen
            self.image.fill((255,255,255))
            self.image.set_alpha(self.playerAlpha)
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
            # Initializing the map
            toadd = MapLevel(self.screen, (0, 0), True, False, 25, 25, len(colors[m]), len(colors[m][0]))
            # Adding the colors to the map
            tempcolors = colors[m]
            tempcoords = coords[m]

            for row in range(len(tempcolors)):
                for col in range((len(tempcolors[row]))):
                    if tempcolors[row][col] not in self.colordict.values(): # If the color is not recognized in color dictionary, set it to defualt color
                        tempcolors[row][col] = (170, 170, 170)
                    elif tempcolors[row][col] == (self.colordict["startcolor"]): # Checking to see if it is the starting position
                        toadd.startPos = (row, col) # Setting the start position#
                    toadd.celllist[row][col].fill(tempcolors[row][col]) # Directly fill it for efficiency

            self.backgroundHandler.maplist.append(toadd)
        
        # Updating the numbers for the level selects
        self.backgroundHandler.initializeLevelButtons()

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
        self.image.fill(self.color)
        self.image.set_alpha(self.playerAlpha)
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


p1 = Player(screen, [], [(100, 100)], 0, (123, 123, 123))
playerSprite = pygame.sprite.Group()
playerSprite.add(p1)

screen.fill((0, 0, 0)) # Clearing screen completely before starting

p1.readfile()

# Starting at the main menu (initializing the buttons, then drawing menu)
p1.backgroundHandler.guiLevelDrawFunctions[p1.backgroundHandler.guiLevel]()

while True:
    if p1.backgroundHandler.isDisplayingLevel():
        p1.handle_keys() # only if playing
        if p1.backgroundHandler.isDisplayingLevel():
            p1.update() # Now rechecking because the player may have exited the level, changing the status
            playerSprite.draw(screen) # Drawing the player
    else:
        p1.backgroundHandler.handle_events() # using this if not playing
        p1.check_new_level() # When not in play the player HAS to check for a new level in order to initialize it if there is a level to display (if bghandler.isDisplayingLevel() == True)

    pygame.display.flip()
