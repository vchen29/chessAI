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

    def hasMove(self, moveRow, moveCol):
        return (moveRow, moveCol) in self.posMoves

    def hasTake(self, takeRow, takeCol):
        return (takeRow, takeCol) in self.takeMoves

    def copy(self):
        return type(self)(self.row, self.col, self.color)
        

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
    moves = set()
    for drow in {-2, -1, 1, 2}:
            for dcol in {-2, -1, 1, 2}:
                if abs(drow) == abs(dcol):
                    continue
                moves.add((drow, dcol))

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
    
    canvas.create_rectangle(0, 0, app.width, app.height,
                            fill = "tan")
    canvas.create_text(app.width / 2, app.chessAITextY,
                       text = "Chess AI", font = "Helvetica 70")
    canvas.create_rectangle(app.twoPlayerButtonX - app.buttonWidth, 
                            app.gameModeButtonY - app.buttonHeight,
                            app.twoPlayerButtonX + app.buttonWidth,
                            app.gameModeButtonY + app.buttonHeight,
                            fill = "brown")
    canvas.create_text(app.twoPlayerButtonX, app.gameModeButtonY,
                       text = "Two Players", fill = "black",
                       font = "Helvetica 25")
    canvas.create_rectangle(app.aiModeButtonX - app.buttonWidth, 
                            app.gameModeButtonY - app.buttonHeight,
                            app.aiModeButtonX + app.buttonWidth,
                            app.gameModeButtonY + app.buttonHeight,
                            fill = "brown")
    canvas.create_text(app.aiModeButtonX, app.gameModeButtonY,
                       text = "AI Mode!", fill = "black",
                       font = "Helvetica 25")

def homeScreenMode_mousePressed(app, event):
    x, y = event.x, event.y
    # if clicked inside 2 player button
    if (x >= (app.twoPlayerButtonX - app.buttonWidth) 
        and x <= (app.twoPlayerButtonX + app.buttonWidth)
        and y >= (app.gameModeButtonY - app.buttonHeight) 
        and y <= (app.gameModeButtonY + app.buttonHeight)):
        app.mode = "gameMode"
    elif (x >= (app.aiModeButtonX - app.buttonWidth) 
          and x <= (app.aiModeButtonX + app.buttonWidth)
          and y >= (app.gameModeButtonY - app.buttonHeight) 
          and y <= (app.gameModeButtonY + app.buttonHeight)):
          pass
    

def homeScreenMode_redrawAll(app, canvas):
    homeScreenMode_drawScreen(app, canvas)

#################################################
# GAME MODE
#################################################

def gameMode_timerFired(app):
    # maybe use to display "time-passed" clock for each player
    pass

########################
# LOGIC FUNCTIONS
######################## 

# checks if the move is a valid move                      
def gameMode_isValidMove(app, moveRow, moveCol, piece):
    print("running isValidMove")
    if rowColInBounds(app, moveRow, moveCol) == False:
        return False
    # print("**** NEW PIECE ****")
    moveSquare = app.gameBoard[moveRow][moveCol]
    if (isinstance(moveSquare, ChessPiece)):
        return False

    currRow, currCol = piece.row, piece.col
    dRow, dCol = (moveRow - currRow), (moveCol - currCol)

    if ((dRow, dCol) not in piece.posMoves 
        or rowColInBounds(app, moveRow, moveCol) == False):
        return False
    # elif: (if move the piece and it leaves your piece vulnerable to check)
    #     pass
    hasNoBlockingPieces = gameMode_checkBlockingPieces(app, moveRow, moveCol, piece)
    isChecked = gameMode_attemptMoveTestForCheck(app, moveCol, moveCol, piece)
    if hasNoBlockingPieces and isChecked == False:
        return True
    else:
        return False

def gameMode_isValidTake(app, takeRow, takeCol, piece):
    print("running isValidTake")

    if rowColInBounds(app, takeRow, takeCol) == False:
        return False
    # check if takeRow, takeCol is a ChessPiece of opposite color to piece
    # print(f"checking if {str(piece)} can take ({takeRow},{takeCol})")
    takeSquare = app.gameBoard[takeRow][takeCol]
    if (isinstance(takeSquare, ChessPiece) == False):
        return False
    elif (isinstance(takeSquare, ChessPiece) and 
          takeSquare.color == piece.color):
        return False
    # print("passed instance tests...", end = "")
    currRow, currCol = piece.row, piece.col
    dRow, dCol = (takeRow - currRow), (takeCol - currCol)

    if ((dRow, dCol) not in piece.takeMoves 
        or rowColInBounds(app, takeRow, takeCol) == False):
        return False
    # print("is inside takeMoves...", end = "")
    hasNoBlockingPieces = gameMode_checkBlockingPieces(app, takeRow, takeCol, piece)
    isChecked = gameMode_attemptMoveTestForCheck(app, takeRow, takeCol, piece)
    if hasNoBlockingPieces and isChecked == False:
        return True
    else:
        return False
    
# split up regular move and a take move such that you can accomodate the 
# unique case for pawns..?
# NOTE: adjust drawMoves() method, gameMode_makeMove(), gameMode_isValidMove(), etc.

# returns True if no blocking pieces exist (move is valid)
# returns False otherwise
def gameMode_checkBlockingPieces(app, moveRow, moveCol, piece):
    print("running checkBlockingPieces")

    currRow, currCol = piece.row, piece.col
    dRow, dCol = (moveRow - currRow), (moveCol - currCol)

    if type(piece) != Knight:
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
        # loopCounter = 0
        # print(f"loop condition: {(tempRow != moveRow) or (tempCol != moveCol)}")
        while (tempRow != moveRow) or (tempCol != moveCol):
            # print(f"loop {loopCounter}:", tempRow, tempCol, type(app.gameBoard[tempRow][tempCol]))
            tempPiece = app.gameBoard[tempRow][tempCol]
            if (isinstance(tempPiece, ChessPiece) and
                tempPiece.color == piece.color):
                return False

            # if piece is diff color & not the desired moveRow, moveCol location
            elif (isinstance(tempPiece, ChessPiece) and
                  tempPiece.color != piece.color and
                  (tempRow != moveRow or tempCol != moveCol)):
                return False
            
            # # if piece is diff color & is the desired moveRow, moveCol location
            # elif (isinstance(tempPiece, ChessPiece) and
            #       tempPiece.color != piece.color and
            #       (tempRow == moveRow or tempCol == moveCol)):
            #     return "takePiece"

            tempRow += unitDRow
            tempCol += unitDCol
            # loopCounter += 1
    return True

# if move is valid, make move and adjust set of same-color pieces accordingly
def gameMode_makeMove(app, row, col):
    print("running gameMode_makeMove")
    oldRow, oldCol = app.activePiece.row, app.activePiece.col
    oldMoved = app.activePiece.moved

    if (gameMode_isValidMove(app, row, col, app.activePiece) and
        gameMode_attemptMoveTestForCheck(app, row, col, app.activePiece) == False):
        app.gameBoard[oldRow][oldCol] = 0
        eval(f"app.{app.activePiece.color}Pieces[str(app.activePiece)].remove(app.activePiece)")

        app.activePiece.row, app.activePiece.col = row, col
        app.activePiece.moved = True
        # if type(app.activePiece == Pawn): # remove pawn jumping option
        #     app.activePiece.posMoves.pop()
        app.gameBoard[row][col] = app.activePiece
        eval(f"app.{app.activePiece.color}Pieces[str(app.activePiece)].add(app.activePiece)")

        oppColor = getOpposingColor(app, app.activePiece)
        if gameMode_isChecked(app, oppColor):
            app.checked = oppColor
            if gameMode_isMated(app, oppColor):
                print("setting gameOver to True...")
                app.gameOver = True
                return
        else:
            app.checked = None

        app.activePiece = None
        app.playerToMoveIdx += 1 

# this function is SO similar to makeMove -- maybe merge them before you get too far?
# if move is valid, take piece and remove piece from respective set of pieces
def gameMode_takePiece(app, row, col):
    print("running takePiece")
    oldRow, oldCol = app.activePiece.row, app.activePiece.col
    oldMoved = app.activePiece.moved
    isValidTake = gameMode_isValidTake(app, row, col, app.activePiece)
    print(isValidTake, gameMode_attemptMoveTestForCheck(app, row, col, app.activePiece))
    if isValidTake and gameMode_attemptMoveTestForCheck(app, row, col, app.activePiece) == False:
        app.gameBoard[oldRow][oldCol] = 0
        eval(f"app.{app.activePiece.color}Pieces[str(app.activePiece)].remove(app.activePiece)")

        app.activePiece.row, app.activePiece.col = row, col
        app.activePiece.moved = True
        # if type(app.activePiece == Pawn): # remove pawn jumping option
        #     app.activePiece.posMoves.pop()
        takenPiece = app.gameBoard[row][col]
        eval(f"app.{takenPiece.color}Pieces[str(takenPiece)].remove(takenPiece)")

        app.gameBoard[row][col] = app.activePiece
        eval(f"app.{app.activePiece.color}Pieces[str(app.activePiece)].add(app.activePiece)")

        oppColor = getOpposingColor(app, app.activePiece)
        if gameMode_isChecked(app, oppColor):
            app.checked = oppColor
            if gameMode_isMated(app, oppColor):
                print("setting gameOver to True...")
                app.gameOver = True
                return
        else:
            app.checked = None

        app.activePiece = None
        app.playerToMoveIdx += 1
    print("is not valid take.")

def gameMode_isChecked(app, color):
    print("running isChecked")
    return gameMode_getCheckedAndPieces(app, color)[1]

def gameMode_getCheckingPieces(app, color):
    print("running getCheckingPieces")
    return gameMode_getCheckedAndPieces(app, color)[0]

def gameMode_getCheckedAndPieces(app, color):
    # print("starting check test!")
    king = eval(f"app.{color}Pieces['K'].pop()")
    eval(f"app.{color}Pieces['K'].add(king)")
    checked = False
    checkingPieces = []

    for (drow, dcol) in Knight.moves:
        row, col = king.row + drow, king.col + dcol
        if rowColInBounds(app, row, col):
            tempPiece = app.gameBoard[row][col]
            if type(tempPiece) == Knight and tempPiece.color != king.color:
                checked = True
                checkingPieces.append(tempPiece)
    
    # print("... no knight checks!")
    for dirRow, dirCol in king.posMoves:
        row, col = king.row + dirRow, king.col + dirCol
        while rowColInBounds(app, row, col):
            boardSq = app.gameBoard[row][col]
            if isinstance(boardSq, ChessPiece) and boardSq.color != king.color:
                # print(row, col, boardSq)
                if boardSq.hasTake(king.row - row, king.col - col):
                    checked = True
                    # print(f"Checked by {str(boardSq)}!")
                    checkingPieces.append(boardSq)
                else:
                    break
            elif isinstance(boardSq, ChessPiece) and boardSq.color == king.color:
                break
            row += dirRow
            col += dirCol
    # print(str(checkingPieces))
    return (checkingPieces, checked)

def gameMode_isMated(app, color):
    # print("checking for mate...", end = "")

    king = eval(f"app.{color}Pieces['K'].pop()")
    eval(f"app.{color}Pieces['K'].add(king)")
    kingRow, kingCol = king.row, king.col

    for drow, dcol in king.posMoves:
        newKing = king.copy()
        newKing.row += drow
        newKing.col += dcol

        if gameMode_isValidMove(app, newKing.row, newKing.col, king) == False:
            continue
        
        eval(f"app.{color}Pieces['K'].pop()")
        eval(f"app.{color}Pieces['K'].add(newKing)")
        if gameMode_isChecked(app, color) == False:
            eval(f"app.{color}Pieces['K'].pop()")
            eval(f"app.{color}Pieces['K'].add(king)")
            print(f"king has move {newKing.row}, {newKing.col}")
            return False
        eval(f"app.{color}Pieces['K'].pop()")
        eval(f"app.{color}Pieces['K'].add(king)")

    # print("no king moves...")
    # input()

    checkingPieces = gameMode_getCheckingPieces(app, color) # get pieces that are checking the king!
    for pieceType in eval(f"app.{color}Pieces"):
        for piece in eval(f"app.{color}Pieces[pieceType]"):
            for checkingPiece in checkingPieces:
                if gameMode_attemptMoveTestForCheck(app, checkingPiece.row, 
                                             checkingPiece.col, piece):
                    return False
    # print("no take moves...", end = "")

    if (len(checkingPieces) == 1) and (isinstance(checkingPieces[0], Knight)):
        print("Mate by Knight!")
        return True

    for pieceType in eval(f"app.{color}Pieces"):
        for piece in eval(f"app.{color}Pieces[pieceType]"):
            # print(f"testing {piece}")
            # input()
            pieceRow, pieceCol = piece.row, piece.col
            for checkingPiece in checkingPieces:
                dRow, dCol = (checkingPiece.row - kingRow), (checkingPiece.col - kingCol)
                dist = math.sqrt(dRow ** 2 + dCol ** 2)
                # print(f"dRow, dCol: {dRow}, {dCol}, dist: {dist}")
                unitDRow, unitDCol = math.ceil(dRow / dist), math.ceil(dCol / dist)
                if dRow / dist < 0:
                    unitDRow = -math.ceil(abs(dRow/dist))
                if dCol / dist < 0:
                    unitDCol = -math.ceil(abs(dCol/dist))
                tempRow, tempCol = kingRow, kingCol
                while tempRow != checkingPiece.row or tempCol != checkingPiece.col:
                    # print(f"tempRow, tempCol: {tempRow}, {tempCol}")
                    # print(f"pieceRow, pieceCol: {pieceRow}, {pieceCol}")
                    # input()
                    if (piece.hasMove(tempRow, tempCol)
                        and gameMode_attemptMoveTestForCheck(app, tempRow, tempCol, 
                                                      piece)):
                        print("returning false!")
                        return False
                    tempRow += unitDRow
                    tempCol += unitDCol
            # print("made through while loop")

    # print("no block moves...", end = "")
    # input()
    # print("mate!")   
    return True

# this function can be cleaned up for sure :')
# returns True if move successfully results in no check
# returns False if it doesn't
def gameMode_attemptMoveTestForCheck(app, tempRow, tempCol, piece):
    print("running attemptMoveTestForCheck")
    tempBoardSq = app.gameBoard[tempRow][tempCol]
    if isinstance(tempBoardSq, ChessPiece) and tempBoardSq.color == piece.color:
        return False
    # print(type(piece), str(piece))
    oppColor = getOpposingColor(app, piece)
    color = piece.color
    pieceCopy = piece.copy()
    whitePiecesCopy = app.whitePieces.copy()
    blackPiecesCopy = app.blackPieces.copy()
    if isinstance(tempBoardSq, ChessPiece) and tempBoardSq.color != piece.color:
        oppColorPiece = tempBoardSq
        if piece.hasTake(tempRow, tempCol):
            eval(f"app.{oppColor}Pieces[str(oppColorPiece)].remove(oppColorPiece)")
            app.gameBoard[tempRow][tempCol] = piece
            app.gameBoard[piece.row][piece.col] = 0
            eval(f"app.{color}Pieces[str(piece)].remove(piece)")

            pieceCopy.row, pieceCopy.col = tempRow, tempCol
            eval(f"app.{color}Pieces[str(pieceCopy)].add(pieceCopy)")

            result = None
            if gameMode_isChecked(app, color):
                result = False
            else:
                result = True

            eval(f"app.{color}Pieces[str(pieceCopy)].remove(pieceCopy)")
            eval(f"app.{color}Pieces[str(piece)].add(piece)")
            eval(f"app.{oppColor}Pieces[str(oppColorPiece)].add(oppColorPiece)")
            app.whitePieces = whitePiecesCopy
            app.blackPieces = blackPiecesCopy
            return result

    else:
        if piece.hasMove(tempRow, tempCol): 
            app.gameBoard[tempRow][tempCol] = piece
            app.gameBoard[piece.row][piece.col] = 0
            eval(f"app.{color}Pieces[str(piece)].remove(piece)")

            pieceCopy.row, pieceCopy.col = tempRow, tempCol
            eval(f"app.{color}Pieces[str(pieceCopy)].add(pieceCopy)")

            result = None
            if gameMode_isChecked(app, color):
                result = False
            else:
                result = True

            eval(f"app.{color}Pieces[str(pieceCopy)].remove(pieceCopy)")
            eval(f"app.{color}Pieces[str(piece)].add(piece)")
            app.whitePieces = whitePiecesCopy
            app.blackPieces = blackPiecesCopy
            return result
    return False

########################
# EVENT FUNCTIONS
########################

def gameMode_mousePressed(app, event):
    if app.gameOver == True:
        return
    
    x, y = event.x, event.y
    if inBoard(app, x, y) == False:
        return
    row, col = getRowCol(app, x, y)
    currPlayerColor = app.players[app.playerToMoveIdx % 2]

    clickedSquare = app.gameBoard[row][col]
    # user clicked on a chess piece
    if isinstance(clickedSquare, ChessPiece):
        if app.activePiece == None and currPlayerColor == clickedSquare.color:
            # if (app.gameBoard[row][col].color != 
            #     app.players[app.playerToMoveIdx % 2]):
            #     return
            app.activePiece = clickedSquare
            # print(app.activePiece)
        elif app.activePiece == None and currPlayerColor != clickedSquare.color:
            return
        else: # app.activePiece != None
            if app.activePiece.color == clickedSquare.color:
                app.activePiece = clickedSquare
            elif app.activePiece.color != clickedSquare.color: # pieces are different colors
                gameMode_takePiece(app, row, col)

    else: # user clicked on an empty space
        # print(f"empty space clicked! {app.activePiece}")
        if app.activePiece != None:
            # print(app.activePiece, gameMode_isValidMove(app, row, col))
            gameMode_makeMove(app, row, col)
            

    print(app.activePiece)
    print(str(app.whitePieces))
    print(str(app.blackPieces))
    print()

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

def gameMode_getValidMoves(app, piece):
    posMoves = piece.posMoves
    currRow, currCol = piece.row, piece.col
    validMoves = set()
    for (dRow, dCol) in posMoves:
        moveRow, moveCol = currRow + dRow, currCol + dCol
        if (gameMode_isValidMove(app, moveRow, moveCol, app.activePiece)):
            validMoves.add((moveRow, moveCol))
    return validMoves

def gameMode_getValidTakes(app, piece):
    posTakes = piece.takeMoves
    currRow, currCol = piece.row, piece.col
    validTakes = set()
    for (dRow, dCol) in posTakes:
        moveRow, moveCol = currRow + dRow, currCol + dCol
        if (gameMode_isValidTake(app, moveRow, moveCol, app.activePiece)):
            validTakes.add((moveRow, moveCol))
    return validTakes

def gameMode_drawMoves(app, canvas):
    for (moveRow, moveCol) in gameMode_getValidMoves(app, app.activePiece):
        x0, y0, x1, y1 = getDimensions(app, moveRow, moveCol)
        x, y = (x0 + x1) / 2, (y0 + y1) / 2
        canvas.create_oval(x - app.moveDotR, y - app.moveDotR,
                           x + app.moveDotR, y + app.moveDotR,
                           fill = app.moveDotColor)
    for (takeRow, takeCol) in gameMode_getValidTakes(app, app.activePiece):
        x0, y0, x1, y1 = getDimensions(app, takeRow, takeCol)
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

def gameMode_drawCheck(app, canvas):
    canvas.create_text(app.width / 2, app.margin, 
                       text = f"{app.checked} check!", font = "Arial 20",
                       fill = "black")

def gameMode_redrawAll(app, canvas):
    if app.gameOver:
        canvas.create_text(app.width / 2, app.height / 2, text = "game over!", 
                            font = "Arial 40", fill = "black")
        return
    gameMode_drawBoard(app, canvas)
    gameMode_drawPieces(app, canvas)
    if app.activePiece != None:
        gameMode_drawMoves(app, canvas)
    if app.checked != None:
        gameMode_drawCheck(app, canvas)
    # canvas.create_image(200, 200, image=ImageTk.PhotoImage(app.whitePawnImg))


#################################################
# GENERAL CONTROLS
#################################################

def getOpposingColor(app, piece):
    if piece.color == "white":
        return "black"
    else:
        return "white"
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
    # chess sprites source: https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Chess_Pieces_Sprite.svg/640px-Chess_Pieces_Sprite.svg.png
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
        app.blackPieces["P"].add(bPawn)
        app.whitePieces["P"].add(wPawn)
    
    for row in {0, app.rows - 1}:
        if row == 0: 
            color = "black"
        else:
            color = "white"

        for col in {0, app.cols - 1}:
            newRook = Rook(row, col, color)
            app.gameBoard[row][col] = newRook
            eval(f"app.{color}Pieces[str(newRook)].add(newRook)")
        for col in {1, app.cols - 2}:
            newKnight = Knight(row, col, color)
            app.gameBoard[row][col] = newKnight
            eval(f"app.{color}Pieces[str(newKnight)].add(newKnight)")
        for col in {2, app.cols - 3}:
            newBishop = Bishop(row, col, color)
            app.gameBoard[row][col] = newBishop
            eval(f"app.{color}Pieces[str(newBishop)].add(newBishop)")

        if color == "white":
            wQueen, wKing = Queen(row, 3, color), King(row, 4, color)
            app.gameBoard[row][3], app.gameBoard[row][4] = wQueen, wKing
            app.whitePieces["Q"] = {wQueen}
            app.whitePieces["K"] = {wKing}
        else:
            bQueen, bKing = Queen(row, 3, color), King(row, 4, color)
            app.gameBoard[row][3] = bQueen
            app.gameBoard[row][4] = bKing
            app.blackPieces["Q"] = {bQueen}
            app.blackPieces["K"] = {bKing}

def initiateHomeScreenVariables(app):
    app.buttonWidth, app.buttonHeight = 100, 30
    app.chessAITextY = app.height * (1/4)
    app.gameModeButtonY = app.height * (1/2)
    app.twoPlayerButtonX = app.width * (1/4)
    app.aiModeButtonX = app.width * (3/4)

# initializes all app variables
def appStarted(app):
    initiateHomeScreenVariables(app)

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
    app.mode = 'homeScreenMode'

    app.activePiece = None
    app.playerToMoveIdx = 0
    app.players = ["white", "black"]

    app.whitePieces = {"P": set(), "B": set(), "N": set(), 
                       "R": set(), "K": set(), "Q": set()}
    app.blackPieces = {"P": set(), "B": set(), "N": set(), 
                       "R": set(), "K": set(), "Q": set()}
    
    app.checked = None
    app.gameOver = False

    app.gameBoard = [[0] * 8 for i in range(8)]
    initializeBoard(app)
        
        
def redrawAll(app, canvas):

    # getting image from app.images
    # photoImage = getCachedPhotoImage(app, image)
    pass

runApp(width = 600, height = 600)