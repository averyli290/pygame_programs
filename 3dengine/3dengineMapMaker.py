from CellBoard import CellBoard
import pygame, sys
from copy import deepcopy
import random

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

class Cube(pygame.sprite.Sprite):
        verticies = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
        faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)]
        colors = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (255, 255, 255), (0, 0, 255),(0, 255, 0)]
        def __init__(self, pos=(0,0,0)):
            pygame.sprite.Sprite.__init__(self)
            
            x,y,z = pos
            # Getting all of the verticies
            self.verts = [(x+X/2, y+Y/2, z+Z/2) for X,Y,Z in self.verticies]


class MapLevel(CellBoard):
    def __init__(self, surface, borders=True, verts=True, cellwidth=20, cellheight=20, boardwidth=25, boardheight=25):

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
        if self.validVert(x1, y1) and self.validVert(x2, y2):
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
        # (cmaplvl = currentmaplevel)
        self.cmaplvlindex = 0 # Different from the number
        self.cmaplvlnum = 0 # Just for cosmetic display

        self.cellwidth = cellwidth
        self.cellheight = cellheight
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.borders = borders

        self.connectqueue = [] 

        # Updating the display
        self.update()

        # 0 = cubes, 1 = verticies/lines (This is a way of using a dictionary to run functions WITH inputs) (pass in x, y, map wanting to edit)
        self.editmodes = {pygame.K_0: 0, pygame.K_1: 1} # For checking whether the number selected there needs to be the pygame key, but to change the mode, the dictionary is needed
        self.editmode = 0
        self.coordFunctions = {0: lambda mx, my, mp: mp.cell_coords(mx, my),
                               1: lambda mx, my, mp: mp.vert_coords(mx, my)}
        self.fillFunctions = {0: lambda x, y, mp: mp.fillCell(x, y),
                              1: lambda x, y, mp: mp.fillVert(x, y, (0, 255, 0))} # Filling the vertexes with green
        self.eraseFunctions = {0: lambda x, y, mp: mp.eraseCell(x, y),
                               1: lambda x, y, mp: mp.eraseVert(x, y)}
        

    def events(self, event):
        
        # Getting the current map 
        cmaplvl = self.maplevels[self.cmaplvlindex]

        if event.type == pygame.KEYDOWN:
            
            # Going between different levels (z-axis) of map

            if event.key == pygame.K_UP:
                # Going to the next map level
                self.cmaplvlindex += 1
                # For updating text
                self.cmaplvlnum += 1

                # Adding a level if there isn't enough
                if self.cmaplvlindex >= len(self.maplevels):
                    # Compensating for borders
                    hbdwidth = self.cellheight/10
                    wbdwidth = self.cellwidth/10

                    s = pygame.Surface((self.cellwidth*self.boardwidth+hbdwidth, self.cellheight*self.boardheight+wbdwidth))
                    m = MapLevel(s)
                    self.maplevels.append(m)

            elif event.key == pygame.K_DOWN:
                # Going to previous map level
                self.cmaplvlindex -= 1
                # For updating text
                self.cmaplvlnum -= 1

                # Adding a level if there isn't enough
                if self.cmaplvlindex < 0:
                    # Compensating for borders
                    hbdwidth = self.cellheight/10
                    wbdwidth = self.cellwidth/10

                    s = pygame.Surface((self.cellwidth*self.boardwidth+hbdwidth, self.cellheight*self.boardheight+wbdwidth))
                    m = MapLevel(s)
                    self.maplevels.insert(0, m)
                    
                    # To no go into negative indexes
                    self.cmaplvlindex += 1

            # Saving the map
            elif event.key == pygame.K_p:
                self.saveMap()

            # Switching between editing modes
            elif event.key in self.editmodes:
                # Modifying the edit mode (if confused, look at the self.editmodes dictionary)
                self.editmode = self.editmodes[event.key] 
        
            # Drawing/placing objects
        elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
            # Left mouse click to place
            if pygame.mouse.get_pressed() == (1, 0, 0):
                mousex, mousey = event.pos
                # Getting the coords in the board from running a function from a dictionary
                x, y = self.coordFunctions[self.editmode](mousex, mousey, cmaplvl)

                # Now filling it
                self.fillFunctions[self.editmode](x, y, cmaplvl)

                # For placing verticies
                if self.editmode == 1:
                    # Adding the vertex to the queue (if proper vertex)
                    if cmaplvl.validVert(x, y):
                        self.connectqueue.append((x, y))
                    # Checking to see if to create line
                    if len(self.connectqueue) == 2:
                        x1, y1 = self.connectqueue[0]
                        x2, y2 = self.connectqueue[1]
                        cmaplvl.connectVerts(x1,y1,x2,y2)
                        # Resetting the connectqueue so we can draw more lines
                        self.connectqueue = []

            # Right mouse to erase
            if pygame.mouse.get_pressed() == (0, 0, 1):
                mousex, mousey = event.pos
                # Getting the coords in the board from running a function from a dictionary
                x, y = self.coordFunctions[self.editmode](mousex, mousey, cmaplvl)
                # Now erasing it
                self.eraseFunctions[self.editmode](x, y, cmaplvl)

                # This assumes that when erasing, the user will want to reclick the verticies again, so clearing the queue
                self.connectqueue = []

    def update(self):
        # Clearing the screen
        self.surface.fill((255, 255, 255))
        
        # Updating the current map
        self.maplevels[self.cmaplvlindex].redraw()

        # Displaying the current map
        self.surface.blit(self.maplevels[self.cmaplvlindex].surface, (0, 0))
        
        # Displaying the current map number
        self.maplabelsurf, self.maplabelrect = display_text("z axis: "+str(self.cmaplvlnum), 20, pygame.font.get_default_font(), (0,0,0))
        self.surface.blit(self.maplabelsurf, (1200, 100))

    def saveMap(self):
        # Getting the name of map to load
        print("Map name: ")
        filename = str(input())
        v = open(filename+"verts.txt", "w")
        e = open(filename+"edges.txt", "w")
        f = open(filename+"faces.txt", "w")
        c = open(filename+"colors.txt", "w")

        for l in range(len(self.maplevels)):
            level = self.maplevels[l]

            # Detecting cubes
            for i in range(level.boardheight):
                for j in range(level.boardwidth):
                    if level.celllist[i][j].isFilled():
                        # Converting from array to coords
                        x, y, z = -j, -l, i
                        # Translating the point so it is at the proper location ((x, y, z) is the center)
                        x -= 0.5
                        y += 1.5
                        z += 0.5
                        temp = Cube((x, y, z))

                        # Writing to files
                        for vert in temp.verts:
                            v.write(str(vert)+";")
                        
                        for edge in temp.edges:
                            e.write(str(edge)+";")

                        for faces in temp.faces:
                            f.write(str(faces)+";")

                        for colors in temp.colors:
                            c.write(str(colors)+";")

                        v.write("\n")
                        e.write("\n")
                        f.write("\n")
                        c.write("\n")

            # Detecting other edges
            for line in level.lines:
                verts = []; edges = []; faces = []; colors = [];
                
                verts.append((line[0][1], -l, line[0][0]))
                verts.append((line[1][1], -l, line[1][0]))
                verts.append((line[0][1], -l+1, line[0][0]))
                verts.append((line[1][1], -l+1, line[1][0]))
                
                edges.append((0, 1))
                edges.append((0, 2))
                edges.append((1, 3))
                edges.append((2, 3))

                faces = [(0, 1, 3, 2)]
                
                colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))]

                # Writing to files
                for vert in verts:
                    v.write(str(vert)+";")
                
                for edge in edges:
                    e.write(str(edge)+";")

                for faces in faces:
                    f.write(str(faces)+";")

                for colors in colors:
                    c.write(str(colors)+";")

                v.write("\n")
                e.write("\n")
                f.write("\n")
                c.write("\n")

        v.close()
        e.close()
        f.close()
        c.close()

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
