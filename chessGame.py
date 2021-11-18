#################################################
# chessGame.py
#
# Your name: Victoria Chen
# Your andrew id: vxc
#################################################

# TO-DOS
    # write checkmate function

from cmu_112_graphics import *
import math
import random

#################################################
# CHESS PIECE CLASSES
#################################################

class ChessPiece(object):
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.hashables = (self.row, self.col, self.color)

        self.moved = False
        self.posMoves = set()
        self.takeMoves = self.posMoves
        self.value = 0

    def __hash__(self):
        return hash(self.hashables)

    # def move(self, newRow, newCol):
    #     # check if in valid move
    #     # if valid, make move
    #     pass
    
    # def isValidMove(self, newRow, newCol):
    #     # checks if newRow, newCol is in list of valid moves or in board
    #     pass

    # def getValidMoves(self):
    #     # returns list of valid moves from current position
    #     pass

class Pawn(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        if self.color == "white":
            self.posMoves = {(-1, 0)} # ignoring -2,0 for now
            self.takeMoves = {(-1, -1), (-1, 1)}
        else: # self.color == "black"
            self.posMoves = {(1, 0)} # ignoring 2,0 for now
            self.takeMoves = {(1, -1), (1, 1)}
        
        self.value = 1

        # when self.moved switches to True, pop (0, +/-2)

    def __repr__(self):
        return "P"

class Rook(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        vertMoves = {(0, i) for i in range(-7,8) if i != 0}
        horMoves = {(i, 0) for i in range(-7,8) if i != 0}
        self.posMoves = set.union(horMoves, vertMoves)
        self.takeMoves = self.posMoves

        self.value = 5

        # castling no longer an option when self.moved = True
    
    def __repr__(self):
        return "R"

class Bishop(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        neMoves = {(-i, i) for i in range(1,8)}
        seMoves = {(i, i) for i in range(1,8)}
        nwMoves = {(-i, -i) for i in range(1,8)}
        swMoves = {(i, -i) for i in range(1,8)}
        self.posMoves = set.union(neMoves, seMoves, nwMoves, swMoves)
        self.takeMoves = self.posMoves

        self.value = 3

    def __repr__(self):
        return "B"

class Knight(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        for drow in {-2, -1, 1, 2}:
            for dcol in {-2, -1, 1, 2}:
                if abs(drow) == abs(dcol):
                    continue
                self.posMoves.add((drow, dcol))
        self.takeMoves = self.posMoves

        self.value = 3

    def __repr__(self):
        return "N"

class King(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        for r in {-1, 0, 1}:
            for c in {-1, 0, 1}:
                if (r, c) != (0, 0):
                    self.posMoves.add((r, c))
        self.takeMoves = self.posMoves

        self.value = 50

    def __repr__(self):
        return "K"

class Queen(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        neMoves = {(-i, i) for i in range(1,8)}
        seMoves = {(i, i) for i in range(1,8)}
        nwMoves = {(-i, -i) for i in range(1,8)}
        swMoves = {(i, -i) for i in range(1,8)}
        vertMoves = {(0, i) for i in range(-7,8) if i != 0}
        horMoves = {(i, 0) for i in range(-7,8) if i != 0}
        self.posMoves = set.union(neMoves, seMoves, nwMoves, swMoves,
                                  vertMoves, horMoves)
        self.takeMoves = self.posMoves
        
        self.value = 10

    def __repr__(self):
        return "Q"

#################################################
# HOME SCREEN
#################################################
def homeScreenMode_drawScreen(app, canvas):
    pass

def homeScreenMode_mousePressed(app, event):
    pass

def homeScreenMode_redrawAll(app, canvas):
    pass

#################################################
# GAME MODE
#################################################

def gameMode_timerFired(app):
    # maybe use to display "time-passed" clock for each player
    pass

########################
# LOGIC FUNCTIONS
######################## 
                                     
def gameMode_isValidMove(app, moveRow, moveCol): # maybe merge and j make this "isValidMove()"
    # print("**** NEW PIECE ****")
    currRow, currCol = app.activePiece.row, app.activePiece.col
    dRow, dCol = (moveRow - currRow), (moveCol - currCol)
    if ((dRow, dCol) not in app.activePiece.posMoves 
        or rowColInBounds(app, moveRow, moveCol) == False):
        return False

    result = gameMode_checkBlockingPieces(app, moveRow, moveCol)
    if result == True or result == "takePiece":
        return True
    else:
        return False

def gameMode_checkBlockingPieces(app, moveRow, moveCol):
    currRow, currCol = app.activePiece.row, app.activePiece.col
    dRow, dCol = (moveRow - currRow), (moveCol - currCol)

    if type(app.activePiece) != Knight:
        dist = math.sqrt(dRow ** 2 + dCol ** 2)
        # print(f"dRow, dCol: {dRow}, {dCol}, dist: {dist}")
        unitDRow, unitDCol = math.ceil(dRow / dist), math.ceil(dCol / dist)
        if dRow / dist < 0:
            unitDRow = -math.ceil(abs(dRow/dist))
        if dCol / dist < 0:
            unitDCol = -math.ceil(abs(dCol/dist))

        tempRow, tempCol =  currRow + unitDRow, currCol + unitDCol
        # print(f"currRow, currCol: {currRow}, {currCol}")
        # print(f"tempRow, tempCol: {tempRow}, {tempCol}")
        # print(f"moveRow, moveCol: {moveRow}, {moveCol} unitDRow, unitDCol: {unitDRow}, {unitDCol}")
        loopCounter = 0
        # print(f"loop condition: {(tempRow != moveRow) or (tempCol != moveCol)}")
        while (tempRow != moveRow + unitDRow) or (tempCol != moveCol + unitDCol):
            # print(f"loop {loopCounter}:", tempRow, tempCol, type(app.gameBoard[tempRow][tempCol]))
            tempPiece = app.gameBoard[tempRow][tempCol]
            if (isinstance(tempPiece, ChessPiece) and
                tempPiece.color == app.activePiece.color):
                return False

            # if piece is diff color & not the desired moveRow, moveCol location
            elif (isinstance(tempPiece, ChessPiece) and
                  tempPiece.color != app.activePiece.color and
                  (tempRow != moveRow or tempCol != moveCol)):
                return False
            
            # if piece is diff color & is the desired moveRow, moveCol location
            elif (isinstance(tempPiece, ChessPiece) and
                  tempPiece.color != app.activePiece.color and
                  (tempRow == moveRow or tempCol == moveCol)):
                return "takePiece"

            tempRow += unitDRow
            tempCol += unitDCol
            # loopCounter += 1
    return True

# if move is valid, make move and adjust set of same-color pieces accordingly
def gameMode_makeMove(app, row, col):
    if gameMode_isValidMove(app, row, col):
        app.gameBoard[app.activePiece.row][app.activePiece.col] = 0
        eval(f"app.{app.activePiece.color}Pieces.remove(app.activePiece)")

        app.activePiece.row, app.activePiece.col = row, col
        app.activePiece.moved = True
        # if type(app.activePiece == Pawn): # remove pawn jumping option
        #     app.activePiece.posMoves.pop()
        app.gameBoard[row][col] = app.activePiece
        eval(f"app.{app.activePiece.color}Pieces.add(app.activePiece)")

        app.activePiece = None
        app.playerToMoveIdx += 1 

# if move is valid, take piece and remove piece from respective set of pieces
def gameMode_takePiece(app, row, col):
    if gameMode_isValidMove(app, row, col):
        app.gameBoard[app.activePiece.row][app.activePiece.col] = 0
        app.activePiece.row, app.activePiece.col = row, col
        app.activePiece.moved = True

        takenPiece = app.gameBoard[row][col]
        eval(f"app.{takenPiece.color}Pieces.remove(takenPiece)")

        app.gameBoard[row][col] = app.activePiece
        # insert code where taken piece is removed from list of color's pieces
            # do this when backtracking/position eval is applied
        app.activePiece = None
        app.playerToMoveIdx += 1

def gameMode_hasCheck(app):

    pass

def gameMode_hasCheckmate(app):
    pass # maybe just make this a regular method since it applies to both 
         # 2 player and AI version of game (perhaps do same for other methods)

########################
# EVENT FUNCTIONS
########################

def gameMode_mousePressed(app, event):
    x, y = event.x, event.y
    if inBoard(app, x, y) == False:
        return
    row, col = getRowCol(app, x, y)
    currPlayerColor = app.players[app.playerToMoveIdx % 2]

    # user clicked on a chess piece
    if isinstance(app.gameBoard[row][col], ChessPiece):
        # if currPlayerColor != color of piece clicked
            # if is valid move
                # take piece
            # else
                # do nothing
        # else # if currPlayerColor == color of piece clicked
            # run existing code below
        if app.activePiece == None:
            if (app.gameBoard[row][col].color != 
                app.players[app.playerToMoveIdx % 2]):
                return
            app.activePiece = app.gameBoard[row][col]
            # print(app.activePiece)
        
        else: # app.activePiece != None
            clickedPiece = app.gameBoard[row][col]
            if app.activePiece.color == clickedPiece.color:
                app.activePiece = clickedPiece
            else: # pieces are different colors
                gameMode_takePiece(app, row, col)
                

    else: # user clicked on an empty space
        # print(f"empty space clicked! {app.activePiece}")
        if app.activePiece != None:
            # print(app.activePiece, gameMode_isValidMove(app, row, col))
            gameMode_makeMove(app, row, col)
            

    # print(app.activePiece)

def gameMode_keyPressed(app, event):
    # if (event.key == 'p'):
    #     app.mode = 'pauseMode'
    pass


########################
# DRAW FUNCTIONS
########################

# draws chess game board --> maybe make this a general method as it'll be
# called in both two player and AI mode
def gameMode_drawBoard(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height,
                            fill = app.backgroundColor)
    for row in range(app.rows):
        for col in range(app.cols):
            x0, y0, x1, y1 = getDimensions(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1,
                                    fill = app.boardColors[(row + col) % 2],
                                    width = app.squareOutlineWidth)

def gameMode_drawMoves(app, canvas):
    posMoves = app.activePiece.posMoves
    currRow, currCol = app.activePiece.row, app.activePiece.col
    for (dRow, dCol) in posMoves:
        moveRow, moveCol = currRow + dRow, currCol + dCol
        if (gameMode_isValidMove(app, moveRow, moveCol) and
            isinstance(app.gameBoard[moveRow][moveCol], ChessPiece) != True):
            x0, y0, x1, y1 = getDimensions(app, moveRow, moveCol)
            x, y = (x0 + x1) / 2, (y0 + y1) / 2
            canvas.create_oval(x - app.moveDotR, y - app.moveDotR,
                               x + app.moveDotR, y + app.moveDotR,
                               fill = app.moveDotColor)
        elif (gameMode_isValidMove(app, moveRow, moveCol) and
              isinstance(app.gameBoard[moveRow][moveCol], ChessPiece) == True and
              app.activePiece.color != app.gameBoard[moveRow][moveCol].color):
            x0, y0, x1, y1 = getDimensions(app, moveRow, moveCol)
            x, y = (x0 + x1) / 2, (y0 + y1) / 2
            canvas.create_oval(x - app.moveDotR, y - app.moveDotR,
                               x + app.moveDotR, y + app.moveDotR,
                               fill = app.takeDotColor)

def gameMode_drawPieces(app, canvas):
    for rowIdx in range(len(app.gameBoard)):
        for colIdx in range(len(app.gameBoard[rowIdx])):
            piece = app.gameBoard[rowIdx][colIdx]
            if type(piece) == int:
                continue
            else:
                x0, y0, x1, y1 = getDimensions(app, rowIdx, colIdx)
                canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                                   text = str(piece), font = "Arial 40",
                                   fill = piece.color)

def gameMode_redrawAll(app, canvas):
    gameMode_drawBoard(app, canvas)
    gameMode_drawPieces(app, canvas)
    # canvas.create_oval(100, 100, 110, 110, fill = "blue")
    if app.activePiece != None:
        gameMode_drawMoves(app, canvas)
    # canvas.create_image(200, 200, image=ImageTk.PhotoImage(app.whitePawnImg))


#################################################
# GENERAL CONTROLS
#################################################

# return True if x, y is inside the chess board
def inBoard(app, x, y):
    # checks if click is outside board entirely
    if ((x < app.margin or x > app.width - app.margin)
        or (y < app.margin or y > app.height - app.margin)): # may need to adjust these values
        return False

    return True

# return true if entered row and col are inside board bounds
def rowColInBounds(app, row, col):
    if row < 0 or row >= app.rows or col < 0 or col >= app.cols:
        return False
    return True

# gets coordinates of row, col square on board
def getDimensions(app, row, col):
    x0 = col * app.squareSize + app.margin
    y0 = row * app.squareSize + app.margin
    x1 = (col + 1) * app.squareSize + app.margin
    y1 = (row + 1) * app.squareSize + app.margin
    return (x0, y0, x1, y1)

# gets row, col that contains x, y
def getRowCol(app, x, y):
    row = int((y - app.margin) // app.squareSize)
    col = int((x - app.margin) // app.squareSize)
    return (row, col)

# code obtained from 15-112 course notes
# def getCachedPhotoImage(app, image):
#     # stores a cached version of the PhotoImage in the PIL/Pillow image
#     if ('cachedPhotoImage' not in image.__dict__):
#         image.cachedPhotoImage = ImageTk.PhotoImage(image)
#     return image.cachedPhotoImage

# def loadChessPieceImages(app):
#     chessPieces = app.loadImage('chessSprites.png')
#     whiteKingImg = chessPieces.crop((0, 0, 200, 200))
#     blackKingImg = chessPieces.crop((0, 200, 200, 400))

#     whiteQueenImg = chessPieces.crop((200, 0, 400, 200))
#     blackQueenImg = chessPieces.crop((200, 200, 400, 400))

#     whiteKnightImg = chessPieces.crop((600, 0, 800, 200))
#     blackKnightImg = chessPieces.crop((600, 200, 800, 400))

#     whiteRookImg = chessPieces.crop((800, 0, 1000, 200))
#     blackRookImg = chessPieces.crop((800, 200, 1000, 400))

#     whitePawnImg = chessPieces.crop((1000, 0, 1200, 200))
#     blackPawnImg = chessPieces.crop((1000, 200, 1200, 400))
    
    # for image in list of images
        # scale image down from 200x200 to whatever equals size of board square
        
def initializeBoard(app):
    for col in range(app.cols):
        bPawn, wPawn = Pawn(1, col, "black"), Pawn(app.rows - 2, col, "white")
        app.gameBoard[1][col] = bPawn
        app.gameBoard[app.rows - 2][col] = wPawn
        app.blackPieces.add(bPawn)
        app.whitePieces.add(wPawn)
    
    for row in {0, app.rows - 1}:
        if row == 0: 
            color = "black"
        else:
            color = "white"

        for col in {0, app.cols - 1}:
            newRook = Rook(row, col, color)
            app.gameBoard[row][col] = newRook
            eval(f"app.{color}Pieces.add(newRook)")
        for col in {1, app.cols - 2}:
            newKnight = Knight(row, col, color)
            app.gameBoard[row][col] = newKnight
            eval(f"app.{color}Pieces.add(newKnight)")
        for col in {2, app.cols - 3}:
            newBishop = Bishop(row, col, color)
            app.gameBoard[row][col] = newBishop
            eval(f"app.{color}Pieces.add(newBishop)")

        if color == "white":
            wQueen, wKing = Queen(row, 3, color), King(row, 4, color)
            app.gameBoard[row][3], app.gameBoard[row][4] = wQueen, wKing
            app.whitePieces = app.whitePieces.union({wQueen, wKing})
        else:
            bQueen, bKing = Queen(row, 4, color), King(row, 3, color)
            app.gameBoard[row][4] = bQueen
            app.gameBoard[row][3] = bKing
            app.blackPieces = app.blackPieces.union({bQueen, bKing})

# initializes all app variables
def appStarted(app):
    # board-related variables
    app.margin = 30
    app.rows, app.cols = 8, 8
    app.squareSize = (app.width - (2 * app.margin)) / 8
    app.squareOutlineWidth = 5
    app.boardColors = ['tan', 'green']
    app.backgroundColor = 'brown'  
    app.moveDotR = 5
    app.moveDotColor = "blue" 
    app.takeDotColor = "red"
    # app.images = dict()
    # chessPieces = app.loadImage('chessSprites.png')
    # app.whitePawnImg = chessPieces.crop((1000, 0, 1200, 200))

    # game-related variables
    app.mode = 'gameMode'

    app.activePiece = None
    app.playerToMoveIdx = 0
    app.players = ["white", "black"]

    app.whitePieces = set()
    app.blackPieces = set()

    app.gameBoard = [[0] * 8 for i in range(8)]
    initializeBoard(app)
        
        
def redrawAll(app, canvas):

    # getting image from app.images
    # photoImage = getCachedPhotoImage(app, image)
    pass

runApp(width = 600, height = 600)