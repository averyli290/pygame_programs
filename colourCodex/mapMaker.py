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
        
        self.colorlist = [(128, 128, 128), (0, 0, 0), (255, 175, 255), (0, 0, 255), (173, 216, 230), (255, 0, 0), (185, 0, 255), (185, 125, 255), (255, 128, 0), (0, 255, 0), (78, 46, 40), (255, 255, 0)]
        self.color = (0, 0, 0)

        # Updating the display
        self.update()

    def events(self, event):
        
        # Getting the current map 
        cmaplvl = self.maplevels[self.cmaplvlindex]
        # For selecting colors
        keycolorlist = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_t, pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o, pygame.K_p, pygame.K_a, pygame.K_s]
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

            # Saving the maps
            elif event.key == pygame.K_0:
                print("What would you like to name your maps?: ", end="")
                self.saveMaps(str(input()))
            # reading the maps
            elif event.key == pygame.K_9:
                print("What would you like to read in?: ", end="")
                self.readfile(str(input()))
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

    def isEmptyMap(self, m):
        # For clearing empty maps
        celllist = m.getCelllist()
        for row in range(len(celllist)):
            for col in range(len(celllist[row])):
                if m.isFilledCell(row, col): # Seeing if the cell is filled, it is is, then map is valid, return false
                    return False
        return True
    
    def clearEmptyMaps(self):
        # Clearing empty maps
        toset = []

        for m in self.maplevels:
            if not self.isEmptyMap(m):
                toset.append(m) # Append all of the maps that are not empty

        self.maplevels = toset

    def saveMaps(self, name):
        f = open(name+".txt", "w")
        
        self.clearEmptyMaps()
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
    
    def readfile(self, filename="levels"):
        # resetting the maps
        self.maplevels = []

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
            # Compensating for borders
            hbdwidth = self.cellheight/10
            wbdwidth = self.cellwidth/10

            s = pygame.Surface((self.cellwidth*self.boardwidth+hbdwidth, self.cellheight*self.boardheight+wbdwidth))
            toadd = MapLevel(s, True, False, 20, 20, len(colors[m]), len(colors[m][0]))

            # Adding the colors to the map
            tempcolors = colors[m]
            tempcoords = coords[m]

            for row in range(len(tempcolors)):
                for col in range((len(tempcolors[row]))):
                    if tempcolors[row][col] not in self.colorlist: # If the color is not recognized in color dictionary, set it to defualt color
                        tempcolors[row][col] = (255, 255, 255)
                    elif tempcolors[row][col] == (self.colorlist[0]): # Checking to see if it is the starting position
                        toadd.startPos = (row, col) # Setting the start position

                    toadd.fillCell(row, col, tempcolors[row][col])

            self.maplevels.append(toadd)

        # Clearing all empty maps
        self.clearEmptyMaps()

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
