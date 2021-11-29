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
def homeScreenMode_drawScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height,
                            fill = "tan")
    canvas.create_text(app.width / 2, app.chessAITextY,
                       text = "Chess AI", font = "Helvetica 70")
    canvas.create_rectangle(app.twoPlayerButtonX - app.buttonWidth, 
                            app.gameModeButtonY - app.buttonHeight,
                            app.twoPlayerButtonX + app.buttonWidth,
                            app.gameModeButtonY + app.buttonHeight,
                            width = app.buttonOutlineWidth, fill = "brown")
    canvas.create_text(app.twoPlayerButtonX, app.gameModeButtonY,
                       text = "Two Players", fill = "black",
                       font = "Helvetica 25")
    canvas.create_rectangle(app.aiModeButtonX - app.buttonWidth, 
                            app.gameModeButtonY - app.buttonHeight,
                            app.aiModeButtonX + app.buttonWidth,
                            app.gameModeButtonY + app.buttonHeight,
                            width = app.buttonOutlineWidth, fill = "brown")
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
    # clicked inside AI mode button
    elif (x >= (app.aiModeButtonX - app.buttonWidth) 
          and x <= (app.aiModeButtonX + app.buttonWidth)
          and y >= (app.gameModeButtonY - app.buttonHeight) 
          and y <= (app.gameModeButtonY + app.buttonHeight)):
          app.mode = "aiMode"
    

def homeScreenMode_redrawAll(app, canvas):
    homeScreenMode_drawScreen(app, canvas)
    

#################################################
# AI MODE
#################################################
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

def aiMode_timerFired(app):
    # tests to see if it's computer's turn
    if app.playerToMoveIdx % 2 == 1:
        gameBoardCopy = copyGameBoard(app, app.gameBoard)

        bestPiece, bestMove = aiMode_getMinimaxBestMove(app, app.whitePieces.copy(), 
                                                app.blackPieces.copy(),
                                                gameBoardCopy)

        app.activePiece = bestPiece
        row, col = bestMove[0], bestMove[1]
        if isValidMove(app, row, col, bestPiece):
            makeMove(app, row, col)
        else: # isValidTake
            takePiece(app, row, col)

        # aiMode_makeAIPlayerMove(app)

def aiMode_mousePressed(app, event):
    if app.gameOver:
        return

    x, y = event.x, event.y
    if app.paused: 
        # quit pressed
        if (x > app.quitX - app.pauseButtonsWidth
           and x < app.quitX + app.pauseButtonsWidth
           and y > app.quitY - app.pauseButtonsHeight
           and y < app.quitY + app.pauseButtonsHeight):
           app.paused = False
           app.mode = "homeScreenMode"
           appStarted(app)
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
        else: # app.activePiece != None
            
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
# MINIMAX FUNCTIONS
######################## 

# returns True if proposed move is a valid move (not take move) for piece
def aiMode_isValidMove(app, whitePieces, blackPieces, gameBoard, piece, moveLoc):
    # print('running isValidMove...')
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
        # print("finishing isValidMove.")
        return False

    kingChecked = aiMode_isChecked(app, whitePieces, blackPieces, gameBoard, piece.color == "white")
    if type(piece) == King and kingChecked and (dRow, dCol) in King.castleMoves:
        return False

    hasNoBlockingPieces = aiMode_checkBlockingPieces(app, gameBoard, piece, moveLoc)
    isStillChecked = aiMode_attemptUndoCheck(app, whitePieces, blackPieces, gameBoard, piece, moveLoc)
    if hasNoBlockingPieces and isStillChecked:
        return True
    else:
        return False

# returns True if proposed move is a valid take move for piece
def aiMode_isValidTake(app, whitePieces, blackPieces, gameBoard, piece, moveLoc):
    # print('running isValidTake...', end = "")
    takeRow, takeCol = moveLoc[0], moveLoc[1]

    if rowColInBounds(app, takeRow, takeCol) == False:
        # print("finishing isValidTake.")
        return False
    # check if takeRow, takeCol is a ChessPiece of opposite color to piece
    # print(f"checking if {str(piece)} can take ({takeRow},{takeCol})")
    takeSquare = gameBoard[takeRow][takeCol]
    if (isinstance(takeSquare, ChessPiece) == False):
        # print("finishing isValidTake.")
        return False
    elif (isinstance(takeSquare, ChessPiece) and 
          takeSquare.color == piece.color):
        # print("finishing isValidTake.")
        return False
    # print("passed instance tests...", end = "")
    currRow, currCol = piece.row, piece.col
    dRow, dCol = (takeRow - currRow), (takeCol - currCol)

    if (dRow, dCol) not in piece.takeMoves:
        # print("finishing isValidTake.")
        return False
    
    hasNoBlockingPieces = aiMode_checkBlockingPieces(app, gameBoard, piece, moveLoc)
    if hasNoBlockingPieces:
        isChecked = aiMode_attemptUndoCheck(app, whitePieces, blackPieces, gameBoard, piece, moveLoc)
        
        # print("finishing isValidTake.")
        return hasNoBlockingPieces and isChecked
    else:
        # print("finishing isValidTake.")
        return False

# applies move to inputted whitePieces and blackPieces (used for minimax algorithm to test moves)
def aiMode_makeMove(app, whitePieces, blackPieces, gameBoard, piece, moveLoc):
    oldRow, oldCol = piece.row, piece.col
    if aiMode_isValidMove(app, whitePieces, blackPieces, gameBoard, piece, moveLoc):
        row, col = moveLoc[0], moveLoc[1]
        gameBoard[oldRow][oldCol] = 0
        eval(f"{piece.color}Pieces[str(piece)].remove(piece)")

        oldMovedState = piece.moved
        piece.moved = True

        dRow, dCol = row - piece.row, col - piece.col
        isCastlingMove = False
        castleDCol = None
        if type(piece) == King and (dRow, dCol) in King.castleMoves:
            # print(f"King {piece.row} {piece.col} to {row}, {col} is castling move!")
            isCastlingMove = True
            castleDCol = dCol
        
        # removes pawn double-move/castle move if piece is a pawn/king respectively
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
            # print(f"\nRook at {piece.row}, {piece.col} moved to {moveLoc}, oldMoved: {oldMovedState}")
            # print(gameBoard)
            color = piece.color
            king = eval(f"{color}Pieces['K'].pop()")
            if king.moved == False:
                # print(f"king loc: {king.row}, {king.col}")
                dRow, dCol = piece.row - king.row, piece.col - king.col
                # print(f"curr dRow, dCol: {dRow}, {dCol}", end = "")

                dRow, dCol = dRow, (abs(dCol) // dCol) * 2
                # print(f"modded dRow, dCol: {dRow}, {dCol}")
                # print(f"king posMoves: {king.posMoves}")
                king.posMoves.remove((dRow, dCol))
            eval(f"{color}Pieces['K'].add(king)")

        piece.row, piece.col = row, col

        gameBoard[row][col] = piece
        eval(f"{piece.color}Pieces[str(piece)].add(piece)")
        # for item in eval(f"{piece.color}Pieces['R']"):
        #     print(f"Rook: at {item.row}, {item.col} has moved: {item.moved}")
        
        # move respective rook to castle
        if isCastlingMove:
            rookSearchDCol = abs(castleDCol) // castleDCol
            tempRow, tempCol = piece.row, piece.col + rookSearchDCol
            rook = None
            # for item in eval(f"{piece.color}Pieces['R']"):
            #     print(f"Rook at {item.row}, {item.col} exists")
            while rook == None:
                if type(gameBoard[tempRow][tempCol]) == Rook:
                    rook = gameBoard[tempRow][tempCol]
                    # print(f"Rook at {tempRow}, {tempCol} is castling rook")
                    gameBoard[tempRow][tempCol] = 0
                    for item in eval(f"{rook.color}Pieces['R']"):
                        if (item.row, item.col) == (rook.row, rook.col):
                            rook = item
                            break
                    eval(f"{rook.color}Pieces['R'].remove(rook)")
                tempCol += rookSearchDCol
            rookDMove = rookSearchDCol * (-1)
            rook.col = piece.col + rookDMove
            rook.moved = True
            gameBoard[rook.row][rook.col] = rook
            eval(f"{rook.color}Pieces['R'].add(rook)")

    return (whitePieces, blackPieces, gameBoard)

# do I need makeMove and takePiece as separate..?
def aiMode_takePiece(app, whitePieces, blackPieces, gameBoard, piece, takeLoc):
    # print("running takePiece...")
    oldRow, oldCol = piece.row, piece.col
    # oldMoved = piece.moved

    if aiMode_isValidTake(app, whitePieces, blackPieces, gameBoard, piece, takeLoc):
        row, col = takeLoc[0], takeLoc[1]
        gameBoard[oldRow][oldCol] = 0
        eval(f"{piece.color}Pieces[str(piece)].remove(piece)")

        oldMovedState = piece.moved
        piece.row, piece.col = row, col
        piece.moved = True
        
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

        gameBoard[row][col] = piece
        eval(f"{piece.color}Pieces[str(piece)].add(piece)")
    # print("finished takePiece.")
    return (whitePieces, blackPieces, gameBoard)

def aiMode_getMovesFromState(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn):
    # print("running getMovesFromState...", end = '')
    if isMaxPlayerTurn: # white's turn
        # print("white's turn...")
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
        # print("finished.")
        return whiteMoves
    else:
        # print("black's turn...")
        blackMoves = set()
        for pieceType in blackPieces:
            for piece in blackPieces[pieceType]:
                for (dRow, dCol) in piece.posMoves.union(piece.takeMoves):
                    moveRow, moveCol = piece.row + dRow, piece.col + dCol
                    # print(f"***Piece and Move: {piece} | {piece.row}, {piece.col} | {moveRow}, {moveCol}")
                    isValidMove = aiMode_isValidMove(app, whitePieces, blackPieces, gameBoard,
                                          piece, (moveRow, moveCol))
                    isValidTake = aiMode_isValidTake(app, whitePieces, blackPieces, gameBoard,
                                              piece, (moveRow, moveCol))
                    # print(f"testing: {isValidMove}, {isValidTake}")
                    if (isValidMove or isValidTake):
                        blackMoves.add((piece, (moveRow, moveCol)))
        # print("finished.")
        return blackMoves

def aiMode_checkBlockingPieces(app, gameBoard, piece, moveLoc):
    # print("running checkBlockingPieces...", end = '')
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
                # print("finished.")
                return False
            elif (isinstance(tempPiece, ChessPiece) and
                  tempPiece.color != piece.color and
                  (tempRow != moveRow or tempCol != moveCol)):
                # print("finished.")
                return False

            tempRow += unitDRow
            tempCol += unitDCol
    # print("finished.")
    return True

def aiMode_attemptUndoCheck(app, whitePieces, blackPieces, gameBoard, piece, moveLoc):
    # print(f"AttemptUndoCheck for {piece}: {moveLoc}")
    # print(f"    White Pieces: ", end = "")
    # for key in whitePieces:
    #     for item in whitePieces[key]:
    #         print(f"{item}: ({item.row},{item.col}) ", end = "")
    
    # print(f"\n    Black Pieces: ", end = "")
    # for key in blackPieces:
    #     for item in blackPieces[key]:
    #         print(f"{item}: ({item.row},{item.col}) ", end = "")
    # print(f"\n    GameBoard: {gameBoard}")

    tempRow, tempCol = moveLoc[0], moveLoc[1]
    tempBoardSq = gameBoard[tempRow][tempCol]
    if isinstance(tempBoardSq, ChessPiece) and tempBoardSq.color == piece.color:
        return False

    oppColor = getOpposingColor(app, piece)
    color = piece.color
    pieceCopy = piece.copy()

    whitePiecesCopy = dict()
    for key in whitePieces:
        for item in whitePieces[key]:
            whitePiecesCopy[key] = whitePiecesCopy.get(key, set())
            whitePiecesCopy[key].add(item.copy())
        
    blackPiecesCopy = dict()
    for key in blackPieces:
        for item in blackPieces[key]:
            blackPiecesCopy[key] = blackPiecesCopy.get(key, set())
            blackPiecesCopy[key].add(item.copy())

    gameBoardCopy = copyGameBoard(app, gameBoard)

    dRow, dCol = tempRow - piece.row, tempCol - piece.col

    if isinstance(tempBoardSq, ChessPiece) and (tempBoardSq.color != piece.color):
        oppColorPiece = tempBoardSq.copy()
        # print(f"tempBoardSq {tempBoardSq}: ({tempBoardSq.row}, {tempBoardSq.col})", end = "")
        # keySet = eval(f"{oppColor}Pieces[str(tempBoardSq)]")
        # print(f"in: {tempBoardSq in keySet}")

        if pieceCopy.hasTake(dRow, dCol):
            # print(f"{oppColor}Pieces: ", end = "")
            # for key in eval(f"{oppColor}Pieces"):
            #     for item in eval(f"{oppColor}Pieces[key]"):
            #         print(f"{item}: ({item.row},{item.col}) ", end = "")
            
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
                # print("move results in check!")
                result = False
            else:
                # print("move isn't check!")
                result = True
            
            # gameBoardCopy[tempRow][tempCol] = oppColorPiece
            # gameBoardCopy[piece.row][piece.col] = piece
            # eval(f"{color}Pieces[str(pieceCopy)].remove(pieceCopy)")
            # eval(f"{color}Pieces[str(piece)].add(piece)")
            # eval(f"{oppColor}Pieces[str(oppColorPiece)].add(oppColorPiece)")
            # whitePieces = whitePiecesCopy
            # blackPieces = blackPiecesCopy
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

            # gameBoard[tempRow][tempCol] = 0
            # gameBoard[piece.row][piece.col] = piece

            # eval(f"{color}Pieces[str(pieceCopy)].remove(pieceCopy)")
            # eval(f"{color}Pieces[str(piece)].add(piece)")
            # whitePieces = whitePiecesCopy
            # blackPieces = blackPiecesCopy
            return result
    return False

def aiMode_isChecked(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn):
    return aiMode_getCheckedAndPieces(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn)[1]

# can remove this if needed as it's not used in the code
def aiMode_getCheckingPieces(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn):
    return aiMode_getCheckedAndPieces(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn)[0]

def aiMode_getCheckedAndPieces(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn):
    color = aiMode_getPlayerColor(isMaxPlayerTurn)
    king = eval(f"{color}Pieces['K'].pop()")
    eval(f"{color}Pieces['K'].add(king)")
    checked = False
    checkingPieces = []

    for (drow, dcol) in Knight.moves:
        row, col = king.row + drow, king.col + dcol
        if rowColInBounds(app, row, col):
            tempPiece = gameBoard[row][col]
            if type(tempPiece) == Knight and tempPiece.color != king.color:
                checked = True
                checkingPieces.append(tempPiece)
    
    for dirRow, dirCol in king.posMoves:
        row, col = king.row + dirRow, king.col + dirCol
        while rowColInBounds(app, row, col):
            boardSq = gameBoard[row][col]
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

    return (checkingPieces, checked)

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

# returns set of valid take moves for given piece
def aiMode_getValidTakes(app, whitePieces, blackPieces, gameBoard, piece):
    posTakes = piece.takeMoves
    currRow, currCol = piece.row, piece.col
    validTakes = set()
    for (dRow, dCol) in posTakes:
        moveRow, moveCol = currRow + dRow, currCol + dCol
        moveLoc = (moveRow, moveCol)
        if (aiMode_isValidTake(app, whitePieces, blackPieces, 
                               gameBoard, piece, moveLoc)):
            # print(f"GameBoard (take) at {moveRow}, {moveCol}: {app.gameBoard[moveRow][moveCol]}")
            validTakes.add((moveRow, moveCol))
    return validTakes

# returns True if the active player is mated in the node state
def aiMode_isMated(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn):
    color = aiMode_getPlayerColor(isMaxPlayerTurn)

    for pieceType in eval(f"{color}Pieces"):
        for piece in eval(f"{color}Pieces[pieceType]"):
            validMoves = aiMode_getValidMoves(app, whitePieces, blackPieces,
                                              gameBoard, piece)
            validTakes = aiMode_getValidTakes(app, whitePieces, blackPieces,
                                              gameBoard, piece)
            if (validMoves != set() or validTakes != set()):
                # print(f"{piece} at {piece.row}, {piece.col} has {validMoves} or {validTakes}")
                return False

    return True

def aiMode_getMinimaxBestMove(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn = False):
    # print("\n\n\nrunning getMinimaxBestMove.")
    bestPiece = None
    bestMove = None
    minVal = None
    # print("getting posMoves...", end = "")
    posMoves = aiMode_getMovesFromState(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn)
    # print(f"PosMoves: {posMoves}")
    # input()
    for (piece, moveLoc) in posMoves:
        # print(piece, moveRow, moveCol)
        moveRow, moveCol = moveLoc[0], moveLoc[1]
        depth = 1
        pieceCopy = None
        whiteCopy = dict()
        for key in whitePieces:
            for item in whitePieces[key]:
                itemCopy = item.copy()
                whiteCopy[key] = whiteCopy.get(key, set())
                whiteCopy[key].add(itemCopy)
                if (item.color, item.row, item.col, item.moved) == (piece.color, piece.row, piece.col, piece.moved):
                    pieceCopy = itemCopy

        blackCopy = dict()
        for key in blackPieces:
            for item in blackPieces[key]:
                itemCopy = item.copy()
                blackCopy[key] = blackCopy.get(key, set())
                blackCopy[key].add(itemCopy)
                if (item.color, item.row, item.col, item.moved) == (piece.color, piece.row, piece.col, item.moved):
                    pieceCopy = itemCopy

        gameBoardCopy = copyGameBoard(app, gameBoard)

        if aiMode_isValidMove(app, whiteCopy, blackCopy, gameBoardCopy,
                              pieceCopy, moveLoc):
            aiMode_makeMove(app, whiteCopy, 
                                                                  blackCopy, gameBoardCopy,
                                                                  pieceCopy, moveLoc)
        else: # isValidTake == True
            aiMode_takePiece(app, whiteCopy, 
                                                                   blackCopy, gameBoardCopy,
                                                                   pieceCopy, moveLoc)

        moveVal = aiMode_minimax(app, whiteCopy, blackCopy, gameBoardCopy, depth, isMaxPlayerTurn)
        if bestMove == None or moveVal < minVal:
            minVal = moveVal
            bestPiece = piece
            bestMove = (moveRow, moveCol)
            # print(f"New Best Move (depth: {depth}): {piece} to {moveLoc}")
    # input()
    return bestPiece, bestMove

# returns current player's color depending on isMaxPlayerTurn value
def aiMode_getPlayerColor(isMaxPlayerTurn):
    if isMaxPlayerTurn:
        return "white"
    else:
        return "black"

# general pseudocode structure: https://www.javatpoint.com/mini-max-algorithm-in-ai
# state stores the temporary set of pieces for both colors (and gameboard??)
# say isMaximizingPlayer is white (player)
def aiMode_minimax(app, whitePieces, blackPieces, gameBoard, depth, isMaxPlayerTurn):
    # print(f"------DEPTH: {depth}, Turn: {isMaxPlayerTurn}------")
    # print(f"    {whitePieces}")
    # print(f"    {blackPieces}")
    # print(f"    {gameBoard}")
    isChecked = aiMode_isChecked(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn)
    isMated = False
    if isChecked:
        isMated = aiMode_isMated(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn)

    # print(gameBoard)
    if depth == 0 or isMated:
        # print(f"returning! {depth} {isMated}")
        posVal = 0
        playerColor = aiMode_getPlayerColor(isMaxPlayerTurn)

        # add "value bonuses" if the move results in a check/mate
        if isMated and playerColor == 'black':
            posVal -= 50
        elif isChecked and playerColor == 'black':
            # print("adding points for black check!")
            posVal -= 5
        elif isMated and playerColor == "white":
            posVal += 50
        elif isChecked and playerColor == "white":
            # print("adding points for white check!")
            posVal += 5

        # print(blackPieces)
        for pieceType in blackPieces:
            for item in blackPieces[pieceType]:
                posVal -= item.value
                # print(f"{item}: ({item.row},{item.col}) ", end = '')
        # print(f"\n{whitePieces}")
        # print()
        for pieceType in whitePieces:
            for item in whitePieces[pieceType]:
                posVal += item.value
                # print(f"{item}: ({item.row},{item.col}) ", end = '')
        # print(f"\nPosVal: {posVal}")
        # input()
        # print()
        return posVal

        # if is check or mate, return higher/lower values
        # return value of state (sum of black and white piece values)
    # print("getting moves from state...", end = '')
    posMovesFromState = aiMode_getMovesFromState(app, whitePieces, blackPieces, gameBoard, isMaxPlayerTurn)
    # print("moves gotten!")
    if isMaxPlayerTurn: 
        # print("maxEval!")
        maxEval = -100000  
        for (piece, moveLoc) in posMovesFromState:
            # print(f"    {piece.color} {piece}, {moveLoc}")
            whiteCopy = dict()
            blackCopy = dict()
            pieceCopy = None

            if piece.color == "white":
                # print(f"piece in whitePieces: {piece in whitePieces[str(piece)]}")
                # print(f"    {str(piece)}: {piece.row}, {piece.col}")
                # print(f"        {whitePieces}")
                # print(f"        {blackPieces}")
                # print(f"        {gameBoard}")
                # for item in whitePieces[str(piece)]:
                    # print(f"    {str(item)}: {item.row}, {item.col}", end = '')
                # print()
                whitePieces[str(piece)].remove(piece)
                pieceCopy = piece.copy()
                whiteCopy[str(piece)] = {pieceCopy}
                # except:
                #     # print(str(piece), whitePieces)
                #     input()

            else:
                # print(f"piece in blackPieces: {piece in blackPieces[str(piece)]}")
                # print(f"    {str(piece)}: {piece.row}, {piece.col}")
                # for item in blackPieces[str(piece)]:
                #     print(f"    {str(item)}: {item.row}, {item.col}", end = '')
                # print()
                blackPieces.remove(piece)
                pieceCopy = piece.copy()
                blackCopy[str(piece)] = {pieceCopy}
                # except:
                #     # print(str(piece), blackPieces)
                #     input()

            for key in whitePieces:
                for item in whitePieces[key]:
                    whiteCopy[key] = whiteCopy.get(key, set())
                    whiteCopy[key].add(item.copy())
            
            for key in blackPieces:
                for item in blackPieces[key]:
                    blackCopy[key] = blackCopy.get(key, set())
                    blackCopy[key].add(item.copy())
            
            if piece.color == "white":
                whitePieces[str(piece)].add(piece)
            else:
                blackPieces[str(piece)].add(piece)

            # watch aliasing between sets and list for pieces/gameboard respectively
        
            gameBoardCopy = copyGameBoard(app, gameBoard)

            isValidMove = aiMode_isValidMove(app, whiteCopy, blackCopy, 
                                             gameBoardCopy, pieceCopy, moveLoc)
            isValidTake = aiMode_isValidTake(app, whiteCopy, blackCopy, 
                                             gameBoardCopy, pieceCopy, moveLoc)
            
            # newState = (whiteCopy, blackCopy, gameBoardCopy)
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
        # print('minEval!')
        minEval = 100000   
        for (piece, moveLoc) in posMovesFromState:
            # print(f"    {piece.color} {piece}, {moveLoc}")
            whiteCopy = dict()
            blackCopy = dict()
            pieceCopy = None
            # i think i can delete this entire initial color == "white" section
            if piece.color == "white":
                # print(f"piece in whitePieces: {piece in whitePieces[str(piece)]}")
                # print(f"    {str(piece)}: {piece.row}, {piece.col}")
                # print(f"        {whitePieces}")
                # print(f"        {blackPieces}")
                # print(f"        {gameBoard}")
                # for item in whitePieces[str(piece)]:
                #     print(f"    {str(item)}: {item.row}, {item.col}", end = '')
                # print()
                whitePieces[str(piece)].remove(piece)
                pieceCopy = piece.copy()
                whiteCopy[str(piece)] = {pieceCopy}
                # except:
                #     # print(str(piece), whitePieces)
                #     input()

            else:
                # print(f"piece in blackPieces: {piece in blackPieces[str(piece)]}")
                # print(f"    {str(piece)}: {piece.row}, {piece.col}")
                # for item in blackPieces[str(piece)]:
                    # print(f"    {str(item)}: {item.row}, {item.col}", end = '')
                # print()
                # for key in blackPieces:
                #     for item in blackPieces[key]:
                #         print(f"{item}: ({item.row}, {item.col}) ", end = "") # PIECE VARIABLE IS ALIASING!!
                # print("\n     before mods ^^^")

                blackPieces[str(piece)].remove(piece) # REMOVE PIECE HERE---------******************
                pieceCopy = piece.copy()
                blackCopy[str(pieceCopy)] = {pieceCopy}
                # print("items in blackCopy:")
                # for key in blackCopy:
                #     for item in blackCopy[key]:
                #         print(f"{item}: {item.row} {item.col}")
                # print("     ^^ so far")

            for key in whitePieces:
                for item in whitePieces[key]:
                    whiteCopy[key] = whiteCopy.get(key, set())
                    whiteCopy[key].add(item.copy())
            
            for key in blackPieces:
                for item in blackPieces[key]:
                    # print(f"{item}: {item.row}, {item.col}")
                    blackCopy[key] = blackCopy.get(key, set())
                    blackCopy[key].add(item.copy())
            # print("     done.")
            # print("readding piece to blackPieces")
            if piece.color == "white":
                whitePieces[str(piece)].add(piece)
            else:
                blackPieces[str(piece)].add(piece)
            # for key in blackPieces:
            #         for item in blackPieces[key]:
            #             print(f"{item}: ({item.row},{item.col}) ", end = "")
            # print("     done.")
        
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
            # print("post move/take:")
            # print("     blackPieces:")
            # for key in blackPieces:
            #         for item in blackPieces[key]:
            #             print(f"{item}: ({item.row},{item.col}) ", end = "")
            # # print("\n     blackCopy:")
            # for key in blackCopy:
            #         for item in blackCopy[key]:
            #             print(f"{item}: ({item.row},{item.col}) ", end = "")
            # input()
        return minEval 


########################
# AI FUNCTIONS
######################## 
        
def aiMode_makeAIPlayerMove(app):
    seenIdxs = set()
    pieceTypes = list(app.blackPieces.keys())

    # iterates for the amount of pieces types there are
    for i in range(len(pieceTypes)):
        # generate random piece type to iterate through
        randIdx = random.randint(0, len(pieceTypes) - 1)
        while randIdx in seenIdxs:
            randIdx = random.randint(0, len(pieceTypes) - 1)
            if randIdx not in seenIdxs:
                seenIdxs.add(randIdx)
        pieceType = pieceTypes[randIdx]
        
        seenIdxs = set()
        pieces = list(app.blackPieces[pieceType])
        # iterates through all pieces of pieceType
        for j in range(len(pieces)):
            randIdx = random.randint(0, len(pieces) - 1)
            while randIdx in seenIdxs:
                randIdx = random.randint(0, len(pieces) - 1)
                if randIdx not in seenIdxs:
                    seenIdxs.add(randIdx)
            piece = pieces[randIdx]

            seenIdxs = set()
            moves = list(piece.posMoves.union(piece.takeMoves))
            # iterate through all possible moves/takes for piece
            for k in range(len(moves)):
                randIdx = random.randint(0, len(moves) - 1)
                while randIdx in seenIdxs:
                    randIdx = random.randint(0, len(moves) - 1)
                    if randIdx not in seenIdxs:
                        seenIdxs.add(randIdx)
                move = moves[randIdx]
                dRow, dCol = move

                moveRow, moveCol = piece.row + dRow, piece.col + dCol
                # if move is valid, AI completes move
                if isValidMove(app, moveRow, moveCol, piece):
                    app.activePiece = piece
                    makeMove(app, moveRow, moveCol)
                    return
                elif isValidTake(app, moveRow, moveCol, piece):
                    app.activePiece = piece
                    takePiece(app, moveRow, moveCol)
                    return

########################
# DRAW FUNCTIONS
######################## 

def aiMode_drawPlayerLabels(app, canvas):
    canvas.create_text(app.width / 2, app.height - app.margin / 2,
                        text = "Player", fill = "black", font = "Arial 20 bold")
    canvas.create_text(app.width / 2, app.margin / 2,
                        text = "Computer", fill = "black", font = "Arial 20 bold")

def aiMode_redrawAll(app, canvas):
    if app.gameOver:
        canvas.create_text(app.width / 2, app.height / 2, text = "game over!", 
                            font = "Arial 40", fill = "black")
        return
    elif app.paused:
        drawPauseMenu(app, canvas)
        return

    drawBoard(app, canvas)
    drawPieces(app, canvas)
    drawTakenPieces(app, canvas)
    aiMode_drawPlayerLabels(app, canvas)
    drawPause(app, canvas)

    # canvas.create_oval(100, 100, 110, 110, fill = "blue")
    if app.activePiece != None:
        drawMoves(app, canvas)
    if app.checked != None:
        drawCheck(app, canvas)

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
def isValidMove(app, moveRow, moveCol, piece):
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
    
    # king can not castle if checked
    kingChecked = isChecked(app, piece.color)
    if type(piece) == King and kingChecked and (dRow, dCol) in King.castleMoves:
        return False
    
    hasNoBlockingPieces = checkBlockingPieces(app, moveRow, moveCol, piece)
    isStillChecked = attemptUndoCheck(app, moveRow, moveCol, piece)
    # print(hasNoBlockingPieces, isChecked)
    if hasNoBlockingPieces and isStillChecked:
        return True
    else:
        return False

def isValidTake(app, takeRow, takeCol, piece):
    if rowColInBounds(app, takeRow, takeCol) == False:
        return False
    # check if takeRow, takeCol is a ChessPiece of opposite color to piece
    # print(f"checking if {str(piece)} can take ({takeRow},{takeCol})")
    takeSquare = app.gameBoard[takeRow][takeCol]
    
    if (isinstance(takeSquare, ChessPiece) == False):
        return False
    # print(f"{takeSquare} {takeSquare.color} and {piece} {piece.color} are same color: {takeSquare.color == piece.color}")
    if (isinstance(takeSquare, ChessPiece) and 
          takeSquare.color == piece.color):
        return False
    # print("passed instance tests...", end = "")
    currRow, currCol = piece.row, piece.col
    dRow, dCol = (takeRow - currRow), (takeCol - currCol)

    if ((dRow, dCol) not in piece.takeMoves 
        or rowColInBounds(app, takeRow, takeCol) == False):
        return False
    # print("is inside takeMoves...", end = "")
    hasNoBlockingPieces = checkBlockingPieces(app, takeRow, takeCol, piece)
    isChecked = attemptUndoCheck(app, takeRow, takeCol, piece)
    if hasNoBlockingPieces and isChecked:
        # print("no blocking pieces... returning True")
        return True
    else:
        # print("has blocking pieces... returning False")
        return False

def checkBlockingPieces(app, moveRow, moveCol, piece):
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

            tempRow += unitDRow
            tempCol += unitDCol
            # loopCounter += 1
    return True

# if move is valid, make move and adjust set of same-color pieces accordingly
def makeMove(app, row, col):
    oldRow, oldCol = app.activePiece.row, app.activePiece.col
    # print(f"isValidMove: {isValidMove(app, row, col, app.activePiece)}")
    if (isValidMove(app, row, col, app.activePiece)):
        # remove piece from gameBoard/app.colorPieces and modify its values
        app.gameBoard[oldRow][oldCol] = 0
        eval(f"app.{app.activePiece.color}Pieces[str(app.activePiece)].remove(app.activePiece)")

        oldMovedState = app.activePiece.moved
        app.activePiece.moved = True

        # checks if move is a castling move
        dRow, dCol = row - app.activePiece.row, col - app.activePiece.col
        isCastlingMove = False
        castleDCol = None
        if type(app.activePiece) == King and (dRow, dCol) in King.castleMoves:
            isCastlingMove = True
            castleDCol = dCol

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

        # move respective rook to castle
        if isCastlingMove:
            rookSearchDCol = abs(castleDCol) // castleDCol
            tempRow, tempCol = app.activePiece.row, app.activePiece.col + rookSearchDCol
            rook = None
            while rook == None:
                if type(app.gameBoard[tempRow][tempCol]) == Rook:
                    rook = app.gameBoard[tempRow][tempCol]
                    app.gameBoard[tempRow][tempCol] = 0
                    eval(f"app.{rook.color}Pieces['R'].remove(rook)")
                tempCol += rookSearchDCol
            rookDMove = rookSearchDCol * (-1)
            rook.col = app.activePiece.col + rookDMove
            rook.moved = True
            app.gameBoard[rook.row][rook.col] = rook
            eval(f"app.{rook.color}Pieces['R'].add(rook)")

        oppColor = getOpposingColor(app, app.activePiece)
        if isChecked(app, oppColor):
            app.checked = oppColor
            print(f"{oppColor} is checked!")
            print(f"{isMated(app, oppColor)}")
            if isMated(app, oppColor):
                # print("setting gameOver to True...")
                app.gameOver = True
                return
        else:
            app.checked = None
        

        app.activePiece = None
        app.validMoves = set()
        app.validTakes = set()
        app.playerToMoveIdx += 1 
    # print("not valid move!")

# this function is SO similar to makeMove -- maybe merge them before you get too far?
# if move is valid, take piece and remove piece from respective set of pieces
def takePiece(app, row, col):
    oldRow, oldCol = app.activePiece.row, app.activePiece.col
    oldMoved = app.activePiece.moved

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
            print(f"{oppColor} is checked!")
            print(f"{isMated(app, oppColor)}")
            if isMated(app, oppColor):
                
                # print("setting gameOver to True...")
                app.gameOver = True
                return
        else:
            app.checked = None

        app.activePiece = None
        app.validMoves = set()
        app.validTakes = set()
        app.playerToMoveIdx += 1
        # print(app.gameBoard)

def isChecked(app, color):
    return getCheckedAndPieces(app, color)[1]

def getCheckingPieces(app, color):
    return getCheckedAndPieces(app, color)[0]

def getCheckedAndPieces(app, color):
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

def isMated(app, color):
    # print(f"checking if {color} is mated...", end = "")
    # input()

    for pieceType in eval(f"app.{color}Pieces"):
        for piece in eval(f"app.{color}Pieces[pieceType]"):
            # print(f"    checking {piece} at ({piece.row}, {piece.col}) moves...")
            # print(f"    getting validMoves...")
            validMoves = getValidMoves(app, piece)
            # print(f"    getting takeMoves...")
            validTakes = getValidTakes(app, piece)
            if (validMoves != set() or validTakes != set()):
                # print(f"{piece} at {piece.row}, {piece.col} has {validMoves} or {validTakes}")
                return False
            # print("made through while loop")

    # print("no moves...", end = "")
    # input()
    # print("mate!")   
    return True

# returns True if move successfully undoes check
# returns False if it doesn't
def attemptUndoCheck(app, tempRow, tempCol, piece):
    # print(type(piece), str(piece))

    tempBoardSq = app.gameBoard[tempRow][tempCol]
    if isinstance(tempBoardSq, ChessPiece) and tempBoardSq.color == piece.color:
        return False
    # print(type(piece), str(piece))
    oppColor = getOpposingColor(app, piece)
    color = piece.color
    pieceCopy = piece.copy()

    whitePiecesCopy = app.whitePieces.copy()
    blackPiecesCopy = app.blackPieces.copy()
    dRow, dCol = tempRow - piece.row, tempCol - piece.col
    if isinstance(tempBoardSq, ChessPiece) and tempBoardSq.color != piece.color:
        oppColorPiece = tempBoardSq
        # print(f"hasTake branch running for {str(piece)} to {tempRow} {tempCol}")
        if piece.hasTake(dRow, dCol):
            eval(f"app.{oppColor}Pieces[str(oppColorPiece)].remove(oppColorPiece)")
            app.gameBoard[tempRow][tempCol] = piece
            app.gameBoard[piece.row][piece.col] = 0
            eval(f"app.{color}Pieces[str(piece)].remove(piece)")

            pieceCopy.row, pieceCopy.col = tempRow, tempCol
            eval(f"app.{color}Pieces[str(pieceCopy)].add(pieceCopy)")

            result = None
            if isChecked(app, color):
                # print("move results in check!")
                result = False
            else:
                # print("move isn't check!")
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
        # print(f"hasMove branch running for {str(piece)} to {tempRow} {tempCol}")
        if piece.hasMove(dRow, dCol): 
            # print('piece does have move!')
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

def gameMode_mousePressed(app, event):
    if app.gameOver:
        return
    x, y = event.x, event.y

    if app.paused: 
        # quit pressed
        if (x > app.quitX - app.pauseButtonsWidth
           and x < app.quitX + app.pauseButtonsWidth
           and y > app.quitY - app.pauseButtonsHeight
           and y < app.quitY + app.pauseButtonsHeight):
           app.paused = False
           app.mode = "homeScreenMode"
           appStarted(app)
        # resume pressed
        elif (x > app.resumeX - app.pauseButtonsWidth
              and x < app.resumeX + app.pauseButtonsWidth
              and y > app.resumeY - app.pauseButtonsHeight
              and y < app.resumeY + app.pauseButtonsHeight):
            app.paused = False
        return

    # pause menu pressed
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
        # print("clicked on chess piece!")
        if app.activePiece == None and currPlayerColor == clickedSquare.color:
            # print("clicked: chess piece of player's color")
            # if (app.gameBoard[row][col].color != 
            #     app.players[app.playerToMoveIdx % 2]):
            #     return
            app.activePiece = clickedSquare
            app.validMoves = getValidMoves(app, app.activePiece)
            app.validTakes = getValidTakes(app, app.activePiece)
            # print(app.activePiece)
        elif app.activePiece == None and currPlayerColor != clickedSquare.color:
            # print("clicked: chess piece of opp player's color")
            return
        else: # app.activePiece != None
            # print("clicked: active piece exists")
            
            if app.activePiece.color == clickedSquare.color:
                app.activePiece = clickedSquare
                app.validMoves = getValidMoves(app, app.activePiece)
                app.validTakes = getValidTakes(app, app.activePiece)
            else: # pieces are different colors
                takePiece(app, row, col)

    else: # user clicked on an empty space
        # print(f"empty space clicked! {app.activePiece}")
        if app.activePiece != None:
            if type(app.activePiece) == King:
                pass
            makeMove(app, row, col)
    # print(app.gameBoard)
    # print(app.activePiece)

def gameMode_keyPressed(app, event):
    # if (event.key == 'p'):
    #     app.mode = 'pauseMode'
    pass


########################
# DRAW FUNCTIONS
########################
def gameMode_redrawAll(app, canvas):
    if app.gameOver:
        canvas.create_text(app.width / 2, app.height / 2, text = "game over!", 
                            font = "Arial 40", fill = "black")
        return
    elif app.paused:
        drawPauseMenu(app, canvas)
        return
        
    drawBoard(app, canvas)
    drawPieces(app, canvas)
    drawTakenPieces(app, canvas)
    drawPause(app, canvas)
    drawPlayerLabels(app, canvas)
    # drawPlayerLabels(app, canvas)

    if app.activePiece != None:
        drawMoves(app, canvas)
    if app.checked != None:
        drawCheck(app, canvas)
    # canvas.create_image(200, 200, image=ImageTk.PhotoImage(app.whitePawnImg))


#################################################
# GENERAL CONTROLS
#################################################
def drawPlayerLabels(app, canvas):
    canvas.create_text(app.width / 2, app.height - app.margin / 2,
                        text = "Player 1", fill = "black", font = "Arial 20 bold")
    canvas.create_text(app.width / 2, app.margin / 2,
                        text = "Player 2", fill = "black", font = "Arial 20 bold")
                        
def getNumberOfPieces(app, d):
    numPieces = 0
    for key in d:
        for piece in d[key]:
            numPieces += 1
    return numPieces

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
                                text = str(piece), font = "Arial 15",
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
                                text = str(piece), font = "Arial 15",
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
                                    text = str(piece), font = "Arial 20",
                                    fill = piece.color)

# draw's small "check" message at top for whichever color is checked
def drawCheck(app, canvas):
    canvas.create_rectangle(app.pauseMargin, app.pauseMargin,
                            app.pauseMargin + app.buttonWidth,
                            app.pauseMargin + app.buttonHeight,
                            width = app.pauseButtonLineWidth,
                            fill = "yellow")
    canvas.create_text(app.pauseMargin + app.buttonWidth / 2, 
                       app.pauseMargin + app.buttonHeight / 2, 
                       text = f"{app.checked} checked!", font = "Arial 10",
                       fill = "black")

# draws player's avaliable moves on canvas
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

def drawPause(app, canvas):
    canvas.create_rectangle(app.pauseX, app.pauseY, 
                            app.pauseX + app.pauseWidth, 
                            app.pauseY + app.pauseWidth,
                            fill = "white", width = app.pauseButtonLineWidth)
    canvas.create_line(app.leftPauseX, app.leftPauseY,
                       app.leftPauseX, app.leftPauseY + app.pauseSignHeight,
                       width = app.pauseButtonLineWidth)
    canvas.create_line(app.rightPauseX, app.rightPauseY,
                       app.rightPauseX, app.rightPauseY + app.pauseSignHeight,
                       width = app.pauseButtonLineWidth)

def drawPauseMenu(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height,
                            fill = "ivory3")
    canvas.create_text(app.pausedTextX, app.pausedTextY,
                       text = "Pause Menu", font = "Arial 40 bold",
                       fill = "black", anchor = "n")
    canvas.create_rectangle(app.resumeX - app.pauseButtonsWidth, 
                            app.resumeY - app.pauseButtonsHeight,
                            app.resumeX + app.pauseButtonsWidth, 
                            app.resumeY + app.pauseButtonsHeight,
                            width = app.buttonOutlineWidth,
                            fill = "tan")
    canvas.create_text(app.resumeX, app.resumeY, text = "Resume",
                       font = "Arial 25", fill = "black")

    canvas.create_rectangle(app.quitX - app.pauseButtonsWidth, 
                            app.quitY - app.pauseButtonsHeight,
                            app.quitX + app.pauseButtonsWidth, 
                            app.quitY + app.pauseButtonsHeight,
                            width = app.buttonOutlineWidth,
                            fill = "tan")
    canvas.create_text(app.quitX, app.quitY, text = "Quit",
                       font = "Arial 25", fill = "black")
        


# returns set of valid moves for given piece
def getValidMoves(app, piece):
    posMoves = piece.posMoves
    currRow, currCol = piece.row, piece.col
    validMoves = set()
    for (dRow, dCol) in posMoves:
        moveRow, moveCol = currRow + dRow, currCol + dCol
        # print(f"{moveRow}, {moveCol}: {attemptUndoCheck(app, moveRow, moveCol, app.activePiece)}")
        if (isValidMove(app, moveRow, moveCol, piece)):
            # and attemptUndoCheck(app, moveRow, moveCol, app.activePiece))
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
            # and attemptUndoCheck(app, moveRow, moveCol, app.activePiece) == False):
            # print(f"GameBoard (take) at {moveRow}, {moveCol}: {app.gameBoard[moveRow][moveCol]}")
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
# https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
# def getCachedPhotoImage(app, image):
#     # stores a cached version of the PhotoImage in the PIL/Pillow image
#     if ('cachedPhotoImage' not in image.__dict__):
#         image.cachedPhotoImage = ImageTk.PhotoImage(image)
#     return image.cachedPhotoImage

# chess sprites: https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Chess_Pieces_Sprite.svg/640px-Chess_Pieces_Sprite.svg.png
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
    app.whitePieces = {"P": set(), "B": set(), "N": set(), 
                       "R": set(), "K": set(), "Q": set()}
    app.blackPieces = {"P": set(), "B": set(), "N": set(), 
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

def initiateHomeScreenVariables(app):
    app.buttonWidth, app.buttonHeight = 100, 30
    app.buttonOutlineWidth = 4
    app.chessAITextY = app.height * (1/4)
    app.gameModeButtonY = app.height * (1/2)
    app.twoPlayerButtonX = app.width * (1/4)
    app.aiModeButtonX = app.width * (3/4)

# initializes all app variables
def appStarted(app):
    initiateHomeScreenVariables(app)

    # board-related variables
    app.margin = 50
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
    app.validTakes = set()
    app.validMoves = set()
    app.playerToMoveIdx = 0
    app.players = ["white", "black"]

    app.whiteTakenPieces = {"P": set(), "B": set(), "N": set(), 
                            "R": set(), "K": set(), "Q": set()}
    app.blackTakenPieces = {"P": set(), "B": set(), "N": set(), 
                            "R": set(), "K": set(), "Q": set()}

    app.checked = None
    app.gameOver = False

    app.gameBoard = [[0] * 8 for i in range(8)]
    initializeBoard(app)
    initPauseButtonVars(app)
        

def redrawAll(app, canvas):

    # getting image from app.images
    # photoImage = getCachedPhotoImage(app, image)
    pass

runApp(width = 600, height = 600)