import pygame

# Initialize the PyGame environment.
pygame.init()

#Set a periodic timer for demo mode.
TIMEREVENT = pygame.USEREVENT+1
pygame.time.set_timer(TIMEREVENT, 1000)
pygame.key.set_repeat(1000,100)

##### Globals
# Read symbols '0' - '4' are immutable. An end symbol 'b' can however be substituted for the '5' symbol.
readSymbols = ['b' , '5']

# Write symbols are '0' - '5'. Note that 'b' cannot be written so does not appear.
writeSymbols = ['0', '1', '2', '3', '4', '5', ' ']

# Move symbols are 'L' and 'R'.
moveSymbols = ['L', 'R', ' ']

# Goto symbols are 'A' - 'F'.
gotoSymbols = ['A', 'B', 'C', 'D', 'E', 'F', 'H', ' ']

# If true state machine will run without stopping, otherwise state machine will run one step at a time.
runState = 'STEP'

# Set to True if the play button was pressed.
playPressed = False
stateMachineRunning = False

# Set to true when a step has been setup and is waiting for the play button to be pressed.
stepReady = False

# Start of state machine running code.
currentState ='A'
currentStep = 'READ'

# The current transition being processed.
currentTransition = None

# Clock required by GUI manager.
clock = pygame.time.Clock()

# Only process mouse over events if the pointer has actually moved.
lastMousePosition = (0, 0)

# Keep track of the tape movement direction for the last transition.
lastMoveDirection = ' '

# Last file name loaded or saved.
lastFilename = ''

# Dictionary to hold the finite state table.
stateTable = {}

# Remember where the individual state panel pieces (A, B, C, D, E, F) have been drawn.
statePanelOffsets = {}

# Remember where all of the panel labels have been drawn.
panelLabelPositions = {}

# Tape values will be stored here.
TAPE_NUMBER_CELLS = 100000
tape = bytearray(TAPE_NUMBER_CELLS)
tapeHead  = int(TAPE_NUMBER_CELLS / 2) # The read/write position on the tape

# Color constants.
BLACK = 0, 0, 0
GREY = 128, 128, 128
WHITE = 255, 255, 255
PURPLE = 255, 128, 255
DARK_PURPLE = 200, 0, 200

# Screen constants.
SCREEN_SIZE = SCREEN_WIDTH,SCREEN_HEIGHT = 800, 480
SCREEN_ATTRIBUTES =  5 #pygame.FULLSCREEN

# Set to full screen for a Raspberry Pi 7" display. 
screen = pygame.display.set_mode(SCREEN_SIZE, SCREEN_ATTRIBUTES)
pygame.display.set_caption('TMD-2')
screen.fill(WHITE)

# Tape constants.
TAPE_START_X = 70
TAPE_START_Y = 70
TAPE_WIDTH = 660
TAPE_HEIGHT = 90
TAPE_BORDER_WIDTH = 3
TAPE_CELLS = 11

# Finite state transition table constants
TAPE_CELL_WIDTH = 60
TAPE_CELL_HEIGHT = 90
TAPE_CELL_FONT_SIZE = 70
TAPE_CELL_NUMBER_FONT_SIZE = 20

# Finite state transition table single state constants.
PANEL_CELL_WIDTH = 20
PANEL_CELL_HEIGHT = 25
PANEL_START_X = TAPE_START_X + PANEL_CELL_WIDTH + int(PANEL_CELL_WIDTH/2)
PANEL_START_Y = TAPE_START_Y + TAPE_CELL_HEIGHT + int(TAPE_CELL_HEIGHT/3)
PANEL_WIDTH = 132
PANEL_HEIGHT = 135
PANEL_BORDER_WIDTH = 2
PANEL_COLUMNS = 6
PANEL_ROWS = 5
PANEL_CELL_FONT_SIZE = 27
PANEL_LABEL_FONT_SIZE = 25

# Create a font for the tiny cell numbers.
cellNumberFont = pygame.font.SysFont('arialbold', TAPE_CELL_NUMBER_FONT_SIZE)

# Cache the tape symbols needed.
cellFont = pygame.font.SysFont('arial', TAPE_CELL_FONT_SIZE)
cellSymbols = {
    0:cellFont.render('0', True, BLACK, WHITE),
    1:cellFont.render('1', True, BLACK, WHITE),
    2:cellFont.render('2', True, BLACK, WHITE),
    3:cellFont.render('3', True, BLACK, WHITE),
    4:cellFont.render('4', True, BLACK, WHITE),
    5:cellFont.render('5', True, BLACK, WHITE),
    6:cellFont.render('b', True, BLACK, WHITE)
    }

# Cache the panel cell symbols needed.
panelCellFont = pygame.font.SysFont('arialbold', PANEL_CELL_FONT_SIZE)
panelCellSymbols = {
    '0':panelCellFont.render('0', True, BLACK, WHITE),
    '1':panelCellFont.render('1', True, BLACK, WHITE),
    '2':panelCellFont.render('2', True, BLACK, WHITE),
    '3':panelCellFont.render('3', True, BLACK, WHITE),
    '4':panelCellFont.render('4', True, BLACK, WHITE),
    '5':panelCellFont.render('5', True, BLACK, WHITE),
    'b':panelCellFont.render('b', True, BLACK, WHITE),
    'L':panelCellFont.render('L', True, BLACK, WHITE),
    'R':panelCellFont.render('R', True, BLACK, WHITE),
    'A':panelCellFont.render('A', True, BLACK, WHITE),
    'B':panelCellFont.render('B', True, BLACK, WHITE),
    'C':panelCellFont.render('C', True, BLACK, WHITE),
    'D':panelCellFont.render('D', True, BLACK, WHITE),
    'E':panelCellFont.render('E', True, BLACK, WHITE),
    'F':panelCellFont.render('F', True, BLACK, WHITE),
    'H':panelCellFont.render('H', True, BLACK, WHITE),
    '0_':panelCellFont.render('0', True, PURPLE, WHITE),
    '1_':panelCellFont.render('1', True, PURPLE, WHITE),
    '2_':panelCellFont.render('2', True, PURPLE, WHITE),
    '3_':panelCellFont.render('3', True, PURPLE, WHITE),
    '4_':panelCellFont.render('4', True, PURPLE, WHITE),
    '5_':panelCellFont.render('5', True, PURPLE, WHITE),
    'b_':panelCellFont.render('b', True, PURPLE, WHITE),
    'L_':panelCellFont.render('L', True, PURPLE, WHITE),
    'R_':panelCellFont.render('R', True, PURPLE, WHITE),
    'A_':panelCellFont.render('A', True, PURPLE, WHITE),
    'B_':panelCellFont.render('B', True, PURPLE, WHITE),
    'C_':panelCellFont.render('C', True, PURPLE, WHITE),
    'D_':panelCellFont.render('D', True, PURPLE, WHITE),
    'E_':panelCellFont.render('E', True, PURPLE, WHITE),
    'F_':panelCellFont.render('F', True, PURPLE, WHITE),
    'H_':panelCellFont.render('H', True, PURPLE, WHITE),
    ' ':panelCellFont.render('   ', True, BLACK, WHITE),
    ' _':panelCellFont.render('   ', True, BLACK, WHITE)
    }

# Cache the panel label symbols and positions needed.
panelLabelFont = pygame.font.SysFont('arialbold', PANEL_LABEL_FONT_SIZE)
panelLabelSymbols = {
    'READ':panelLabelFont.render('READ', True, BLACK, WHITE),
    'WRITE':panelLabelFont.render('WRITE', True, BLACK, WHITE),
    'MOVE':panelLabelFont.render('MOVE', True, BLACK, WHITE),
    'GOTO':panelLabelFont.render('GOTO', True, BLACK, WHITE),
    'STEP':panelLabelFont.render('STEP', True, BLACK, WHITE),
    'RUN':panelLabelFont.render('RUN', True, BLACK, WHITE),
    'DEMO':panelLabelFont.render('DEMO', True, BLACK, WHITE),
    'LOAD':panelLabelFont.render('LOAD', True, DARK_PURPLE, WHITE),
    'SAVE':panelLabelFont.render('SAVE', True, DARK_PURPLE, WHITE),
    'READ_':panelLabelFont.render('READ', True, PURPLE, WHITE),
    'WRITE_':panelLabelFont.render('WRITE', True, PURPLE, WHITE),
    'MOVE_':panelLabelFont.render('MOVE', True, PURPLE, WHITE),
    'GOTO_':panelLabelFont.render('GOTO', True, PURPLE, WHITE),
    'STEP_':panelLabelFont.render('STEP', True, PURPLE, WHITE),
    'RUN_':panelLabelFont.render('RUN', True, PURPLE, WHITE),
    'DEMO_':panelLabelFont.render('DEMO', True, PURPLE, WHITE),
    'LOAD_':panelLabelFont.render('LOAD', True, PURPLE, WHITE),
    'SAVE_':panelLabelFont.render('SAVE', True, PURPLE, WHITE)
    }
##### Function and classes.
# Implement a generic dialog box.
class Dialog(pygame.sprite.Sprite):
    
    def __init__(self, screen, title, message, buttonLabels, font, textBox):
        super(Dialog, self).__init__()
        self.screen = screen
        self.title = title
        self.message = message
        self.buttonLabels = buttonLabels
        self.font = font
        self.textBox = textBox
        self.cursor = self.font.render('_    ', True, DARK_PURPLE, WHITE)
        
    def update(self):
        if self.textBox:
            showText = self.font.render(self.text, True, BLACK, WHITE)
            self.screen.blit(showText, (self.panelX+self.textX, self.panelY + self.textY))
            self.screen.blit(self.cursor, (self.panelX+self.textX+showText.get_width(), self.panelY + self.textY))
            pygame.display.flip()
        
    def run(self):
        global lastFilename
        saveScreen = self.screen.copy()
        
        # Grey out the screen
        dark = pygame.Surface(self.screen.get_size(), 32)
        dark.set_alpha(128, pygame.RLEACCEL)
        self.screen.blit(dark, (0, 0))
        
        # Create the dialog box.
        self.title = self.font.render(self.title, True, PURPLE, WHITE)
        self.message = self.font.render(self.message, True, BLACK, WHITE)
        msgWidth, msgHeight = self.message.get_rect().size
        panelWidth = msgWidth + 60
        panelHeight = msgHeight + 50
        if self.buttonLabels != None:
            panelHeight += 40
        if self.textBox:
            panelHeight += 20
        
        self.panel = pygame.Surface((panelWidth, panelHeight))
        self.panel.fill((WHITE))
        pygame.draw.rect(self.panel, PURPLE, (1,1,panelWidth-3,panelHeight-3), 4)
        
        # Calculate where it will appear on the screen.
        self.panelX = int(self.screen.get_width()/2-panelWidth/2)
        self.panelY = int(self.screen.get_height()/2-panelHeight/2)
        
        # Add the title and message.
        self.panel.blit(self.title, (10, 10))
        if self.textBox:
            msgY = int(panelHeight/2-msgHeight*1.5)
        else:
            msgY = int(panelHeight/2-msgHeight/2)
        self.panel.blit(self.message, (int((panelWidth-msgWidth)/2), msgY))
        
        # Add a message box.
        if self.textBox:
            textWidth = int(panelWidth*.8)
            textHeight = int(msgHeight*1.5)
            textX = int(panelWidth*.2/2)
            textY = int(panelHeight/2)
            pygame.draw.rect(self.panel, PURPLE, (textX, textY, textWidth, textHeight), 2)
            self.text=lastFilename
            self.textX = textX + 10
            self.textY = textY + 5 
            self.update()          
        
        # Add buttons if there are any.
        dialogButtons = []
        for buttonLabel in self.buttonLabels:
            image = self.font.render(buttonLabel, True, DARK_PURPLE, WHITE)
            imageHighlight = self.font.render(buttonLabel, True, PURPLE, WHITE)
            button = {}
            createButton(buttonLabel, button, image, imageHighlight, (0,0), None)
            dialogButtons.append(button)
        
        startX = panelWidth
        startY = panelHeight - 25
        for button in reversed(dialogButtons):
            image =  button['image']
            startX = startX - image.get_width() - 10
            self.panel.blit(image, (startX, startY))
            button['rect'] = pygame.Rect(self.panelX + startX, self.panelY + startY, 
                                  image.get_width(), image.get_height())
        
        # Show the dialog box on the main screen
        self.screen.blit(self.panel, (self.panelX, self.panelY))
        
        # Show the text cursor if necessary.
        if self.textBox:
            self.update()
        
        # Update the sprite variables.
        self.surf = self.panel
        self.rect = self.surf.get_rect()
        pygame.display.flip()
        
        # Handle events till mouse is clicked pressed.
        done = False
        buttonClicked = None
        while not done:
            # Check the event queue. 
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in dialogButtons:
                        if buttonOnClick(button, event):
                            buttonClicked = button['name']
                            if self.textBox:
                                lastFilename = self.text
                            done = True
                            break # Break out of for loop.
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        buttonClicked = dialogButtons[0]['name']
                        if self.textBox:
                            lastFilename = self.text
                        done = True
                        break
                    if event.key == pygame.K_ESCAPE:
                        buttonClicked = dialogButtons[1]['name']
                        done = True
                        break
                    if event.key == pygame.K_BACKSPACE:
                        if self.textBox:
                            self.text = self.text[:-1]
                    else:
                        if self.textBox:
                            if len(self.text) < 35:
                                self.text += event.unicode
                    self.update()
            if checkForMouseovers(dialogButtons):
                pygame.display.flip()
            
        self.kill()
        self.screen.blit(saveScreen, (0,0))
        
        if self.textBox:
            return buttonClicked,self.text.strip()
        else:
            return buttonClicked
        
# Used to setup the tape screen controls.
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
            # Make sure we are actually on the button.
            pixel = screen.get_at(event.pos)
            if pixel == (255,255,255,255)  and (button['name'] == 'left' or button['name'] == 'right' or button['name'] == 'down'):
                return False
            if button["callback"] != None:
                button["callback"](button)
            else:
                return True
    return False
    
# Highlight buttons when the mouse is over them.   
def checkForMouseovers(buttons):
    global lastMousePosition
    changed = False
    # Check for mouse over button.
    pointer = pygame.mouse.get_pos() # (x, y) location of pointer in every frame.
    if pointer != lastMousePosition:
        lastMousePosition = pointer
        for button in buttons:
            pixel = screen.get_at(pointer)
            
            # Lock out the tape buttons when running a program.
            if stateMachineRunning and (button['name'] == 'left' or button['name'] == 'right' or button['name'] == 'down'):
                continue
            
            # If pointer is inside the button rectangle and is not white or black...
            if button['rect'].collidepoint(pointer):
                # Check the arrow keys for white space.
                if pixel == (255,255,255,255)  and (button['name'] == 'left' or button['name'] == 'right' or button['name'] == 'down'):
                    if button['highlighted'] == True:
                        showButton(button)
                        changed = True
                else:
                    if button['highlighted'] == False:
                        showButton(button, True)
                        changed = True
            else:
                if button['highlighted'] == True:
                    showButton(button)
                    changed = True
    return changed

# Handle the left button mouse press.
def pushButtonLeft(_):
    global tapeHead
    if tapeHead < TAPE_NUMBER_CELLS - int(TAPE_CELLS/2) - 1:
        tapeHead += 1
        drawTape()

# Handle the right button mouse press. 
def pushButtonRight(_):
    global tapeHead
    if tapeHead > int(TAPE_CELLS/2) + 1:
        tapeHead -= 1
        drawTape()

# Handle the down button mouse press.
def pushButtonDown(_):
    tape[tapeHead] = (tape[tapeHead] + 1) % 7;
    drawTapeCell(tapeHead, int(TAPE_CELLS/2))

# Handle the reset button mouse press.    
def pushButtonReset(_):
    # Clear the tape.
    resetRuntime(True)
    setStartingMode()
    pygame.display.flip()
    
    # Check before clearing the state transition table.
    dialog = Dialog(screen, 'Warning', 'Are you sure that you want to clear the State Transition Table?', ['YES','NO'], panelLabelFont, False)
    answer = dialog.run()

    # Clear the events queue.
    if answer == 'YES':
        clearStateTable()
    redrawStateTable() 

# Set the state machine to it's initial position (A-READ) but not running. 
# Optionally clear the tape to blanks (0) and center the tape head.   
def resetRuntime(resetTape = False):
    if resetTape:
        clearTape()
        drawTape()
    resetPanelLabels()
    resetState('A', 'READ')

# Set the running state.
def resetState(state, step):
    global currentState 
    global currentStep
    global stepReady
    global playPressed
    global stateMachineRunning
    currentState = state
    currentStep = step
    stepReady = False
    playPressed = False
    stateMachineRunning = False

# Make sure that all of the panel labels for the state passed are not highlighted.
def resetPanelLabels():
    global currentState 
    drawPanelState(currentState)
    drawPanelLabel(currentState, 'READ')
    drawPanelLabel(currentState, 'WRITE')
    drawPanelLabel(currentState, 'MOVE')
    drawPanelLabel(currentState, 'GOTO')

# Handle the halt button mouse press.
def pushButtonHalt(_):
    haltStateMachine()

# Switch the play button to green (running) and the halt button to normal.
def setRunningMode():
    # Show the play button in running mode.
    if runState == 'STEP':
        playButton['image'] = runningImage
    else:   
        playButton['image'] = highlightRunningImage
    playButton['imageLight'] = highlightRunningImage
    showButton(playButton, True)
    
    # Make sure that the halt button is set to normal mode.
    haltButton['image'] = haltImage
    haltButton['imageLight'] = haltHighlightImage
    showButton(haltButton)

# Set the play, halt, and reset buttons to normal.
def setStartingMode():
    # Show the play button in running mode.
    playButton['image'] = playImage
    playButton['imageLight'] = playHighlightImage
    showButton(playButton)
    
    # Make sure that the halt button is set to normal mode.
    haltButton['image'] = haltImage
    haltButton['imageLight'] = haltHighlightImage
    showButton(haltButton)
    
    # Make sure the reset button is set to normal.
    showButton(resetButton)

# Handle the play button mouse press.
def pushButtonPlay(_):
    global startTime
    global playPressed
    global stateMachineRunning
    
    if stateMachineRunning == False:
        # Play highlighted, halt normal. 
        setRunningMode()
        # Start the state machine running.
        stateMachineRunning = True
    else:
        playPressed = True

# Pop up a dialog with the error message from the exception passed.    
def showErrorMessage(ex):
    msg = str(ex)
    index = msg.index(']')+1
    msg = msg[index:len(msg)]
    dialog = Dialog(screen, 'Error', msg, ['OK'], panelLabelFont, False)
    dialog.run()  

# Handle the load label button mouse press.
def pushButtonLoad(_):
    global stateTable
    global tape
    global tapeHead
    global currentState
    global currentStep
    global currentTransition
    
    dialog = Dialog(screen, 'Load', 'Enter the name of the file to load from then press OK.', ['OK', 'CANCEL'], panelLabelFont, True)
    buttonPressed,filename = dialog.run()
    
    if buttonPressed == 'OK' and filename != None:
        try:
            f = open(filename+'.tmd2',"r")
            saveText = f.read()
            f.close()
            save = eval(saveText)
            compressed = save['tape']
            decodeTape(compressed)
            stateTable = save['table']
            tapeHead = save['tapehead']
            state = save['state']
            step = save['step']
            currentTransition = save['transition']
            
            drawTape()
            redrawStateTable()
            showButton(loadButton)
            
            resetPanelLabels()
            resetState(state, step)
            if currentTransition !=  None:
                drawPanelState(state, True)
                drawPanelLabel(state, step, True)
            
        except Exception as ex:
            showErrorMessage(ex)
            
            
            # Clear the events queue.
            pygame.event.clear()

# Create a text file with the current tape and state machine information.          
def dumpWorkspace():
    global tape
    global stateTable
    
    # Build the output string here.
    workspace = ""
    
    # Find the position of the first non zero symbol on the tape.
    for start in range(0, TAPE_NUMBER_CELLS-1):
        if tape[start] != 0:
            break
    # Find the position of the last non zero symbol on the tape.
    for end in range(TAPE_NUMBER_CELLS-1, 0, -1):
        if tape[end] != 0:
            break
        
    # Show the range of non blank (zero) cells.   
    workspace += "Showing tape from cell {0} to cell {1}.\n".format(start-int(TAPE_NUMBER_CELLS/2), end-int(TAPE_NUMBER_CELLS/2))
    for pos in range(0, len(workspace)-1):
        workspace += '~'
    workspace += '\n'
    # Show the tape and count the number of each symbol.
    counts = {}
    counts['0'] = 0
    counts['1'] = 0
    counts['2'] = 0
    counts['3'] = 0
    counts['4'] = 0
    counts['5'] = 0
    counts['6'] = 0
    
    for pos in range(start, end+1):
        counts[str(tape[pos])] += 1
        if tape[pos] == 6:
            workspace += "| b "
        else:
            workspace += "| {0} ".format(str(tape[pos]))
    workspace += "|\n\nCounts\n~~~~~~\n"
    
    for key, value in counts.items():
        if key == '6':
            key = 'b'
        workspace += key + ': ' + str(value) + '\n'
    
    workspace += '\nState Transition Table\n~~~~~~~~~~~~~~~~~~~~~~\n'
    for state in ('A', 'B', 'C', 'D','E','F'):
        workspace += '            '+state+'\n'
        for row in range(0, 4):
            for col in range(0,6):
                value = stateTable[state+str(col)][row]
                if value == ' ':
                    value = '-'
                workspace += '| ' + value + ' '   
            workspace += '|\n'
        workspace += '\n'
    return workspace

# Handle the save label button mouse press.
def pushButtonSave(_):
    global stateTable
    dialog = Dialog(screen, 'Save', 'Enter the name of the file to save to then press OK.', ['OK', 'CANCEL'], panelLabelFont, True)
    buttonPressed, filename = dialog.run()
    # Clear the events queue.
    pygame.event.clear()
    if buttonPressed == 'OK' and filename != None:
        compressed = encodeTape()
        try:
            # Save the raw tape and state transition table.
            save = {}
            save['tape'] = compressed
            save['table'] = stateTable
            save['tapehead'] = tapeHead
            save['state'] = currentState
            save['step'] = currentStep
            save['transition'] = currentTransition
            f = open(filename+'.tmd2',"w")
            f.write( str(save) )
            f.close()
            
            # Save a readable version of the tape and state transition table.
            f = open(filename+'.txt',"w")
            f.write( dumpWorkspace() )
            f.close()
            
            showButton(saveButton)
            
        except Exception as ex:
            showErrorMessage(ex)
            

# Handle the step radio button mouse press.            
def pushButtonStep(button):
    global runState
    if runState != 'STEP':
        # Switch to step state. Update the run and step buttons.
        for button in buttons:
            if button["name"] == "run":
                button["image"] = radioImage
                button["imageLight"] = radioHighlightImage
                showButton(button)
            if button["name"] == "step":
                button["image"] = selectedRadioImage
                button["imageLight"] = selectedRadioImage
                showButton(button)
            if button["name"] == "demo":
                button["image"] = radioImage
                button["imageLight"] = radioHighlightImage
                showButton(button)
        runState = 'STEP'

# Handle the run radio button mouse press.
def pushButtonRun(button):
    global runState
    if runState != 'RUN':
        # Switch to run state. Update the run and step buttons.
        for button in buttons:
            if button["name"] == "run":
                button["image"] = selectedRadioImage
                button["imageLight"] = selectedRadioImage
                showButton(button)
            if button["name"] == "step":
                button["image"] = radioImage
                button["imageLight"] = radioHighlightImage
                showButton(button)
            if button["name"] == "demo":
                button["image"] = radioImage
                button["imageLight"] = radioHighlightImage
                showButton(button)
        runState = 'RUN'

# Handle the demo radio button mouse press.     
def pushButtonDemo(button):
    global runState
    if runState != 'DEMO':
        # Switch to run state. Update the run and step buttons.
        for button in buttons:
            if button["name"] == "run":
                button["image"] = radioImage
                button["imageLight"] = radioHighlightImage
                showButton(button)
            if button["name"] == "step":
                button["image"] = radioImage
                button["imageLight"] = radioHighlightImage
                showButton(button)
            if button["name"] == "demo":
                button["image"] = selectedRadioImage
                button["imageLight"] = selectedRadioImage
                showButton(button)
        runState = 'DEMO'

# Draw the symbol from the tape at tapePosition to the screen at cellPosition.
def drawTapeCell(tapePosition, cellPosition):
    # Draw the symbol at the tape position passed.
    symbol = tape[tapePosition]
    symbolImage = cellSymbols[symbol]
    screen.blit(symbolImage, 
                (int((TAPE_START_X + cellPosition * TAPE_CELL_WIDTH) + (TAPE_CELL_WIDTH - symbolImage.get_width())/2), 
                 int(TAPE_START_Y + (TAPE_CELL_HEIGHT - symbolImage.get_height())/5*4)))
    # Create a cell number.
    numberPanel = pygame.Surface((40,12))
    numberPanel.fill(WHITE)
    numberText = cellNumberFont.render(str(tapePosition-int(TAPE_NUMBER_CELLS/2)), True, BLACK, WHITE)
    numberPanel.blit(numberText, (0,0))
    screen.blit(numberPanel, (TAPE_START_X + cellPosition * TAPE_CELL_WIDTH + 5, TAPE_START_Y + 5))

# Draw the button passed onto the screen with optional highlighting.
def showButton(button, highlight=False):
    if highlight:
        screen.blit(button["imageLight"], button["rect"])
        button["highlighted"] = True
    else:
        screen.blit(button["image"], button["rect"])
        button["highlighted"] = False

# Draw the whole tape onto the screen
def drawTape():
    # Show the tape characters.
    cellPosition = 0;
    for i in range(tapeHead-int(TAPE_CELLS/2),tapeHead+int(TAPE_CELLS/2)+1):
        drawTapeCell(i, cellPosition)
        cellPosition+=1

# Run length encode the tape for saving.
def encodeTape():
    compressed = ''
    start = 0
    cell = tape[0]
    for pos in range(1, TAPE_NUMBER_CELLS):
        if tape[pos] != cell or pos == TAPE_NUMBER_CELLS-1:
            count = pos - start
            if count > 5:
                compressed += '[' + str(count) + ']' + str(cell)
            else:
                for i in range(start, pos):
                    compressed += str(tape[i])
            start = pos
            cell = tape[pos]
    return compressed      

# Decode the run length encoding passed into the tape.
def decodeTape(compressed):
    tapePos = 0
    pos =  0 
    while pos < len(compressed):
        if compressed[pos] == '[':
            pos += 1
            countStr = ''
            while compressed[pos] != ']': 
                countStr += compressed[pos]
                pos += 1
            pos += 1
            count = int(countStr)
            while count > 0:
                tape[tapePos] = int(compressed[pos])
                tapePos += 1
                count -= 1
            pos += 1
        else:
            tape[tapePos] = int(compressed[pos])
            tapePos += 1
            pos += 1
        
# Set the tape to all blanks (0).
def clearTape():
    # 0 will be the blank character.
    global tape
    global tapeHead
    for i in range(0, TAPE_NUMBER_CELLS):
        tape[i] = 0
    tapeHead = int(TAPE_NUMBER_CELLS / 2) 

# Set the play button to normal and the halt button to halted (red).
def setHaltedMode():
    # Show the play button in normal mode.
    playButton['image'] = playImage
    playButton['imageLight'] = playHighlightImage
    showButton(playButton)
    
    # Show the halt button in halted mode.
    haltButton['image'] = haltedImage
    haltButton['imageLight'] = haltedImage
    showButton(haltButton)

# Stop the state machine at the current step. Note that the program can be 
# resumed from this point by pressing play. 
def haltStateMachine():
    global stateMachineRunning
    
    # Play normal, halt highlighted. 
    setHaltedMode()
    
    # Redraw the tape if necessary.
    if runState == 'RUN':
        drawTape()
        
    # Clear the current transition.
    currentTransition = None
    
    # Prevent the state machine from running.
    stateMachineRunning = False

# Draw a single state panel.    
def drawStatePanel(startX, startY, stateName):
    panelBorder = pygame.Rect(startX, startY, PANEL_WIDTH, PANEL_HEIGHT)
    statePanelOffsets[stateName] = (panelBorder)
    pygame.draw.rect(screen, BLACK, panelBorder, PANEL_BORDER_WIDTH)
    
    for y in range(1,PANEL_ROWS):
        pygame.draw.line(screen, BLACK, 
                         (startX, startY + y*(PANEL_CELL_HEIGHT+PANEL_BORDER_WIDTH)), 
                         (startX + PANEL_WIDTH, startY + y*(PANEL_CELL_HEIGHT+PANEL_BORDER_WIDTH)), 
                         PANEL_BORDER_WIDTH)
    for x in range(1,PANEL_COLUMNS):
        pygame.draw.line(screen, BLACK, 
                         (startX+x*(PANEL_CELL_WIDTH+PANEL_BORDER_WIDTH)-1, startY + (PANEL_CELL_HEIGHT+PANEL_BORDER_WIDTH)), 
                         (startX+x*(PANEL_CELL_WIDTH+PANEL_BORDER_WIDTH)-1, startY + PANEL_ROWS*(PANEL_CELL_HEIGHT+PANEL_BORDER_WIDTH)), 
                         PANEL_BORDER_WIDTH)
    
    symbolImage = panelCellSymbols[stateName]
    offsetX = int(startX + PANEL_WIDTH/2 - symbolImage.get_width()/3)
    offsetY = int(startY + PANEL_CELL_HEIGHT/2 - symbolImage.get_height()/3.5)
    panelLabelPositions[stateName] = (offsetX, offsetY)
    screen.blit(symbolImage, (offsetX, offsetY))
    
    # Draw the row labels if this is state A or D
    if stateName == 'A' or stateName == 'D':
        startText = startX - panelLabelSymbols['WRITE'].get_width() - int(PANEL_CELL_WIDTH/3)
        text_offset = symbolImage.get_height()/3.5
        
        symbolImage = panelLabelSymbols['READ']
        offsetY = int(startY + (PANEL_CELL_HEIGHT+PANEL_BORDER_WIDTH) + PANEL_CELL_HEIGHT/2 - text_offset)
        panelLabelPositions['READ'+stateName] = (startText, offsetY);
        screen.blit(symbolImage, (startText, offsetY))
        
        symbolImage = panelLabelSymbols['WRITE']
        offsetY = int(startY + (PANEL_CELL_HEIGHT+PANEL_BORDER_WIDTH) * 2 + PANEL_CELL_HEIGHT/2 - text_offset)
        panelLabelPositions['WRITE'+stateName] = (startText, offsetY);
        screen.blit(symbolImage, (startText, offsetY))
        
        symbolImage = panelLabelSymbols['MOVE']
        offsetY = int(startY + (PANEL_CELL_HEIGHT+PANEL_BORDER_WIDTH) * 3 + PANEL_CELL_HEIGHT/2 - text_offset)
        panelLabelPositions['MOVE'+stateName] = (startText, offsetY);
        screen.blit(symbolImage, (startText, offsetY))
        
        symbolImage = panelLabelSymbols['GOTO']
        offsetY = int(startY + (PANEL_CELL_HEIGHT+PANEL_BORDER_WIDTH) * 4 + PANEL_CELL_HEIGHT/2 - text_offset)
        panelLabelPositions['GOTO'+stateName] = (startText, offsetY);
        screen.blit(symbolImage, (startText, offsetY))

# Draw the state label passed to the left of the appropriate panels with optional highlighting.
def drawPanelLabel(state, label, highlight=False):
    if state == 'A' or state == 'B' or state == 'C':
        state = 'A'
    else:
        state = 'D'
    if highlight:
        symbolImage = panelLabelSymbols[label+'_']
    else:
        symbolImage = panelLabelSymbols[label]
    position = panelLabelPositions[label+state]
    screen.blit(symbolImage, position)

# Draw the state name passed at the top of the appropriate panel with optional highlighting.
def drawPanelState(state, highlight=False):
    if highlight:
        symbolImage = panelCellSymbols[state+'_']
    else:
        symbolImage = panelCellSymbols[state]
    position = panelLabelPositions[state] 
    screen.blit(symbolImage, position)

# Draw the symbol passed into the appropriate state transition table cell with optional highlighting.
def drawStateSymbol(state, row, column, symbol, highlight=False):
    startX,startY,_,_ = statePanelOffsets[state]
    if highlight:
        symbolImage =  panelCellSymbols[symbol+'_']
    else:
        symbolImage =  panelCellSymbols[symbol]
    screen.blit(panelCellSymbols[' '], # Clear the cell
                (int(startX + (PANEL_CELL_WIDTH + PANEL_BORDER_WIDTH)*column + PANEL_CELL_WIDTH/2 - symbolImage.get_width()/3.5 - 1), 
                 int(startY + (PANEL_CELL_HEIGHT + PANEL_BORDER_WIDTH)*row + PANEL_CELL_HEIGHT/2 - 2 - symbolImage.get_height()/3.5)))
    screen.blit(symbolImage, 
                (int(startX + (PANEL_CELL_WIDTH + PANEL_BORDER_WIDTH)*column + PANEL_CELL_WIDTH/2 - symbolImage.get_width()/3.5), 
                 int(startY + (PANEL_CELL_HEIGHT + PANEL_BORDER_WIDTH)*row + PANEL_CELL_HEIGHT/2 - 2 - symbolImage.get_height()/3.5)))

# Set the state transition table data structure to default values.
def clearStateTable():
    for state in ('A', 'B', 'C', 'D', 'E', 'F'):
        for value in ('0', '1', '2', '3', '4', '5'):
            stateTable[state+value] = [value, ' ', ' ', ' ']
    currentTransition = None

# Draw the symbols from the state transition table structure to the screen.  
def redrawStateTable():
    for state in ('A', 'B', 'C', 'D', 'E', 'F'):
        for value in ('0', '1', '2', '3', '4', '5'):
            drawStateSymbol(state, 1, int(value), stateTable[state+value][0])
            drawStateSymbol(state, 2, int(value), stateTable[state+value][1])
            drawStateSymbol(state, 3, int(value), stateTable[state+value][2])
            drawStateSymbol(state, 4, int(value), stateTable[state+value][3])

# Show the active transition column of the state table.
def highlightTransition(state, transition):
    if transition[0] == 'b':
        col = 5
    else:
        col = int(currentTransition[0])
    drawStateSymbol(state, 1, col, transition[0], True)
    drawStateSymbol(state, 2, col, transition[1], True)
    drawStateSymbol(state, 3, col, transition[2], True)
    drawStateSymbol(state, 4, col, transition[3], True)
    
# Show the transition not defined error.
def showStateTableError():
    msg = 'Transition ' + currentState + currentTransition[0] + ' is not defined. Resetting to start state.'
    dialog = Dialog(screen, 'Warning', msg, ['OK'], panelLabelFont, False)
    dialog.run()
    
def runFast():
    global tape
    global tapeHead
    global stateTable
    global currentTransition
    global currentState
    global currentStep
    global lastMoveDirection
    
    # Clear the state table of highlights.
    resetPanelLabels()
    redrawStateTable()
    pygame.display.flip()
    
    # Check halt button for mouse over.
    buttons = []
    buttons.append(haltButton)
           
    # Pre-compute boundary conditions.
    LEFT_STOP = int(TAPE_CELLS/2) + 1
    RIGHT_STOP = TAPE_NUMBER_CELLS - int(TAPE_CELLS/2) - 1

    loops = 0
    while True:   
        # Read
        value = tape[tapeHead]
        if value == 6:
            currentTransition = stateTable[currentState+'5']
        else:
            currentTransition = stateTable[currentState+str(value)]
        
        # Check for invalid state transition table.  
        if currentTransition[1] == ' ' or currentTransition[2] == ' ' or currentTransition[3] == ' ':
            currentStep = 'READ'
            return 'E'
        
        # Write. Do not write over a 'b'.
        if currentTransition[1] != 'b':
            tape[tapeHead] = int(currentTransition[1])
            
        # Move. Check for boundary conditions.
        if currentTransition[0] == 'b' and currentTransition[2] == lastMoveDirection:
            # Cannot go past a boundary.
            currentStep = 'MOVE'
            return 'H'
        
        if currentTransition[2] != 'R':
            if tapeHead < RIGHT_STOP:
                tapeHead += 1
            else:
                # Out of bounds.
                currentStep = 'MOVE'
                return 'H'
        else:
            if tapeHead > LEFT_STOP:
                tapeHead -= 1
            else:
                # Out of bounds.
                currentStep = 'MOVE'
                return 'H'
        
        # Record the last move direction.
        lastMoveDirection = currentTransition[2]
                        
        # Goto. Set the new state.
        if currentTransition[3] == 'H':
            currentStep = 'GOTO'
            return 'H'
        else:
            currentState = currentTransition[3]
        
        # Periodically check for mouse events.
        loops += 1;
        if loops % 100000 == 0:
            # See if the halt button needs to be highlighted.
            if checkForMouseovers(buttons):
                pygame.display.flip()
            
            # Watch for the halt button pressed.
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and haltButton["rect"].collidepoint(event.pos):
                    currentTransition = None
                    currentStep = 'READ'
                    return 'H'

##### Screen setup.          
# Draw the tape frame.
tapeBorder = pygame.Rect(TAPE_START_X, TAPE_START_Y, TAPE_WIDTH, TAPE_HEIGHT)
pygame.draw.rect(screen, BLACK, tapeBorder, TAPE_BORDER_WIDTH)
for x in range(TAPE_CELLS-1):
    pygame.draw.line(screen, BLACK, 
                     ((x+1)*TAPE_CELL_WIDTH+TAPE_START_X, TAPE_START_Y), 
                     ((x+1)*TAPE_CELL_WIDTH+TAPE_START_X, TAPE_CELL_HEIGHT+TAPE_START_Y), 
                     TAPE_BORDER_WIDTH)
# Show the tape characters
clearTape()
drawTape()
    
# Create and draw the tape controls. Left arrow.
buttons = []
image = pygame.image.load('left_arrow.png')
highlightImage = pygame.image.load('left_arrow_light.png')
buttonWidth, buttonHeight = image.get_rect().size
leftArrowButton = {}
createButton("left", leftArrowButton, image, highlightImage,
              (int(TAPE_START_X-buttonWidth-buttonWidth/3),
               int(TAPE_START_Y+(TAPE_CELL_HEIGHT-buttonHeight)/2)), pushButtonLeft)
showButton(leftArrowButton)
buttons.append(leftArrowButton)

# Right arrow.
image = pygame.image.load('right_arrow.png')
highlightImage = pygame.image.load('right_arrow_light.png')
buttonWidth, buttonHeight = image.get_rect().size
rightArrowButton = {}
createButton("right", rightArrowButton, image, highlightImage,
              (int(TAPE_START_X+TAPE_WIDTH+buttonWidth/3),
               int(TAPE_START_Y+(TAPE_CELL_HEIGHT-buttonHeight)/2)), pushButtonRight)
showButton(rightArrowButton)
buttons.append(rightArrowButton)

# Down arrow.
image = pygame.image.load('down_arrow.png')
highlightImage = pygame.image.load('down_arrow_light.png')
buttonWidth, buttonHeight = image.get_rect().size
downArrowButton = {}
createButton("down", downArrowButton, image, highlightImage, 
              (int(TAPE_WIDTH/2+buttonWidth/2),
               int(TAPE_START_Y-buttonHeight-buttonHeight/4)), pushButtonDown)
showButton(downArrowButton)
buttons.append(downArrowButton)

# Calculate the center point for the console control buttons.
buttonCenterX = SCREEN_WIDTH - int((SCREEN_WIDTH - (TAPE_START_X + PANEL_WIDTH*3))/2.2)
buttonCenterY = SCREEN_HEIGHT - int((SCREEN_HEIGHT - PANEL_START_Y)/1.9)

# Reset.
image = pygame.image.load('reset.png')
highlightImage = pygame.image.load('reset_light.png')
buttonWidth, buttonHeight = image.get_rect().size
resetButton = {}
createButton("reset", resetButton, image, highlightImage, 
              (int(buttonCenterX - buttonWidth - buttonWidth/8),
               int(buttonCenterY - buttonHeight - buttonHeight/8)), pushButtonReset)
showButton(resetButton)
buttons.append(resetButton)

# Halt.
haltImage = pygame.image.load('halt.png')
haltHighlightImage = pygame.image.load('halt_light.png')
haltedImage = pygame.image.load('halted.png')
buttonWidth, buttonHeight = haltImage.get_rect().size
haltButton = {}
createButton("halt", haltButton, haltImage, haltHighlightImage, 
              (int(buttonCenterX + buttonWidth/8),
               int(buttonCenterY - buttonHeight - buttonHeight/8)), pushButtonHalt)
showButton(haltButton)
buttons.append(haltButton)

# Play.
playImage = pygame.image.load('play.png')
playHighlightImage = pygame.image.load('play_light.png')
runningImage = pygame.image.load('running.png')
highlightRunningImage = pygame.image.load('running_light.png')
playbuttonWidth, playbuttonHeight = playImage.get_rect().size
playButton = {}
createButton("play", playButton, playImage, playHighlightImage, 
              (int(buttonCenterX + playbuttonWidth/8),
               int(buttonCenterY + playbuttonHeight/8)), pushButtonPlay)
showButton(playButton)
buttons.append(playButton)

# Load.
loadImage = panelLabelSymbols['LOAD']
loadHighlightImage = panelLabelSymbols['LOAD_']
loadbuttonWidth, buttonHeight = loadImage.get_rect().size
loadButton = {}
createButton("load", loadButton, loadImage, loadHighlightImage, 
              (20, 20), pushButtonLoad)
showButton(loadButton)
buttons.append(loadButton)

# Save.
saveImage = panelLabelSymbols['SAVE']
saveHighlightImage = panelLabelSymbols['SAVE_']
buttonWidth, buttonHeight = saveImage.get_rect().size
saveButton = {}
createButton("save", saveButton, saveImage, saveHighlightImage, 
              (loadbuttonWidth + 40, 20), pushButtonSave)
showButton(saveButton)
buttons.append(saveButton)


# Find the center of the step/run/demo "button" area. 
imageButtonWidth = playbuttonWidth   # NOTE: using play button dimensions.
imageButtonHeight = playbuttonHeight

stepRunCenterX = int(buttonCenterX - imageButtonWidth/1.5)
stepRunCenterY = int(buttonCenterY + imageButtonHeight/2)

# Run. Remember the images used for the run button.
radioImage = pygame.image.load('radio.png')
radioHighlightImage = pygame.image.load('radio_light.png')
buttonWidth, buttonHeight = radioImage.get_rect().size
runButton = {}
createButton("run", runButton, radioImage, radioHighlightImage,
              (int(stepRunCenterX - imageButtonWidth/6 - buttonWidth),
               int(stepRunCenterY - buttonHeight - buttonHeight/3)), pushButtonRun)
showButton(runButton)
buttons.append(runButton)
symbolImage = panelLabelSymbols['RUN']
screen.blit(symbolImage, 
                (int(stepRunCenterX - imageButtonWidth/6 + buttonWidth/4), 
                 int(stepRunCenterY - buttonHeight - buttonHeight/6)))

# Step. Remember the images used for the step button.
selectedRadioImage = pygame.image.load('radio_selected.png')
selectedHighlightRadioImage = pygame.image.load('radio_selected.png')
buttonWidth, buttonHeight = selectedRadioImage.get_rect().size
stepButton = {}
createButton("step", stepButton, selectedRadioImage, selectedHighlightRadioImage,
              (int(stepRunCenterX - imageButtonWidth/6 - buttonWidth),
               int(stepRunCenterY)), pushButtonStep)
showButton(stepButton)
buttons.append(stepButton)
symbolImage = panelLabelSymbols['STEP']
screen.blit(symbolImage, 
                (int(stepRunCenterX - imageButtonWidth/6 + buttonWidth/4), 
                 int(stepRunCenterY + buttonHeight/6)))

# Demo. 
image = pygame.image.load('radio.png')
highlightImage = pygame.image.load('radio_light.png')
buttonWidth, buttonHeight = image.get_rect().size
demoButton = {}
createButton("demo", demoButton, image, highlightImage, 
              (int(stepRunCenterX - imageButtonWidth/6 - buttonWidth),
               int(stepRunCenterY + buttonHeight + buttonHeight/3)), pushButtonDemo)
showButton(demoButton)
buttons.append(demoButton)
symbolImage = panelLabelSymbols['DEMO']
screen.blit(symbolImage, 
                (int(stepRunCenterX - imageButtonWidth/6 + buttonWidth/4), 
                 int(stepRunCenterY + buttonHeight + buttonHeight/2)))

# Draw the state transition table.
drawStatePanel(PANEL_START_X, PANEL_START_Y, 'A')
drawStatePanel(PANEL_START_X + PANEL_WIDTH, PANEL_START_Y, 'B')
drawStatePanel(PANEL_START_X + PANEL_WIDTH * 2, PANEL_START_Y, 'C')
drawStatePanel(PANEL_START_X, PANEL_START_Y + PANEL_HEIGHT, 'D')
drawStatePanel(PANEL_START_X + PANEL_WIDTH, PANEL_START_Y + PANEL_HEIGHT, 'E')
drawStatePanel(PANEL_START_X + PANEL_WIDTH * 2, PANEL_START_Y + PANEL_HEIGHT, 'F')

# Show the default panel symbols.
clearStateTable()
redrawStateTable()

##### Main loop.
# Process the PyGame events.
done = False
while not done:
    # Check the event queue. 
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                done = True
            elif event.key == pygame.K_LEFT:
                pushButtonLeft(None)
            elif event.key == pygame.K_RIGHT:
                pushButtonRight(None)
        elif event.type == pygame.QUIT:
            pygame.quit()
            done = True
        elif event.type == TIMEREVENT:
            if runState == 'DEMO':
                playPressed = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            
            # First check all the buttons.
            buttonOnClick(leftArrowButton, event)
            buttonOnClick(rightArrowButton, event)
            buttonOnClick(downArrowButton, event)
            buttonOnClick(resetButton, event)
            buttonOnClick(haltButton, event)
            buttonOnClick(playButton, event)
            buttonOnClick(runButton, event)
            buttonOnClick(stepButton, event)
            buttonOnClick(demoButton, event)
            buttonOnClick(loadButton, event)
            buttonOnClick(saveButton, event)
       
            # Do not allow the tape of state cells to be modified while running.
            if not stateMachineRunning:
                # Check to see if a tape cell has been clicked.
                if tapeBorder.collidepoint(event.pos):
                    # Determine which cell.
                    cellPosition = int((event.pos[0] - TAPE_START_X) / TAPE_CELL_WIDTH)
                    # Find the cell position on the tape.
                    tapePosition = tapeHead - int(TAPE_CELLS/2) + cellPosition
                    
                    # Check for scroll wheel event.
                    if event.button == 4 or event.button == 5:
                        # 4 means scrolling up 5 means scrolling down.
                        positionY = event.button - 4
                    else :
                        # See if the y position is in the upper or lower part of the cell.
                        positionY = int((event.pos[1] - TAPE_START_Y) / (TAPE_CELL_HEIGHT/2))
                        
                    if positionY == 0:
                        tape[tapePosition] = (tape[tapePosition] - 1) % 7;
                    else:
                        tape[tapePosition] = (tape[tapePosition] + 1) % 7;
                    drawTapeCell(tapePosition, cellPosition)
                    
                # Check to see if a state table cell has been clicked.
                for state in statePanelOffsets:
                    # Check each panel.
                    panelBounds = statePanelOffsets[state]
                    if panelBounds.collidepoint(event.pos):
                        # Found clicked panel, find out which cell.
                        col = int((event.pos[0] - panelBounds[0])/(PANEL_CELL_WIDTH+PANEL_BORDER_WIDTH))
                        row = int((event.pos[1] - panelBounds[1])/(PANEL_CELL_HEIGHT+PANEL_BORDER_WIDTH))
                        
                        # Determine if event in upper or lower part of cell.
                        top = panelBounds[1]+(PANEL_CELL_HEIGHT+PANEL_BORDER_WIDTH)*(row)
                        bottom = top + PANEL_CELL_HEIGHT
                        middle = int((top + bottom) / 2)
                        
                        # If upper decrease the cell value, otherwise increase the cell value.
                        # Also check for mouse wheel events.
                        if event.button == 4:
                            offset =-1
                        elif event.button == 5:
                            offset = 1
                        elif event.pos[1] < middle:
                            offset = -1
                        else: 
                            offset = 1
                      
                        # Read symbols. Only the last column can be changed in the read row.
                        if row == 1 and col == 5:
                            value = stateTable[state+str(col)][0]
                            size = len(readSymbols)
                            pos = readSymbols.index(value)
                            index = (pos+offset) % size
                            value = readSymbols[index]
                            stateTable[state+str(col)][0] = value
                            drawStateSymbol(state, 1, 5, value) 
                            # Special case for 'b'.
                            if value == 'b':
                                stateTable[state+str(col)][1] = value
                                drawStateSymbol(state, 2, 5, value) 
                            else:
                                stateTable[state+str(col)][1] = ' '
                                drawStateSymbol(state, 2, 5, ' ') 
                        elif row == 2:
                            value = stateTable[state+str(col)][1]
                            if value != 'b':
                                size = len(writeSymbols)
                                pos = writeSymbols.index(value)
                                index = (pos+offset) % size
                                value = writeSymbols[index]
                                stateTable[state+str(col)][1] = value
                                drawStateSymbol(state, 2, col, value)
                        elif row == 3:
                            value = stateTable[state+str(col)][2]
                            size = len(moveSymbols)
                            pos = moveSymbols.index(value)
                            index = (pos+offset) % size
                            value = moveSymbols[index]
                            stateTable[state+str(col)][2] = value
                            drawStateSymbol(state, 3, col, value) 
                        elif row == 4:
                            value = stateTable[state+str(col)][3]
                            size = len(gotoSymbols)
                            pos = gotoSymbols.index(value)
                            index = (pos+offset) % size
                            value = gotoSymbols[index]
                            stateTable[state+str(col)][3] = value
                            drawStateSymbol(state, 4, col, value)
        
    if done:
        break # Break out of the while loop.
    
    # Highlight any buttons the mouse is over.
    checkForMouseovers(buttons)
                
    # Don't start running the state machine until play pressed.
    if stateMachineRunning == False:
        # Show the changes to the screen.
        pygame.display.flip()
        continue
    
    # If RUN use the optimized method. 
    if runState == 'RUN':
        if currentStep == 'READ':
            
            # Run the optimized state machine.
            result = runFast()
            if result == 'E':
                showStateTableError()
            haltStateMachine()
            continue
        else:
            # Run fast is expecting the current step to be READ. Synchronize!
            stepReady = True
            playPressed = True
        
            
    # Read.
    if currentStep == 'READ':
        if stepReady == False:
            # Highlight the state and read labels.
            drawPanelLabel(currentState, 'READ', True)
            drawPanelState(currentState, True)
            
            # Highlight the tape head.
            showButton(downArrowButton, True)
            
            # Indicate read ready for play press.
            stepReady = True
        if playPressed:
            # Read the symbol at the tape head position and determine the transition tuple.
            value = tape[tapeHead]
            if value == 6:
                currentTransition = stateTable[currentState+'5']
            else:
                currentTransition = stateTable[currentState+str(value)]
                
            if currentTransition[1] == ' ' or currentTransition[2] == ' ' or currentTransition[3] == ' ':
                
                showStateTableError()
                
                # Reset to starting state.
                playPressed = False
                resetRuntime()
                setStartingMode()
             
                continue
                
            # Highlight the transition column selected.
            highlightTransition(currentState, currentTransition)
            
            # Set the READ label to normal.
            drawPanelLabel(currentState, 'READ')
            
            # Advance to the next step.
            currentStep = 'WRITE'
            playPressed = False
            stepReady = False
            
    # Write.
    if currentStep == 'WRITE':
        if stepReady == False:
            # Highlight the write label.
            drawPanelLabel(currentState, 'WRITE', True)  
             
            # Indicate write ready for play press.
            stepReady = True
        if playPressed:
            # Update the tape with the new value. If is 'b' don't write,
            if currentTransition[1] != 'b':
                tape[tapeHead] = int(currentTransition[1])
                
            # Show the updated tape cell.
            cellPosition = int(TAPE_CELLS/2)
            drawTapeCell(tapeHead, cellPosition)
              
            # Set the WRITE label to normal.
            drawPanelLabel(currentState, 'WRITE')
            
            # Remove highlight from tape head.
            showButton(downArrowButton)
                
            # Advance to the next step.
            currentStep = 'MOVE'
            playPressed = False
            stepReady = False
            
    # Move.
    if currentStep == 'MOVE':
        if stepReady == False:
            # Highlight the move label.
            drawPanelLabel(currentState, 'MOVE', True)  
            
            # Highlight the appropriate tape direction arrow.
            if currentTransition[2] != 'R':
                showButton(leftArrowButton, True)
            else:
                showButton(rightArrowButton, True)
             
            # Indicate write ready for play press.
            stepReady = True
        
        if playPressed:
            # Check for boundary conditions.
            if currentTransition[0] == 'b' and currentTransition[2] == lastMoveDirection:
                # Cannot go past a boundary.
                haltStateMachine()
            else:  
                # Move the tape.
                if currentTransition[2] != 'R':
                    if tapeHead < TAPE_NUMBER_CELLS - int(TAPE_CELLS/2) - 1:
                        tapeHead += 1
                    else:
                        # Out of bounds.
                        haltStateMachine()
                    button = leftArrowButton
                else:
                    if tapeHead > int(TAPE_CELLS/2) + 1:
                        tapeHead -= 1
                    else:
                        # Out of bounds.
                        haltStateMachine()
                    button = rightArrowButton
                    
                # Set the tape arrow button to normal.
                showButton(button)
                
                # Set the MOVE label to normal.
                drawPanelLabel(currentState, 'MOVE')
                
                # Show the updated tape.
                drawTape()
                    
                # Record the last move direction.
                lastMoveDirection = currentTransition[2]
                
                # Advance to the next step.
                currentStep = 'GOTO'
                playPressed = False
                stepReady = False
    
    # Goto.
    if currentStep == 'GOTO':
        if stepReady == False:
            # Highlight the move label.
            drawPanelLabel(currentState, 'GOTO', True)  
             
            # Indicate write ready for play press.
            stepReady = True
        if playPressed:
                
            # Set the MOVE label and state to normal.
            drawPanelLabel(currentState, 'GOTO')
            drawPanelState(currentState)
            
            # Set the transition column selected to normal.
            if currentTransition[0] == 'b':
                col = 5
            else:
                col = int(currentTransition[0])
            drawStateSymbol(currentState, 1, col, currentTransition[0])
            drawStateSymbol(currentState, 2, col, currentTransition[1])
            drawStateSymbol(currentState, 3, col, currentTransition[2])
            drawStateSymbol(currentState, 4, col, currentTransition[3])
            
            # Set the new state.
            if currentTransition[3] == 'H':
                haltStateMachine()
            else:
                currentState = currentTransition[3]
                
            # Clear the current transition.
            currentTransition = None
            
            # Advance to the next step.
            currentStep = 'READ'
            playPressed = False
            stepReady = False
           
    # Show the changes to the screen.
    pygame.display.flip()
    clock.tick(60)