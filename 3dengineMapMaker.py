from CellBoard import CellBoard
import pygame, sys

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
        self.edges = []

    def connectVerts(x1, y1, x2, y2):
        if self.validVert(x1, y1) and self.validVert(x2, y2):
            self.edges.append((x1, y1, x2, y2))
        # Finish this 
    
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

                self.update()

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

                self.update()

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

            # Right mouse click to erase
            if pygame.mouse.get_pressed() == (0, 0, 1):
                mousex, mousey = event.pos
                cellx, celly = cmaplvl.cell_coords(mousex, mousey)
                cmaplvl.eraseCell(cellx, celly)

    def update(self):
        # Clearing the screen
        self.surface.fill((255, 255, 255))
               
        # Displaying the current map
        self.surface.blit(self.maplevels[self.cmaplvlindex].surface, (0, 0))
        
        # Displaying the current map number
        self.maplabelsurf, self.maplabelrect = display_text("z axis: "+str(self.cmaplvlnum), 20, pygame.font.get_default_font(), (0,0,0))
        self.surface.blit(self.maplabelsurf, (1200, 100))

    def saveMap(self):
        filename = "test.txt"
        f = open(filename, "w")

        # For keeping track of how many the edges/faces should be increment by
        cubecount = 0

        for l in range(len(self.maplevels)):
            level = self.maplevels[l]
            for i in range(level.boardheight):
                for j in range(level.boardwidth):
                    if level.celllist[i][j].isFilled:
                        # x, y, z = j, -l, i 
                        f.write(str(j)+" "+str(-l)+" "+str(i)+"\n")

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

    pygame.display.flip()
