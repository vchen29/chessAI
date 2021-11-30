#################################################
# chessGame.py
#
# Your name: Victoria Chen
# Your andrew id: vxc
#################################################

from cmu_112_graphics import *
import math
import copy
import random

#################################################
# CHESS PIECE CLASSES
#################################################

# ChessPiece class
class ChessPiece(object):
    def __init__(self, row, col, color, moved = False, posMoves = set(), takeMoves = set()):
        self.row = row
        self.col = col
        self.color = color
        self.hashables = (self.row, self.col, self.color)

        self.moved = moved
        self.posMoves = posMoves
        self.takeMoves = takeMoves
        self.value = 0
        
    def __hash__(self):
        return hash(self.hashables)

    def hasMove(self, moveRow, moveCol):
        return (moveRow, moveCol) in self.posMoves

    def hasTake(self, takeRow, takeCol):
        return (takeRow, takeCol) in self.takeMoves

    def copy(self):
        return type(self)(self.row, self.col, self.color, self.moved, self.posMoves, self.takeMoves)

# Pawn class (subclass of ChessPiece)   
class Pawn(ChessPiece):
    def __init__(self, row, col, color, moved = False, posMoves = set(), takeMoves = set()):
        super().__init__(row, col, color, moved, posMoves, takeMoves)

        if self.color == "white":
            if moved:
                self.posMoves = {(-1, 0)}
            else:
                self.posMoves = {(-1, 0), (-2, 0)}
            self.takeMoves = {(-1, -1), (-1, 1)}
        else: # self.color == "black"
            if moved:
                self.posMoves = {(1, 0)}
            else:
                self.posMoves = {(1, 0), (2, 0)}
            self.takeMoves = {(1, -1), (1, 1)}
        
        self.value = 1

    def __repr__(self):
        return f"P"

# Rook class (subclass of ChessPiece)
class Rook(ChessPiece):
    def __init__(self, row, col, color, moved = False, posMoves = set(), takeMoves = set()):
        super().__init__(row, col, color, moved, posMoves, takeMoves)

        vertMoves = {(0, i) for i in range(-7,8) if i != 0}
        horMoves = {(i, 0) for i in range(-7,8) if i != 0}
        self.posMoves = set.union(horMoves, vertMoves)
        self.takeMoves = self.posMoves

        self.value = 5
    
    def __repr__(self):
        return f"R"

# Bishop class (subclass of ChessPiece)
class Bishop(ChessPiece):
    def __init__(self, row, col, color, moved = False, posMoves = set(), takeMoves = set()):
        super().__init__(row, col, color, moved, posMoves, takeMoves)

        neMoves = {(-i, i) for i in range(1,8)}
        seMoves = {(i, i) for i in range(1,8)}
        nwMoves = {(-i, -i) for i in range(1,8)}
        swMoves = {(i, -i) for i in range(1,8)}
        self.posMoves = set.union(neMoves, seMoves, nwMoves, swMoves)
        self.takeMoves = self.posMoves

        self.value = 3

    def __repr__(self):
        return f"B"

# Knight class (subclass of ChessPiece)
class Knight(ChessPiece):
    moves = set()
    for drow in {-2, -1, 1, 2}:
            for dcol in {-2, -1, 1, 2}:
                if abs(drow) == abs(dcol):
                    continue
                moves.add((drow, dcol))

    def __init__(self, row, col, color, moved = False, posMoves = set(), takeMoves = set()):
        super().__init__(row, col, color, moved, posMoves, takeMoves)

        for drow in {-2, -1, 1, 2}:
            for dcol in {-2, -1, 1, 2}:
                if abs(drow) == abs(dcol):
                    continue
                self.posMoves.add((drow, dcol))
        self.takeMoves = self.posMoves

        self.value = 3

    def __repr__(self):
        return f"N"

# King class (subclass of ChessPiece)
class King(ChessPiece):
    castleMoves = {(0, -2), (0, 2)}

    def __init__(self, row, col, color, moved = False, posMoves = set(), takeMoves = set()):
        super().__init__(row, col, color, moved, posMoves, takeMoves)

        if self.posMoves == set():
            for r in {-1, 0, 1}:
                for c in {-1, 0, 1}:
                    if (r, c) != (0, 0):
                        self.posMoves.add((r, c))

        if moved == False:
            self.posMoves = self.posMoves.union(King.castleMoves)

        if self.takeMoves == set():
            for r in {-1, 0, 1}:
                for c in {-1, 0, 1}:
                    if (r, c) != (0, 0):
                        self.takeMoves.add((r, c))

        self.value = 50

    def __repr__(self):
        return f"K"

# Queen class (subclass of ChessPiece)
class Queen(ChessPiece):
    def __init__(self, row, col, color, moved = False, posMoves = set(), takeMoves = set()):
        super().__init__(row, col, color, moved, posMoves, takeMoves)

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
        return f"Q"

#################################################
# HOME SCREEN
#################################################

def homeScreenMode_mouseMoved(app, event):
    x, y = event.x, event.y
    app.twoPlayerButtonColor = app.normalButtonColor
    app.aiModeButtonColor = app.normalButtonColor
    # if hovering inside 2 player button
    if (x >= (app.twoPlayerButtonX - app.buttonWidth) 
        and x <= (app.twoPlayerButtonX + app.buttonWidth)
        and y >= (app.gameModeButtonY - app.buttonHeight) 
        and y <= (app.gameModeButtonY + app.buttonHeight)):
        app.twoPlayerButtonColor = app.hoverColor
    # if hovering inside AI mode button
    elif (x >= (app.aiModeButtonX - app.buttonWidth) 
          and x <= (app.aiModeButtonX + app.buttonWidth)
          and y >= (app.gameModeButtonY - app.buttonHeight) 
          and y <= (app.gameModeButtonY + app.buttonHeight)):
          app.aiModeButtonColor = app.hoverColor        

# mouse pressed function responsible for home screen functionalities
def homeScreenMode_mousePressed(app, event):
    x, y = event.x, event.y
    # if clicked inside 2 player button
    if (x >= (app.twoPlayerButtonX - app.buttonWidth) 
        and x <= (app.twoPlayerButtonX + app.buttonWidth)
        and y >= (app.gameModeButtonY - app.buttonHeight) 
        and y <= (app.gameModeButtonY + app.buttonHeight)):
        app.mode = "twoPlayer"
    # clicked inside AI mode button
    elif (x >= (app.aiModeButtonX - app.buttonWidth) 
          and x <= (app.aiModeButtonX + app.buttonWidth)
          and y >= (app.gameModeButtonY - app.buttonHeight) 
          and y <= (app.gameModeButtonY + app.buttonHeight)):
          app.mode = "aiMode"
    
# draws home screen images and buttons
def homeScreenMode_drawScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height,
                            fill = "tan")
    canvas.create_text(app.width / 2, app.chessAITextY,
                       text = "Chess AI", font = (app.font, 70))
    canvas.create_rectangle(app.twoPlayerButtonX - app.buttonWidth, 
                            app.gameModeButtonY - app.buttonHeight,
                            app.twoPlayerButtonX + app.buttonWidth,
                            app.gameModeButtonY + app.buttonHeight,
                            width = app.buttonOutlineWidth, fill = app.twoPlayerButtonColor)
    canvas.create_text(app.twoPlayerButtonX, app.gameModeButtonY,
                       text = "Two Players", fill = "black",
                       font = (app.font,  20))
    canvas.create_rectangle(app.aiModeButtonX - app.buttonWidth, 
                            app.gameModeButtonY - app.buttonHeight,
                            app.aiModeButtonX + app.buttonWidth,
                            app.gameModeButtonY + app.buttonHeight,
                            width = app.buttonOutlineWidth, fill = app.aiModeButtonColor)
    canvas.create_text(app.aiModeButtonX, app.gameModeButtonY,
                       text = "AI Mode", fill = "black",
                       font = (app.font,  20))

def homeScreenMode_keyPressed(app, event):
    key = event.key
    if key == "g":
        if app.fancyGraphics == True:
            app.font = app.normalFont
        else:
            app.font = app.fancyFont
        app.fancyGraphics = not app.fancyGraphics
            
# draw all home screen features
def homeScreenMode_redrawAll(app, canvas):
    homeScreenMode_drawScreen(app, canvas)
    if app.fancyGraphics == True:
        canvas.create_image(125, 450, image= ImageTk.PhotoImage(app.frogImg))
        canvas.create_text(app.width / 2, app.height * (3/4), text = "graphic design is my passion",
                        font = (app.font,  25))
    

#################################################
# AI MODE
#################################################

########################
# SYSTEM FUNCTIONS
######################## 

# timer fired function
def aiMode_timerFired(app):
    if app.gameOver or app.paused:
        return
    # tests to see if it's computer's turn
    if app.playerToMoveIdx % 2 == 1:
        gameBoardCopy = copyGameBoard(app, app.gameBoard)
        # whiteCopy = copyPieces(app, app.whitePieces)
        # blackCopy = copyPieces(app, app.blackPieces)
        bestPiece, bestMove = aiMode_getMinimaxBestMove(app, app.whitePieces.copy(), 
                                                app.blackPieces.copy(),
                                                gameBoardCopy)
        app.activePiece = bestPiece
        row, col = bestMove[0], bestMove[1]
        if isinstance(app.gameBoard[row][col], int):
            makeMove(app, row, col)
        else: # take move
            takePiece(app, row, col)

def aiMode_mouseMoved(app, event):    
    x, y = event.x, event.y
    app.resumeButtonColor = app.normalButtonColor
    app.quitButtonColor = app.normalButtonColor
    app.pauseButtonColor = app.normalButtonColor
    app.okButtonColor = app.normalButtonColor
    if app.paused:
        # if hovering inside resume button
        if (x > app.resumeX - app.pauseButtonsWidth
            and x < app.resumeX + app.pauseButtonsWidth
            and y > app.resumeY - app.pauseButtonsHeight
            and y < app.resumeY + app.pauseButtonsHeight):
            app.resumeButtonColor = app.hoverColor
        # if hovering inside quit button
        elif (x > app.quitX - app.pauseButtonsWidth
              and x < app.quitX + app.pauseButtonsWidth
              and y > app.quitY - app.pauseButtonsHeight
              and y < app.quitY + app.pauseButtonsHeight):
            app.quitButtonColor = app.hoverColor
    elif app.gameOver:
        if (x > app.okButtonX - app.okButtonWidth and 
            x < app.okButtonX + app.okButtonWidth and
            y > app.okButtonY - app.okButtonHeight and 
            y < app.okButtonY + app.okButtonHeight):
            app.okButtonColor = app.hoverColor
    elif (x > app.pauseX and y > app.pauseY 
        and x < app.pauseX + app.pauseWidth 
        and y < app.pauseY + app.pauseWidth):
        app.pauseButtonColor = app.hoverColor


def aiMode_keyPressed(app, event):
    key = event.key
    if key == "g":
        if app.fancyGraphics == True:
            app.font = app.normalFont
        else:
            app.font = app.fancyFont
        app.fancyGraphics = not app.fancyGraphics
    keyPressed(app, event)

# mouse pressed function responsible for moving pieces and game functionalities
def aiMode_mousePressed(app, event):
    x, y = event.x, event.y

    # only responds to game over buttons
    if app.gameOver:
        if (x > app.okButtonX - app.okButtonWidth and 
            x < app.okButtonX + app.okButtonWidth and
            y > app.okButtonY - app.okButtonHeight and 
            y < app.okButtonY + app.okButtonHeight):
            app.mode = "homeScreenMode"
            restartGame(app)
        return
    
    # only responds to pause menu buttons
    if app.paused: 
        # quit pressed
        if (x > app.quitX - app.pauseButtonsWidth
           and x < app.quitX + app.pauseButtonsWidth
           and y > app.quitY - app.pauseButtonsHeight
           and y < app.quitY + app.pauseButtonsHeight):
           app.paused = False
           app.mode = "homeScreenMode"
           restartGame(app)
        # resume pressed
        elif (x > app.resumeX - app.pauseButtonsWidth
              and x < app.resumeX + app.pauseButtonsWidth
              and y > app.resumeY - app.pauseButtonsHeight
              and y < app.resumeY + app.pauseButtonsHeight):
            app.paused = False
        return
    
    # assuming player is always white, stops mouse pressed if it's not white's turn
    if app.playerToMoveIdx % 2 != 0:
        return

    # if x, y within pause button bounds
    if (x > app.pauseX and y > app.pauseY 
        and x < app.pauseX + app.pauseWidth 
        and y < app.pauseY + app.pauseWidth):
        app.paused = True
        return
    
    if inBoard(app, x, y) == False:
        return

    row, col = getRowCol(app, x, y)
    currPlayerColor = app.players[app.playerToMoveIdx % 2]

    clickedSquare = app.gameBoard[row][col]

    # user clicked on a chess piece
    if isinstance(clickedSquare, ChessPiece):
        if app.activePiece == None and currPlayerColor == clickedSquare.color:
            if (app.gameBoard[row][col].color != 
                app.players[app.playerToMoveIdx % 2]):
                return
            app.activePiece = clickedSquare
            app.validMoves = getValidMoves(app, app.activePiece)
            app.validTakes = getValidTakes(app, app.activePiece)
        elif app.activePiece == None and currPlayerColor != clickedSquare.color:
            return
        
        # app.activePiece is not None
        else:
            if app.activePiece.color == clickedSquare.color:
                app.activePiece = clickedSquare
                app.validMoves = getValidMoves(app, app.activePiece)
                app.validTakes = getValidTakes(app, app.activePiece)
            else: # pieces are different colors
                takePiece(app, row, col)

    else: # user clicked on an empty space
        if app.activePiece != None:
            makeMove(app, row, col)

########################
# AI HELPER FUNCTIONS
######################## 

def aiMode_isStalemate(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn):
    color = aiMode_getPlayerColor(isMaxPlayerTurn)
    king = eval(f"{color}Pieces['K'].pop()")
    eval(f"{color}Pieces['K'].add(king)")
    numPieces = getNumberOfPieces(app, eval(f"{color}Pieces"))
    kingMoves = aiMode_getValidMoves(app, whitePieces, blackPieces, gameBoard, king)
    kingTakes = aiMode_getValidTakes(app, whitePieces, blackPieces, gameBoard, king)
    totalPosMoves = kingMoves.union(kingTakes)
    if numPieces == 1 and len(totalPosMoves) == 0:
        return True
    return False

# returns True if proposed move is a valid move for piece
def aiMode_isValidMove(app, whitePieces, blackPieces, gameBoard, piece, moveLoc):
    moveRow, moveCol = moveLoc[0], moveLoc[1]

    if rowColInBounds(app, moveRow, moveCol) == False:
        return False

    moveSquare = gameBoard[moveRow][moveCol]
    if (isinstance(moveSquare, ChessPiece)):
        return False

    currRow, currCol = piece.row, piece.col
    dRow, dCol = (moveRow - currRow), (moveCol - currCol)

    if ((dRow, dCol) not in piece.posMoves
        or rowColInBounds(app, moveRow, moveCol) == False):
        return False
    kingChecked = aiMode_isChecked(app, whitePieces, blackPieces, gameBoard, piece.color == "white")
    if type(piece) == King and kingChecked and (dRow, dCol) in King.castleMoves:
        return False

    castleDCol = None
        
    if type(piece) == King and (dRow, dCol) in King.castleMoves:
        castleDCol = dCol
        rookSearchDCol = abs(castleDCol) // castleDCol
        newKingRow, newKingCol = piece.row + dRow, piece.col + dCol
        tempRow, tempCol = newKingRow, newKingCol + rookSearchDCol
        rook = None

        # find rook
        while rook == None:
            if type(gameBoard[tempRow][tempCol]) == Rook:
                rook = gameBoard[tempRow][tempCol]
                for item in eval(f"{rook.color}Pieces['R']"):
                    if (item.row, item.col) == (rook.row, rook.col):
                        return True
                        
            elif isinstance(gameBoard[tempRow][tempCol], ChessPiece):
                return False
    
            tempCol += rookSearchDCol
        
    hasNoBlockingPieces = aiMode_checkBlockingPieces(app, gameBoard, piece, moveLoc)
    isStillChecked = aiMode_attemptUndoCheck(app, whitePieces, blackPieces, gameBoard, piece, moveLoc)
    if hasNoBlockingPieces and isStillChecked:
        return True
    else:
        return False

# returns True if proposed move is a valid take move for piece
def aiMode_isValidTake(app, whitePieces, blackPieces, gameBoard, piece, moveLoc):
    takeRow, takeCol = moveLoc[0], moveLoc[1]

    if rowColInBounds(app, takeRow, takeCol) == False:
        return False

    # check if takeRow, takeCol is a ChessPiece of opposite color to piece
    takeSquare = gameBoard[takeRow][takeCol]
    if (isinstance(takeSquare, ChessPiece) == False):
        return False
    elif (isinstance(takeSquare, ChessPiece) and 
          takeSquare.color == piece.color):
        return False
    currRow, currCol = piece.row, piece.col
    dRow, dCol = (takeRow - currRow), (takeCol - currCol)

    if (dRow, dCol) not in piece.takeMoves:
        return False
    
    hasNoBlockingPieces = aiMode_checkBlockingPieces(app, gameBoard, piece, moveLoc)
    if hasNoBlockingPieces:
        isChecked = aiMode_attemptUndoCheck(app, whitePieces, blackPieces, gameBoard, piece, moveLoc)
        return hasNoBlockingPieces and isChecked
    else:
        return False

# returns new piece and board state after moving piece to moveLoc
def aiMode_makeMove(app, whitePieces, blackPieces, gameBoard, piece, moveLoc):
    oldRow, oldCol = piece.row, piece.col
    if aiMode_isValidMove(app, whitePieces, blackPieces, gameBoard, piece, moveLoc):
        row, col = moveLoc[0], moveLoc[1]
        gameBoard[oldRow][oldCol] = 0

        oldMovedState = piece.moved
        piece.moved = True

        dRow, dCol = row - piece.row, col - piece.col
        castleDCol = None
        
        if type(piece) == King and (dRow, dCol) in King.castleMoves:
            castleDCol = dCol

            rookSearchDCol = abs(castleDCol) // castleDCol
            newKingRow, newKingCol = piece.row + dRow, piece.col + dCol
            tempRow, tempCol = newKingRow, newKingCol + rookSearchDCol
            rook = None

            # find rook
            while rook == None and rowColInBounds(app, tempRow, tempCol):
                if type(gameBoard[tempRow][tempCol]) == Rook:
                    rook = gameBoard[tempRow][tempCol]
                    for item in eval(f"{rook.color}Pieces['R']"):
                        if (item.row, item.col) == (rook.row, rook.col):
                            rook = item
                            gameBoard[tempRow][tempCol] = 0
                            break
            
                tempCol += rookSearchDCol

            rookDMove = rookSearchDCol * (-1)
            eval(f"{rook.color}Pieces['R'].remove(rook)")

            rook.col = newKingCol + rookDMove
            rook.moved = True
            gameBoard[rook.row][rook.col] = rook
            eval(f"{rook.color}Pieces['R'].add(rook)")

        eval(f"{piece.color}Pieces[str(piece)].remove(piece)")

        # removes pawn double-move/castle move if piece is a pawn/king or rook respectively
        if oldMovedState != True and type(piece) == Pawn:
            if piece.color == "white":
                piece.posMoves.remove((-2, 0))
            else:
                piece.posMoves.remove((2, 0))
        elif oldMovedState != True and type(piece) == King:
            for move in King.castleMoves:
                if move in piece.posMoves:
                    piece.posMoves.remove(move)
        elif oldMovedState != True and type(piece) == Rook:
            color = piece.color
            king = eval(f"{color}Pieces['K'].pop()")
            if king.moved == False:
                dRow, dCol = piece.row - king.row, piece.col - king.col
                dRow, dCol = dRow, (abs(dCol) // dCol) * 2
                king.posMoves.remove((dRow, dCol))
            eval(f"{color}Pieces['K'].add(king)")

        piece.row, piece.col = row, col

        gameBoard[row][col] = piece
        eval(f"{piece.color}Pieces[str(piece)].add(piece)")

    return (whitePieces, blackPieces, gameBoard)

# returns new piece and board state after taking piece at takeLoc
def aiMode_takePiece(app, whitePieces, blackPieces, gameBoard, piece, takeLoc):
    oldRow, oldCol = piece.row, piece.col

    if aiMode_isValidTake(app, whitePieces, blackPieces, gameBoard, piece, takeLoc):
        row, col = takeLoc[0], takeLoc[1]
        gameBoard[oldRow][oldCol] = 0
        eval(f"{piece.color}Pieces[str(piece)].remove(piece)")

        oldMovedState = piece.moved
        piece.moved = True
        
        # removes pawn double-move/castle move if piece is a pawn/king or rook respectively
        if oldMovedState != True and type(piece) == Pawn:
            if piece.color == "white":
                piece.posMoves.remove((-2, 0))
            else:
                piece.posMoves.remove((2, 0))
        elif oldMovedState != True and type(piece) == King:
            for move in King.castleMoves:
                if move in piece.posMoves:
                    piece.posMoves.remove(move)
        elif oldMovedState != True and type(piece) == Rook:
            color = piece.color
            king = eval(f"{color}Pieces['K'].pop()")
            if king.moved == False:
                dRow, dCol = piece.row - king.row, piece.col - king.col
                dRow, dCol = dRow, (abs(dCol) // dCol) * 2
                king.posMoves.remove((dRow, dCol))
            eval(f"{color}Pieces['K'].add(king)")
            
        takenPiece = gameBoard[row][col]
        for item in eval(f"{takenPiece.color}Pieces[str(takenPiece)]"):
            if (item.row, item.col, item.moved) == (takenPiece.row, takenPiece.col, takenPiece.moved):
                takenPiece = item
        eval(f"{takenPiece.color}Pieces[str(takenPiece)].remove(takenPiece)")

        piece.row, piece.col = row, col
        gameBoard[row][col] = piece
        eval(f"{piece.color}Pieces[str(piece)].add(piece)")

    return (whitePieces, blackPieces, gameBoard)

# returns all moves for current player in minimax node state
def aiMode_getMovesFromState(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn):
    if isMaxPlayerTurn: # white's turn
        whiteMoves = set()

        for pieceType in whitePieces:
            for piece in whitePieces[pieceType]:
                for (dRow, dCol) in piece.posMoves.union(piece.takeMoves):
                    moveRow, moveCol = piece.row + dRow, piece.col + dCol
                    if (aiMode_isValidMove(app, whitePieces, blackPieces, gameBoard,
                                          piece, (moveRow, moveCol))
                        or aiMode_isValidTake(app, whitePieces, blackPieces, gameBoard,
                                              piece, (moveRow, moveCol))):
                        whiteMoves.add((piece, (moveRow, moveCol)))
        return whiteMoves
    else:
        blackMoves = set()
        for pieceType in blackPieces:
            for piece in blackPieces[pieceType]:
                for (dRow, dCol) in piece.posMoves.union(piece.takeMoves):
                    moveRow, moveCol = piece.row + dRow, piece.col + dCol
                    isValidMove = aiMode_isValidMove(app, whitePieces, blackPieces, gameBoard,
                                          piece, (moveRow, moveCol))
                    isValidTake = aiMode_isValidTake(app, whitePieces, blackPieces, gameBoard,
                                              piece, (moveRow, moveCol))

                    if (isValidMove or isValidTake):
                        blackMoves.add((piece, (moveRow, moveCol)))
        return blackMoves

# return True if there are pieces blocking piece from moveLoc in minimax node state
def aiMode_checkBlockingPieces(app, gameBoard, piece, moveLoc):
    moveRow, moveCol = moveLoc[0], moveLoc[1]
    currRow, currCol = piece.row, piece.col 
    dRow, dCol = (moveRow - currRow), (moveCol - currCol)

    if type(piece) != Knight:
        dist = math.sqrt(dRow ** 2 + dCol ** 2)
        unitDRow, unitDCol = math.ceil(dRow / dist), math.ceil(dCol / dist)
        if dRow / dist < 0:
            unitDRow = -math.ceil(abs(dRow/dist))
        if dCol / dist < 0:
            unitDCol = -math.ceil(abs(dCol/dist))
        tempRow, tempCol =  currRow + unitDRow, currCol + unitDCol

        while (tempRow != moveRow) or (tempCol != moveCol):
            tempPiece = gameBoard[tempRow][tempCol]
            if (isinstance(tempPiece, ChessPiece) and
                tempPiece.color == piece.color):
                return False
            elif (isinstance(tempPiece, ChessPiece) and
                  tempPiece.color != piece.color and
                  (tempRow != moveRow or tempCol != moveCol)):
                return False

            tempRow += unitDRow
            tempCol += unitDCol
    return True

# returns True if move does not result in check in minimax node state
def aiMode_attemptUndoCheck(app, whitePieces, blackPieces, gameBoard, piece, moveLoc):
    tempRow, tempCol = moveLoc[0], moveLoc[1]
    tempBoardSq = gameBoard[tempRow][tempCol]
    if isinstance(tempBoardSq, ChessPiece) and tempBoardSq.color == piece.color:
        return False

    oppColor = getOpposingColor(app, piece)
    color = piece.color
    pieceCopy = piece.copy()
    whitePiecesCopy = copyPieces(app, whitePieces)
    blackPiecesCopy = copyPieces(app, blackPieces)
    gameBoardCopy = copyGameBoard(app, gameBoard)

    dRow, dCol = tempRow - piece.row, tempCol - piece.col

    if isinstance(tempBoardSq, ChessPiece) and (tempBoardSq.color != piece.color):
        oppColorPiece = tempBoardSq.copy()

        if pieceCopy.hasTake(dRow, dCol):
            for item in eval(f"{oppColor}PiecesCopy[str(oppColorPiece)]"):
                if (item.row, item.col) == (oppColorPiece.row, oppColorPiece.col):
                    oppColorPiece = item
                    eval(f"{oppColor}PiecesCopy[str(oppColorPiece)].remove(oppColorPiece)")
                    break

            for item in eval(f"{color}PiecesCopy[str(piece)]"):
                if (item.row, item.col) == (piece.row, piece.col):
                    pieceCopy = item
                    eval(f"{color}PiecesCopy[str(piece)].remove(pieceCopy)")
                    break

            gameBoardCopy[tempRow][tempCol] = piece
            gameBoardCopy[piece.row][piece.col] = 0

            pieceCopy.row, pieceCopy.col = tempRow, tempCol
            eval(f"{color}PiecesCopy[str(pieceCopy)].add(pieceCopy)")

            result = None
            if aiMode_isChecked(app, whitePiecesCopy, blackPiecesCopy, 
                                gameBoardCopy, piece.color == "white"):
                result = False
            else:
                result = True
            return result
    else:
        if pieceCopy.hasMove(dRow, dCol): 
            gameBoardCopy[tempRow][tempCol] = piece
            gameBoardCopy[piece.row][piece.col] = 0

            for item in eval(f"{pieceCopy.color}PiecesCopy[str(pieceCopy)]"):
                if (item.row, item.col, item.moved) == (pieceCopy.row, pieceCopy.col, pieceCopy.moved):
                    pieceCopy = item
                    eval(f"{color}PiecesCopy[str(piece)].remove(pieceCopy)")
                    break

            pieceCopy.row, pieceCopy.col = tempRow, tempCol
            eval(f"{color}PiecesCopy[str(pieceCopy)].add(pieceCopy)")
            result = None
            if aiMode_isChecked(app, whitePiecesCopy, blackPiecesCopy, 
                                gameBoardCopy, pieceCopy.color == "white"):
                result = False
            else:
                result = True

            return result
    return False

# returns True if color is checked in minimax node state
def aiMode_isChecked(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn):
    color = aiMode_getPlayerColor(isMaxPlayerTurn)
    king = eval(f"{color}Pieces['K'].pop()")
    eval(f"{color}Pieces['K'].add(king)")
    oppColor = None
    if color == "white":
        oppColor = "black"
    else:
        oppColor = "white"

    for knight in eval(f"{oppColor}Pieces['N']"):
        (dRow, dCol) = (king.row - knight.row, king.col - knight.col)
        if (dRow, dCol) in knight.takeMoves:
            return True
    
    for key in {'P','B','R','Q','K'}:
        for piece in eval(f"{oppColor}Pieces[key]"):
            (dRow, dCol) = (king.row - piece.row, king.col - piece.col)
            if ((dRow, dCol) in piece.takeMoves and 
                aiMode_checkBlockingPieces(app, gameBoard, piece, (king.row, king.col))):
                return True
    return False

# returns set of valid moves for given piece in minimax node state
def aiMode_getValidMoves(app, whitePieces, blackPieces, gameBoard, piece):
    posMoves = piece.posMoves
    currRow, currCol = piece.row, piece.col
    validMoves = set()
    for (dRow, dCol) in posMoves:
        moveRow, moveCol = currRow + dRow, currCol + dCol
        moveLoc = (moveRow, moveCol)
        if (aiMode_isValidTake(app, whitePieces, blackPieces, 
                               gameBoard, piece, moveLoc)):
            validMoves.add((moveRow, moveCol))
    return validMoves

# returns set of valid take moves for given piece in minimax node state
def aiMode_getValidTakes(app, whitePieces, blackPieces, gameBoard, piece):
    posTakes = piece.takeMoves
    currRow, currCol = piece.row, piece.col
    validTakes = set()
    for (dRow, dCol) in posTakes:
        moveRow, moveCol = currRow + dRow, currCol + dCol
        moveLoc = (moveRow, moveCol)
        if (aiMode_isValidTake(app, whitePieces, blackPieces, 
                               gameBoard, piece, moveLoc)):
            validTakes.add((moveRow, moveCol))
    return validTakes

# returns True if the active player is mated in minimax node state
def aiMode_isMated(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn):
    color = aiMode_getPlayerColor(isMaxPlayerTurn)

    for pieceType in eval(f"{color}Pieces"):
        for piece in eval(f"{color}Pieces[pieceType]"):
            validMoves = aiMode_getValidMoves(app, whitePieces, blackPieces,
                                              gameBoard, piece)
            validTakes = aiMode_getValidTakes(app, whitePieces, blackPieces,
                                              gameBoard, piece)
            if (validMoves != set() or validTakes != set()):
                return False
    return True

# returns current player color depending on isMaxPlayerTurn value
def aiMode_getPlayerColor(isMaxPlayerTurn):
    if isMaxPlayerTurn:
        return "white"
    else:
        return "black"

########################
# AI FUNCTIONS
######################## 

# wrapper function for minimax function, returns best move for AI
def aiMode_getMinimaxBestMove(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn = False):
    bestPiece = None
    bestMove = None
    minVal = None
    posMoves = aiMode_getMovesFromState(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn)
    print("\n\n")
    for (piece, moveLoc) in posMoves:
        moveRow, moveCol = moveLoc[0], moveLoc[1]
        depth = 1
        pieceCopy = None
        whiteCopy = dict()
        for key in whitePieces:
            whiteCopy[key] = whiteCopy.get(key, set())
            for item in whitePieces[key]:
                itemCopy = item.copy()
                whiteCopy[key].add(itemCopy)
                if (item.color, item.row, item.col, item.moved) == (piece.color, piece.row, piece.col, piece.moved):
                    pieceCopy = itemCopy

        blackCopy = dict()
        for key in blackPieces:
            blackCopy[key] = blackCopy.get(key, set())
            for item in blackPieces[key]:
                itemCopy = item.copy()
                blackCopy[key].add(itemCopy)
                if (item.color, item.row, item.col, item.moved) == (piece.color, piece.row, piece.col, item.moved):
                    pieceCopy = itemCopy

        gameBoardCopy = copyGameBoard(app, gameBoard)

        if aiMode_isValidMove(app, whiteCopy, blackCopy, gameBoardCopy,
                              pieceCopy, moveLoc):
            aiMode_makeMove(app, whiteCopy, blackCopy, gameBoardCopy,
                            pieceCopy, moveLoc)
        else: # isValidTake == True
            aiMode_takePiece(app, whiteCopy, blackCopy, gameBoardCopy,
                             pieceCopy, moveLoc)
        moveVal = aiMode_minimax(app, whiteCopy, blackCopy, gameBoardCopy, depth, True)
        if bestMove == None or moveVal < minVal:
            minVal = moveVal
            bestPiece = piece
            bestMove = (moveRow, moveCol)
            print(bestPiece, bestMove, minVal)
    return bestPiece, bestMove

# general pseudocode structure: https://www.javatpoint.com/mini-max-algorithm-in-ai
# backtracking minimax AI for computer player (black)
# assumed that maximizing player is white
def aiMode_minimax(app, whitePieces, blackPieces, gameBoard, depth, isMaxPlayerTurn):
    isChecked = aiMode_isChecked(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn)
    isMated = False
    if isChecked:
        isMated = aiMode_isMated(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn)

    if depth == 0 or isMated:
        posVal = 0
        playerColor = aiMode_getPlayerColor(isMaxPlayerTurn)

        # add "value bonuses" if the move results in a check or mate
        if isMated and playerColor == 'black':
            posVal += 50
        elif isChecked and playerColor == 'black':
            posVal += 15
        elif isMated and playerColor == "white":
            posVal -= 50
        elif isChecked and playerColor == "white":
            posVal -= 15

        for pieceType in blackPieces:
            for item in blackPieces[pieceType]:
                posVal -= item.value
        
        for pieceType in whitePieces:
            for item in whitePieces[pieceType]:
                posVal += item.value
       
        return posVal
    # elif aiMode_isStalemate(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn):
    #     if isMaxPlayerTurn:
    #         return 100000
    #     else:
    #         return -100000
    posMovesFromState = aiMode_getMovesFromState(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn)
    if isMaxPlayerTurn: 
        maxEval = -100000  
        for (piece, moveLoc) in posMovesFromState:
            whiteCopy = copyPieces(app, whitePieces)
            blackCopy = copyPieces(app, blackPieces)
            pieceCopy = None

            whitePieces[str(piece)].remove(piece)
            pieceCopy = piece.copy()
            whiteCopy[str(piece)] = {pieceCopy}
            whitePieces[str(piece)].add(piece)
        
            gameBoardCopy = copyGameBoard(app, gameBoard)

            isValidMove = aiMode_isValidMove(app, whiteCopy, blackCopy, 
                                             gameBoardCopy, pieceCopy, moveLoc)
            isValidTake = aiMode_isValidTake(app, whiteCopy, blackCopy, 
                                             gameBoardCopy, pieceCopy, moveLoc)
            
            if isValidMove:
                newState = aiMode_makeMove(app, whiteCopy, blackCopy, 
                                           gameBoardCopy, pieceCopy, moveLoc)
                
            elif isValidTake:
                newState = aiMode_takePiece(app, whiteCopy, blackCopy, 
                                           gameBoardCopy, pieceCopy, moveLoc)
            newWhitePieces, newBlackPieces, newGameBoard = newState[0], newState[1], newState[2]
            eval = aiMode_minimax(app, newWhitePieces, newBlackPieces, newGameBoard, 
                                    depth - 1, not isMaxPlayerTurn)  
            maxEval = max(maxEval, eval)

        return maxEval
        
    else:    
        minEval = 100000   
        for (piece, moveLoc) in posMovesFromState:
            whiteCopy = copyPieces(app, whitePieces)
            blackCopy = copyPieces(app, blackPieces)
            pieceCopy = None

            blackPieces[str(piece)].remove(piece)
            pieceCopy = piece.copy()
            blackCopy[str(pieceCopy)] = {pieceCopy}
            blackPieces[str(piece)].add(piece)

            gameBoardCopy = copyGameBoard(app, gameBoard)

            isValidMove = aiMode_isValidMove(app, whiteCopy, blackCopy, 
                                             gameBoardCopy, pieceCopy, moveLoc)
            isValidTake = aiMode_isValidTake(app, whiteCopy, blackCopy, 
                                             gameBoardCopy, pieceCopy, moveLoc)

            if isValidMove or isValidTake:
                newState = aiMode_makeMove(app, whiteCopy, blackCopy, 
                                           gameBoardCopy, pieceCopy, moveLoc)

                newWhitePieces, newBlackPieces, newGameBoard = newState[0], newState[1], newState[2]
                eval = aiMode_minimax(app, newWhitePieces, newBlackPieces, newGameBoard, 
                                      depth - 1, not isMaxPlayerTurn)  
                minEval = min(minEval, eval)    

        return minEval 

########################
# DRAW FUNCTIONS
######################## 

# draws player labels for aiMode
def aiMode_drawPlayerLabels(app, canvas):
    canvas.create_text(app.width / 2, app.height - app.margin / 2,
                        text = "Player", fill = "black", font = (app.font,  20))
    canvas.create_text(app.width / 2, app.margin / 2,
                        text = "Computer", fill = "black", font = (app.font,  20))

# draws all components of aiMode
def aiMode_redrawAll(app, canvas):
    if app.gameOver:
        drawGameOverScreen(app, canvas)
        return
    elif app.paused:
        drawPauseMenu(app, canvas)
        return

    drawBoard(app, canvas)
    drawPieces(app, canvas)
    drawTakenPieces(app, canvas)
    aiMode_drawPlayerLabels(app, canvas)
    drawPause(app, canvas)

    if app.activePiece != None:
        drawMoves(app, canvas)
    if app.checked != None:
        drawCheck(app, canvas)

#################################################
# GAME MODE
#################################################

# timer fired function for twoPlayer mode
def twoPlayer_timerFired(app):
    # maybe use to display "time-passed" clock for each player
    pass

def twoPlayer_mouseMoved(app, event):    
    x, y = event.x, event.y
    app.resumeButtonColor = app.normalButtonColor
    app.quitButtonColor = app.normalButtonColor
    app.pauseButtonColor = app.normalButtonColor
    app.okButtonColor = app.normalButtonColor
    if app.paused:
        # if hovering inside resume button
        if (x > app.resumeX - app.pauseButtonsWidth
            and x < app.resumeX + app.pauseButtonsWidth
            and y > app.resumeY - app.pauseButtonsHeight
            and y < app.resumeY + app.pauseButtonsHeight):
            app.resumeButtonColor = app.hoverColor
        # if hovering inside quit button
        elif (x > app.quitX - app.pauseButtonsWidth
              and x < app.quitX + app.pauseButtonsWidth
              and y > app.quitY - app.pauseButtonsHeight
              and y < app.quitY + app.pauseButtonsHeight):
            app.quitButtonColor = app.hoverColor
    elif app.gameOver:
        if (x > app.okButtonX - app.okButtonWidth and 
            x < app.okButtonX + app.okButtonWidth and
            y > app.okButtonY - app.okButtonHeight and 
            y < app.okButtonY + app.okButtonHeight):
            app.okButtonColor = app.hoverColor
    elif (x > app.pauseX and y > app.pauseY 
        and x < app.pauseX + app.pauseWidth 
        and y < app.pauseY + app.pauseWidth):
        app.pauseButtonColor = app.hoverColor
########################
# LOGIC FUNCTIONS
######################## 

# returns True if move is a valid move                    
def isValidMove(app, moveRow, moveCol, piece):
    if rowColInBounds(app, moveRow, moveCol) == False:
        return False

    moveSquare = app.gameBoard[moveRow][moveCol]
    if (isinstance(moveSquare, ChessPiece)):
        return False

    currRow, currCol = piece.row, piece.col
    dRow, dCol = (moveRow - currRow), (moveCol - currCol)

    if ((dRow, dCol) not in piece.posMoves 
        or rowColInBounds(app, moveRow, moveCol) == False):
        return False
    
    # king can not castle if checked
    kingChecked = isChecked(app, piece.color)
    if type(piece) == King and kingChecked and (dRow, dCol) in King.castleMoves:
        return False
    
    # if king attempting castle move, check if it's valid for rook and king
    castleDCol = None
        
    if type(piece) == King and (dRow, dCol) in King.castleMoves:
        castleDCol = dCol
        rookSearchDCol = abs(castleDCol) // castleDCol
        newKingRow, newKingCol = piece.row + dRow, piece.col + dCol
        tempRow, tempCol = newKingRow, newKingCol + rookSearchDCol
        rook = None

        # find rook
        while rook == None:
            if type(app.gameBoard[tempRow][tempCol]) == Rook:
                rook = app.gameBoard[tempRow][tempCol]
                for item in eval(f"app.{rook.color}Pieces['R']"):
                    if (item.row, item.col) == (rook.row, rook.col):
                        return True
                        
            elif isinstance(app.gameBoard[tempRow][tempCol], ChessPiece):
                return False
    
            tempCol += rookSearchDCol

    hasNoBlockingPieces = checkBlockingPieces(app, moveRow, moveCol, piece)
    isStillChecked = attemptUndoCheck(app, moveRow, moveCol, piece)
    if hasNoBlockingPieces and isStillChecked:
        return True
    else:
        return False

# returns True if takeRow, takeCol is a valid take move for piece
def isValidTake(app, takeRow, takeCol, piece):
    if rowColInBounds(app, takeRow, takeCol) == False:
        return False

    takeSquare = app.gameBoard[takeRow][takeCol]
    
    if (isinstance(takeSquare, ChessPiece) == False):
        return False

    if (isinstance(takeSquare, ChessPiece) and 
          takeSquare.color == piece.color):
        return False

    currRow, currCol = piece.row, piece.col
    dRow, dCol = (takeRow - currRow), (takeCol - currCol)

    if ((dRow, dCol) not in piece.takeMoves 
        or rowColInBounds(app, takeRow, takeCol) == False):
        return False

    hasNoBlockingPieces = checkBlockingPieces(app, takeRow, takeCol, piece)
    isChecked = attemptUndoCheck(app, takeRow, takeCol, piece)
    if hasNoBlockingPieces and isChecked:
        return True
    else:
        return False

# return True if there are pieces blocking piece from moveRow, moveCol
def checkBlockingPieces(app, moveRow, moveCol, piece):
    currRow, currCol = piece.row, piece.col
    dRow, dCol = (moveRow - currRow), (moveCol - currCol)
    if type(piece) != Knight:
        dist = math.sqrt(dRow ** 2 + dCol ** 2)
        unitDRow, unitDCol = math.ceil(dRow / dist), math.ceil(dCol / dist)
        
        if dRow / dist < 0:
            unitDRow = -math.ceil(abs(dRow/dist))
        if dCol / dist < 0:
            unitDCol = -math.ceil(abs(dCol/dist))
        tempRow, tempCol =  currRow + unitDRow, currCol + unitDCol

        while (tempRow != moveRow) or (tempCol != moveCol):
            tempPiece = app.gameBoard[tempRow][tempCol]
            if (isinstance(tempPiece, ChessPiece) and
                tempPiece.color == piece.color):
                return False
            # if piece is diff color & not the desired moveRow, moveCol location
            elif (isinstance(tempPiece, ChessPiece) and
                  tempPiece.color != piece.color and
                  (tempRow != moveRow or tempCol != moveCol)):
                return False
            tempRow += unitDRow
            tempCol += unitDCol

    return True

# if move is valid, make move and adjust set of same-color pieces accordingly
def makeMove(app, row, col):
    oldRow, oldCol = app.activePiece.row, app.activePiece.col

    if (isValidMove(app, row, col, app.activePiece)):
        # remove piece from gameBoard/app.colorPieces and modify its values
        app.gameBoard[oldRow][oldCol] = 0
        oldMovedState = app.activePiece.moved
        app.activePiece.moved = True

        # checks if move is a castling move
        dRow, dCol = row - app.activePiece.row, col - app.activePiece.col
        castleDCol = None

        if type(app.activePiece) == King and (dRow, dCol) in King.castleMoves:
            castleDCol = dCol

            rookSearchDCol = abs(castleDCol) // castleDCol
            newKingRow, newKingCol = app.activePiece.row + dRow, app.activePiece.col + dCol
            tempRow, tempCol = newKingRow, newKingCol + rookSearchDCol
            rook = None

            # find rook
            while rook == None and rowColInBounds(app, tempRow, tempCol):
                if type(app.gameBoard[tempRow][tempCol]) == Rook:
                    rook = app.gameBoard[tempRow][tempCol]
                    for item in eval(f"app.{rook.color}Pieces['R']"):
                        if (item.row, item.col) == (rook.row, rook.col):
                            rook = item
                            app.gameBoard[tempRow][tempCol] = 0
                            break
                tempCol += rookSearchDCol

            rookDMove = rookSearchDCol * (-1)
            eval(f"app.{rook.color}Pieces['R'].remove(rook)")

            rook.col = newKingCol + rookDMove
            rook.moved = True
            app.gameBoard[rook.row][rook.col] = rook
            eval(f"app.{rook.color}Pieces['R'].add(rook)")

        eval(f"app.{app.activePiece.color}Pieces[str(app.activePiece)].remove(app.activePiece)")

        # removes pawn double-move/castle move if piece is a pawn/king respectively
        if oldMovedState != True and type(app.activePiece) == Pawn:
            if app.activePiece.color == "white":
                app.activePiece.posMoves.remove((-2, 0))
            else:
                app.activePiece.posMoves.remove((2, 0))
        elif oldMovedState != True and type(app.activePiece) == King:
            for move in King.castleMoves:
                if move in app.activePiece.posMoves:
                    app.activePiece.posMoves.remove(move)
        elif oldMovedState != True and type(app.activePiece) == Rook:
            color = app.activePiece.color
            king = eval(f"app.{color}Pieces['K'].pop()")
            if king.moved == False:
                dRow, dCol = app.activePiece.row - king.row, app.activePiece.col - king.col
                dRow, dCol = dRow, (abs(dCol) // dCol) * 2
                king.posMoves.remove((dRow, dCol))
            eval(f"app.{color}Pieces['K'].add(king)")

        app.activePiece.row, app.activePiece.col = row, col

        # add modified piece back to gameBoard and app.colorPieces
        app.gameBoard[row][col] = app.activePiece
        eval(f"app.{app.activePiece.color}Pieces[str(app.activePiece)].add(app.activePiece)")

        oppColor = getOpposingColor(app, app.activePiece)
        if isChecked(app, oppColor):
            app.checked = oppColor
            if isMated(app, oppColor):
                app.gameOver = True
                return
        else:
            app.checked = None

        app.activePiece = None
        app.validMoves = set()
        app.validTakes = set()
        app.playerToMoveIdx += 1 

# if take is valid, take + remove piece from pieces and gameBoard
def takePiece(app, row, col):
    oldRow, oldCol = app.activePiece.row, app.activePiece.col

    if (isValidTake(app, row, col, app.activePiece)):
        app.gameBoard[oldRow][oldCol] = 0
        eval(f"app.{app.activePiece.color}Pieces[str(app.activePiece)].remove(app.activePiece)")

        oldMovedState = app.activePiece.moved
        app.activePiece.row, app.activePiece.col = row, col
        app.activePiece.moved = True
        if oldMovedState != True and type(app.activePiece) == Pawn:
            if app.activePiece.color == "white":
                app.activePiece.posMoves.remove((-2, 0))
            else:
                app.activePiece.posMoves.remove((2, 0))
        elif oldMovedState != True and type(app.activePiece) == King:
            for move in King.castleMoves:
                if move in app.activePiece.posMoves:
                    app.activePiece.posMoves.remove(move)
        elif oldMovedState != True and type(app.activePiece) == Rook:
            color = app.activePiece.color
            king = eval(f"app.{color}Pieces['K'].pop()")
            if king.moved == False:
                dRow, dCol = app.activePiece.row - king.row, app.activePiece.col - king.col
                dRow, dCol = dRow, (abs(dCol) // dCol) * 2
                king.posMoves.remove((dRow, dCol))
            eval(f"app.{color}Pieces['K'].add(king)")

        takenPiece = app.gameBoard[row][col]
        eval(f"app.{takenPiece.color}Pieces[str(takenPiece)].remove(takenPiece)")
        eval(f"app.{takenPiece.color}TakenPieces[str(takenPiece)].add(takenPiece)")

        app.gameBoard[row][col] = app.activePiece
        eval(f"app.{app.activePiece.color}Pieces[str(app.activePiece)].add(app.activePiece)")

        oppColor = getOpposingColor(app, app.activePiece)
        if isChecked(app, oppColor):
            app.checked = oppColor
            if isMated(app, oppColor):
                app.gameOver = True
                return
        else:
            app.checked = None

        app.activePiece = None
        app.validMoves = set()
        app.validTakes = set()
        app.playerToMoveIdx += 1

# returns True if checked
def isChecked(app, color):
    king = eval(f"app.{color}Pieces['K'].pop()")
    eval(f"app.{color}Pieces['K'].add(king)")
    oppColor = None
    if color == "white":
        oppColor = "black"
    else:
        oppColor = "white"

    for knight in eval(f"app.{oppColor}Pieces['N']"):
        (dRow, dCol) = (king.row - knight.row, king.col - knight.col)
        if (dRow, dCol) in knight.takeMoves:
            return True
    
    for key in {'P','B','R','Q','K'}:
        for piece in eval(f"app.{oppColor}Pieces[key]"):
            (dRow, dCol) = (king.row - piece.row, king.col - piece.col)
            if ((dRow, dCol) in piece.takeMoves and 
                checkBlockingPieces(app, king.row, king.col, piece)):
                return True
    return False


# return True if color is mated
def isMated(app, color):
    for pieceType in eval(f"app.{color}Pieces"):
        for piece in eval(f"app.{color}Pieces[pieceType]"):
            validMoves = getValidMoves(app, piece)
            validTakes = getValidTakes(app, piece)
            if (validMoves != set() or validTakes != set()):
                return False
    return True

# returns True if move does not result in check
def attemptUndoCheck(app, tempRow, tempCol, piece):
    tempBoardSq = app.gameBoard[tempRow][tempCol]
    if isinstance(tempBoardSq, ChessPiece) and tempBoardSq.color == piece.color:
        return False
    oppColor = getOpposingColor(app, piece)
    color = piece.color
    pieceCopy = piece.copy()

    whitePiecesCopy = app.whitePieces.copy()
    blackPiecesCopy = app.blackPieces.copy()
    dRow, dCol = tempRow - piece.row, tempCol - piece.col
    if isinstance(tempBoardSq, ChessPiece) and tempBoardSq.color != piece.color:
        oppColorPiece = tempBoardSq
        if piece.hasTake(dRow, dCol):
            eval(f"app.{oppColor}Pieces[str(oppColorPiece)].remove(oppColorPiece)")
            app.gameBoard[tempRow][tempCol] = piece
            app.gameBoard[piece.row][piece.col] = 0
            eval(f"app.{color}Pieces[str(piece)].remove(piece)")

            pieceCopy.row, pieceCopy.col = tempRow, tempCol
            eval(f"app.{color}Pieces[str(pieceCopy)].add(pieceCopy)")

            result = None
            if isChecked(app, color):
                result = False
            else:
                result = True
            
            app.gameBoard[tempRow][tempCol] = oppColorPiece

            app.gameBoard[piece.row][piece.col] = piece
            eval(f"app.{color}Pieces[str(pieceCopy)].remove(pieceCopy)")
            eval(f"app.{color}Pieces[str(piece)].add(piece)")
            eval(f"app.{oppColor}Pieces[str(oppColorPiece)].add(oppColorPiece)")
            app.whitePieces = whitePiecesCopy
            app.blackPieces = blackPiecesCopy
            return result
    else:
        if piece.hasMove(dRow, dCol): 
            app.gameBoard[tempRow][tempCol] = piece
            app.gameBoard[piece.row][piece.col] = 0
            eval(f"app.{color}Pieces[str(piece)].remove(piece)")

            pieceCopy.row, pieceCopy.col = tempRow, tempCol
            eval(f"app.{color}Pieces[str(pieceCopy)].add(pieceCopy)")
            result = None
            if isChecked(app, color):
                result = False
            else:
                result = True

            app.gameBoard[tempRow][tempCol] = 0
            app.gameBoard[piece.row][piece.col] = piece

            eval(f"app.{color}Pieces[str(pieceCopy)].remove(pieceCopy)")
            eval(f"app.{color}Pieces[str(piece)].add(piece)")
            app.whitePieces = whitePiecesCopy
            app.blackPieces = blackPiecesCopy
            return result
    return False

########################
# EVENT FUNCTIONS
########################

# mouse pressed function responsible for moving pieces and game functionalities
def twoPlayer_mousePressed(app, event):
    x, y = event.x, event.y
    # if game is over respond only to user clicking ok button
    if app.gameOver:
        if (x > app.okButtonX - app.okButtonWidth and 
            x < app.okButtonX + app.okButtonWidth and
            y > app.okButtonY - app.okButtonHeight and 
            y < app.okButtonY + app.okButtonHeight):
            app.mode = "homeScreenMode"
            restartGame(app)
        return

    # if pause menu is open, respond only to pause menu buttons
    if app.paused: 
        # quit pressed
        if (x > app.quitX - app.pauseButtonsWidth
           and x < app.quitX + app.pauseButtonsWidth
           and y > app.quitY - app.pauseButtonsHeight
           and y < app.quitY + app.pauseButtonsHeight):
           app.paused = False
           app.mode = "homeScreenMode"
           restartGame(app)
        # resume pressed
        elif (x > app.resumeX - app.pauseButtonsWidth
              and x < app.resumeX + app.pauseButtonsWidth
              and y > app.resumeY - app.pauseButtonsHeight
              and y < app.resumeY + app.pauseButtonsHeight):
            app.paused = False
        return

    # checks if pause menu pressed
    if (x > app.pauseX and y > app.pauseY 
        and x < app.pauseX + app.pauseWidth 
        and y < app.pauseY + app.pauseWidth):
        app.paused = True
        return
    
    # if click not in board, do nothing
    if inBoard(app, x, y) == False:
        return

    # click is in board, evaluate click
    row, col = getRowCol(app, x, y)
    currPlayerColor = app.players[app.playerToMoveIdx % 2]
    clickedSquare = app.gameBoard[row][col]

    # user clicked on a chess piece
    if isinstance(clickedSquare, ChessPiece):
        if app.activePiece == None and currPlayerColor == clickedSquare.color:
            app.activePiece = clickedSquare
            app.validMoves = getValidMoves(app, app.activePiece)
            app.validTakes = getValidTakes(app, app.activePiece)
            
        elif app.activePiece == None and currPlayerColor != clickedSquare.color:
            return

        else: # app.activePiece != None            
            if app.activePiece.color == clickedSquare.color:
                app.activePiece = clickedSquare
                app.validMoves = getValidMoves(app, app.activePiece)
                app.validTakes = getValidTakes(app, app.activePiece)
            else: # pieces are different colors
                takePiece(app, row, col)
    # user clicked on an empty space
    else:
        if app.activePiece != None:
            if type(app.activePiece) == King:
                pass
            makeMove(app, row, col)

def twoPlayer_keyPressed(app, event):
    key = event.key
    if key == "g":
        if app.fancyGraphics == True:
            app.font = app.normalFont
        else:
            app.font = app.fancyFont
        app.fancyGraphics = not app.fancyGraphics
    keyPressed(app, event)

########################
# DRAW FUNCTIONS
########################

# draws player labels
def drawPlayerLabels(app, canvas):
    if app.playerToMoveIdx % 2 == 0:
        canvas.create_text(app.width / 2, app.height - app.margin / 2,
                            text = "Player 1", fill = "gold", font = (app.font,  20))
        canvas.create_text(app.width / 2, app.margin / 2,
                            text = "Player 2", fill = "black", font = (app.font,  20))
    else:
        canvas.create_text(app.width / 2, app.height - app.margin / 2,
                            text = "Player 1", fill = "black", font = (app.font,  20))
        canvas.create_text(app.width / 2, app.margin / 2,
                            text = "Player 2", fill = "gold", font = (app.font,  20))

# draws taken pieces on side of the chess board                     
def drawTakenPieces(app, canvas):
    idx = 0
    defaultPieceDict = {"P": set(), "B": set(), "N": set(), 
                        "R": set(), "K": set(), "Q": set()}
    if app.whiteTakenPieces != defaultPieceDict:
        numWhiteTaken = getNumberOfPieces(app, app.whiteTakenPieces)
        canvas.create_rectangle(app.width - app.margin + app.pauseMargin,
                                app.margin,
                                app.width - app.pauseMargin,
                                app.margin + (app.margin / 2) * numWhiteTaken,
                                fill = "tan", width = app.pauseButtonLineWidth)
        for pieceType in ['P','N','B','R','Q']:
            for piece in app.whiteTakenPieces[pieceType]:
                x0, y0, x1, y1 = getDimensions(app, piece.row, piece.col)
                canvas.create_text(app.width - (app.margin / 2),  
                                app.margin * (5/4) + (app.margin / 2) * idx,
                                text = str(piece), font = (app.font, 15),
                                fill = piece.color)
                idx += 1

    
    idx = 0
    if app.blackTakenPieces != defaultPieceDict:
        numBlackTaken = getNumberOfPieces(app, app.blackTakenPieces)
        canvas.create_rectangle(app.pauseMargin,
                                app.height - app.margin,
                                app.margin - app.pauseMargin,
                                app.height - app.margin - (app.margin / 2) * numBlackTaken,
                                fill = "tan", width = app.pauseButtonLineWidth)
        for pieceType in ['Q','R','B','N','P']:
            for piece in app.blackTakenPieces[pieceType]:
                x0, y0, x1, y1 = getDimensions(app, piece.row, piece.col)
                canvas.create_text(app.margin / 2,
                                (app.height - app.margin * (5/4)) - (app.margin / 2) * idx,
                                text = str(piece), font = (app.font,  15),
                                fill = piece.color)
                idx += 1


# draw chess game board
def drawBoard(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height,
                            fill = app.backgroundColor)
    for row in range(app.rows):
        for col in range(app.cols):
            x0, y0, x1, y1 = getDimensions(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1,
                                    fill = app.boardColors[(row + col) % 2],
                                    width = app.squareOutlineWidth)
    
    # highlight active piece square
    if app.activePiece == None:
        return

    x0, y0, x1, y1 = getDimensions(app, app.activePiece.row, app.activePiece.col)
    canvas.create_rectangle(x0, y0, x1, y1,
                            fill = app.boardColors[(app.activePiece.row + app.activePiece.col) % 2],
                            width = app.squareOutlineWidth - 2,
                            outline = "gold")

# draw pieces on game board
def drawPieces(app, canvas):
    for pieceType in {'P', 'N', 'B', 'R', 'Q', 'K'}:
        whiteTypePieces = app.whitePieces[pieceType]
        blackTypePieces = app.blackPieces[pieceType]
        for piece in whiteTypePieces.union(blackTypePieces):
            x0, y0, x1, y1 = getDimensions(app, piece.row, piece.col)
            canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                                    text = str(piece), font = (app.font,  20),
                                    fill = piece.color)

# draws "check" message at top for whichever color is checked
def drawCheck(app, canvas):
    canvas.create_rectangle(app.pauseMargin, app.pauseMargin,
                            app.pauseMargin + app.buttonWidth,
                            app.pauseMargin + app.buttonHeight,
                            width = app.pauseButtonLineWidth,
                            fill = "yellow")
    canvas.create_text(app.pauseMargin + app.buttonWidth / 2, 
                       app.pauseMargin + app.buttonHeight / 2, 
                       text = f"{app.checked} checked", font = (app.font,  9),
                       fill = "black")

# draws player's avaliable moves and takes
def drawMoves(app, canvas):
    for (moveRow, moveCol) in app.validMoves:
        x0, y0, x1, y1 = getDimensions(app, moveRow, moveCol)
        x, y = (x0 + x1) / 2, (y0 + y1) / 2
        canvas.create_oval(x - app.moveDotR, y - app.moveDotR,
                               x + app.moveDotR, y + app.moveDotR,
                               fill = app.moveDotColor)

    for (takeRow, takeCol) in app.validTakes:
        x0, y0, x1, y1 = getDimensions(app, takeRow, takeCol)
        x, y = (x0 + x1) / 2, (y0 + y1) / 2
        canvas.create_oval(x - app.moveDotR, y - app.moveDotR,
                               x + app.moveDotR, y + app.moveDotR,
                               fill = app.takeDotColor)

# draws pause button
def drawPause(app, canvas):
    canvas.create_rectangle(app.pauseX, app.pauseY, 
                            app.pauseX + app.pauseWidth, 
                            app.pauseY + app.pauseWidth,
                            fill = app.pauseButtonColor, width = app.pauseButtonLineWidth)
    canvas.create_line(app.leftPauseX, app.leftPauseY,
                       app.leftPauseX, app.leftPauseY + app.pauseSignHeight,
                       width = app.pauseButtonLineWidth)
    canvas.create_line(app.rightPauseX, app.rightPauseY,
                       app.rightPauseX, app.rightPauseY + app.pauseSignHeight,
                       width = app.pauseButtonLineWidth)

# draws pause menu
def drawPauseMenu(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height,
                            fill = app.menuBackground)
    canvas.create_text(app.pausedTextX, app.pausedTextY,
                       text = "Pause Menu", font = (app.font,  40),
                       fill = "black", anchor = "n")
    canvas.create_rectangle(app.resumeX - app.pauseButtonsWidth, 
                            app.resumeY - app.pauseButtonsHeight,
                            app.resumeX + app.pauseButtonsWidth, 
                            app.resumeY + app.pauseButtonsHeight,
                            width = app.buttonOutlineWidth,
                            fill = app.resumeButtonColor)
    canvas.create_text(app.resumeX, app.resumeY, text = "Resume",
                       font = (app.font,  25), fill = "black")

    canvas.create_rectangle(app.quitX - app.pauseButtonsWidth, 
                            app.quitY - app.pauseButtonsHeight,
                            app.quitX + app.pauseButtonsWidth, 
                            app.quitY + app.pauseButtonsHeight,
                            width = app.buttonOutlineWidth,
                            fill = app.quitButtonColor)
    canvas.create_text(app.quitX, app.quitY, text = "Quit",
                       font = (app.font,  25), fill = "black")

# draws game over screen      
def drawGameOverScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height,
                            fill = app.gameOverScreenColor)
    canvas.create_text(app.width / 2, app.height * (6/16), text = "Game Over!", 
                            font = (app.font,  40), fill = "black")

    winningColor = None
    if app.checked == "white":
        winningColor = "black"
    else:
        winningColor = "white"

    canvas.create_text(app.width / 2, app.height * (1/2), text = f"{winningColor} wins!", 
                        font = (app.font,  25), fill = "black")
    
    canvas.create_rectangle(app.okButtonX - app.okButtonWidth, 
                            app.okButtonY - app.okButtonHeight,
                            app.okButtonX + app.okButtonWidth, 
                            app.okButtonY + app.okButtonHeight,
                            width = app.okButtonLineWidth, fill = app.okButtonColor)
    canvas.create_text(app.okButtonX, app.okButtonY, text = "OK",
                       font = (app.font,  20))

# draws all game mode components
def twoPlayer_redrawAll(app, canvas):
    if app.gameOver:
        drawGameOverScreen(app, canvas)
        return
    elif app.paused:
        drawPauseMenu(app, canvas)
        return
        
    drawBoard(app, canvas)
    drawPieces(app, canvas)
    drawTakenPieces(app, canvas)
    drawPause(app, canvas)
    drawPlayerLabels(app, canvas)

    if app.activePiece != None:
        drawMoves(app, canvas)
    if app.checked != None:
        drawCheck(app, canvas)


#################################################
# GENERAL CONTROLS
#################################################

def keyPressed(app, event):
    key = event.key
    restartGame(app)
    if key.isdigit() and key != "2":
        app.whitePieces = {"P": set(), "B": set(), "N": set(), 
                        "R": set(), "K": set(), "Q": set()}
        app.blackPieces = {"P": set(), "B": set(), "N": set(), 
                        "R": set(), "K": set(), "Q": set()}
        app.gameBoard = [[0] * 8 for i in range(8)]
    if key == "1": # knight-queen mate
        wKnight1 = Knight(3, 3, "white")
        wQueen = Queen(1, 2, 'white')
        wKing = King(7, 4, 'white', True)
        for whitePiece in {wKnight1, wQueen, wKing}:
            app.whitePieces[str(whitePiece)].add(whitePiece)
            app.gameBoard[whitePiece.row][whitePiece.col] = whitePiece

        bKing = King(0, 4, "black", True)
        app.blackPieces[str(bKing)].add(bKing)
        app.gameBoard[bKing.row][bKing.col] = bKing

    elif key == "2": # fool's mate (against white)
        app.activePiece = app.gameBoard[6][5]
        makeMove(app, 5, 5)
        app.activePiece = app.gameBoard[1][4]
        makeMove(app, 3, 4)
        app.activePiece = app.gameBoard[6][6]
        makeMove(app, 4, 6)

    elif key == "3": # backrank mate (against black)
        wQueen = Queen(7, 3, 'white')
        wKing = King(7, 4, 'white', True)
        for whitePiece in {wQueen, wKing}:
            app.whitePieces[str(whitePiece)].add(whitePiece)
            app.gameBoard[whitePiece.row][whitePiece.col] = whitePiece

        bKing = King(0, 6, "black", True)
        bPawn1 = Pawn(1, 5, "black")
        bPawn2 = Pawn(1, 6, "black")
        bPawn3 = Pawn(1, 7, "black")
        for blackPiece in {bPawn1, bPawn2, bPawn3, bKing}:
            app.blackPieces[str(blackPiece)].add(blackPiece)
            app.gameBoard[blackPiece.row][blackPiece.col] = blackPiece

    elif key == "4": # two-rook mate (against white)
        wKing = King(6, 1, "white", True)
        app.whitePieces['K'].add(wKing)
        app.gameBoard[wKing.row][wKing.col] = wKing

        bKing = King(0, 4, "black", True)
        bRook1 = Rook(5, 7, "black", True)
        bRook2 = Rook(4, 6, "black", True)
        for blackPiece in {bKing, bRook1, bRook2}:
            app.blackPieces[str(blackPiece)].add(blackPiece)
            app.gameBoard[blackPiece.row][blackPiece.col] = blackPiece
    elif key == "5":
        pass # check situation 1
    elif key == "6":
        pass # check situation 2
    elif key == "7":
        pass # check situation 3
    elif key == "8":
        pass # near-side castle
    elif key == "9":
        pass # far-side castle
    elif key == "0":
        restartGame(app)

# returns number of pieces in dictionary
def getNumberOfPieces(app, d):
    numPieces = 0
    for key in d:
        for piece in d[key]:
            numPieces += 1
    return numPieces

# returns set of valid moves for given piece
def getValidMoves(app, piece):
    posMoves = piece.posMoves
    currRow, currCol = piece.row, piece.col
    validMoves = set()
    for (dRow, dCol) in posMoves:
        moveRow, moveCol = currRow + dRow, currCol + dCol
        if (isValidMove(app, moveRow, moveCol, piece)):
            validMoves.add((moveRow, moveCol))
    return validMoves

# returns set of valid take moves for given piece
def getValidTakes(app, piece):
    posTakes = piece.takeMoves
    currRow, currCol = piece.row, piece.col
    validTakes = set()
    for (dRow, dCol) in posTakes:
        moveRow, moveCol = currRow + dRow, currCol + dCol
        if (isValidTake(app, moveRow, moveCol, piece)):
            validTakes.add((moveRow, moveCol))
    return validTakes

# returns opposite color to piece given
def getOpposingColor(app, piece):
    if piece.color == "white":
        return "black"
    else:
        return "white"

# return True if x, y is inside the chess board
def inBoard(app, x, y):
    if ((x < app.margin or x > app.width - app.margin)
        or (y < app.margin or y > app.height - app.margin)):
        return False

    return True

# return True if row, col are inside board bounds
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

# copies inputted 2D list
def copyGameBoard(app, board):
    gameBoardCopy = []
    for rowIdx in range(len(board)):
        rowCopy = []
        for colIdx in range(len(board)):
            piece = board[rowIdx][colIdx]
            if isinstance(piece, ChessPiece):
                rowCopy.append(piece.copy())
            else:
                rowCopy.append(0)
        gameBoardCopy.append(rowCopy)
    return gameBoardCopy

# copies inputted dict and pieces inside
def copyPieces(app, pieceDict):
    pieceDictCopy = dict()
    for key in pieceDict:
        pieceDictCopy[key] = pieceDictCopy.get(key, set())
        for piece in pieceDict[key]:
            pieceDictCopy[key].add(piece.copy())
    return pieceDictCopy

#################################################
# APP STARTED METHODS
#################################################

# initializes all graphics related variables (fonts, images, etc.)
def initGraphicsVars(app):
    app.fancyGraphics = False
    app.normalFont = "Algerian"
    app.fancyFont = "Comic Sans MS"
    app.font = app.normalFont
    app.frogImg = app.loadImage('graphicFrog.jpeg')

# initializes all game board variables
def initGameBoardVars(app):
    app.margin = 50
    app.rows, app.cols = 8, 8
    app.squareSize = (app.width - (2 * app.margin)) / 8
    app.squareOutlineWidth = 5
    app.boardColors = ['tan', 'lightsalmon4']
    app.backgroundColor = 'firebrick4'  
    app.moveDotR = 5
    app.moveDotColor = "blue" 
    app.takeDotColor = "red"

# initializes all chess board variables 
def initBoardVars(app):
    app.whitePieces = {"P": set(), "B": set(), "N": set(), 
                       "R": set(), "K": set(), "Q": set()}
    app.blackPieces = {"P": set(), "B": set(), "N": set(), 
                       "R": set(), "K": set(), "Q": set()}
    app.whiteTakenPieces = {"P": set(), "B": set(), "N": set(), 
                            "R": set(), "K": set(), "Q": set()}
    app.blackTakenPieces = {"P": set(), "B": set(), "N": set(), 
                            "R": set(), "K": set(), "Q": set()}

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
            eval(f"app.{color}Pieces['R'].add(newRook)")
        for col in {1, app.cols - 2}:
            newKnight = Knight(row, col, color)
            app.gameBoard[row][col] = newKnight
            eval(f"app.{color}Pieces['N'].add(newKnight)")
        for col in {2, app.cols - 3}:
            newBishop = Bishop(row, col, color)
            app.gameBoard[row][col] = newBishop
            eval(f"app.{color}Pieces['B'].add(newBishop)")

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

# initiate variables related to pause button and menu
def initPauseButtonVars(app):
    app.paused = False
    app.pauseMargin = 10
    app.pauseWidth = 30
    app.pauseButtonLineWidth = 3
    app.pauseX, app.pauseY = app.width - app.margin + app.pauseMargin, app.pauseMargin
    app.pauseSignHeight = 20
    app.leftPauseX, app.rightPauseX = app.pauseX + app.pauseMargin, app.pauseX + (app.pauseWidth - app.pauseMargin)
    app.leftPauseY = app.rightPauseY = app.pauseY + (app.pauseMargin / 2)

    # buttons in pause menu
    app.pausedTextX, app.pausedTextY = app.width / 2, app.height * (1/4)
    
    app.pauseButtonsWidth, app.pauseButtonsHeight = 100, 30

    app.resumeX = app.width / 2
    app.resumeY = app.height * (7/16)

    app.quitX = app.width / 2
    app.quitY = app.height * (3/5)
    
# initiates game over screen related variables
def initGameOverVars(app):
    app.gameOverScreenColor = "grey"
    app.okButtonX = app.width / 2
    app.okButtonY = app.height * (3/5)
    app.okButtonWidth = 50
    app.okButtonHeight = 15
    app.okButtonLineWidth = 3
    
# initiates home screen related variables
def initHomeScreenVars(app):
    app.buttonWidth, app.buttonHeight = 100, 30
    app.buttonOutlineWidth = 3
    app.chessAITextY = app.height * (1/4)
    app.gameModeButtonY = app.height * (1/2)
    app.twoPlayerButtonX = app.width * (1/4)
    app.aiModeButtonX = app.width * (3/4)

def initButtonVars(app):
    app.isHoveringOnButton = False
    app.normalButtonColor = 'blanchedalmond'
    app.hoverColor = 'burlywood1'
    app.quitButtonColor = app.resumeButtonColor = app.normalButtonColor
    app.twoPlayerButtonColor = app.aiModeButtonColor = app.normalButtonColor
    app.okButtonColor = app.pauseButtonColor = app.normalButtonColor

def restartGame(app):
    initGameBoardVars(app)
    initButtonVars(app)

    app.activePiece = None
    app.validTakes = set()
    app.validMoves = set()
    app.playerToMoveIdx = 0
    app.checked = None
    app.gameOver = False
    app.gameBoard = [[0] * 8 for i in range(8)]
    initBoardVars(app)

# initializes all app variables
def appStarted(app):
    initHomeScreenVars(app)
    initGameBoardVars(app)    
    initGraphicsVars(app)
    initButtonVars(app)
    app.menuBackground = "tan"

    # game-related variables
    app.mode = 'homeScreenMode'

    app.activePiece = None
    app.validTakes = set()
    app.validMoves = set()
    app.playerToMoveIdx = 0
    app.players = ["white", "black"]

    app.checked = None
    app.gameOver = False

    app.gameBoard = [[0] * 8 for i in range(8)]
    initGraphicsVars(app)
    initBoardVars(app)
    initPauseButtonVars(app)
    initGameOverVars(app)
        

def redrawAll(app, canvas):
    pass

runApp(width = 600, height = 600)