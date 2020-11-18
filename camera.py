import pygame
import math
import cv2
import ocr
from picamera import PiCamera

pygame.init()

debug = False

# Screen constants.
SCREEN_SIZE = SCREEN_WIDTH,SCREEN_HEIGHT = 800, 480

# Define the corner boxes.
CORNER_RADIUS = 30

# Get ready to take a picture.
camera = PiCamera()
camera.rotation = 180
camera.resolution = (2592, 1944)

# Remember the bounding cox if it has been defined.
boundingBox = None

# Color constants.
BLACK = 0, 0, 0
GREY = 128, 128, 128
WHITE = 255, 255, 255
PURPLE = 255, 128, 255
DARK_PURPLE = 200, 0, 200

# Cache the panel label symbols and positions needed.
PANEL_LABEL_FONT_SIZE = 25
panelLabelFont = pygame.font.SysFont('arialbold', PANEL_LABEL_FONT_SIZE)
panelLabelSymbols = {
    'CANCEL':panelLabelFont.render('CANCEL', True, DARK_PURPLE, WHITE),
    'START':panelLabelFont.render('START', True, DARK_PURPLE, WHITE),
    'REFRESH':panelLabelFont.render('REFRESH', True, DARK_PURPLE, WHITE),
    'CANCEL_':panelLabelFont.render('CANCEL', True, PURPLE, WHITE),
    'START_':panelLabelFont.render('START', True, PURPLE, WHITE),
    'REFRESH_':panelLabelFont.render('REFRESH', True, PURPLE, WHITE),
    'SCAN':panelLabelFont.render('Scan', True, PURPLE, WHITE)
    }

# Used to setup the screen controls.
def createButton(name, button, image, imageLight, position, callback):
    button["name"] = name
    button["image"] = image
    button["imageLight"] = imageLight
    button["rect"] = image.get_rect(topleft=position)
    button["callback"] = callback
    button["highlighted"] = False

# When a button is clicked redirects to the buttons callback function.
def buttonOnClick(button, event):
    if event.button == 1:
        if button["rect"].collidepoint(event.pos):
            if button["callback"] != None:
                return button["callback"](button)
            else:
                return False
    
# Highlight buttons when the mouse is over them.
def checkForMouseovers(screen, buttons):
    # Check for mouse over button.
    pointer = pygame.mouse.get_pos() # (x, y) location of pointer in every frame.
    for button in buttons:
        # If pointer is inside the button rectangle...
        if button['rect'].collidepoint(pointer):
            # Highlioght the button.
            showButton(screen, button, True)

# Handle the CANCEL button.
def pushButtonCancel(_):
    return True

# Handle the START button.
def pushButtonStart(_):
    return True
    
# Handle the RESET button.
def pushButtonRefresh(_):
    return True

# Grab a fresh image from the camera.
def refreshCameraImage():
    # Get the image.
    camera.capture('stateTable.jpg')
    image = pygame.image.load('stateTable.jpg')
    
    # Calculate the image scaling factor.
    imageWidth, imageHeight = image.get_rect().size
    imageScale = (SCREEN_HEIGHT-CORNER_RADIUS*3)/imageHeight
    showWidth = int(imageWidth * imageScale)
    showHeight = int(imageHeight * imageScale)
    imageDim = (showWidth, showHeight)
    
    # Get the scaled image.
    return pygame.transform.scale(image, imageDim),imageScale
    
    
# Draw the button passed onto the screen with optional highlighting.
def showButton(screen, button, highlight=False):
    if highlight:
        screen.blit(button["imageLight"], button["rect"])
        button["highlighted"] = True
    else:
        screen.blit(button["image"], button["rect"])
        button["highlighted"] = False

# Process the image of the finite state table.
def readValues(imageScale, boundingBox, imageX, imageY):
    image = cv2.imread('stateTable.jpg')
    scale = 1/imageScale
    topLeftX = int(boundingBox['topLeft'][0]*scale-imageX*scale)
    topLeftY = int(boundingBox['topLeft'][1]*scale-imageY*scale)
    bottomRightX = int(boundingBox['bottomRight'][0]*scale-imageX*scale)
    bottomRightY = int(boundingBox['bottomRight'][1]*scale-imageY*scale)
    cropped = image[topLeftY:bottomRightY, topLeftX:bottomRightX]
    if debug:
        cv2.imwrite('1 cropped.png', cropped)
    ocr.doOCR(cropped)

# Have the user outline the state transition table.
def getImageStateTable(screen):
    global boundingBox

    # Capture an image and scale it.
    showImage, imageScale = refreshCameraImage()
    refresh = False

    # Setup some corner points so that the user can select the table area from the picture.
    showWidth, showHeight = showImage.get_rect().size
    imageX = int((SCREEN_WIDTH - showWidth)/2)
    imageY = int((SCREEN_HEIGHT - showHeight)/2)
    centerX = int(showWidth/2) + imageX
    centerY = int(showHeight/2) + imageY
    
    if boundingBox == None:
        boundingBox = {
            'topLeft': (centerX-CORNER_RADIUS, centerY-CORNER_RADIUS),
            'topRight': (centerX+CORNER_RADIUS, centerY-CORNER_RADIUS),
            'bottomLeft': (centerX-CORNER_RADIUS, centerY+CORNER_RADIUS),
            'bottomRight': (centerX+CORNER_RADIUS, centerY+CORNER_RADIUS)
            }
    boxBounds = {
        'topLeft': (imageX, imageY, centerX-CORNER_RADIUS, centerY-CORNER_RADIUS),
        'topRight': (centerX+CORNER_RADIUS, imageY, showWidth+imageX, centerY-CORNER_RADIUS),
        'bottomLeft': (imageX, centerY+CORNER_RADIUS, centerX-CORNER_RADIUS, showHeight+imageY),
        'bottomRight': (centerX+CORNER_RADIUS, centerY+CORNER_RADIUS, showWidth+imageX, showHeight+imageY)
        }
    dragging = ''
    dragOffsetX = 0
    dragOffsetY = 0
    dragMinX = 0
    dragMinY = 0
    dragMaxX = 0
    dragMaxY = 0
    
    # Check buttons for mouse over.
    buttons = []
    
    # Define CANCEL button.
    cancelImage = panelLabelSymbols['CANCEL']
    cancelHighlightImage = panelLabelSymbols['CANCEL_']
    cancelButtonWidth, buttonHeight = cancelImage.get_rect().size
    cancelButton = {}
    createButton("cancel", cancelButton, cancelImage, cancelHighlightImage, 
                  (SCREEN_WIDTH  - cancelButtonWidth - 15, SCREEN_HEIGHT - buttonHeight - 5), pushButtonCancel)
    buttons.append(cancelButton)
    
    # Define START button.
    startImage = panelLabelSymbols['START']
    startHighlightImage = panelLabelSymbols['START_']
    startButtonWidth, buttonHeight = startImage.get_rect().size
    startButton = {}
    createButton("start", startButton, startImage, startHighlightImage, 
                  (SCREEN_WIDTH  - cancelButtonWidth - startButtonWidth - 30, SCREEN_HEIGHT - buttonHeight - 5), pushButtonStart)
    buttons.append(startButton)
    
    # Define REFRESH button.
    refreshImage = panelLabelSymbols['REFRESH']
    refreshHighlightImage = panelLabelSymbols['REFRESH_']
    refreshButtonWidth, buttonHeight = refreshImage.get_rect().size
    refreshButton = {}
    createButton("refresh", refreshButton, refreshImage, refreshHighlightImage, 
                  (SCREEN_WIDTH  - cancelButtonWidth - startButtonWidth - refreshButtonWidth - 45, SCREEN_HEIGHT - buttonHeight - 5), pushButtonRefresh)
    buttons.append(refreshButton)

    # Process the PyGame events.
    done = False

    while not done:
        
        if refresh:
            showImage, imageScale = refreshCameraImage()
        
        screen.fill(WHITE)
        screen.blit(showImage, (imageX, imageY))
        pygame.draw.rect(screen, BLACK, ((imageX, imageY), (showWidth, showHeight)), 4)
        pygame.draw.rect(screen, PURPLE, ((0, 0) , (SCREEN_WIDTH, SCREEN_HEIGHT)), 4)
        
        # Show the title.
        screen.blit(panelLabelSymbols['SCAN'], (10,10))
        
        # Draw the buttons.       
        showButton(screen, startButton)
        showButton(screen, cancelButton)
        showButton(screen, refreshButton)
        checkForMouseovers(screen, buttons)
        
        # Draw the bounding box.
        for corner in boundingBox:
            pygame.draw.circle(screen, PURPLE, boundingBox[corner], 30, 3)
            pygame.draw.circle(screen, PURPLE, boundingBox[corner], 6, 3)
        pygame.draw.line(screen, PURPLE, boundingBox['topLeft'], boundingBox['topRight'], 3)
        pygame.draw.line(screen, PURPLE, boundingBox['topLeft'], boundingBox['bottomLeft'], 3)
        pygame.draw.line(screen, PURPLE, boundingBox['bottomLeft'], boundingBox['bottomRight'], 3)
        pygame.draw.line(screen, PURPLE, boundingBox['topRight'], boundingBox['bottomRight'], 3)

        # Show the changes to the screen.
        pygame.display.flip()
        
        # Check the event queue. 
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            elif event.type == pygame.QUIT:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # First check all the buttons.
                if buttonOnClick(cancelButton, event):
                    return False
                
                if buttonOnClick(startButton, event):
                    readValues(imageScale, boundingBox, imageX, imageY)
                    return True
                
                if buttonOnClick(refreshButton, event):
                    if refresh:
                        refresh = False
                    else:
                        refresh = True
    
                
                if event.button == 1:
                    # See if the mouse is on one of the corners of the bounding box.
                    for corner in boundingBox:
                        cornerX = boundingBox[corner][0]
                        cornerY = boundingBox[corner][1]
                        mouseX, mouseY = event.pos
                        distance = math.sqrt( ((cornerX-mouseX)**2)+((cornerY-mouseY)**2) )
                        if distance < CORNER_RADIUS:
                            dragging = corner
                            dragOffsetX = cornerX - mouseX
                            dragOffsetY = cornerY - mouseY
                            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:            
                    dragging = ''

            elif event.type == pygame.MOUSEMOTION:
                if dragging != '':
                    mouseX, mouseY = event.pos
                    newX = mouseX+dragOffsetX
                    newY = mouseY+dragOffsetY
                    
                    # Make sure that the corners stay in their own quadrant.
                    if newX < boxBounds[dragging][0]:
                        newX = boxBounds[dragging][0]
                    elif newX > boxBounds[dragging][2]:
                        newX = boxBounds[dragging][2]
                    if newY < boxBounds[dragging][1]:
                        newY = boxBounds[dragging][1]
                    elif newY > boxBounds[dragging][3]:
                        newY = boxBounds[dragging][3]
                    boundingBox[dragging] = (newX, newY)
                    
                    # Only allow the user to define a rectangle.
                    if dragging == 'topLeft':
                        boundingBox['topRight'] = (boundingBox['topRight'][0], newY)
                        boundingBox['bottomLeft'] = (newX, boundingBox['bottomLeft'][1])
                    elif dragging == 'topRight':
                        boundingBox['topLeft'] = (boundingBox['topLeft'][0], newY)
                        boundingBox['bottomRight'] = (newX, boundingBox['bottomRight'][1])
                    elif dragging == 'bottomLeft':
                        boundingBox['bottomRight'] = (boundingBox['bottomRight'][0], newY)
                        boundingBox['topLeft'] = (newX, boundingBox['topRight'][1])
                    elif dragging == 'bottomRight':
                        boundingBox['bottomLeft'] = (boundingBox['bottomLeft'][0], newY)
                        boundingBox['topRight'] = (newX, boundingBox['topRight'][1]) 
