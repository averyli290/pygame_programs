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

    def eraseVert(self, x, y): # Rewriting the function to erase edges when a vertex is remove
        # Have to add boolean for returning later
        valid = False

        # Keeping the old code
        if self.validVert(x, y):
            self.vertlist[x][y].clear()
            valid = True
            
        # Adding removing edges
        if valid:
            for line in self.lines[::-1]: # Have to reverse when removing things or else the length of the list will change causing skipping every other time, reversing keeps the old order in the part of the list untouched
                if (x, y) in line:
                    self.lines.remove(line)

            # Now adding blitting because the lines are now updated
            self.surface.blit(self.boardSurface, (0, 0))

        return valid



    def connectVerts(self, x1, y1, x2, y2):
        if self.validVert(x1, y1) and self.validVert(x2, y2) and (x1, y1) != (x2, y2):
            # Adding the edges to the list for updating later
            self.lines.append(((x1, y1), (x2, y2)))
            # Converting to screen coords
            screenx1 = x1*self.cellwidth
            screeny1 = y1*self.cellheight
            screenx2 = x2*self.cellwidth
            screeny2 = y2*self.cellheight
            return True
        return False

    def redraw(self):
        for l in self.celllist:
            for cell in l:
                cell.drawCell()

        try:
            for l in self.vertlist:
                for vert in l:
                    vert.drawCell()

        except:
            pass
    
        for line in self.lines:
            # Drawing the edges from the format in connectVerts
            # Converted to screen coords
            screenx1, screeny1 = line[0]
            screenx2, screeny2 = line[1]
            screenx1, screeny1 = screenx1*self.cellwidth, screeny1*self.cellheight
            screenx2, screeny2 = screenx2*self.cellwidth, screeny2*self.cellheight
            pygame.draw.line(self.surface, (0, 255, 0), (screenx1, screeny1), (screenx2, screeny2), 2)
    
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

        # Updating the display
        self.update()


    def events(self, event):
        
        # Getting the current map 
        cmaplvl = self.maplevels[self.cmaplvlindex]

        if event.type == pygame.KEYDOWN:
            
            # Going between different levels (z-axis) of map

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
            elif event.key == pygame.K_p:
                self.saveMap()

            # Drawing/placing objects
        elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
            # Left mouse click to place
            if pygame.mouse.get_pressed() == (1, 0, 0):
                mousex, mousey = event.pos
                # Getting the coords in the board from running a function from a dictionary
                x, y = cmaplvl.cell_coords(mousex, mousey)

                # Now filling it
                cmaplvl.fillCell(x, y)

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
        self.maplabelsurf, self.maplabelrect = display_text("Map level: "+str(self.cmaplvlindex), 20, pygame.font.get_default_font(), (0,0,0))
        self.surface.blit(self.maplabelsurf, (1200, 100))

    def saveMap(self):
        pass


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
