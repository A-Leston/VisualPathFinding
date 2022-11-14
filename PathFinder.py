import pygame
import sys
import numpy as np
import time

# search algorithim program by Ariel Leston.
# "left click" to add walls, "right click" to remove walls
# "1" to move starting position, "2" to move end position, "enter" to search, "space" to reset


class Node:
    def __init__(self, parent=None, position=None):     # defining node class, each node will correspond to a coordinate
        self.parent = parent                            # the path will be a linked chain of nodes
        self.position = position
        self.g = 0                                      # g is used for tracking total cost of path
        self.h = 0                                      # h is used for distance metric of current node to end node
        self.f = 0                                      # f is g + h, lowest f score will be best path

    def __eq__(self, other):
        return self.position == other.position          # allowing nodes to be checked for equality based on coordinates


def returnPath(current_node):
    # gets called by search, after finding path from start to end
    # current_node should be end point, with its parent line being the path back to start point
    path = []                              # create empty list for path
    current = current_node                 # start iterating through given node parent line
    while current is not None:             # for each node: add it to path list, then move to its parent node and repeat
        path.append(current.position)
        current = current.parent
    path = path[::-1]                      # reverses path list as it was created backwards
    return path                            # send back resulting path through maze


def AStarSearch(win, block_size, grid, start, end):
    # creates linked chain of nodes where root is start, and final child is end.
    start_node = Node(None, tuple(start))          # establish starting location
    end_node = Node(None, tuple(end))              # establish ending location

    to_visit = []                                  # create two lists to keep track of whats visited vs unvisited
    visited = []

    to_visit.append(start_node)                    # add start node to to_visit list (unvisited)

    outer_iterations = 0
    max_iterations = (len(grid) // 2) ** 5         # establish max iterations for the search, based on size of maze

    move = [[-1, 0],                               # establish the 4 possible moves: down, left, up, right
            [0, -1],
            [1, 0],
            [0, 1]]

    num_rows, num_columns = np.shape(grid)         # get dimensions of the given maze (length by width)

    while len(to_visit) > 0:                       # start searching
        outer_iterations += 1                      # start keeping count of search loops
        current_node = to_visit[0]                 # start checking node by node
        current_index = 0
        for index, item in enumerate(to_visit):    # for each node by index in the unvisited list:
            if item.f < current_node.f:            # if another node has a lower f-score, move to that node
                current_node = item
                current_index = index

        if outer_iterations > max_iterations:      # if search loop count exceeds limit, say it cant be found
            print("Too many iterations done, cant find path")
            return returnPath(current_node)

        to_visit.pop(current_index)                # remove current node from unvisited and add it to visited list
        visited.append(current_node)

        if current_node == end_node:               # if current node is equal to end node then search is done
            return returnPath(current_node)        # sends path to return_path so it can be processed and output

        children = []                              # create list for children nodes to be placed into, the steps in path

        for new_position in move:                  # try each of the 4 possible moves:
            node_position = (current_node.position[0] + new_position[0],
                             current_node.position[1] + new_position[1])

            if (node_position[0] > (num_rows - 1)           # if it would result in an "out of bounds" position, skip it
                    or node_position[1] > (num_columns - 1)
                    or node_position[0] < 0
                    or node_position[1] < 0):
                continue

            if grid[node_position[0]][node_position[1]] == 1 or grid[node_position[0]][node_position[1]] == 5:
                continue            # if that position is a 1 or 5, skip it, means its a wall(1) or already checked(5)
            # removing 5 as a restriction will allow it to reconsider paths, but it will be much slower.

            new_node = Node(current_node, node_position)   # otherwise, pick that position as a new node (to check)
            children.append(new_node)                      # and add it to the list of children
            for child in children:               # loop through each child in children list (looking for best next step)
                if len([visited_child for visited_child in visited if visited_child == child]) > 0:
                    continue                        # skip if it would cause backtracking

                child.g = current_node.g + 1            # g keeps track of cost to traverse path (how many steps)

                # h used as a "distance to end" metric, calculated with euclidean function
                # child.h = (((child.position[0] - end_node.position[0]) ** 2) ** 1/2 + ((child.position[1] - end_node.position[1]) ** 2) ** 1/2)

                # h using taxi-cab metric instead
                child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])

                # this is essentially the educated guess of how to find its target, a more complex heuristic can be used
                # but with euclidean function its just going to try and move in the general direction of the endpoint

                child.f = child.g + child.h                # f is g + h, best path will have the lowest f-value

                cpos = str(child.position[0]) + str(child.position[1])
                epos = str(end[0]) + str(end[1])
                if cpos != epos:                                    # to prevent endpoint from being recolored
                    grid[child.position[0]][child.position[1]] = 5  # changing considered path to yellow

                if len([i for i in to_visit if child == i and child.f > i.f]) > 0:
                    continue        # skip child if its unvisited AND has a higher f-cost than another unvisited choice

                to_visit.append(child)    # otherwise, add that child to the unvisited list and re-loop (move here next)

                drawGrid(win, block_size, grid)  # to see path search in realtime
        pygame.event.pump()    # prevent pygame timeouts


def drawGrid(win, block_size, grid):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    x_pos = 0
    y_pos = 0
    for row in grid:
        for col in row:
            if col == 0:
                pygame.draw.rect(win, WHITE, (x_pos, y_pos, block_size, block_size))     # white box (available path)
                pygame.draw.rect(win, BLACK, (x_pos, y_pos, block_size, block_size), 1)  # border
            elif col == 1:
                pygame.draw.rect(win, BLACK, (x_pos, y_pos, block_size, block_size))     # solid black box (wall)
            elif col == 2:
                pygame.draw.rect(win, GREEN, (x_pos, y_pos, block_size, block_size))     # green box (start)
                pygame.draw.rect(win, BLACK, (x_pos, y_pos, block_size, block_size), 1)  # border
            elif col == 3:
                pygame.draw.rect(win, RED, (x_pos, y_pos, block_size, block_size))       # red box (end)
                pygame.draw.rect(win, BLACK, (x_pos, y_pos, block_size, block_size), 1)  # border
            elif col == 4:
                pygame.draw.rect(win, BLUE, (x_pos, y_pos, block_size, block_size))      # blue box (taken path)
                pygame.draw.rect(win, BLACK, (x_pos, y_pos, block_size, block_size), 1)  # border
            elif col == 5:
                pygame.draw.rect(win, YELLOW, (x_pos, y_pos, block_size, block_size))    # box (considered path)
                pygame.draw.rect(win, BLACK, (x_pos, y_pos, block_size, block_size), 1)  # border
            x_pos += block_size
        y_pos += block_size
        x_pos = 0

    pygame.display.update()


def drawMenu(win):
    GRAY = (125, 125, 125)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)
    menuWidth = win.get_width() - win.get_height()
    pygame.draw.rect(win, GRAY, (win.get_height(), 0, menuWidth, win.get_height()))  # menu background
    margin = int(win.get_height() * 0.05)
    buttonSize = (menuWidth - margin*2, int(win.get_height() * 0.05))

    # first the run button
    x_pos = win.get_height() + margin  # menu area starts where grid ends, and grid length = height of window (since its square)
    y_pos = win.get_height() - buttonSize[1] - margin
    pygame.draw.rect(win, GREEN, (x_pos, y_pos, buttonSize[0], buttonSize[1]))  # button
    font = pygame.font.Font('freesansbold.ttf', 25)
    text = font.render('Run', True, (0, 0, 0), GREEN)
    textRect = text.get_rect()
    textRect.center = (x_pos + buttonSize[0]//2,  y_pos + buttonSize[1]//2)
    win.blit(text, textRect)

    # then the reset button
    y_pos = win.get_height() - buttonSize[1] - 3*margin
    pygame.draw.rect(win, RED, (x_pos, y_pos, buttonSize[0], buttonSize[1]))  # button
    font = pygame.font.Font('freesansbold.ttf', 25)
    text = font.render('Reset', True, (0, 0, 0), RED)
    textRect = text.get_rect()
    textRect.center = (x_pos + buttonSize[0]//2,  y_pos + buttonSize[1]//2)
    win.blit(text, textRect)
    pygame.display.update()


def runWindow(win, grid_size):
    block_size = (win.get_height() // grid_size)
    grid = [[0 for i in range(grid_size)] for j in range(grid_size)]  # creating grid of 0's
    grid[0][0] = 2  # placing default start node
    grid[grid_size - 1][grid_size - 1] = 3  # placing default end node
    start = [0, 0]  # storing start node
    end = [grid_size - 1, grid_size - 1]  # storing end node
    running = True
    searched = False
    left_hold = False
    right_hold = False
    drawMenu(win)
    while running:  # start of main loop
        drawGrid(win, block_size, grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # to close properly
                pygame.quit()
                sys.exit()

            # left click in grid to add wall blocks
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and (pygame.mouse.get_pos()[0] // block_size) < grid_size \
                    and (pygame.mouse.get_pos()[1] // block_size) < grid_size:
                left_hold = True
                pos = pygame.mouse.get_pos()
                col = pos[0] // block_size
                row = pos[1] // block_size
                if grid[row][col] == 0:
                    grid[row][col] = 1

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # for dragging
                left_hold = False

            # right click in grid to remove wall blocks
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 \
                    and (pygame.mouse.get_pos()[0] // block_size) < grid_size \
                    and (pygame.mouse.get_pos()[1] // block_size) < grid_size:
                right_hold = True
                pos = pygame.mouse.get_pos()
                col = pos[0] // block_size
                row = pos[1] // block_size
                if grid[row][col] == 1:
                    grid[row][col] = 0

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:  # for dragging
                right_hold = False

            elif event.type == pygame.MOUSEMOTION \
                    and (pygame.mouse.get_pos()[0] // block_size) < grid_size \
                    and (pygame.mouse.get_pos()[1] // block_size) < grid_size:      # also for dragging
                pos = pygame.mouse.get_pos()
                col = pos[0] // block_size
                row = pos[1] // block_size
                if left_hold and grid[row][col] == 0:  # left hold adds walls while dragging
                        grid[row][col] = 1    # if empty spot (label 0), turn it into a wall (label 1)
                elif right_hold and grid[row][col] == 1:  # right hold removes walls while dragging
                        grid[row][col] = 0   # if wall (label 1), turn it into a empty spot (label 0)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and (win.get_height() + int(win.get_height() * 0.05)) < pygame.mouse.get_pos()[0] < (win.get_width() - int(win.get_height() * 0.05)) \
                    and (win.get_height() - (int(win.get_height() * 0.1))) < pygame.mouse.get_pos()[1] < (win.get_height() - int(win.get_height() * 0.05)):
                # if clicked in "run" box, then run the thing
                t0 = time.time()
                path = AStarSearch(win, block_size, grid, start, end)  # calling A*, and timing it
                t1 = time.time()

                for x in range(1, len(path) - 1):  # makes the path blue, except for start/end nodes
                    step = path[x]
                    grid[step[0]][step[1]] = 4  # the change to blue (4 = blue)

                searched = True
                print("path found!")  # fun stats :D  ***probly want this being put to screen aswell
                print("the path is " + str(len(path) - 1) + " steps.")
                print("the search took " + str("{:.3f}".format(t1 - t0)) + " seconds.")

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                 and (win.get_height() + int(win.get_height() * 0.05)) < pygame.mouse.get_pos()[0] < (win.get_width() - int(win.get_height() * 0.05)) \
                 and (win.get_height() - (int(win.get_height() * 0.2))) < pygame.mouse.get_pos()[1] < (win.get_height() - int(win.get_height() * 0.15)):
                # if clicked in "reset" box then reset the thing
                grid = [[0 for i in range(grid_size)] for j in range(grid_size)]  # makes new grid
                grid[0][0] = 2  # places start point (2 = green)
                grid[grid_size - 1][grid_size - 1] = 3  # places end point (3 = red)
                start = [0, 0]  # store start
                end = [grid_size - 1, grid_size - 1]  # store end
                searched = False  # clear search state

            elif event.type == pygame.KEYDOWN:  # for keyboard presses (some buttons repeated but for keyboard now)
                if event.key == pygame.K_SPACE:  # space key will reset everything to default
                    grid = [[0 for i in range(grid_size)] for j in range(grid_size)]  # makes new grid
                    grid[0][0] = 2  # places start point (2 = green)
                    grid[grid_size - 1][grid_size - 1] = 3  # places end point (3 = red)
                    start = [0, 0]  # store start
                    end = [grid_size - 1, grid_size - 1]  # store end
                    searched = False  # clear search state

                elif event.key == pygame.K_RETURN and not searched:  # enter key will preform the A* search
                    t0 = time.time()
                    path = AStarSearch(win, block_size, grid, start, end)  # calling A*, and timing it
                    t1 = time.time()

                    for x in range(1, len(path) - 1):  # makes the path blue, except for start/end nodes
                        step = path[x]
                        grid[step[0]][step[1]] = 4  # the change to blue (4 = blue)

                    searched = True
                    print("path found!")  # fun stats :D
                    print("the path is " + str(len(path) - 1) + " steps.")
                    print("the search took " + str("{:.3f}".format(t1 - t0)) + " seconds.")

                # the "1" key moves start point
                elif event.key == pygame.K_1 \
                        and (pygame.mouse.get_pos()[0] // block_size) < grid_size \
                        and (pygame.mouse.get_pos()[1] // block_size) < grid_size:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // block_size
                    row = pos[1] // block_size
                    if [col, row] != end:  # if new point isnt the end point
                        grid[start[0]][start[1]] = 0  # changes previous start to a 0
                        grid[row][col] = 2  # assigns new start position (2 = green)
                        start = [row, col]  # store new start

                # the "2" key moves end point
                elif event.key == pygame.K_2 \
                        and (pygame.mouse.get_pos()[0] // block_size) < grid_size \
                        and (pygame.mouse.get_pos()[1] // block_size) < grid_size:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // block_size
                    row = pos[1] // block_size
                    if [col, row] != start:  # if new point isnt start point
                        grid[end[0]][end[1]] = 0  # changes previous end to a 0
                        grid[row][col] = 3  # assigns new end position (3 = red)
                        end = [row, col]  # store new end


if __name__ == '__main__':
    pygame.init()
    size = 900                      # height of window, width will be larger to fit side menu
    win = pygame.display.set_mode((int(size * 1.25), size))  # window width by window height
    gSize = 20                      # size of grid, x by x blocks
    runWindow(win, gSize)
