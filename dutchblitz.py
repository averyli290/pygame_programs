import pygame
from copy import *
import math
import sys
import random

def main():
    ## All of the first things to initialize
    pygame.init()
    size = width, height = 1440, 900
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Dutch Blitz")
    screen.fill((7, 99, 36)) # Setting the background color to that of a card table
    
    def random_deck():
        deck = [color+num for color in ["r", "g", "b", "y"] for num in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]]
        random.shuffle(deck)
        return deck

    def text_objects(text, font, color, rotation=0):
        textSurface = font.render(text, True, color)
        textSurface = pygame.transform.rotate(textSurface, rotation)
        return textSurface, textSurface.get_rect()

    def display_text(text, size, font, color, rotation=0):
        torender = pygame.font.Font(font, size)
        TextSurf, TextRect = text_objects(text, torender, color, rotation)
        TextRect.center = (0, 0) 
        return TextSurf, TextRect

    class Card(pygame.sprite.Sprite):
        def __init__(self, playerID, color, number, bdwidth, width, height, topLeft, placeHolder = False):
            pygame.sprite.Sprite.__init__(self)
           
            # If needed, number can be a string to represent a different thing

            # Making each sprite have their own surface and moving that surface around the screen
            #self.surface = pygame.Surface(screen.get_size())
            self.surface = pygame.Surface((width+bdwidth*2, height+bdwidth*2))
            self.surface.fill((7, 99, 36))

            # Reinitializing variables for later use
            self.playerID = playerID # For scoring in Dutch Blitz later
            self.number = number
            self.topLeft = topLeft
            self.color = color
            self.fontcolor = (0, 0, 0)
            # If the color is black, then the fontcolor has to be white
            if self.color == (0, 0, 0): self.fontcolor = (255, 255, 255)
            self.height = height
            self.width = width
            self.bdwidth = bdwidth
            self.placeHolder = placeHolder

            # Determining the font size (default is 18)
            self.fontsize = int(width/75*30)

            # Initializing the card shape
            if not placeHolder: # placeHolders don't have color
                self.card = pygame.draw.rect(self.surface, color, (bdwidth, bdwidth, width, height))
             
            self.cardBorder = pygame.draw.rect(self.surface, (0, 0, 0), (0, 0, self.width+self.bdwidth, self.height+self.bdwidth), self.bdwidth) # Border always has a black color to start

            if not placeHolder: # placeHolders don't have numbers
                # Displaying the number on the top of the card and the bottom of the card
                self.numberSurf1, self.numberRect1 = display_text(str(number), self.fontsize, "freesansbold.ttf", self.fontcolor)
                self.numberSurf2, self.numberRect2 = display_text(str(number), self.fontsize, "freesansbold.ttf", self.fontcolor, 180) # Rotating this number 
            
                # The text objects function returns the surface, so we get the surface to blit it to the card surface, which is blitted to the screen 
                self.surface.blit(self.numberSurf1, (width/2-self.numberRect1.width/2, 2*height/9-self.numberRect1.height/2))
                self.surface.blit(self.numberSurf2, (width/2-self.numberRect2.width/2, 7*height/9-self.numberRect2.height/2))

            # Blitting in everything 
            screen.blit(self.surface, topLeft) # Adding the surface to the screen because the rectangle is on the surface so it now appears on the screen. Adjusting the position of the surface now changes the position of the rectangle

        def move(self, topLeft):
            screen.fill((7, 99, 36))
            screen.blit(self.surface, topLeft)
            self.topLeft = topLeft # Updating the position

        def redraw(self): # When a card is moved, the screen is refilled with green, so redrawing is needed
            screen.blit(self.surface, self.topLeft)

        def highlight(self):
            self.cardBorder = pygame.draw.rect(self.surface, (255, 223, 0), (0, 0, width+self.bdwidth, height+self.bdwidth), self.bdwidth) # Border is golden if selected 
            self.redraw()

        def unhighlight(self):
            self.cardBorder = pygame.draw.rect(self.surface, (0, 0, 0), (0, 0, width+self.bdwidth, height+self.bdwidth), self.bdwidth) # Border is golden if selected 
            self.redraw()

    class Stack(pygame.sprite.Sprite):
        def __init__(self, playerID, startList, stackType, topLeft, hotkey, cardwidth, cardheight, cardbdwidth):
            pygame.sprite.Sprite.__init__(self)
            
            placeHolderSizeRatio = 1.2
            self.placeHolderTopLeft = (topLeft[0]-cardwidth*(placeHolderSizeRatio-1)/2, topLeft[1]-cardwidth*(placeHolderSizeRatio-1)/2)

            # Initializing variables for later use
            self.stackType = stackType
            self.topLeft = topLeft
            self.hotkey = hotkey
            self.playerID = playerID
            self.cardbdwidth = cardbdwidth

            # Border width, rectangle dimensions, and position changes
            # If the pile is a dutch pile, the placeHolder card has no border (it is invisible)
            if self.stackType == "dutch":
                self.cardbdwidth = 1 

            self.stackList = [Card(playerID, (0, 0, 0), 0, self.cardbdwidth, cardwidth*placeHolderSizeRatio, cardheight+cardwidth*(placeHolderSizeRatio-1), self.placeHolderTopLeft, True)] 

            # Updating the stackList
            self.stackList += startList

            # Showing the hotkey for the stack (fontsize is 2/3's of the cards font size)
            #self.hotkeySurf = pygame.Surface(self.stackList[0].fontSize)

            # If the stacking is on "post", then the id's have to be the same
            # Stack choices are "blitz", "wood", "post", and "dutch"
            # offset is for "wood" and "post"

            # Checking to make sure that the dutch pile always starts with 1
            if self.stackType == "dutch":
                if len(self.stackList) > 1:
                    if self.stackList[1].number != 1:
                        self.stackList = self.stackList[0] # Only placeholder now

            # Putting all of the cards into position
            self.initializeCardPositions()
            
            self.drawStack() # To make it show up on the screen
        
        def deselect_top_card(self):
            self.stackList[-1].unhighlight() 

        def select_top_card(self):
            self.stackList[-1].highlight()

        def drawStack(self):
            for card in self.stackList:
                card.redraw()

        def stackCard(self, card, checking=False, initialization=False):
            ## Checking variable is for seeing if the stacking is valid
            toStack = False
            
            # If the card below is a placeHolder for post, blitz and wood piles, then just true (dutch piles ineed 1 at bottom)
            if self.stackList[-1].placeHolder and self.stackType != "dutch":
                toStack = True

            # Wood and blitz piles can have any stack config ONLY if this is in initialization, otherwise there is no stacking on these piles 
            elif self.stackType in ["wood", "blitz"] and initialization:
                toStack = True

            # Two cases for dutch piles: There is only a placeholder, or there are already other cards
            # Case 1:
            elif self.stackType == "dutch" and len(self.stackList) == 1 and card.number == 1: # There is a only a placeholder only if len(self.stackList) == 1, then add card if the number is 1
                toStack = True
            
                
            # Checking for dutch piles
            if len(self.stackList) > 1: # If there is a card other than a placeholder in the stack

                # Two cases for dutch piles: There is only a placeholder, or there are already other cards
                # Case 2:
                if self.stackType == "dutch" and self.stackList[-1].color == card.color and self.stackList[-1].number == card.number-1 and self.stackList[1].number == 1: # (Making sure that the dutch pile always starts with 1, but checking second card because 1st crad is placeholder)
                    toStack = True

                # Checking the color validity
                if (self.stackList[-1].color in [(255, 0, 0), (0, 0, 255)] and card.color in [(0, 255, 0), (255, 255, 0)]) or (card.color in [(255, 0, 0), (0, 0, 255)] and self.stackList[-1].color in [(0, 255, 0), (255, 255, 0)]):
                    # Now checking the number validity for "post" piles
                    if self.stackType == "post" and self.stackList[-1].number == card.number + 1:
                        toStack = True 
            
            # Making sure not to stack placeholders
            if card.placeHolder:
                toStack = False

            # Blitz piles cannot have more than 10 cards (+ placeholder)
            if len(self.stackList) >= 11 and self.stackType == "blitz":
                toStack = False

            # Now stacking the card if toStack == True and it is not just checking
            if toStack and not checking:
                self.stackList.append(card)

                # Offsets are for realistic stacking
                # No yadjust for "post" piles
                # For "dutch" piles there is random xadjust and yadjust for making it look like a "pile"
                yadjust = 0
                xadjust = 0

                if self.stackType in ["wood", "post"]: # Checking if there is stacking adjust
                    yadjust = card.height/4
                elif self.stackType == "dutch":
                    xadjust = random.randrange(-25, 25)/100*card.width
                    yadjust = random.randrange(-25, 25)/100*card.width
                
                if self.stackType == "wood": # Now checking for x offset
                    xadjust = card.width/4

                if self.stackType != "dutch": # "dutch" piles are set a limited distance away from the pile, so there is no xadjust*_, only xadjust
                    # Depending on the number of cards in stack, the offset is in multiple increments (-1 for the first card, and then -1 again for the placeHolder)
                    card.move((self.topLeft[0]+xadjust*(len(self.stackList)-2), self.topLeft[1]+yadjust*(len(self.stackList)-2)))
                else:
                    card.move((self.topLeft[0]+xadjust, self.topLeft[1]+yadjust))
            
            self.drawStack() # To reblit the cards

            return toStack
        
        def stackCardList(self, cardlist, checking=False):
            # Temp list for resetting the stackList to later
            #tempList = deepcopy(self.stackList)
            prevlen = len(self.stackList)
            # Stacking every card in the list
            for card in cardlist:
                # Checking to make sure that they are all valid first
                if self.stackCard(card, True) == False: # If it isn't then returning false at end (using the checking mode)
                    # Putting the stackList back to normal
                    self.stackList = self.stackList[:prevlen]
                    return False
                # Now appending the card to the stackList because the later cards depend on stacking on the cards before it, so we need to update the list
                # Basically simulating stacking without stacking
                self.stackList.append(card)
            

            # Putting the stackList back to normal
            self.stackList = self.stackList[:prevlen] 
            
            ## Only stacking if not checking
            if not checking:
                for card in cardlist:
                    # Now stacking because from here we know that they are all valid
                    self.stackCard(card)

            return True # Returning that we can stack the cards
        
        def poptopcard(self):
            # Checking to make sure that the placeHolder card is still there
            if len(self.stackList) > 1:
                self.stackList.pop()

        def initializeCardPositions(self):
            stackqueue = self.stackList[1:] # Stacking each individual card to make sure that it is valid
            self.stackList = [self.stackList[0]] 

            for card in stackqueue:
                self.stackCard(card, False, True)

        def returnCards(self):
            # Return every card except for the placeholder
            return self.stackList[1:]
        
        def clearCards(self):
            # Clears every card except for the placeholder
            self.stackList = [self.stackList[0]]
            return self.stackList[0]


    
    class Player:
        def __init__(self, playerID, hotkeysetup, cardwidth, cardheight, cardbdwidth, dutchpiles=None):
            ##### ADD IN BOT

            self.deck = random_deck() # Creating a random deck
            self.hotkeydict = {} # keeping track of hotkeys linked to decks
            self.hotkeysetup = hotkeysetup # (woodpilehotkey, blitzpilehotkey, [postpilehotkey1, postpilehotkey2, postpilehotkey3], [dutchpilehotkey1, ..., dutchpilehotkeyn], changeshifthotkey, fliphotkey) GIVEN AS TUPLE

            # Reinitializing values for later use
            self.playerID = playerID
            self.cardwidth = cardwidth
            self.cardheight = cardheight
            self.cardbdwidth = cardbdwidth
            
            # The hotkeyfor the pile that was selected at first. If nothing was pressed/ it was reset, it is None. 
            self.prevhotkey = None

            # For going through the wood pile deck
            self.woodpilepos = 0
            self.woodpileadder = 0 # When a card is played from the wood pile, the adder is butracted by one so it only displays two cards now (basically adjusting the number of cards shown when using the wood pile)
            # The adder starts at 0 because no cards are shown in the wood pile to start
            self.validMove = False # For checking whether there is still a valid move or not (so eventually the player can flip a card to the bottom of their wood pile from the top) 

        def handle_keys(self):
            # Finding whether there is a valid move or not
            self.validMove = self.findValidMove() if not self.validMove else True


            for event in pygame.event.get():
                if event.type == pygame.QUIT: # Detecting for quitting
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    for hotkey in self.hotkeydict:
                        if event.key == hotkey:
                            print([0 for c in self.woodpile if c == 0])
                            # If there was no previous pile selected, then the pile variable is set to the pile selected
                            if self.prevhotkey == None:
                                self.prevhotkey = hotkey
                                # Making the illusion of selecting
                                self.hotkeydict[hotkey].select_top_card()

                            elif self.prevhotkey == hotkey:
                                self.hotkeydict[hotkey].deselect_top_card()

                            else: # The stacking part
                                # Stacking a stack on top of another
                                if self.hotkeydict[self.prevhotkey].stackType == "post" and self.hotkeydict[hotkey].stackType == "post": # Only case where there is a stack of cards to stack on top of another stack
                                    cardlist = self.hotkeydict[self.prevhotkey].returnCards()
                                    if self.hotkeydict[hotkey].stackCardList(cardlist):# if stacking is successful, then clear the rest of the cards where there was a stack before
                                        self.hotkeydict[self.prevhotkey].clearCards()

                                # If the stacking if valid, popping the top card of the stack that has been accessed
                                elif self.hotkeydict[hotkey].stackCard(self.hotkeydict[self.prevhotkey].stackList[-1]):

                                    # For the wood pile, it is needed to fill in the space with 0 (explained in function "removeZeroes") 
                                    if self.hotkeydict[hotkey].stackList[-1] in self.woodpile:
                                        prevplace = self.woodpile.index(self.hotkeydict[hotkey].stackList[-1])
                                        
                                        # Completely remaking the woodpile (if you self the previous card to 0, then the card changes in the stack that it has been moved to)
                                        self.woodpile = self.woodpile[:]
                                        self.woodpile[prevplace] = 0 # Setting to 0 for removal later
                                        self.woodpileadder -= 1 # Modifying the adder to show less cards when updating
                                    self.hotkeydict[self.prevhotkey].poptopcard()


                                # Deselecting the card seletected before
                                self.hotkeydict[hotkey].deselect_top_card()
                                self.hotkeydict[self.prevhotkey].deselect_top_card()

                                # Resetting the selectedpile
                                self.prevhotkey = None

                            self.drawStacks()
                        
                    else:
                        # If an invalid key was pressed or the flip key, then the previous selected card is deselected
                        if hotkey not in self.hotkeydict or hotkey == self.hotkeysetup[-1]:
                            self.hotkeydict[self.prevhotkey].deselect_top_card()

                    if event.key == self.hotkeysetup[-1]: # For flipping wood pile
                        self.flipWoodPile()
                        self.drawStacks()


        def removeZeroes(self):
            # The zeroes are generated when a wood pile card is played, and there is an empty spot in the list left
            # However, the holes need to be filled with 0's in order to keep the rest of the list in the same order
            for card in self.woodpile:
                if card == 0:
                    self.woodpile.remove(card)


        def convertTextToCard(self, abbrev):
            # Just converting the abbreviations when genrating cards to cards

            color = [0, 0, 0]
            if abbrev[0] == "r":
                color[0] += 255
            elif abbrev[0] == "g":
                color[1] += 255
            elif abbrev[0] == "b":
                color[2] += 255
            else:
                color[0] += 255
                color[1] += 255

            color = tuple(color)

            # Getting the number
            number = int(abbrev[1]) if len(abbrev) == 2 else int(abbrev[1:3])

            return Card(self.playerID, color, number, self.cardbdwidth, self.cardwidth, self.cardheight, (0, 0))

        def initializePiles(self):
            # Initializing the piles

            self.blitzpile = [self.convertTextToCard(abbrev) for abbrev in self.deck[:10]]
            self.hotkeydict[self.hotkeysetup[1]] = Stack(self.playerID, self.blitzpile, "blitz", (475, 600), self.hotkeysetup[1], self.cardwidth, self.cardheight, self.cardbdwidth)
            
            self.postpile1 = [self.convertTextToCard(self.deck[10])]
            self.hotkeydict[self.hotkeysetup[2][0]] = Stack(self.playerID, self.postpile1, "post", (650, 600), self.hotkeysetup[2][0], self.cardwidth, self.cardheight, self.cardbdwidth)

            self.postpile2 = [self.convertTextToCard(self.deck[11])]
            self.hotkeydict[self.hotkeysetup[2][1]] = Stack(self.playerID, self.postpile2, "post", (775, 600), self.hotkeysetup[2][1], self.cardwidth, self.cardheight, self.cardbdwidth)
            
            self.postpile3 = [self.convertTextToCard(self.deck[12])]
            self.hotkeydict[self.hotkeysetup[2][2]] = Stack(self.playerID, self.postpile3, "post", (900, 600), self.hotkeysetup[2][2], self.cardwidth, self.cardheight, self.cardbdwidth)
           
            # The spacer is placed so when the user flips to the end, it acts as a signal for the endpoint of the deck (actually the beginning, but the deck is on a circle) 
            # Spacer uses string instead of number
            spacer = Card(self.playerID, (0, 0, 0), "End", self.cardbdwidth, self.cardwidth, self.cardheight, (0, 0))
            self.woodpile = [spacer]*3+[self.convertTextToCard(abbrev) for abbrev in self.deck[13:]]
            self.hotkeydict[self.hotkeysetup[0]] = Stack(self.playerID, [], "wood", (250, 600), self.hotkeysetup[0], self.cardwidth, self.cardheight, self.cardbdwidth)
            # The wood pile always starts out empty

            # Initializing the piles in the middle
            for i in range(len(self.hotkeysetup[3])):
                # Dutch puiles start out empty
                self.hotkeydict[self.hotkeysetup[3][i]] = Stack(self.playerID, [], "dutch", (150+125*i, 300), self.hotkeysetup[3][i], self.cardwidth, self.cardheight, self.cardbdwidth)

            self.drawStacks()

        def flipWoodPile(self):
            # Removing all 0's when starting to flip through
            if self.woodpilepos in [0, 1, 2, 3, 4, 5]:
                self.removeZeroes()

            self.woodpilepos += 3 # Iterating by 3

            if self.woodpilepos >= len(self.woodpile): # Greater than or equal to otherwise it will show the placeholder card at the end
                if not self.validMove: # Detects whether there is a move or not that works
                    print("No moves left.")

                # Resets self.validMove for the next round of flipping
                self.validMove = False
                
                # Since everything is flipped, there is a spacer card at the end for style/playability
                self.woodpilepos = 0 
                
                # The shift is only temporary because once it cycles through, the holes don't need to be accounted for anymore
                self.woodpileshift = 0
            
            # Resetting the adder because when a new set of three is flipped, it always shows three cards
            self.woodpileadder = 3

        def findValidMove(self):
            # This returns whether there is a valid move or not

            #### Checking for whether stacking on post piles is possible (post-post, wood-post, blitz-post)
            #### Same for dutch (wood-dutch, blitz-dutch, post-dutch)
           

            # Looking at two stacks and comparing them for each case

            for hotkey1 in self.hotkeydict:
                for hotkey2 in self.hotkeydict:
                    if hotkey1 != hotkey2:
                        # POST-POST
                        if self.hotkeydict[hotkey1].stackType == "post" and self.hotkeydict[hotkey2].stackType == "post":
                            if self.hotkeydict[hotkey2].stackCardList(self.hotkeydict[hotkey1].stackList, True):
                                print(hotkey1, hotkey2)
                                return True 

                        # WOOD-POST
                        elif self.hotkeydict[hotkey1].stackType == "wood" and self.hotkeydict[hotkey2].stackType == "post":
                            if self.hotkeydict[hotkey2].stackCard(self.hotkeydict[hotkey1].stackList[-1], True):
                                print(hotkey1, hotkey2)
                                return True
                        
                        # BLITZ-POST
                        elif self.hotkeydict[hotkey1].stackType == "blitz" and self.hotkeydict[hotkey2].stackType == "post":
                            if self.hotkeydict[hotkey2].stackCard(self.hotkeydict[hotkey1].stackList[-1], True):
                                print(hotkey1, hotkey2)
                                return True

                        # WOOD-DUTCH
                        elif self.hotkeydict[hotkey1].stackType == "wood" and self.hotkeydict[hotkey2].stackType == "dutch":
                            if self.hotkeydict[hotkey2].stackCard(self.hotkeydict[hotkey1].stackList[-1], True):
                                print(hotkey1, hotkey2)
                                return True 
                        
                        # BLITZ-DUTCH
                        elif self.hotkeydict[hotkey1].stackType == "blitz" and self.hotkeydict[hotkey2].stackType == "dutch":
                            if self.hotkeydict[hotkey2].stackCard(self.hotkeydict[hotkey1].stackList[-1], True):
                                print(hotkey1, hotkey2)
                                return True

                        # POST-DUTCH
                        elif self.hotkeydict[hotkey1].stackType == "post" and self.hotkeydict[hotkey2].stackType == "dutch":
                            if self.hotkeydict[hotkey2].stackCard(self.hotkeydict[hotkey1].stackList[-1], True):
                                print(hotkey1, hotkey2)
                                return True 

            return False 


        def drawStacks(self):
            # Wood pile only shows top 3 cards
            self.hotkeydict[self.hotkeysetup[0]] = Stack(self.playerID, self.woodpile[self.woodpilepos:self.woodpilepos+self.woodpileadder], "wood", (250, 600), self.hotkeysetup[0], self.cardwidth, self.cardheight, self.cardbdwidth)

            for hotkey in self.hotkeydict:
                self.hotkeydict[hotkey].drawStack()

        def changeShift(self):
            # This is for when the players get stuck, put the top card of the stack on the bottom
            # The top 3 cards are spacers, so take the 4th (3rd in 0-indexing)
            topCard = self.woodpile[3]
            self.woodpile.remove(topCard)
            self.woodpile += [topCard]
                
    hotkeys = (pygame.K_g, pygame.K_h, (pygame.K_j, pygame.K_k, pygame.K_l), (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8), pygame.K_c, pygame.K_SPACE)

    p1 = Player(1, hotkeys, 75, 112.5, 2)
    p1.initializePiles()

    ###################################
    ## USER PRESSES X IN TOP TO EXIT ##
    ###################################

    # Making the loop that runs the program
    mainloop = True
    while mainloop:

        p1.handle_keys() # Having the player class handle the keys

        pygame.display.flip() # Updating the screen
        
main()
