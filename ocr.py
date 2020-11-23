import pygame
import pytesseract
import cv2
import numpy as np

debug = True

# Read symbols '0' - '4' are immutable. An end symbol 'b' can however be substituted for the '5' symbol.
readSymbols = ['0', '1', '2', '3', '4', '5', 'b']

# Write symbols are '0' - '5'. Note that 'b' cannot be written so does not appear.
writeSymbols = ['0', '1', '2', '3', '4', '5']

# Move symbols are 'L' and 'R'.
moveSymbols = ['L', 'R']

# Goto symbols are 'A' - 'F'.
gotoSymbols = ['A', 'B', 'C', 'D', 'E', 'F', 'H']

# Scanned state table values go here.
scannedValues = [' ']*144

WHITE = 255, 255, 255
BLACK = 0, 0, 0
PURPLE = 255, 128, 255

# Globals. Will be used to iterate through the cells to fetch their values.
scanImage = None
imageWidth = 0
imageHeight = 0
panelWidth = 0
panelHeight = 0
cellWidth = 0
cellHeight = 0
nextPanelX = 0
nextPanelY = 0
nextCellX = 0
nextCellY = 0
scanDone = False

# Draw the title passed on the screen.
def drawTitle(screen, title):
    titleFont = pygame.font.SysFont('arialbold', 25)
    screen.blit(titleFont.render(title, True, PURPLE, WHITE), (10,10))

#
# Have Tesseract check the image passed for a single character.
# Special case for periods to avoid the rather slow Tesseract call.
# Return the character found.
#
def ocrCell(image, x, y, width, height):
    customConfig = r'-c tessedit_char_whitelist=.012345bLRABCDEF --oem 1 --psm 10'
    cell = image[y:y+height, x:x+width]
    if debug:
        cv2.imwrite('6 - cell.png', cell)

    count = width * height - cv2.countNonZero(cell)
    if count < 1000: 
        cellValue = " "
    else: 
        cellValue = (pytesseract.image_to_string(cell, config=customConfig)).strip()
    return cellValue

# Return the sub image at the coordinates passed.
def ocrCellImage(image, x, y, width, height):
    return image[y:y+height, x:x+width]

# Calculate the cell rectangles in the panel whose coordinates are passed and ocr them for the character they contain.
def nextCellValue():
    global scanImage
    global imageWidth
    global imageHeight
    global panelWidth
    global panelHeight
    global cellWidth
    global cellHeight
    global nextPanelX
    global nextPanelY
    global nextCellX
    global nextCellY
    global scanDone
    if scanDone == True:
        value = 'x'
    else:
        # Get the cached value.
        cellY = nextCellY
        if cellY < 5:
            cellY -= 1
        else:
            cellY -= 2
        value = scannedValues[nextPanelY*72+nextPanelX*6+cellY*18+nextCellX]
        if value == 'X':
            # There was a problem with the word OCR so try cell OCR.
            value = ocrCell(scanImage, nextPanelX*panelWidth+nextCellX*cellWidth, nextPanelY*panelHeight+nextCellY*cellHeight, cellWidth, cellHeight)
        if value == 'M':
            value = ' '
        nextCellX += 1
        if nextCellX == 6:
            nextCellX = 0
            nextCellY += 1
            if nextCellY == 5:
                nextCellY = 1
                nextCellX = 5
                nextPanelX += 1
                if nextPanelX == 3:
                    nextPanelX = 0;
                    nextPanelY += 1
                    if nextPanelY == 2:
                        nextPanelY = 0
                        scanDone = True   
    return value

# Process the image passed and calculate the state transition values.
def doOCR(originalImage, screen, boundingBox):
    global scanImage
    global imageWidth
    global imageHeight
    global panelWidth
    global panelHeight
    global cellWidth
    global cellHeight
    global nextPanelX
    global nextPanelY
    global nextCellX
    global nextCellY
    global scanDone
    
    title = 'Scanning . . .'
    drawTitle(screen, title)
    pygame.display.flip()
    
    # Convert to gray scale.
    grayImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
    if debug:
        cv2.imwrite('2 gray.png', grayImage)
    
    # Equalize the image with a CLAHE object (Arguments are optional).
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    equalizedImage = clahe.apply(grayImage)
    if debug:
        cv2.imwrite('3 equalized.png', equalizedImage)
    
    # Convert to binary.
    _, binaryImage = cv2.threshold(equalizedImage,140,255,cv2.THRESH_BINARY)
        
    # Now remove most of table lines in the binary image with a flood fill.
    for i in range(50):
        if binaryImage[i,i] == 0:
            cv2.floodFill(binaryImage, None, (i,i), [255,255,255])
    if debug:
        cv2.imwrite('4 binary.png', binaryImage)
    
    # Get rid of any noise.
    kernel = np.ones((5,5),np.uint8)
    dilatedImage = cv2.dilate(binaryImage,kernel,iterations = 1)
    if debug:
        cv2.imwrite('5 dilated.png',dilatedImage)
    
    # Setup the globals so that a call to get each cell value can be made from the UI.
    scanImage = dilatedImage
    imageHeight,imageWidth = scanImage.shape
    panelWidth = int(imageWidth / 3)
    panelHeight = int(imageHeight / 2)
    cellWidth = int(panelWidth/6)
    cellHeight = int(panelHeight/5)
    nextPanelX = 0
    nextPanelY = 0
    nextCellX = 5
    nextCellY = 1
    scanDone = False
    
    # Create a cell sized M surface.
    symbolM = pygame.Surface((cellWidth, cellHeight))
    symbolM.fill(WHITE)
    symbolMFont = pygame.font.SysFont('arialbold', int(cellHeight*1.1))
    symbolMSurface = symbolMFont.render('M', True, BLACK, WHITE)
    symbolMWidth, symbolMHeight = symbolMSurface.get_rect().size
    symbolM.blit(symbolMSurface, (int((cellWidth-symbolMWidth)/2), (int((cellHeight-symbolMHeight)/2))))
    imageX = pygame.surfarray.array2d(symbolM)
    imageX = imageX.swapaxes(0, 1)
    
    # Replace all of the blank spaces in the image with an M symbol.
    while not scanDone:
        x = nextPanelX*panelWidth+nextCellX*cellWidth
        y = nextPanelY*panelHeight+nextCellY*cellHeight
        cellImage = ocrCellImage(scanImage, x, y, cellWidth, cellHeight)
        count = cellWidth * cellHeight - cv2.countNonZero(cellImage)
        if count < 1000:
            # Replace blank image with X so ocr will "see" it.
            scanImage[y:y+cellHeight, x:x+cellWidth] = imageX
            
        nextCellX += 1
        if nextCellX == 6:
            nextCellX = 0
            nextCellY += 1
            if nextCellY == 5:
                nextCellY = 1
                nextCellX = 5
                nextPanelX += 1
                if nextPanelX == 3:
                    nextPanelX = 0;
                    nextPanelY += 1
                    if nextPanelY == 2:
                        nextPanelY = 0
                        scanDone = True
    if debug:
        cv2.imwrite('7 mmed.png',scanImage)
    
    # For each row OCR the symbols as words. Cache the results for the UI calls.
    customConfig = r'-c tessedit_char_whitelist=.012345bLRABCDEFHM --oem 1 --psm 8'
    nextValue = 0
    rectX,rectY = boundingBox['topLeft']
    rectWidth = boundingBox['bottomRight'][0]-rectX
    rectHeight = int((boundingBox['bottomRight'][1]-rectY)/10)
    box = pygame.Surface((rectWidth,rectHeight))  
    box.set_alpha(128)                
    box.fill(PURPLE)           

    for row in range(10):
        if row == 0 or row == 5:
            continue
        
        # Update the camera screen with our progress.
        title += ' .'
        drawTitle(screen, title)
        screen.blit(box, (rectX,rectY+rectHeight*row))   
        pygame.display.flip()
        
        y = row * cellHeight
        rowImage = scanImage[y:y+cellHeight, 0:imageWidth]
        rowValue = (pytesseract.image_to_string(rowImage, config=customConfig)).replace(" ", "")
        if debug:
            print(rowValue)
            
        # Remove any characters not in the set we are looking for. 
        cleanRow = ""
        for i in range(len(rowValue)):
            value = rowValue[i]
            if value == 'M' or value in readSymbols or value in writeSymbols\
                            or value in moveSymbols or value in gotoSymbols:
                cleanRow += value              
        if debug:
            print(cleanRow)
        
        # Remove trailing Ms.
        while len(cleanRow) > 18:
            if cleanRow[len(cleanRow)-1] == 'M':
                cleanRow = cleanRow[:len(cleanRow)-1]
        
        if len(cleanRow) == 18:
            for i in range(18):
                scannedValues[nextValue] = cleanRow[i]
                nextValue+=1  
        else:
            # Missing or extra character. Force cell based OCR.
            for i in range(18):
                scannedValues[nextValue] = 'X'
                nextValue+=1     
    
    # Reset for UI calls.
    nextPanelX = 0
    nextPanelY = 0
    nextCellX = 5
    nextCellY = 1
    scanDone = False

    

