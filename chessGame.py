#################################################
# chessGame.py
#
# Your name: Victoria Chen
# Your andrew id: vxc
#################################################

from cmu_112_graphics import *

#################################################
# CHESS PIECE CLASSES
#################################################

class ChessPiece(object):
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.moved = False

        self.posMoves = set()
        self.value = 0

    def move(self, newRow, newCol):
        # check if in valid move
        # if valid, make move
        pass
    
    def isValidMove(self, newRow, newCol):
        # checks if newRow, newCol is in list of valid moves or in board
        pass

    def getValidMoves(self):
        # returns list of valid moves from current position
        pass

class Pawn(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)

        if self.color == "white":
            self.posMoves = {(-1, 0), (-2, 0)}
        else: # self.color == "black"
            self.posMoves = {(1, 0), (2, 0)}
        self.value = 1

        # when self.moved switches to True, pop (0, +/-2)

    def __repr__(self):
        return "P"

class Rook(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        vertMoves1 = {(0, i) for i in range(1,8)}
        vertMoves2 = {(0, -i) for i in range(1,8)}
        horMoves1 = {(i, 0) for i in range(1,8)}
        horMoves2 = {(-i, 0) for i in range(1,8)}
        self.posMoves = set.union(horMoves1, horMoves2, vertMoves1, vertMoves2)
        self.value = 5

        # castling no longer an option when self.moved = True
    
    def __repr__(self):
        return "R"

class Bishop(ChessPiece):
    # def __init__(self, row, col, color):
    #     super().__init__(row, col, color)
    #     vertMoves = {(0, i) for i in range(1,8)}
    #     horMoves = {(i, 0) for i in range(1,8)}
    #     self.posMoves = set.union(horMoves, vertMoves)
    #     self.value = 5
    def __repr__(self):
        return "B"

class Knight(ChessPiece):
    def __repr__(self):
        return "N"

class King(ChessPiece):
    def __repr__(self):
        return "K"

class Queen(ChessPiece):
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

def gameMode_timerFired(app):
    # maybe use to display "time-passed" clock for each player
    pass

def gameMode_drawMoves(app, canvas):
    posMoves = app.activePiece.posMoves

def gameMode_checkBlockingPiece(app, canvas):
    # make case for knights
    # if not a knight
        # dx, dy (get unit directional movement)
        # for magnitude in range(1, 8):
            # moveX, moveY = dx * mag, dy * mag
            # while moveX, moveY in posMoves:
                # row, col = (app.activePiece.row + moveX,
                            # app.activePiece.col + moveY)
                # if gameBoard[row][col] is ChessPiece
                    # return True
    # return False
    pass

def gameMode_mousePressed(app, event):
    x = event.x
    y = event.y
    print(app.activePiece)
    row, col = getRowCol(app, x, y)
    if isinstance(app.gameBoard[row][col], ChessPiece):
        if app.activePiece == None:
            app.activePiece = app.gameBoard[row][col]
            print(app.activePiece)
        else: # app.activePiece != None
            clickedPiece = app.gameBoard[row][col]
            if app.activePiece.color == clickedPiece.color:
                app.activePiece = clickedPiece
            else:
                # check if taking the piece is possible
                pass
    else:
        print("non-piece clicked!")
        if app.activePiece != None:
            dx = row - app.activePiece.row
            dy = col - app.activePiece.col
            print(dx, dy)
            print(f"posMoves: {app.activePiece.posMoves}")
            if (dx, dy) in app.activePiece.posMoves:
                app.gameBoard[app.activePiece.row][app.activePiece.col] = 0
                app.activePiece.row, app.activePiece.col = row, col
                app.activePiece.moved = True
                # if type(app.activePiece == Pawn): # remove pawn dumping option
                #     app.activePiece.posMoves.pop()
                app.gameBoard[row][col] = app.activePiece
                app.activePiece = None
                print("move made!")

        
    # check where click falls
    # if chess piece is inside that square
        # extract which piece is there
        # project piece's potential moves
        # set some value such that it's stored that the piece has been selected
    # if no chess piece is inside that square
        # check if there's a selected piece
        # if selected piece exists:
            # see if move is valid, if it is, make move
        # else:
            # do nothing

def gameMode_keyPressed(app, event):
    # if (event.key == 'p'):
    #     app.mode = 'pauseMode'
    pass

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
    if app.activePiece != None:
        gameMode_drawMoves(app, canvas)
    # canvas.create_image(200, 200, image=ImageTk.PhotoImage(app.whitePawnImg))


#################################################
# GENERAL CONTROLS
#################################################

# return True if row, col is inside the chess board
def inBoard(app, row, col):
    if (row < 0 or row >= app.rows) or (col < 0 or col >= app.cols):
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
        

# initializes all app variables
def appStarted(app):
    # board-related variables
    app.margin = 30
    app.rows, app.cols = 8, 8
    app.squareSize = (app.width - (2 * app.margin)) / 8
    app.squareOutlineWidth = 5
    app.boardColors = ['green', 'tan']
    app.backgroundColor = 'brown'    
    # app.images = dict()
    # chessPieces = app.loadImage('chessSprites.png')
    # app.whitePawnImg = chessPieces.crop((1000, 0, 1200, 200))

    # game-related variables
    app.mode = 'gameMode'

    app.activePiece = None
    app.playerToMove = "white"

    app.gameBoard = [[0] * 8 for i in range(8)]
    for col in range(app.cols):
        app.gameBoard[1][col] = Pawn(1, col, "black")
        app.gameBoard[app.rows - 2][col] = Pawn(app.rows - 2, col, "white")
    
    for row in {0, -1}:
        if row == 0: 
            color = "black" 
        else:
            color = "white"
        # add color parameter in once that's put into the classes
        for col in {0, -1}:
            app.gameBoard[row][col] = Rook(row, col, color)
        for col in {1, -2}:
            app.gameBoard[row][col] = Knight(row, col, color)
        for col in {2, -3}:
            app.gameBoard[row][col] = Bishop(row, col, color)
        
def redrawAll(app, canvas):

    # getting image from app.images
    # photoImage = getCachedPhotoImage(app, image)
    pass

runApp(width = 600, height = 600)