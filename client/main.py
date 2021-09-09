import socketio
import pygame
import os
import random
import uuid

print("Please enter your player name.")
pname = input()

sio = socketio.Client()

identifier = str(uuid.uuid4())

colors = ["red", "blue", "green", "yellow"]
numbers = ["0","1","2","3","4","5","6","7","8","9","plustwo","reverse"]

cardCursor = 0

lastCard = {}

showColorPicker = False
colorPickerReason = ""
colorPickerCursor = 0
players = []

currentPlayer = {
    "playerNick": pname,
    "identifier": identifier
}


class CardSprite(pygame.sprite.Sprite):
    def __init__(self, cardPath):
        super(CardSprite, self).__init__()
        self.surf = pygame.image.load(os.path.abspath(cardPath))

userCards = []

for xr in range(5):
    randColor = random.choice(colors)
    randType = random.choice(numbers)

    if(random.randint(0,10) > 6):
        randColor = "black"
        if(random.randint(0,1) == 1):
            randType = "plusfour"
        else:
            randType = "colorswap"

    cardPath = "cards/" + randColor + "_" + randType + ".png"
    cardSprite = CardSprite(cardPath)
    userCards.append({
        "cardType": randType,
        "cardColor": randColor,
        "cardFileName": cardPath,
        "cardSprite": cardSprite
    })


@sio.event
def connect():
    print('connection established')
    sio.emit('connected', { "name": pname, "identifier": identifier })

@sio.on('card')
def register_card_play(*args,**kwargs):
    data = args[0]
    if(identifier == data["playerIdentifier"]):
        print("Ignoring self echo event.")
        return

    cardColor = data["cardColor"]
    cardType = data["cardType"]

    cardPath = "cards/" + cardColor + "_" + cardType + ".png"
    if(data["cardMeta"] == "ModifiedColorswap"):
        cardPath = "cards/black_colorswap.png"
    if(data["cardMeta"] == "ModifiedPlusfour"):
        cardPath = "cards/black_plusfour.png"
    cardSprite = CardSprite(cardPath)
    global lastCard
    lastCard = {
        "cardType": cardType,
        "cardColor": cardColor,
        "cardFileName": cardPath,
        "cardSprite": cardSprite
    }
@sio.on('player_list_update')
def register_playerlist_update(*args,**kwargs):
    global players
    players = args[0]
    
@sio.on('new_turn')
def register_player_turn(*args,**kwargs):
    global currentPlayer
    currentPlayer = args[0]

@sio.on('plus_cards')
def register_plus_card(*args,**kwargs):
    extraCardCount = args[0]
    for x in range(extraCardCount):
        global userCards
        randColor = random.choice(colors)
        randType = random.choice(numbers)

        if(random.randint(0,10) > 6):
            randColor = "black"
            if(random.randint(0,1) == 1):
                randType = "plusfour"
            else:
                randType = "colorswap"

        cardPath = "cards/" + randColor + "_" + randType + ".png"
        cardSprite = CardSprite(cardPath)
        userCards.append({
            "cardType": randType,
            "cardColor": randColor,
            "cardFileName": cardPath,
            "cardSprite": cardSprite
        })
    

sio.connect('http://abduco.skyfallen.org:9375')

pygame.init()
pygame.font.init()

myfont = pygame.font.SysFont('Segoe UI', 10)

screen = pygame.display.set_mode([1000, 1000])
running = True
while running:
    cl = len(userCards)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if (event.type == pygame.KEYDOWN and showColorPicker == False and currentPlayer["playerIdentifier"] == identifier):
            if(event.key == pygame.K_LEFT):
                if(cardCursor != 0):
                    cardCursor = cardCursor - 1
            if(event.key == pygame.K_RIGHT):
                if((cardCursor + 1) != cl):
                    cardCursor = cardCursor + 1
            if(event.key == pygame.K_RETURN):
                if (lastCard == {} or (lastCard["cardType"] == userCards[cardCursor]["cardType"]) or (lastCard["cardColor"] == userCards[cardCursor]["cardColor"]) or (userCards[cardCursor]["cardColor"] == "black")):
                    cardType = userCards[cardCursor]["cardType"]
                    lastCard = userCards[cardCursor]
                    sio.emit("card", {
                        "cardType": lastCard["cardType"],
                        "cardColor": lastCard["cardColor"],
                        "playerIdentifier": identifier,
                        "cardMeta": "stdCard"
                    })
                    userCards.pop(cardCursor)
                    cardCursor = 0
                    turnOver = True
                    if(cardType == "colorswap"):
                        showColorPicker = True
                        colorPickerReason = "Colorswap"
                        turnOver = False
                    if(cardType == "plusfour"):
                        showColorPicker = True
                        colorPickerReason = "Plusfour"
                        turnOver = False
                    if(turnOver):
                        sio.emit("turn_over", {
                            "identifier": identifier
                        })
                else:
                    print("This card can not be used.")
            if(event.key == pygame.K_n):
                randColor = random.choice(colors)
                randType = random.choice(numbers)

                if(random.randint(0,10) > 6):
                    randColor = "black"
                    if(random.randint(0,1) == 1):
                        randType = "plusfour"
                    else:
                        randType = "colorswap"

                cardPath = "cards/" + randColor + "_" + randType + ".png"
                cardSprite = CardSprite(cardPath)
                userCards.append({
                    "cardType": randType,
                    "cardColor": randColor,
                    "cardFileName": cardPath,
                    "cardSprite": cardSprite
                })         
        if (event.type == pygame.KEYDOWN and showColorPicker):
            if(event.key == pygame.K_LEFT):
                if(colorPickerCursor != 0):
                    colorPickerCursor = colorPickerCursor - 1
                else:
                    colorPickerCursor = 3
            if(event.key == pygame.K_RIGHT):
                if(colorPickerCursor != 3):
                    colorPickerCursor = colorPickerCursor + 1
                else:
                    colorPickerCursor = 0
            if(event.key == pygame.K_a):
                color = "black"
                if(colorPickerCursor == 0):
                    color = "red"
                if(colorPickerCursor == 1):
                    color = "green"
                if(colorPickerCursor == 2):
                    color = "blue"
                if(colorPickerCursor == 3):
                    color = "yellow"
                cardSprite = CardSprite("cards/black_"+colorPickerReason+".png")
                cardObj = {
                    "cardType": "colorswap",
                    "cardColor": color,
                    "cardFileName": cardPath,
                    "cardSprite": cardSprite
                }
                lastCard = cardObj
                sio.emit("card", {
                    "cardType": lastCard["cardType"],
                    "cardColor": lastCard["cardColor"],
                    "cardMeta": "Modified"+colorPickerReason,
                    "playerIdentifier": identifier
                })
                sio.emit("turn_over", {
                    "identifier": identifier
                })
                showColorPicker = False          

    screen.fill((255, 255, 255))

    playerListXCur = 150

    for player in players:
        cpT = ""
        if(currentPlayer == player):
            cpT = "[Currently Playing] "
        textsurface = myfont.render(cpT + player["playerNick"], False, (0, 0, 0))
        screen.blit(textsurface,(50,playerListXCur))
        playerListXCur = playerListXCur + 20

    i = 0

    for x in userCards:
        posX = ((1000/(cl+2))*(i+1))
        card = x["cardSprite"]
        posY = 700
        if(i == cardCursor):
            posY = 550
        screen.blit(card.surf, (posX, posY))
        i = i + 1
    if(lastCard != {}):
        screen.blit(lastCard["cardSprite"].surf, (468, 300))
    if(cl == 0):
        textsurface = myfont.render('You won!', False, (0, 0, 0))
        screen.blit(textsurface,(200,800))
    if showColorPicker == True:
        if(colorPickerCursor == 0):
            pygame.draw.rect(screen, (255,0,0), pygame.Rect(30, 30, 60, 60))
        if(colorPickerCursor == 1):
            pygame.draw.rect(screen, (0,255,0), pygame.Rect(30, 30, 60, 60))
        if(colorPickerCursor == 2):
            pygame.draw.rect(screen, (0,0,255), pygame.Rect(30, 30, 60, 60))
        if(colorPickerCursor == 3):
            pygame.draw.rect(screen, (255,255,0), pygame.Rect(30, 30, 60, 60))
    textsurface = myfont.render('Python UNO', False, (0, 0, 0))
    screen.blit(textsurface,(20,10))
    if (lastCard != {} and lastCard["cardType"] == "colorswap" and showColorPicker == False):
        if(lastCard["cardColor"] == "red"):
            pygame.draw.rect(screen, (255,0,0), pygame.Rect(900, 30, 60, 60))
        if(lastCard["cardColor"] == "green"):
            pygame.draw.rect(screen, (0,255,0), pygame.Rect(900, 30, 60, 60))
        if(lastCard["cardColor"] == "blue"):
            pygame.draw.rect(screen, (0,0,255), pygame.Rect(900, 30, 60, 60))
        if(lastCard["cardColor"] == "yellow"):
            pygame.draw.rect(screen, (255,255,0), pygame.Rect(900, 30, 60, 60)) 

    pygame.display.flip()

pygame.quit()
