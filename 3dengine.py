import pygame, sys, math

# FROM YOUTUBE VIDEO https://www.youtube.com/watch?v=g4E9iq0BixA
# This was learned, not just copied

def main():
    # Setup
    pygame.init()
    size = width, height = 1440, 900

    screen = pygame.display.set_mode(size)

    # Locking the mouse to pygame
    pygame.event.get()
    pygame.mouse.get_rel()
    pygame.mouse.set_visible(0)
    pygame.event.set_grab(1)

    class Player(pygame.sprite.Sprite):
        def __init__(self, screen, color, pos=(0, 0, 0), rot=(0, 0)):
            pygame.sprite.Sprite.__init__(self)

            self.color = color
            self.screen = screen

            # List of verticies and edges for the map
            self.verts = []
            self.edges = []
            
            # The variable that is divided by z for simulating depth (The width of the screen divided by 2 because that is the center)
            self.depthVar = self.screen.get_width() 
            # Center of screen
            self.cx = self.screen.get_width()//2
            self.cy = self.screen.get_height()//2

            # Camera variables
            self.campos = list(pos)
            self.camrot = list(rot)
            self.clock = pygame.time.Clock()

            self.mousesens = 10

        def events(self, event):
            if event.type == pygame.MOUSEMOTION:
                x, y = event.rel
                x /= self.mousesens
                y /= self.mousesens

                self.camrot[0] += y
                self.camrot[1] += x

        def update(self, dt, key):
            
            # Adding movements
            s = dt*10

            if key[pygame.K_q]: self.campos[1] += s
            if key[pygame.K_e]: self.campos[1] -= s
            
            #x, y = s*math.sin(self.camrot[1]), s*math.cos(self.camrot[1])

            if key[pygame.K_w]: self.campos[2] += s
            if key[pygame.K_a]: self.campos[0] -= s
            if key[pygame.K_s]: self.campos[2] -= s
            if key[pygame.K_d]: self.campos[0] += s
            
        def handle_keys(self):
            dt = self.clock.tick()/1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                self.events(event)

            # Updating camera view depending on key inputs (in small increments, hence the 1000)
            key = pygame.key.get_pressed()
            self.update(dt, key)

        def initializeSetting(self):
            self.verts = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
            self.edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)] 

        def rotate2d(self, pos, rad):
            # Based on unit circle (counterclockwise)
            #  X  Y
            # (0, 1)   : (sin, cos)
            # (1, 0)   : (cos, -sin)
            # (0,-1)   : (-sin, -cos)
            # (-1 0)   : (-sin, cos)
            
            # Invert sin to make it clockwise
            x, y = pos
            s, c = math.sin(rad), math.cos(rad)

            # Adding in the rotation
            return x*c-y*s, y*c+x*s

        def renderPoints(self):
            
            # Clearing the screen
            screen.fill((255, 255, 255))
            
            # Rendering verticies
            for x,y,z in self.verts:

                x -= self.campos[0]
                y -= self.campos[1]
                z -= self.campos[2]

                # Adding in the mouse rotation
                # Rotating on the y axis first, then x axis
                x, z = self.rotate2d((x, z), self.camrot[1])
                y, z = self.rotate2d((y, z), self.camrot[0])


                # Simulating depth (The larger z is, the further away it will appear)
                depth = self.depthVar/z
                x, y = x*depth, y*depth

                # Creating the verticies (self.cx and self.cy because that is the center)
                pygame.draw.circle(self.screen, (0, 0, 0), (self.cx+int(x), self.cy+int(y)), 6)

            pygame.display.flip()
        
        def renderEdges(self):
            
            # Clearing the screen
            screen.fill((255, 255, 255))
            
            # Rendering edges
            for edge in self.edges:
                
                # Putting the edge points into a list
                points = []
                
                for x,y,z in (self.verts[edge[0]], self.verts[edge[1]]):

                    x -= self.campos[0]
                    y -= self.campos[1]
                    z -= self.campos[2]

                    # Adding in the mouse rotation
                    # Rotating on the y axis first, then x axis

                    x, z = self.rotate2d((x, z), self.camrot[1])
                    y, z = self.rotate2d((y, z), self.camrot[0])

                    # Getting the x and y coords for both points
                    depth = self.depthVar/z
                    x, y = x*depth, y*depth

                    # Adding the point to the list
                    points += [(self.cx+int(x), self.cy+int(y))]

                pygame.draw.line(self.screen, (0, 0, 0), points[0], points[1], 1)

            pygame.display.flip()

    p = Player(screen, (0, 255, 255), (0, 0, -5))
    p.initializeSetting()

    while True:
        p.handle_keys()
        p.renderEdges()

main()
