import numpy as np
import copy as copy
import sys as sys


class Node(object):
    def __init__(self, data, parent, depth):
        self.data = data
        self.children = []
        self.parent = parent
        self.depth = depth

    def add_child(self, child):
        self.children.append(child)

    def get_data(self):
        return self.data

    def get_children(self):
        return self.children

    def get_depth(self):
        return self.depth

    def get_parent(self):
        return self.parent

    def __str__(self, level=0):
        ret = "\t" * level + repr(self.data) + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

    def __repr__(self):
        return '<tree node representation>'


# arguments: (node, matrix, integer)
# returns a tree containing all possible moves at a certain depth
def generateTree(treeNode, depth):
    sys.stdout.write("\r Generating solutions... might take a while")
    sys.stdout.flush()
    if depth == 0:
        return
    # print(treeNode.get_data())
    validMoves = generateValidMoves(treeNode.get_data()[0])
    for move in validMoves:
        childNode = Node(move, treeNode, treeNode.get_depth() + 1)
        treeNode.add_child(childNode)
        generateTree(childNode, depth - 1)
    return treeNode


# arguments: (node, list, integer)
# modifies the list containing all children at the depth
def traverse(child, childList, depth):
    for childNode in child.get_children():
        traverse(childNode, childList, depth)
    if child.get_depth() == depth:
        childList.append(child)


# arguments: list
# returns a list containing the first discovered win
def checkWinsList(childList):
    movesList = []
    for tree in childList:
        if checkWin(tree.get_data()[0]):
            while not tree.get_parent() is None:
                movesList.append(tree.get_data()[1])
                tree = tree.get_parent()
            break
    return list(reversed(movesList))


# takes in matrix as argument
# returns a list of matrices containing the board state after valid moves
def generateValidMoves(puzzle):
    validMoves = []
    enemyRows = []
    enemyCols = []

    # count the number of enemies on each ring
    for row in range(0, len(puzzle)):
        if 1 in puzzle[row]:
            enemyRows.append(row)
    for row in enemyRows:
        for rotations in range(1, 12):
            copyPuzzle = copy.deepcopy(puzzle)
            actionStr = "spin ring #" + str(row) + " by " + str(rotations) + " rotations CW"
            validMoves.append([spinRing(row, rotations, copyPuzzle), actionStr])

    # count the number of enemies on each slice
    transposePuzzle = np.transpose(puzzle).tolist()
    newPuzzle = []
    # combine the columns that are directly opposite each other
    for i in range(0, 6):
        newPuzzle.append(transposePuzzle[i] + list(reversed(transposePuzzle[i + 6])))

    for col in range(0, len(newPuzzle)):
        if 1 in newPuzzle[col]:
            enemyCols.append(col)
    for col in enemyCols:
        for shifts in range(1, 8):
            copyPuzzle = copy.deepcopy(puzzle)
            actionStr = "shift slice #" + str(col) + " by " + str(shifts) + " spaces"
            validMoves.append([shiftSlice(col, shifts, copyPuzzle), actionStr])

    return validMoves


# arguments: (integer, integer, matrix)
# returns a matrix that has the specified ring spun the number of rotations
def spinRing(ring, rotations, puzzle):
    # print(type(puzzle))
    if not isinstance(puzzle, list):
        puzzle = puzzle.tolist()
    a = rotations % len(puzzle[ring])
    puzzle[ring] = puzzle[ring][-a:] + puzzle[ring][:-a]
    return puzzle


# arguments: (integer, integer, matrix)
# returns a matrix that has the specified slice shifted the number of shifts
def shiftSlice(pieslice, shifts, puzzle):
    # transpose the array to sort by column
    transposePuzzle = np.transpose(puzzle).tolist()
    newPuzzle = []
    # combine the columns that are directly opposite each other
    for i in range(0, 6):
        newPuzzle.append(transposePuzzle[i] + list(reversed(transposePuzzle[i + 6])))
    # print np.array(newPuzzle)

    # do the shifting
    a = shifts % len(newPuzzle[pieslice])
    newPuzzle[pieslice] = newPuzzle[pieslice][-a:] + newPuzzle[pieslice][:-a]
    # print np.array(newPuzzle)

    # split the combined columns and rearrange
    for i in range(0, 6):
        transposePuzzle[i] = newPuzzle[i][0:4]
    for i in range(6, 12):
        transposePuzzle[i] = list(reversed(newPuzzle[i - 6][4:8]))
    # print np.array(transposePuzzle)
    return np.transpose(transposePuzzle)


# arguments: matrix
# returns a boolean to whether the board state is solved or unsolved
def checkWin(puzzle):
    puzzleCopy = copy.deepcopy(puzzle)
    for row in range(0, len(puzzleCopy)):
        for col in range(0, len(puzzleCopy[row])):
            if puzzleCopy[row][col] == 1:
                if not hammerCheck(row, col, puzzleCopy) and not lineupCheck(col, puzzleCopy):
                    return False
    return True


# arguments: (integer, integer, matrix)
# returns a boolean to whether an enemy is eligible for a hammer combo
def hammerCheck(row, col, puzzle):
    # first check to see if the enemy is positioned on row 2
    if row == 2:
        if puzzle[3][col] == 0:  # enemies on row 2 must have enemies directly positioned below them
            return False

        if col < 11:
            # enemies must be adjacent to each other on the same row
            if puzzle[2][col - 1] == 0:  # if there is not an enemy to the left, then it must be on the right, and below
                if puzzle[2][col + 1] == 1 and puzzle[3][col + 1] == 1:  # remove enemies from board and return true
                    puzzle[2][col] = 0
                    puzzle[3][col] = 0
                    puzzle[2][col + 1] = 0
                    puzzle[3][col + 1] = 0
                    return True
                return False
            if puzzle[2][col + 1] == 0:  # if there is not an enemy to the right, then it must be on the left, and below
                if puzzle[2][col - 1] == 1 and puzzle[3][col - 1] == 1:
                    puzzle[2][col] = 0
                    puzzle[3][col] = 0
                    puzzle[2][col - 1] = 0
                    puzzle[3][col - 1] = 0
                    return True
                return False

        if col == 11:  # program the edge case
            if puzzle[2][col - 1] == 0:  # if there is not an enemy to the left, then it must be on the right, and below
                if puzzle[2][0] == 1 and puzzle[3][0] == 1:
                    puzzle[2][col] = 0
                    puzzle[3][col] = 0
                    puzzle[2][0] = 0
                    puzzle[3][0] = 0
                    return True
                return False
            if puzzle[2][0] == 0:  # if there is not an enemy to the right, then it must be on the left, and below
                if puzzle[2][col - 1] == 1 and puzzle[3][col - 1] == 1:
                    puzzle[2][col] = 0
                    puzzle[3][col] = 0
                    puzzle[2][col - 1] = 0
                    puzzle[3][col - 1] = 0
                    return True
                return False

    return False  # if the enemy is not located on 2, it is not eligible to be hammered


# arguments: (integer, matrix)
# returns a boolean to whether the enemy is eligible for a lineup attack
def lineupCheck(col, puzzle):
    # check if the column is filled with enemies
    enemiesArray = []
    for i in range(0, len(puzzle)):
        enemiesArray.append(puzzle[i][col])
    if enemiesArray.count(enemiesArray[0]) == len(enemiesArray) and enemiesArray[0] == 1:
        # remove enemies from the board and return true
        for i in range(0, len(puzzle)):
            puzzle[i][col] = 0
        return True
    return False


# driver

prompt = True
enemyCol = []
enemyRow = []
ringmoves = 3

puzzleBoard = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


numEnemies = input("Please enter the number of enemies: ")

if numEnemies != 0:
    for enemy in range(1, numEnemies + 1):
        enemyCol.append(input("Please enter the slice of enemy #" + str(enemy) + ": "))
        enemyRow.append(input("Please enter the ring of enemy #" + str(enemy) + ": "))

    ringmoves = input("Please enter the number of ring moves: ")

    for i in range(0, len(enemyRow)):
        puzzleBoard[enemyRow[i]][enemyCol[i]] = 1

else:
    puzzleBoard = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
                   [1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
                   [0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0],
                   [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]]
    ringmoves = 3
    prompt = False

print(np.array(puzzleBoard))

root = Node([puzzleBoard, ['root']], None, 0)

solutionTree = generateTree(root, ringmoves)
# print(str(tree))

youngestChildList = []
traverse(solutionTree, youngestChildList, ringmoves)
print('\n')
print(checkWinsList(youngestChildList))
