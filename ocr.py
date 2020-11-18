import pytesseract
import cv2
import numpy as np

debug = False

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
        value = ocrCell(scanImage, nextPanelX*panelWidth+nextCellX*cellWidth, nextPanelY*panelHeight+nextCellY*cellHeight, cellWidth, cellHeight)
    
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
def doOCR(originalImage):
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
            print(i)
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
    
    

    

