from CellBoard import CellBoard
import pygame, sys
from copy import deepcopy
import random, math

size = x, y = 1440, 900
screen = pygame.display.set_mode((size))
screen.fill((255, 255, 255))

pygame.font.init()

def text_objects(text, font, color, rotation=0):
    textSurface = font.render(text, True, color)
    textSurface = pygame.transform.rotate(textSurface, rotation)
    return textSurface, textSurface.get_rect()

def display_text(text, size, font, color, rotation=0):
    torender = pygame.font.Font(font, size)
    TextSurf, TextRect = text_objects(text, torender, color, rotation)
    TextRect.center = (0, 0)
    return TextSurf, TextRect

class MapLevel(CellBoard):
    def __init__(self, surface, borders=True, verts=False, cellwidth=20, cellheight=20, boardwidth=25, boardheight=25):

        CellBoard.__init__(self, surface, borders, verts, cellwidth, cellheight, boardwidth, boardheight)

        # For connecting verticies
        self.lines = []

    def redraw(self):
        for l in self.celllist:
            for cell in l:
                cell.drawCell()

    def getCelllist(self):
        return self.celllist

class MapCreator:
    def __init__(self, surface, maplevels=[], cellwidth=20, cellheight=20, boardwidth=25, boardheight=25, borders=True):

        self.surface = surface

        self.maplevels = maplevels
        self.cmaplvlindex = 0 # Index and displayed 

        self.cellwidth = cellwidth
        self.cellheight = cellheight
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.borders = borders

        self.colorlist = [(0, 0, 0), (255, 175, 255), (255, 0, 0), (185, 0, 255), (185, 125, 255), (255, 128, 0), (255, 255, 0)]
        self.color = (0, 0, 0)

        # Updating the display
        self.update()

    def events(self, event):
        
        # Getting the current map 
        cmaplvl = self.maplevels[self.cmaplvlindex]
        # For selecting colors
        keycolorlist = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
        if event.type == pygame.KEYDOWN:
            
            # Going between different levels

            if event.key == pygame.K_RIGHT:
                # Going to the next map level
                self.cmaplvlindex += 1

                # Adding a level if there isn't enough
                if self.cmaplvlindex >= len(self.maplevels):
                    # Compensating for borders
                    hbdwidth = self.cellheight/10
                    wbdwidth = self.cellwidth/10

                    s = pygame.Surface((self.cellwidth*self.boardwidth+hbdwidth, self.cellheight*self.boardheight+wbdwidth))
                    m = MapLevel(s)
                    self.maplevels.append(m)

            elif event.key == pygame.K_LEFT:
                # Going to previous map level (min 0)
                self.cmaplvlindex = max(0, self.cmaplvlindex-1)

            # Saving the map
            elif event.key == pygame.K_s:
                print("What would you like to name your maps?: ", end="")
                self.saveMaps(str(input()))

            # If number, select color
            elif event.key in keycolorlist:
                try:
                    self.color = self.colorlist[keycolorlist.index(event.key)]
                    print(self.color)
                except:
                    # Error message for telling range of numbers to select
                    print("You have selected an unknown color. Please select numbers only in the range (0, " + str(len(self.colorlist)-1) + str(")"))
        
        elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
            # Left mouse click to place
            if pygame.mouse.get_pressed() == (1, 0, 0):
                mousex, mousey = event.pos
                # Getting the coords in the board from running a function from a dictionary
                x, y = cmaplvl.cell_coords(mousex, mousey)

                # Now filling it
                cmaplvl.fillCell(x, y, self.color)

            # Right mouse to erase
            if pygame.mouse.get_pressed() == (0, 0, 1):
                mousex, mousey = event.pos
                # Getting the coords in the board from running a function from a dictionary
                x, y = cmaplvl.cell_coords(mousex, mousey)
                # Now erasing it
                cmaplvl.eraseCell(x, y)

    def update(self):
        # Clearing the screen
        self.surface.fill((255, 255, 255))
        
        # Updating the current map
        self.maplevels[self.cmaplvlindex].redraw()

        # Displaying the current map
        self.surface.blit(self.maplevels[self.cmaplvlindex].surface, (0, 0))

        # Displaying the current map number
        self.maplabelsurf, self.maplabelrect = display_text("Level: "+str(self.cmaplvlindex), 20, pygame.font.get_default_font(), (0,0,0))
        self.surface.blit(self.maplabelsurf, (1200, 100))

    def saveMaps(self, name):
        f = open(name+".txt", "w")

        celllists = [m.getCelllist() for m in self.maplevels]

        for celllist in celllists:
            # SPACER for multiple maps
            f.write("SPACER")
            f.write("\n")
            for i in range(len(celllist)):
                for j in range(len(celllist[0])):
                    f.write(str(celllist[i][j].color)+";("+str(i)+","+str(j)+")")
                    f.write("\n")
        
        f.close()

s1 = pygame.Surface((502, 502))
m = MapCreator(screen, [MapLevel(s1)])

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        
        m.events(event)

    # Updating the display
    m.update()

    pygame.display.flip()
