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
        self.lines= []

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
        self.cmaplvlnum = 0

        # Making the text for showing the map level
        self.maplabelsurf, self.maplabelrect = display_text("z axis: 0", 20, pygame.font.get_default_font(), (0,0,0))
        self.surface.blit(self.maplabelsurf, (1200, 100))

        self.cellwidth = cellwidth
        self.cellheight = cellheight
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.borders = borders

        self.connectqueue = [] 

        # Updating the display
        self.update()

    def events(self, event):
        
        # Getting the current map 
        cmaplvl = self.maplevels[self.cmaplvlindex]

        if event.type == pygame.KEYDOWN:
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

            elif event.key == pygame.K_p:
                self.saveMap()
        
        # Drawing/placing objects
        # Add drawing with verts
        elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
            # Left mouse click to place cube 
            if pygame.mouse.get_pressed() == (1, 0, 0):
                mousex, mousey = event.pos
                cellx, celly = cmaplvl.cell_coords(mousex, mousey)
                cmaplvl.fillCell(cellx, celly, (0, 0, 0))

            # Right mouse click to place vertex 
            if pygame.mouse.get_pressed() == (0, 0, 1):
                mousex, mousey = event.pos
                vertx, verty = cmaplvl.vert_coords(mousex, mousey)
                cmaplvl.fillVert(vertx, verty, (0, 255, 0))
                self.connectqueue.append((vertx, verty)) 
                if len(self.connectqueue) == 2:
                    x1, y1 = self.connectqueue[0]
                    x2, y2 = self.connectqueue[1]
                    cmaplvl.connectVerts(x1,y1,x2,y2)
                    self.connectqueue = [] 

            # Middle mouse click to erase
            if pygame.mouse.get_pressed() == (0, 1, 0):
                mousex, mousey = event.pos
                cellx, celly = cmaplvl.cell_coords(mousex, mousey)
                cmaplvl.eraseCell(cellx, celly)

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
                    if level.celllist[i][j].isFilled:
                        # x, y, z = j, -l, i 
                        temp = Cube((j, -l, i))
                        
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
                #verts.append((line[0][0], line[0][1], l))
                #verts.append((line[1][0], line[0][1], l))
                #verts.append((line[0][0], line[0][1], l+1))
                #verts.append((line[1][0], line[1][1], l+1))

                verts.append((line[0][1], -l, line[0][0]))
                verts.append((line[1][1], -l, line[1][0]))
                verts.append((line[0][1], -l+2, line[0][0]))
                verts.append((line[1][1], -l+2, line[1][0]))
                
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
