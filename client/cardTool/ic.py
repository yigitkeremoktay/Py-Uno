import cv2

img = cv2.imread('cards.png')

posX = 0
posY = 0

cardCountX = 14
cardCountY = 8

height, width = img.shape[:2]

cardHeight = int(height/cardCountY)
cardWidth = int(width/cardCountX)

for y in range(cardCountY):
    print('PosX'+str(posX))
    for x in range(cardCountX):
        print('PosY'+str(posY))
        cardEndX = posX+cardWidth
        cardEndY = posY+cardHeight
        cardBuf = img[posY:cardEndY, posX:cardEndX]
        posX = posX + cardWidth
        #tmp = cv2.cvtColor(cardBuf, cv2.COLOR_BGR2GRAY)
        #_,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
        #b, g, r = cv2.split(cardBuf)
        #rgba = [b,g,r, alpha]
        #dst = cv2.merge(rgba,4)
        dst = cardBuf
        cv2.imwrite('cards/card_'+str(y)+'_'+str(x)+'.png', dst)
    posY = posY + cardHeight
    posX = 0
