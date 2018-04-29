from CellBoard import CellBoard
import pygame, sys

size = x, y = 1440, 900
screen = pygame.display.set_mode((size))
screen.fill((255, 255, 255))

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
    def __init__(self, surface, cellwidth=20, cellheight=20, boardwidth=25, boardheight=25, borders=True):

        CellBoard.__init__(self, surface, cellwidth, cellheight, boardwidth, boardheight, borders)
    
class MapCreator:
    def __init__(self, surface, maplevels=[], cellwidth=20, cellheight=20, boardwidth=25, boardheight=25, borders=True):


        self.surface = surface
        self.maplevels = maplevels
        # (cmaplvl = currentmaplevel)
        self.cmaplvlindex = 0
        
        self.cellwidth = cellwidth
        self.cellheight = cellheight
        self.boardwidth = boardwidth
        self.boardheight = boardheight
        self.borders = borders
        

    def events(self, event):
        
        # Getting the current map 
        cmaplvl = self.maplevels[self.cmaplvlindex]

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
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

                self.maplevels[self.cmaplvlindex].redraw()

                self.update()

            elif event.key == pygame.K_DOWN:
                # Going to previous map level (not less than 0)
                self.cmaplvlindex = max(self.cmaplvlindex-1, 0)

                self.maplevels[self.cmaplvlindex].redraw()

                self.update()

            elif event.key == pygame.K_p:
                self.saveMap()
                
        elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
            # Left mouse click to place cube 
            if pygame.mouse.get_pressed() == (1, 0, 0):
                mousex, mousey = event.pos
                cellx, celly = cmaplvl.cell_coords(mousex, mousey)
                cmaplvl.fillCell(cellx, celly)

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


m = MapCreator(screen, [MapLevel(screen)])

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
