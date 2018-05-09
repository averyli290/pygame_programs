import pygame, sys, math, random, re

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
    
    class Cube(pygame.sprite.Sprite):
        verticies = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)] 
        faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5 , 4), (2, 3, 7 ,6), (0, 3, 7, 4), (1, 2, 6, 5)]
        colors = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (255, 255, 255), (0, 0, 255), (0, 255, 0)]
        def __init__(self, pos=(0,0,0)):
            pygame.sprite.Sprite.__init__(self)

            x,y,z = pos
            # Getting all of the verticies
            self.verts = [(x+X/2, y+Y/2, z+Z/2) for X,Y,Z in self.verticies]

    class Obj3d(pygame.sprite.Sprite):
        def __init__(self, verts, edges, faces, colors):
            pygame.sprite.Sprite.__init__(self)

            self.verts = verts
            self.edges = edges
            self.faces = faces
            self.colors = colors

            avgx = 0
            avgy = 0
            avgz = 0

            for i in range(len(self.verts)):
                avgx += self.verts[i][0]
                avgy += self.verts[i][1]
                avgz += self.verts[i][2]
            avgx, avgy, avgz = avgx/3, avgy/3, avgz/3

            self.center = (avgx, avgy, avgz)

    class Crosshair(pygame.sprite.Sprite):
        def __init__(self, screen, color=(192,192,192), width=12, height=12, thickness=2, centergap=6):
            pygame.sprite.Sprite.__init__(self)

            # Surface that crosshair will be on
            self.surface = pygame.Surface(((width*2+centergap, height*2+centergap)))
            # Making it transparent
            self.surface.set_colorkey((0, 0, 0))

            self.screen = screen
            self.rect = self.surface.get_rect()
            self.color = color
            self.width = width
            self.height = height
            self.thickness = thickness
            self.centergap = centergap 
            
            # For collision detection with targets
            self.chcenterlength = 1 # Width and height of the rectangle is going to be checked for collision detection
            self.image = pygame.Surface((self.chcenterlength, self.chcenterlength))
            self.image.fill((0, 0, 0))
            self.rect = self.image.get_rect()
            # Adding in the crosshair (it is invis because colorkey = (0,0,0))
            self.surface.blit(self.image, ((width*2-self.chcenterlength)/2, (height*2-self.chcenterlength)/2))

            self.totalwidth = self.width*2
            self.totalheight = self.height*2

            # drawing crosshair
            pygame.draw.rect(self.surface, color, (width-int(self.thickness/2), 0, self.thickness, height-int(self.centergap/2)))
            pygame.draw.rect(self.surface, color, (0, height-int(self.thickness/2), width-int(self.centergap/2), self.thickness))
            pygame.draw.rect(self.surface, color, (width-int(self.thickness/2), self.height+int(self.centergap/2), self.thickness, height-int(self.centergap/2)))
            pygame.draw.rect(self.surface, color, (self.width+int(self.centergap/2), self.height-int(self.thickness/2), width-int(self.centergap/2), self.thickness))

            self.screen.blit(self.surface, ((self.screen.get_width()-self.totalwidth)/2, (self.screen.get_height()-self.totalheight)/2))

        def redraw(self): 
            # redrawing crosshair at the center of the screen
            self.screen.blit(self.surface, ((self.screen.get_width()-self.totalwidth)/2, (self.screen.get_height()-self.totalheight)/2))

    class Player(pygame.sprite.Sprite):
        def __init__(self, screen, color, bgcolor, playerHeight=1.5, pos=(0,0,0), viewdistance=70, objlist=[], rot=(0, 0), verts=[], edges=[], faces=[]):
            pygame.sprite.Sprite.__init__(self)

            self.color = color
            self.bgcolor = bgcolor 
            self.screen = screen

            # List of objects, faces, verticies and edges for the map
            self.verts = verts
            self.edges = edges
            self.faces = faces
            self.objlist = objlist
            
            # The variable that is divided by z for simulating depth (The width of the screen divided by 2 because that is the center)
            self.depthVar = self.screen.get_width() 
            # Center of screen
            self.cx = self.screen.get_width()//2
            self.cy = self.screen.get_height()//2

            # Camera variables
            self.campos = list(pos)
            self.camrot = list(rot)
            self.clock = pygame.time.Clock()

            # Player variables
            self.playerHeight = playerHeight
            
            # Making crosshair
            self.crosshair = Crosshair(self.screen, (0, 255, 0))
            
            # How far the player can view 17500 standard
            self.viewdistance = viewdistance 

            # The higher this variable is, the lower the sensitivity (because we are dividing values by this number to get the rotation)
            self.mousesens = 500 
            
            # For gravity
            self.dy = 0
            self.gravcap = -100
            self.startfalldy = -0.1
            self.fallfactorincrease = 2 # Ratio for increase when falling

        def events(self, event):
            if event.type == pygame.MOUSEMOTION:
                x,y = event.rel

                x /= self.mousesens
                y /= self.mousesens

                self.camrot[0] += y
                self.camrot[1] += x 

        def objectsInView(self):
            # To optimize rendering by returning the list of objects that are close enough to be rendered
            returnme = [] 

            for obj in self.objlist:
                distance = math.sqrt(sum([(self.campos[i]-obj.center[i])**2 for i in range(3)]))
                if distance < self.viewdistance:
                    returnme += [obj]
            
            return returnme

        def updateGravity(self):
            applygravity = True 
            for obj in self.objectsInView():
                # Getting the ranges of the x, y, and z

                rangex = [min(vert[0] for vert in obj.verts), max(vert[0] for vert in obj.verts)]
                rangey = [min(vert[1] for vert in obj.verts), max(vert[1] for vert in obj.verts)]
                rangez = [min(vert[2] for vert in obj.verts), max(vert[2] for vert in obj.verts)]

                if self.campos[0] > rangex[0] and self.campos[0] < rangex[1] and self.campos[2] > rangez[0] and self.campos[2] < rangez[1]: 
                    if self.campos[1]+self.playerHeight >= min(rangey): # Checking to see how far the object below is
                        applygravity = False

                        # Remember, -y axis goes UP

            if applygravity:
                # If no gravity was applied earlier
                if self.dy == 0:
                    self.dy = self.startfalldy
                else:
                    self.dy = max(self.startfalldy, self.dy*self.fallfactorincrease)
            else:
                self.dy = 0

                    
        def update(self, dt, key):
            
            # Adding movements (s is the movement speed)
            s = dt*10

            # Checking for gravity

            if key[pygame.K_q]: self.campos[1] += s
            if key[pygame.K_e]: self.campos[1] -= s
            
            x, y = s*math.sin(self.camrot[1]), s*math.cos(self.camrot[1])
            
            # Applying the respective movements
            if key[pygame.K_w]: self.campos[0] += x; self.campos[2] += y
            if key[pygame.K_a]: self.campos[0] -= y; self.campos[2] += x
            if key[pygame.K_s]: self.campos[0] -= x; self.campos[2] -= y
            if key[pygame.K_d]: self.campos[0] += y; self.campos[2] -= x
            
            self.updateGravity()
            self.campos[1] -= self.dy

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
            
            self.renderFaces()
            # Updating camera view depending on key inputs (in small increments, hence the 1000)
            key = pygame.key.get_pressed()
            self.update(dt, key)

        def initializeSetting(self):
            phi = 1.618
            self.verts = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
            #self.verts = [(phi, 1, 0), (phi, -1, 0), (-1*phi, 1, 0), (-1*phi, -1, 0), (1, 0, phi), (-1, 0, phi), (1, 0, -1*phi), (-1, 0, -1*phi), (0, phi, 1), (0, phi, -1), (0, -1*phi, 1), (0, -1*phi, -1)]
            self.edges =[(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)] 
            #self.faces = [(0,1,4), (0, 1, 6)]

            self.faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5 , 4), (2, 3, 7 ,6), (0, 3, 7, 4), (1, 2, 6, 5)]

        def readfile(self, filename):

            try:
                vstep0 = []
                estep0 = []
                fstep0 = []
                cstep0 = []

                with open(filename+"verts.txt", "r") as v:
                    for line in v:
                        vstep0.append(line)

                with open(filename+"edges.txt", "r") as e:
                    for line in e:
                        estep0.append(line)

                with open(filename+"faces.txt", "r") as f: 
                    for line in f:
                        fstep0.append(line)

                with open(filename+"colors.txt", "r") as c: 
                    for line in c:
                        cstep0.append(line)

                vstep1 = [re.split(";", str(val)) for val in vstep0]
                estep1 = [re.split(";", str(val)) for val in estep0]
                fstep1 = [re.split(";", str(val)) for val in fstep0]
                cstep1 = [re.split(";", str(val)) for val in cstep0]
                
                vstep2 = [[re.sub(r"[^0-9\.\,\(\)]", "", val) for val in val0] for val0 in vstep1]
                estep2 = [[re.sub(r"[^0-9\.\,\(\)]", "", val) for val in val0] for val0 in estep1]
                fstep2 = [[re.sub(r"[^0-9\.\,\(\)]", "", val) for val in val0] for val0 in fstep1]
                cstep2 = [[re.sub(r"[^0-9\.\,\(\)]", "", val) for val in val0] for val0 in cstep1]

                vstep3 = [[val for val in val0 if val != ""] for val0 in vstep2]
                estep3 = [[val for val in val0 if val != ""] for val0 in estep2]
                fstep3 = [[val for val in val0 if val != ""] for val0 in fstep2]
                cstep3 = [[val for val in val0 if val != ""] for val0 in cstep2]

                vstep4 = [[eval(val) for val in val0] for val0 in vstep3]
                estep4 = [[eval(val) for val in val0] for val0 in estep3]
                fstep4 = [[eval(val) for val in val0] for val0 in fstep3]
                cstep4 = [[eval(val) for val in val0] for val0 in cstep3]

                self.objlist = []
                
                for i in range(len(vstep4)):
                    self.objlist.append(Obj3d(vstep4[i], estep4[i], fstep4[i], cstep4[i]))
            
            except Exception as e:
                print("Your file could not be read.")
            
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
        
        def convertCoords(self, x, y, z):
            # If perspective, applying the depth to x and y

            # This converts the coords from 3d to 2d for pygame
            x -= self.campos[0]
            y -= self.campos[1]
            z -= self.campos[2]

            # Making sure that there is no division by zero
            z = 1 if z == 0 else z

            # Rotating on the y axis first, then x axis
            x, z = self.rotate2d((x, z), self.camrot[1])
            y, z = self.rotate2d((y, z), self.camrot[0])
            
            # Simulating depth (The larger z is, the further away it will appear)
            depth = self.depthVar/z
            x, y = x*depth, y*depth
            
            return x, y, z 


        def renderPoints(self):
            # Clearing the screen
            screen.fill(self.bgcolor)
            
            # Rendering verticies
            for x,y,z in self.verts:
                
                # Converting coords
                x,y,z = self.convertCoords(x, y, z)

                # Creating the verticies (self.cx and self.cy because that is the center) 
                # Making the radius of the verticies
                radius = abs(int(20/z))
                pygame.draw.circle(self.screen, (0, 0, 0), (self.cx+int(x), self.cy+int(y)), radius) 

            pygame.display.flip()
        
        def renderEdges(self):
            # Clearing the screen
            screen.fill(self.bgcolor)
            
            # Rendering edges
            for edge in self.edges:
                
                # Putting the edge points into a list
                screen_coords = []
                
                for x,y,z in (self.verts[edge[0]], self.verts[edge[1]]):

                    # Converting coords
                    x,y,z = self.convertCoords(x, y, z)
                    
                    # Adding the point to the list
                    screen_coords += [(self.cx+int(x), self.cy+int(y))]
                    
                    # Thickness of lines (has to be at least 1, max is 100)
                    width = min(100, max(abs(int(30/z)), 1))
                
                pygame.draw.line(self.screen, (0, 0, 0), screen_coords[0], screen_coords[1], width)

            pygame.display.flip()

        def renderFaces(self):
            # Clearing the screen
            screen.fill(self.bgcolor)
            
            # Stores all face data
            face_list = []; distance_list = []; color_list = []
            
            for obj in self.objectsInView():
                # Translating all verticies to start, points is for 3d, screen_coords for 2d
                points = []
                screen_coords = []
                
                for x,y,z in obj.verts:
                    x -= self.campos[0]
                    y -= self.campos[1]
                    z -= self.campos[2]

                    x, z = self.rotate2d((x, z), self.camrot[1])
                    y, z = self.rotate2d((y, z), self.camrot[0])

                    points += [(x,y,z)]
                        
                    # Making sure that there is no division by zero
                    z = 1 if z == 0 else z

                    depth = self.depthVar/z
                    x,y = x*depth, y*depth
                        
                    screen_coords += [(self.cx+int(x), self.cy+int(y))]

                for f in range(len(obj.faces)):
                    face = obj.faces[f]
                
                    # Making sure that the face is in front of the camera
                    on_screen = False
                
                    # For each of the verticies in the face, if the z coord is > 0, then it is in front of the camera (draw it out!) 
                    for i in face:
                        x, y = screen_coords[i]
                        # checking to see whether to clip or not
                        if points[i][2] > 0 and x>0 and x<self.screen.get_width() and y>0 and y<self.screen.get_height(): on_screen = True; break
                    if on_screen:
                        # Getting the coordinates for each vertex on the face since we know that it is in front of the player
                        coords = [screen_coords[i] for i in face]

                        # Getting the color for the current face (f is an index within the cube faces)
                        color_list += [obj.colors[f]] 

                        # Putting the coords into the list for drawing later
                        face_list += [coords]

                        # Adding in the distance from player for sorting later (distance formula)
                        distance_list += [sum(sum(points[j][i] for j in face)**2 for i in range(3))]
          
            # Sorting the list by distance (the order is in indexes so it can be used for getting colors later)
            order = sorted(range(len(face_list)), key=lambda i: distance_list[i], reverse=True)
            
            # Final drawing part
            for i in order: 
                try: pygame.draw.polygon(self.screen, color_list[i], face_list[i])
                except: pass

            # Addding in the crosshair
            self.crosshair.redraw()

    #p = Player(screen, (0, 255, 255), (0, 0, 70), [Cube((0, 0, 0)), Cube((0, 0, 1)), Cube((1, 0, 0))])
    p = Player(screen, (0, 255, 255), (0, 0, 70))

    # Reading in the file
    print("What file would you like to read in?: ", end = "")
    filename = str(input())
    p.readfile(filename)

    while True:
        p.handle_keys()
        pygame.display.flip()


main()
