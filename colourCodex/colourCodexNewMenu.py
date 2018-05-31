import pygame, sys
import math
import time
import random
import re
from CellBoard import CellBoard, Cell
from Button import *
from colourCodexBasicFunctions import *

pygame.init()
screen_width, screen_height = size = 625,625
screen = pygame.display.set_mode(size)

# GENERAL FUNCTIONS

def buttonListClicked(self, mx, my, buttonList):
    # Given a list of buttons, will return a list of button that have been clicked
    clicked = []
    for button in buttonList:
        if button.isClicked(mx, my):
            clicked.append(button)
    return clicked

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

def playBackroundMusic(filename, filetype):
    # Plays background music
    pygame.mixer.init()
    pygame.mixer.music.load(filename+filetype)
    pygame.mixer.music.play(-1,0.0)

def playSoundEffect(filename, filetype):
    # Plays a sound effect
    pygame.mixer.init()
    soundeffect = pygame.mixer.Sound(filename+filetype)
    soundeffect.play()
    return soundeffect

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

    colorlist, colorConversionRGB, colorConversionEffect = readColors() # Getting the colors

    def __init__(self, surface):
        
        # Variables
        self.levelpacks = {} # "Pack Name: [maplist]" 
        self.levelpacksorder = [] # For always drawing them in the same order b.c. dictionaries are not ordered
        self.currentPack = None # The map pack being used
        self.maplist = None # Will be dependent on the current Pack being used
        self.surface = surface
        self.currentmapnum = 0
        self.displayingLevel = False
        self.currentbuttons = []
        
        # For converting the names into numbers that the program can use in dictionaries 
        self.guiLevelNamesConversion = {"Main Menu": "0.0",
                                        "Level Packs": "0.1",
                                        "Block Dictionary": "0.1.2",
                                        "Levels": "0.2", # For enabling using other numbers for the id of packs
                                        "Tutorials": "0.1.2", # Same level as info so it goes back to main menu
                                        "Tutorial": "0.1.1"}

        # redrawing the buttons for the menus
        self.guiLevelDrawFunctions = {self.guiLevelNamesConversion["Main Menu"]: lambda: self.drawMainMenu(),
                                      self.guiLevelNamesConversion["Level Packs"]: lambda: self.drawLevelPackMenu(),
                                      self.guiLevelNamesConversion["Levels"]: lambda: self.drawLevelMenu(), 
                                      self.guiLevelNamesConversion["Tutorials"]: lambda: self.drawLevelMenu(), 
                                      self.guiLevelNamesConversion["Tutorial"]: lambda: self.drawTutorialMenu(),
                                      self.guiLevelNamesConversion["Block Dictionary"]: lambda: self.drawBlockDictionaryMenu()}
        
        self.guiLevel = "0.0" 

        # Initializing the numbers to choose the map
        self.initializeLevelButtons()
       
        # Effects of buttons clicked (changes level, starts level, uses clamping to keep in range)
        self.buttonEffectsDict = {
                                  "<<": lambda: self.reduceGUILevel(), # For going back a gui level
                                  # Level Screen
                                  "<": lambda: [self.setPrevMap(), self.drawLevelMenu()],
                                  ">": lambda: [self.setNextMap(), self.drawLevelMenu()],
                                  "|<": lambda: [self.setCurrentMap(0), self.drawLevelMenu()],
                                  ">|": lambda: [self.setCurrentMap(len(self.maplist)-1), self.drawLevelMenu()],
                                  "Start": lambda: self.setDisplayingMap(True),
                                  # Main Menu
                                  "Level Packs": lambda: [self.setGUILevel(self.guiLevelNamesConversion["Level Packs"]),
                                                          self.drawCurrentMenu()],
                                  "Tutorial": lambda: [self.setGUILevel(self.guiLevelNamesConversion["Tutorial"]),
                                                   self.drawCurrentMenu()], # After the next button is pressed, the tutorials start
                                  "Block Dictionary": lambda: [self.setGUILevel(self.guiLevelNamesConversion["Block Dictionary"]),
                                                               self.drawCurrentMenu()],
                                  # Tutorial Start Page
                                  "Next": lambda: [self.setGUILevel(self.guiLevelNamesConversion["Tutorials"]),
                                                   self.setLevelPack("Tutorials"), self.drawCurrentMenu()], # Sets the tutorial levels from the info screen
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

    def reduceGUILevel(self):
        # Reduces gui level by 1 base level and takes off the float
        maxGuiLevel = max([eval(guiLevel[:3]) for guiLevel in self.guiLevelNamesConversion.values()]) # taking the first digit and the one after the decimal point (v.x)
        self.guiLevel = eval(self.guiLevel[:3]) # Modifying the current level the same way, just takes the first number before and after the decimal point
        self.guiLevel = str(float(max(0, min(float(self.guiLevel)-0.1, maxGuiLevel)))) # Sets the guiLevel to a lower base(1 dec float)level, clamping and converting it to the format needed (a string)
        surface_fade_out(self.surface, 30) # Fade effect
        self.drawCurrentMenu() # Redrawing the menu to update

    def setLevelPack(self, packname):
        # Sets the maplist to a list of maps provided by the name and the current pack
        self.currentPack = packname
        self.maplist = self.levelpacks[packname]
        # Also resetting the map number in order to not have out of range errors when changing level packs as some level packs have a longer length
        self.currentmapnum = 0

    def getCurrentLevelPack(self):
        return self.currentPack
    
    def createBackButton(self):
        # Creating an escape button in the top left corner and returning it
        # Constructing the parameters
        text = "<<"
        fontsize = 20
        color = (0, 0, 0)
        imagecolor = (200, 200, 200)
        alpha = 175 
        textalpha = 175
        margin = 1.75 

        frameButton = TextButton(self.surface, 0, 0, text, fontsize, color, imagecolor, 0, textalpha, margin) # For getting width and height
        screenmargin = frameButton.image.get_height()//2
        escbutton = TextButton(self.surface, screenmargin, screenmargin, text, fontsize, color, imagecolor, alpha, textalpha, margin) # For getting width and height

        return escbutton
    
    # Initializing button functions for each gui level
    def initializeLevelButtons(self):
        # Creates buttons for the level screen

        self.currentbuttons = []

        buttonQueue = ["|<", "<", "Start", ">", ">|"] # Buttons to make
        
        # Constructing the parameters
        fontsize = 35 
        color = (0, 0, 0)
        imagecolor = (200, 200, 200)
        alpha = 175 

        frameButtons = [TextButton(self.surface, 0, 0, text, fontsize, color, imagecolor, alpha) for text in buttonQueue] # For getting width and height

        xmargin = (self.surface.get_width()-sum([frameButton.image.get_width() for frameButton in frameButtons]))/(len(buttonQueue)+1) # Getting the margin
        
        # Starting coordinates
        x = 0 
        y = (self.surface.get_height() - frameButtons[0].image.get_height())/2

        for text in buttonQueue:
            # Making margin and distance adjustments
            if len(self.currentbuttons) > 0: x += self.currentbuttons[-1].image.get_width()
            x += xmargin

            self.currentbuttons.append(TextButton(self.surface, x, y, text, fontsize, color, imagecolor, alpha))

        # Creating escape button
        self.currentbuttons.append(self.createBackButton())

    def initializeTutorialButtons(self):
        # Creates buttons for the level screen

        self.currentbuttons = []

        buttonQueue = ["Next"] # Buttons to make
        # The next button takes you the the tutorial levels
        
        # Constructing the parameters
        fontsize = 35 
        color = (0, 0, 0)
        imagecolor = (200, 200, 200)
        alpha = 175 

        frameButtons = [TextButton(self.surface, 0, 0, text, fontsize, color, imagecolor, alpha) for text in buttonQueue] # For getting width and height

        # Starting coordinates
        x = self.surface.get_width() - frameButtons[0].image.get_width()*1.2
        y = self.surface.get_height() - frameButtons[0].image.get_height()*1.2

        for text in buttonQueue:
            # Making margin and distance adjustments
            if len(self.currentbuttons) > 0: x += self.currentbuttons[-1].image.get_width()

            self.currentbuttons.append(TextButton(self.surface, x, y, text, fontsize, color, imagecolor, alpha))

    def initializeMainMenuButtons(self):
        # Creates buttons for the main menu

        self.currentbuttons = []

        buttonQueue = ["Level Packs", "Tutorial", "Block Dictionary"] # Buttons to make 
        
        # Constructing the parameters
        fontsize = 35 
        color = (0, 0, 0)
        imagecolor = (200, 200, 200)
        alpha = 175 

        frameButtons = [TextButton(self.surface, 0, 0, text, fontsize, color, imagecolor, alpha) for text in buttonQueue] # For getting width and height

        # getting the starting coordinates and the margins
        x = self.surface.get_width()//2
        y = 0
        ymargin = (self.surface.get_height()-sum([frameButton.image.get_height() for frameButton in frameButtons]))/(len(buttonQueue)+1) # Getting the margin (do the math!)

        for text in buttonQueue:
            frameButton = TextButton(self.surface, 0, 0, text, fontsize, color, imagecolor, alpha) # For getting the width and height
            # Making margin and distance adjustments
            if len(self.currentbuttons) > 0: y += self.currentbuttons[-1].image.get_height()
            x = (self.surface.get_width()-frameButton.image.get_width())//2
            y += ymargin 
            self.currentbuttons.append(TextButton(self.surface, x, y, text, fontsize, color, imagecolor, alpha))

    def initializeLevelPackButtons(self):
        # Creates buttons for the main menu

        self.currentbuttons = []

        buttonQueue = [key for key in self.levelpacksorder] # Buttons to make, they are in a specific order
        
        # Constructing the parameters
        fontsize = 35 
        color = (0, 0, 0)
        imagecolor = (200, 200, 200)
        alpha = 175 

        frameButtons = [TextButton(self.surface, 0, 0, text, fontsize, color, imagecolor, alpha) for text in buttonQueue] # For getting width and height

        # getting the starting coordinates and the margins
        x = self.surface.get_width()//2
        y = 0
        ymargin = (self.surface.get_height()-sum([frameButton.image.get_height() for frameButton in frameButtons]))/(len(buttonQueue)+1) # Getting the margin (do the math!)

        for text in buttonQueue:
            frameButton = TextButton(self.surface, 0, 0, text, fontsize, color, imagecolor, alpha) # For getting the width and height
            # Making margin and distance adjustments
            if len(self.currentbuttons) > 0: y += self.currentbuttons[-1].image.get_height()
            x = (self.surface.get_width()-frameButton.image.get_width())//2
            y += ymargin
            self.currentbuttons.append(TextButton(self.surface, x, y, text, fontsize, color, imagecolor, alpha))

        # Creating escape button
        self.currentbuttons.append(self.createBackButton())

    def initializeBlockDictionaryButtons(self):
        # Creates buttons for the Block Dictionary Menu
        self.currentbuttons = []

        # Creating escape button
        self.currentbuttons.append(self.createBackButton())

    def drawBlockDictionaryMenu(self):

        # Setting values and clearing 
        self.displayingLevel = False
        self.surface.fill((0, 0, 0))

        # Initialzing the buttons
        self.initializeBlockDictionaryButtons()

        # Making variables for the text
        referencePoint = (self.surface.get_width()/10, self.surface.get_height()/10)
        text = "" 
        size = 30 
        font = pygame.font.get_default_font()
        margin = 1
        centered = False
        textcolor = (200,200,200)
        bgcolor = (0,0,0)
        
        # Writing the effects
        for color in self.colorConversionEffect:
            if self.colorConversionEffect[color] != None: # Only printing if it is a color being used
                effect = self.colorConversionEffect[color]
                text += str(color) + ": " + str(effect) + "\n"

        # Displaying text
        display_text_paragraph(self.surface, referencePoint, text, size, font, margin, centered, textcolor, bgcolor)       

        # redrawing buttons
        self.redrawButtons()
   
        surface_fade_in(self.surface, 30) # Fade effect

    # The Drawing fucntions for each gui level
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

        # Drawing the level number as a fraction with the level pack name
        text = self.currentPack + ": " + str(self.getCurrentMapNum()) + "/" + str(len(self.levelpacks[self.getCurrentLevelPack()])-1)
        fontsize = 30 
        color = (200, 200, 200)
        imagecolor = (0, 0, 0)
        alpha = 150 
        levelNumberFrame = TextButton(self.surface, 0, 0, text, fontsize, color, imagecolor, 0)
        x, y = (self.surface.get_width()-levelNumberFrame.image.get_width())/2, levelNumberFrame.image.get_height()
        levelNumber = TextButton(self.surface, x, y, text, fontsize, (0, 0, 0), imagecolor, alpha)
        
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

        surface_fade_in(self.surface, 30) # Fade effect

    def drawMainMenu(self):
        # Initializing the buttons
        self.initializeMainMenuButtons()

        # Setting values and clearing 
        self.displayingLevel = False
        self.surface.fill((0, 0, 0))

        # redrawing buttons
        self.redrawButtons()
   
        surface_fade_in(self.surface, 30) # Fade effect

    def drawTutorialMenu(self):
        # Initializing the buttons
        self.initializeTutorialButtons()

        # Setting values and clearing 
        self.displayingLevel = False
        self.surface.fill((0, 0, 0))
        
        # making some variables for text
        referencePoint = (self.surface.get_width()/20, self.surface.get_height()/20)
        text = "Use the arrow keys to move\nthe player towards the\nyellow cells but \nthere are more colours \nto find out about...\n\n\nPress \"Next\" to continue!\n\n\n\n\nPress Escape to exit a level!"
        size = 35 
        font = pygame.font.get_default_font()
        margin = 1
        centered = False
        color = (200,200,200)
        bgcolor = (0,0,0)

        # Displaying text
        display_text_paragraph(self.surface, referencePoint, text, size, font, margin, centered, color, bgcolor)

        # redrawing buttons
        self.redrawButtons()

        surface_fade_in(self.surface, 30) # Fade effect
    
    # A general function for initializing the current menu
    def initializeCurrentMenu(self):
        # Initializes the menu
        self.guiLevelInitializeFunctions[self.guiLevel]()
    
    # A general function for drawing the current menu
    def drawCurrentMenu(self):
        # Draws the menu
        self.guiLevelDrawFunctions[self.guiLevel]()

    # Redraws buttons
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
               self.reduceGUILevel() 

    def checkButtonClicked(self, mx, my):
        # Checking to see if any button has been clicked
        for button in self.currentbuttons:
            if button.isClicked(mx, my):
                return button.getText()

        return None
    
    def readlevelpack(self, filename="levels"):
        # This function reads in level packs
        # creating another level
        levelpack = []

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
            toadd = MapLevel(self.surface, (0, 0), True, False, 25, 25, len(colors[m]), len(colors[m][0]))
            # Adding the colors to the map
            tempcolors = colors[m]
            tempcoords = coords[m]

            for row in range(len(tempcolors)):
                for col in range((len(tempcolors[row]))):
                    if tempcolors[row][col] not in list(self.colorConversionRGB.values()) or tempcolors[row][col]==(255,255,255): # If the color is not recognized in color dictionary, set it to defualt color, or if it is white
                        tempcolors[row][col] = (170, 170, 170)
                    elif tempcolors[row][col] == dict((v, k) for k, v in self.colorConversionEffect.items())["startposition"]: # Checking to see if it is the starting position
                        toadd.startPos = (row, col) # Setting the start position#
                    toadd.celllist[row][col].fill(tempcolors[row][col]) # Directly fill it for efficiency

            levelpack.append(toadd)
        
        # Each level pack has its own id number for reference, and the list of maps in it is stored in a dictionary of self.levelpacks
        # Adding the level pack to the dictionaries
        
        # Capitalizing the words in the filename
        filename = filename.capitalize() # does basically the same thing - filename = ' '.join([word[0].upper()+word[1:].lower() for word in filename.split()])
        self.levelpacks[filename] = levelpack

        # Getting a distinct id number
        i = 1 
        idNumber = self.guiLevelNamesConversion["Levels"]+".0"+str(i) # Giving the pack its own distinct id number (actually a string)
        while self.guiLevelNamesConversion["Levels"]+".0"+str(i) in self.guiLevelNamesConversion.values(): #Keeps on adding until the id is not in the dictionary values
            i += 1 # For adding onto the end of the string
            idNumber = self.guiLevelNamesConversion["Levels"]+".0"+str(i) # Giving the pack its own distinct id number (actually a string)

        if filename in self.guiLevelNamesConversion: # If the pack already exists, just take the idnumber already there
            idnumber = self.guiLevelNamesConversion[filename]

        self.guiLevelNamesConversion[filename] = idNumber # Setting the id number
        self.guiLevelDrawFunctions[idNumber] = lambda: self.drawLevelMenu() # Making another simple dictionary assignment
        # THIS USES A FILENAME FOR A KEY since when a button effect if run, the text of the button is looked at and then used to look inside of the dictionary
        self.buttonEffectsDict[filename] = lambda: [self.setLevelPack(filename),
                                           self.setGUILevel(self.guiLevelNamesConversion[filename]),
                                           self.drawCurrentMenu()] # This has to set a level pack to the maplist first, then set the gui level and draw the menu

        # Adding the level pack to the order it is to drawn in
        self.levelpacksorder.append(filename)

    def readlevelpacks(self, filenamelist):
        # Reads multiple level packs
        for filename in filenamelist:
            self.readlevelpack(filename)

    # Just for the splash screen in the beginning
    def runSplashScreen(self, filenamelist):
        # Makes a loading screen
        # !!!! This also loads the level packs at the same time

        # Making paramaters for text
        fontsize = 35
        font = pygame.font.get_default_font()
        color = (0,0,0)
        bgcolor = (50,50,50)

        self.surface.fill(bgcolor) # Clears the screen

        title = display_text_paragraph(self.surface, (self.surface.get_width()/2, self.surface.get_height()/4), "Colour Codex", 
                                                      60, pygame.font.get_default_font(), 1.25, True, (0,0,0), bgcolor) # Displaying the title
        surface_fade_in(self.surface, 125, 5) # Fade effect in 

        # Reading in the level packs 
        for i in range(len(filenamelist)):
            self.readlevelpack(filenamelist[i]) # Reading in the level packs
            # Updating the progress indicator
            text = "Loaded "+str(i+1)+" out of "+str(len(filenamelist))+" Level Packs..." # Making text
            prgrsIndctrMarginSurf, prgrsIndctrTextSurf, prgrsIndctrTextRect = display_text(text, fontsize, font, color, bgcolor) # making a progress indicator (prgrsIndctr)

            self.surface.fill(bgcolor) # Clears the screen

            self.surface.blit(prgrsIndctrMarginSurf, ((self.surface.get_width()-prgrsIndctrMarginSurf.get_width())/2,
                                                  (self.surface.get_height()*3/5))) # Adding the text to the screen

            title = display_text_paragraph(self.surface, (self.surface.get_width()/2, self.surface.get_height()/4), "Colour Codex", 
                                           60, pygame.font.get_default_font(), 1.25, True, (0,0,0), bgcolor) # Displaying the title

            pygame.display.flip() # updating display

        surface_fade_out(self.surface, 125, 3) # Fade effect out

class Player(pygame.sprite.Sprite):

    wallcolor = (0, 0, 0) # If crashing into wall, then dead
    usualblockwidth = 25 # For scaling the speed later
    scalefactor = 1.4 # The scale of player width to block width
    minimumPlayerAlpha = 20 # Minimum player alpha level

    colorlist, colorConversionRGB, colorConversionEffect = readColors() # Getting the colors

    def __init__(self, screen, startposlist=[], rotation=0, bgcolor=(0,0,0)):
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

        # Level Stats (resets per level)
        self.attemptCount = 0
        self.starttime = time.time() 
        self.buttonsClicked = 0
    
        # Image values
        self.color = (255, 255, 255)
        self.playerAlpha = 255 
        self.image = pygame.Surface((0, 0))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()

        self.cx = 0
        self.cy = 0

        self.backgroundHandler = BackgroundHandler(self.screen)

        # Other values/things
        self.bgcolor = bgcolor
        self.startposlist = startposlist

        self.maplevel = 0

        # Dictionary for applying certain effects
        # Without lambda, function always runs at beginning
        self.effectFunctions = {self.colorConversionRGB["red"]: lambda: self.applySpeedUp(), # Red - Speed up
                                self.colorConversionRGB["green"]: lambda: self.gainKey(), # Green - Key to go through brown
                                self.colorConversionRGB["yellow"]: lambda: [self.staticanimation(), self.finishLevel(), self.resetPlayerStats()], # Yellow - Finish
                                self.colorConversionRGB["blue"]: lambda: self.teleportPlayer(), # Teleports player to light lue
                                self.colorConversionRGB["skyblue"]: lambda: None, # Does nothing (player teleports to this)
                                self.colorConversionRGB["pink"]: lambda: self.applyRegulateSpeed(), # Pink - Regulate speed
                                self.colorConversionRGB["orange"]: lambda: self.applyRegulateSize(), # Orange - Regulate size
                                self.colorConversionRGB["purple"]: lambda: self.applyShrinkSize(), # Purple - Shrink size
                                self.colorConversionRGB["lavender"]: lambda: self.applySuperShrinkSize(), # Light Purple - Shrink size
                                self.colorConversionRGB["brown"]: lambda: self.checkKey(), # Brown - Door that requires green
                                self.colorConversionRGB["beige"]: lambda: self.applyLowerAlpha(), # Beige - lowers the player's alpha
                                self.colorConversionRGB["coral"]: lambda: self.applyRegulateAlpha(), # Coral - sets the player's alpha back to normal
                                self.colorConversionRGB["black"]: lambda: [self.staticanimation(), self.initializeMap(self.backgroundHandler.getCurrentMapNum()), self.addAttempt()] # Black - Wall (kills you!)
                                }

    
    def finishLevel(self):
        # Setting the finish time
        finishtime = time.time()
        # a fading rectangle into screen with text inside of it

        for f in range(0, 25): # The alpha only goes up to 25
            # Making the level finished text
            alphaSurf, textSurf, textRect = display_text_alpha("Level Finished!", 45, pygame.font.get_default_font(), (255, 255, 255), f, (30, 30, 30), 0.75)

            self.screen.blit(alphaSurf, (self.screen.get_width()//2-alphaSurf.get_width()//2, alphaSurf.get_height()*1.75))# Adding it to the screen and centering using math

            # Drawing the stats with the alpha
            self.drawCurrentStats(f, finishtime)
            
            # Drawing a button for continuing
            continueButton = TextButton(self.screen, self.screen.get_width(), self.screen.get_height(), "Continue", 30, (255, 255, 255), (30, 30, 30), f, 255) # Setting it off of the screen
            continueButton.setCenter(self.screen.get_width()//2, self.screen.get_height()-continueButton.image.get_height()*1.5) # Then moving it
            continueButton.redraw()

            pygame.display.flip() # Displaying the screen 

            # Sleeping for emphasizing fade effect
            time.sleep(0.02)

        # Waiting until a button is pressed 
        buttonNotPressed = True 
        while buttonNotPressed:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Checking for click and if button was clicked. breaks out of this loop
                        mx, my = pygame.mouse.get_pos()
                        if continueButton.isClicked(mx, my):
                            buttonNotPressed = False 

                elif event.type == pygame.KEYDOWN: # Pressing escape will also break this
                    if event.key == pygame.K_ESCAPE:
                        buttonNotPressed = False 

                elif event.type == pygame.QUIT: # Checking for quitting
                    pygame.quit()
                    sys.exit()

        # Fading out
        surface_fade_out(self.screen, 60)
        
        # Automatically progresses to next map and then draws menu
        self.backgroundHandler.setNextMap()
        self.backgroundHandler.drawLevelMenu()

    def drawCurrentStats(self, alpha, finishtime=time.time()):
        # Getting time since start
        completiontime = round(finishtime-self.starttime, 2) # To the nearest hundredth
        # Statistics List
        stats_list = ["Attempts: "+str(self.attemptCount), "Buttons Pressed: "+str(self.buttonsClicked), "Time: "+str(completiontime)+" seconds"]

        # Constructing the parameters for the text
        fontsize = 27 
        font = pygame.font.get_default_font()
        color = (255, 255, 255)
        imagecolor = (30,30,30)
        alpha = alpha # Adjusting to make the same color as the other text
        margin = 0.5 
            
        frameTexts = [display_text_alpha(text, fontsize, font, color, 0, (0,0,0), margin) for text in stats_list] # For making margins between text
        
        # For making the backdrop later (using extremes to make sure that the first values get accepted)
        minX = 100000000
        minY = 100000000
        maxX = -100000000
        maxY = -100000000


        # Making start x and start y
        x = self.screen.get_width()//2
        y = self.screen.get_height()/2 - frameTexts[0][0].get_height()*2

        for i in range(len(stats_list)):
            text = stats_list[i] # Getting the text
            frameAlphaRect = frameTexts[i][0] # For reference later

            # Making margin and distance adjustments
            y += frameAlphaRect.get_height()*max(margin, 1)
            x = (self.screen.get_width()-frameAlphaRect.get_width())//2

            # Setting the min's and max's
            minX, minY = min(x, minX), min(y, minY)
            maxX, maxY = max(x+frameAlphaRect.get_width(), maxX), max(y+frameAlphaRect.get_height(), maxY)

            # Now making the text
            alphaRect, textSurf, textRect = display_text_alpha(text, fontsize, font, color, alpha, imagecolor, margin)
            alphaRect.set_colorkey(imagecolor) # Making the backpart entirely transparent

            # blitting to screen
            self.screen.blit(alphaRect, (x, y))
        
        # Creating a backdrop for the stats (has to be just a little bit larger than the minimum to cover)
        backdrop = pygame.Surface(((maxX-minX), (maxY-minY)))
        backdrop.fill((30, 30, 30)); backdrop.set_alpha(alpha)
        # Adding it to the screen centered properly
        self.screen.blit(backdrop, (minX-(backdrop.get_width()-(maxX-minX))/2, minY-(backdrop.get_height()-(maxY-minY))/2))

    def initializeMap(self, index):
        # Getting the current map
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

    def clearEffectQueue(self):
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
                    self.buttonsClicked += 1
                elif event.key == pygame.K_DOWN:
                    self.down(dt)
                    self.buttonsClicked += 1
                elif event.key == pygame.K_LEFT:
                    self.left(dt)
                    self.buttonsClicked += 1
                elif event.key == pygame.K_RIGHT:
                    self.right(dt)
                    self.buttonsClicked += 1
                
                elif event.key == pygame.K_ESCAPE:
                    self.exitLevel()

    def check_new_level(self):
        if self.backgroundHandler.isDisplayingLevel(): # Checking to see if displaying a level, in other words to see if to display level
            self.initializeMap(self.backgroundHandler.getCurrentMapNum()) # Getting the index of the map and initalizing map
            self.resetTimer() # Starts the timer again when a new level starts
    
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

    def applyLowerAlpha(self):
        self.playerAlpha = max(self.playerAlpha*0.6, self.minimumPlayerAlpha) # Makes the player alpha go down, but not below a minimum

    def applyRegulateAlpha(self):
        self.playerAlpha = 255
        self.image.set_alpha(self.playerAlpha)
    
    def gainKey(self):
        self.hasKey = True # Player gains passage through brown doors
        self.image.fill(self.colorConversionRGB["brown"]) # brown tint effect to make it so the player can be seen
        self.image.set_alpha(220) # Making it slightly

    def checkKey(self):
        # If no key and brown collision, then player dies
        if self.hasKey == False:
            self.effectFunctions[self.colorConversionRGB["black"]]() # Running death function 
        # Otherwise, nothing happens

    def teleportPlayer(self):
        # This teleports the player the location of a light blue square
        currentmap = self.backgroundHandler.getCurrentMap()
        cellwidth = currentmap.cellwidth
        cellheight = currentmap.cellheight
        celllist = currentmap.celllist 
        # Searching for sky blue block to teleport to 
        for row in range(len(celllist)):
            for col in range(len(celllist[row])):
                if celllist[row][col].color == self.colorConversionRGB["skyblue"]:
                    self.px, self.py = row*cellwidth+cellwidth/2, col*cellheight+cellheight/2 # Converting to pygame coordinates

    def addAttempt(self):
        # Adds one ot the attempt count
        self.attemptCount += 1

    def resetPlayerParams(self):
        # Resets all params, dx, and dy
        for i in range(len(self.parameters)):
            self.parameters[i] = 1
        
        self.dx = 0
        self.dy = 0
        self.playerAlpha = 255

    def resetTimer(self):
        # resets the timer
        self.starttime = time.time()

    def resetPlayerStats(self):
        # Resets all of the stats for the level
        self.attemptCount = 1 # starts at 1 
        self.resetTimer()
        self.buttonsClicked = 0

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
    
    def update(self):
        if self.dx == 0 and self.dy == 0: self.applyRegulateAlpha() # If it just spawned, then it will regulate the alpha

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


p1 = Player(screen, [(100, 100)], 0, (123, 123, 123))
playerSprite = pygame.sprite.Group()
playerSprite.add(p1)

screen.fill((255, 255, 255)) # Clearing screen completely before starting

p1.backgroundHandler.runSplashScreen(["levels", "tutorials", "tests"])

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
