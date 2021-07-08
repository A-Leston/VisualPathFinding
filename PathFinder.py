import pygame
import sys
import numpy as np

# search algorithim program by Ariel Leston.
# "left click" to add walls, "right click" to remove walls
# "1" to move starting position, "2" to move end position, "enter" to search, "space" to reset
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

win_size = 500                      # changes how window will scale. x by x window
grid_size = 20                      # changes how grid will scale. x by x grid
block_size = win_size // grid_size
win = pygame.display.set_mode((win_size, win_size))


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


def AStarSearch(maze, cost, start, end):
    # creates linked chain of nodes where root is start, and final child is end.
    start_node = Node(None, tuple(start))          # establish starting location
    start_node.g = start_node.h = start_node.f = 0

    end_node = Node(None, tuple(end))              # establish ending location
    end_node.g = end_node.h = end_node.f = 0

    to_visit = []                                  # create two lists to keep track of whats visited vs unvisited
    visited = []

    to_visit.append(start_node)                    # add start node to to_visit list (unvisited)

    outer_iterations = 0
    max_iterations = (len(maze) // 2) ** 5         # establish max iterations for the search, based on size of maze

    move = [[-1, 0],                               # establish the 4 possible moves: down, left, up, right
            [0, -1],
            [1, 0],
            [0, 1]]

    num_rows, num_columns = np.shape(maze)         # get dimensions of the given maze (length by width)

    while len(to_visit) > 0:                       # start searching
        outer_iterations += 1                      # start keeping count of search loops
        current_node = to_visit[0]                 # start checking node by node
        current_index = 0
        for index, item in enumerate(to_visit):    # for each node by index in the unvisited list:
            pygame.event.pump()                    # to prevent pygame from timing out on long loads

            if item.f < current_node.f:            # if another node has a lower f-score, move to that node
                current_node = item
                current_index = index

        if outer_iterations > max_iterations:      # if search loop count exceeds limit, say it cant be found
            print("Too many iterations done, cant find path")
            return returnPath(current_node)

        to_visit.pop(current_index)                # remove current node from unvisited and add it to visited list
        visited.append(current_node)

        if current_node == end_node:               # if current node is equal to end node then search is done
            print("Done! It took " + str(outer_iterations) + " iterations to find the path.")
            return returnPath(current_node)        # sends path to return_path so it can be processed and output

        children = []                              # create list for children nodes to be placed into, the steps in path

        for new_position in move:                  # try each of the 4 possible moves:
            pygame.event.pump()                    # to prevent pygame from timing out on long loads
            node_position = (current_node.position[0] + new_position[0],
                             current_node.position[1] + new_position[1])

            if (node_position[0] > (num_rows - 1)           # if it would result in an "out of bounds" position, skip it
                    or node_position[1] > (num_columns - 1)
                    or node_position[0] < 0
                    or node_position[1] < 0):
                continue

            if maze[node_position[0]][node_position[1]] == 1:  # if that position is not 0, skip it, means its a wall
                continue

            new_node = Node(current_node, node_position)   # otherwise, pick that position as a new node (to check)
            children.append(new_node)                      # and add it to the list of children
            for child in children:               # loop through each child in children list (looking for best next step)
                pygame.event.pump()              # to prevent pygame from timing out on long loads

                if len([visited_child for visited_child in visited if visited_child == child]) > 0:
                    continue                               # if this child node has already been visited then skip it

                child.g = current_node.g + cost            # g keeps track of cost to traverse path (how many steps)

                child.h = (((child.position[0] - end_node.position[0]) ** 2) ** 1/2 +
                           ((child.position[1] - end_node.position[1]) ** 2) ** 1/2)
                # h used as a "distance to end" metric, calculated with euclidean function

                child.f = child.g + child.h                # f is g + h, best path will have the lowest f-value

                if len([i for i in to_visit if child == i and child.g > i.g]) > 0:
                    grid[child.position[0]][child.position[1]] = 5  # changing considered path to yellow
                    continue         # skip child if its unvisited AND has a higher g-cost than another unvisited choice

                if child.position[0] != end[0] and child.position[1] != end[1]:
                    grid[child.position[0]][child.position[1]] = 5  # changing considered path to yellow

                drawGrid()
                pygame.display.update()
                to_visit.append(child)    # otherwise, add that child to the unvisited list and re-loop (move here next)
        print("Iterations: " + str(outer_iterations))


def drawGrid():
    win.fill(WHITE)
    x_pos = 0
    y_pos = 0
    for row in grid:
        for col in row:
            if col == 0:
                pygame.draw.rect(win, BLACK, (x_pos, y_pos, block_size, block_size), 1)  # white box (available path)
            elif col == 1:
                pygame.draw.rect(win, BLACK, (x_pos, y_pos, block_size, block_size))     # solid black box (wall)
            elif col == 2:
                pygame.draw.rect(win, GREEN, (x_pos, y_pos, block_size, block_size))     # solid green box (start)
            elif col == 3:
                pygame.draw.rect(win, RED, (x_pos, y_pos, block_size, block_size))       # solid red box (end)
            elif col == 4:
                pygame.draw.rect(win, BLUE, (x_pos, y_pos, block_size, block_size))      # solid blue box (taken path)
            elif col == 5:
                pygame.draw.rect(win, YELLOW, (x_pos, y_pos, block_size, block_size))    # yellow box (considered path)
            x_pos += block_size
        y_pos += block_size
        x_pos = 0


if __name__ == '__main__':
    grid = [[0 for i in range(grid_size)] for j in range(grid_size)]    # creating grid of 0's
    grid[0][0] = 2                                                      # placing default start node
    grid[grid_size - 1][grid_size - 1] = 3                              # placing default end node
    start = [0, 0]                                                      # storing start node
    end = [grid_size - 1, grid_size - 1]                                # storing end node
    cost = 1
    searched = False
    clock = pygame.time.Clock()
    running = True
    left_hold = False
    right_hold = False
    while running:                                                      # start of main loop
            drawGrid()
            for event in pygame.event.get():                            # to close properly
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # left click to add wall blocks
                    left_hold = True
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // block_size
                    row = pos[1] // block_size
                    if grid[row][col] == 0:
                        grid[row][col] = 1

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    left_hold = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # right click to remove wall blocks
                    right_hold = True
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // block_size
                    row = pos[1] // block_size
                    if grid[row][col] == 1:
                        grid[row][col] = 0

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    right_hold = False

                elif event.type == pygame.MOUSEMOTION:
                    if left_hold:                                              # left hold adds walls while dragging
                        pos = pygame.mouse.get_pos()
                        col = pos[0] // block_size
                        row = pos[1] // block_size
                        if grid[row][col] == 0:
                            grid[row][col] = 1
                    elif right_hold:                                           # right hold removes walls while dragging
                        pos = pygame.mouse.get_pos()
                        col = pos[0] // block_size
                        row = pos[1] // block_size
                        if grid[row][col] == 1:
                            grid[row][col] = 0

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:                         # space key will reset everything to default
                        grid = [[0 for i in range(grid_size)] for j in range(grid_size)]
                        grid[0][0] = 2
                        grid[grid_size - 1][grid_size - 1] = 3
                        start = [0, 0]
                        end = [grid_size - 1, grid_size - 1]
                        searched = False

                    elif event.key == pygame.K_RETURN and not searched:     # enter key will preform the A* search
                        path = AStarSearch(grid, cost, start, end)
                        for x in range(len(path) - 1):                # makes the path blue, except for start/end nodes
                            if x != 0:                                # ignores first and last in path
                                step = path[x]
                                grid[step[0]][step[1]] = 4            # the change to blue (4 = blue)
                        searched = True

                    elif event.key == pygame.K_1:                            # the "1" key moves start point
                        pos = pygame.mouse.get_pos()
                        col = pos[0] // block_size
                        row = pos[1] // block_size
                        if pos != end[0]:                              # if new point isnt the end point
                            grid[start[0]][start[1]] = 0               # changes previous start to a 0
                            grid[row][col] = 2                         # assigns new start position (2 = green)
                            start = [row, col]                         # store new start

                    elif event.key == pygame.K_2:                            # the "2" key moves end point
                        pos = pygame.mouse.get_pos()
                        col = pos[0] // block_size
                        row = pos[1] // block_size
                        if pos != start[0]:                            # if new point isnt the start point
                            grid[end[0]][end[1]] = 0                   # changes previous end to a 0
                            grid[row][col] = 3                         # assigns new end position (3 = red)
                            end = [row, col]                           # store new end

            clock.tick(60)
            pygame.display.update()
