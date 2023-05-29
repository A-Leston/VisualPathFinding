import pygame
import sys
import numpy as np
import time

# **TODO: add fun stats to menu screen, add dropdown select for algorithm choice, then add more algorithms, possibly optimize run window function?

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
    path = []  # create empty list for path
    current = current_node  # start iterating through given node parent line
    while current is not None:  # for each node: add it to path list, then move to its parent node and repeat
        path.append(current.position)
        current = current.parent
    path = path[::-1]  # reverses path list as it was created backwards
    return path  # send back resulting path through maze


def AStarSearch(win, block_size, grid, start, end):
    # creates linked chain of nodes where root is start, and final child is end.
    start_node = Node(None, tuple(start))  # establish starting location
    end_node = Node(None, tuple(end))  # establish ending location
    to_visit = []  # create two lists to keep track of whats visited vs unvisited
    visited = []
    to_visit.append(start_node)  # add start node to to_visit list (unvisited)
    outer_iterations = 0
    max_iterations = (len(grid) // 2) ** 5  # establish max iterations for the search, based on size of maze

    move = [[-1, 0],  # establish the 4 possible moves: down, left, up, right
            [0, -1],
            [1, 0],
            [0, 1]]

    num_rows, num_columns = np.shape(grid)  # get dimensions of the given maze (length by width)

    while len(to_visit) > 0:  # start searching
        outer_iterations += 1  # start keeping count of search loops
        current_node = to_visit[0]  # start checking node by node
        current_index = 0
        for index, item in enumerate(to_visit):  # for each node by index in the unvisited list:
            if item.f < current_node.f:  # if another node has a lower f-score, move to that node
                current_node = item
                current_index = index

        if outer_iterations > max_iterations:  # if search loop count exceeds limit, say it cant be found
            print("Too many iterations done, cant find path")
            return returnPath(current_node)

        to_visit.pop(current_index)  # remove current node from unvisited and add it to visited list
        visited.append(current_node)

        if current_node == end_node:  # if current node is equal to end node then search is done
            return returnPath(current_node)  # sends path to return_path so it can be processed and output

        children = []  # create list for children nodes to be placed into, the steps in path

        for new_position in move:  # try each of the 4 possible moves:
            node_position = (current_node.position[0] + new_position[0],
                             current_node.position[1] + new_position[1])  # new_position is step, for step in moves...

            if (node_position[0] > (num_rows - 1)  # if it would result in an "out of bounds" position, skip it
                    or node_position[1] > (num_columns - 1)
                    or node_position[0] < 0
                    or node_position[1] < 0):
                continue

            if grid[node_position[0]][node_position[1]] == 1 or grid[node_position[0]][node_position[1]] == 5:
                continue  # if that position is a 1 or 5, skip it, means its a wall(1) or already checked(5)
            # removing 5 as a restriction will allow it to reconsider paths, but it will be much slower.

            new_node = Node(current_node, node_position)  # otherwise, pick that position as a new node (to check)
            children.append(new_node)  # and add it to the list of children
            for child in children:  # loop through each child in children list (looking for best next step)
                if len([visited_child for visited_child in visited if visited_child == child]) > 0:
                    continue  # skip if it would cause backtracking

                child.g = current_node.g + 1  # g keeps track of cost to traverse path (how many steps)

                # h used as a "distance to end" metric, calculated with euclidean function
                # child.h = (((child.position[0] - end_node.position[0]) ** 2) ** 1/2 + ((child.position[1] - end_node.position[1]) ** 2) ** 1/2)
                # this is essentially the educated guess of how to find its target, a more complex heuristic can be used
                # but with euclidean function its just going to try and move in the general direction of the endpoint

                # h using taxi-cab metric instead
                child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])

                child.f = child.g + child.h  # f is g + h, best path will have the lowest f-value

                if len([i for i in to_visit if child == i and child.f > i.f]) > 0:
                    continue  # skip child if its unvisited AND has a higher f-cost than another unvisited choice
                to_visit.append(child)  # otherwise, add that child to the unvisited list and re-loop (move there next)

                # ---below only for visual part---
                cpos = str(child.position[0]) + str(child.position[1])
                epos = str(end[0]) + str(end[1])
                if cpos != epos:  # to prevent endpoint from being recolored yellow
                    grid[child.position[0]][child.position[1]] = 5  # changing considered path to yellow

                win.drawGrid(block_size, grid)  # redraw screen to see path search in realtime

        pygame.event.pump()  # prevent pygame timeouts as its loading


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (125, 125, 125)


class Box:
    def __init__(self, x, y, block_size, state):
        self.position = (x, y)
        self.size = block_size
        self.state = state
        self.colors = [WHITE, BLACK, GREEN, RED, BLUE, YELLOW]
        self.color = self.colors[self.state]  # this makes state number correlate to color, 0 = white, 5 = yellow, ect

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.position[0], self.position[1], self.size, self.size))
        pygame.draw.rect(win, BLACK, (self.position[0], self.position[1], self.size, self.size), 1)


class Button:
    def __init__(self, position, length, width, color, text, text_color, text_size):
        self.position = position   # pos = (x, y)
        self.length = length
        self.width = width
        self.rect = pygame.Rect(position[0], position[1], length, width)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.text_size = text_size

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)
        font = pygame.font.Font('freesansbold.ttf', self.text_size)
        text = font.render(self.text, True, self.text_color, self.color)
        text_rect = text.get_rect(center=self.rect.center)
        win.blit(text, text_rect)


class Window:
    def __init__(self, width, height, rel_menu_size, grid_size):
        self.width = width
        self.height = height
        self.rel_menu_size = rel_menu_size
        self.grid_size = grid_size
        self.win = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)  # Create the outer screen
        self.game_screen = pygame.Surface((int(self.width * (1 - self.rel_menu_size)), int(self.width * (1 - self.rel_menu_size))))  # Create the first inner screen (game screen)
        self.menu_screen = pygame.Surface((self.width * self.rel_menu_size, self.height))  # Create the second inner screen (menu screen)
        self.buttons = []
        self.runWindow()

    def drawGrid(self, block_size, grid):  # given grid should be 2D array of values 0-5
        x_pos = 0
        y_pos = 0
        for row in grid:
            for col in row:
                grid_box = Box(x_pos, y_pos, block_size, col)
                grid_box.draw(self.game_screen)
                x_pos += block_size
            y_pos += block_size
            x_pos = 0
        self.win.blit(self.game_screen, (0, 0))
        pygame.display.update()

    def drawMenu(self):
        self.buttons = []
        pygame.draw.rect(self.menu_screen, GRAY, (0, 0, self.menu_screen.get_width(), self.menu_screen.get_height()))  # menu background
        margin = int(self.menu_screen.get_width() * 0.1)
        button_len = int(self.menu_screen.get_width() * 0.5)
        button_width = int(self.menu_screen.get_height() * 0.07)
        text_size = int(self.menu_screen.get_height() * 0.025)

        # Create buttons
        button_position = (int(self.menu_screen.get_width() * 0.25), int(self.menu_screen.get_height() * 0.85))
        run_button = Button(button_position, button_len, button_width, GREEN, 'Run', BLACK, text_size)
        self.buttons.append(run_button)

        button_position = (button_position[0], button_position[1] - button_width - margin)
        reset_button = Button(button_position, button_len, button_width, RED, 'Reset', BLACK, text_size)
        self.buttons.append(reset_button)

        # Draw buttons
        run_button.draw(self.menu_screen)
        reset_button.draw(self.menu_screen)
        self.win.blit(self.menu_screen, (self.game_screen.get_width(), 0))
        pygame.display.update()

    def runWindow(self):
        grid = [[0 for i in range(self.grid_size)] for j in range(self.grid_size)]  # creating grid of 0's
        grid[0][0] = 2  # placing default start node
        grid[self.grid_size - 1][self.grid_size - 1] = 3  # placing default end node
        start = [0, 0]  # storing start node
        end = [self.grid_size - 1, self.grid_size - 1]  # storing end node
        running = True
        searched = False
        left_hold = False
        right_hold = False
        while running:  # start of main loop
            block_size = (self.game_screen.get_height() // self.grid_size)
            self.drawGrid(block_size, grid)
            self.drawMenu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:   # to close properly
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    self.win = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    if int(event.w * (1 - self.rel_menu_size)) > event.h:   # 2 setups for game screen to ensure it never cuts off screen with rescales
                        self.game_screen = pygame.Surface((int(event.w * (1 - self.rel_menu_size)), event.h))  # Create the first inner screen (game screen)
                    else:
                        self.game_screen = pygame.Surface((int(event.w * (1 - self.rel_menu_size)), int(event.w * (1 - self.rel_menu_size))))
                    self.menu_screen = pygame.Surface((event.w * self.rel_menu_size, event.h))  # Create the second inner screen (menu screen)

                # left click in grid to add wall blocks
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                        and pygame.mouse.get_pos()[0] < self.game_screen.get_width() \
                        and pygame.mouse.get_pos()[1] < self.game_screen.get_height():
                    left_hold = True
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // block_size
                    row = pos[1] // block_size
                    if col >= gridSize:
                        col = gridSize - 1
                    if row >= gridSize:
                        row = gridSize - 1
                    if grid[row][col] == 0:
                        grid[row][col] = 1

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # for dragging
                    left_hold = False

                # right click in grid to remove wall blocks
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 \
                        and pygame.mouse.get_pos()[0] < self.game_screen.get_width() \
                        and pygame.mouse.get_pos()[1] < self.game_screen.get_height():
                    right_hold = True
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // block_size
                    row = pos[1] // block_size
                    if col >= gridSize:
                        col = gridSize - 1
                    if row >= gridSize:
                        row = gridSize - 1
                    if grid[row][col] == 1:
                        grid[row][col] = 0

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:  # for dragging
                    right_hold = False

                elif event.type == pygame.MOUSEMOTION \
                        and pygame.mouse.get_pos()[0] < self.game_screen.get_width() \
                        and pygame.mouse.get_pos()[1] < self.game_screen.get_height():      # also for dragging
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // block_size
                    row = pos[1] // block_size
                    if col >= gridSize:
                        col = gridSize - 1
                    if row >= gridSize:
                        row = gridSize - 1
                    if left_hold and grid[row][col] == 0:  # left hold adds walls while dragging
                            grid[row][col] = 1    # if empty spot (label 0), turn it into a wall (label 1)
                    elif right_hold and grid[row][col] == 1:  # right hold removes walls while dragging
                            grid[row][col] = 0   # if wall (label 1), turn it into a empty spot (label 0)

                # if clicked in "run" box, then run the thing
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                        and self.buttons[0].position[0] + self.game_screen.get_width() + self.buttons[0].length > pygame.mouse.get_pos()[0] > self.buttons[0].position[0] + self.game_screen.get_width() \
                        and self.buttons[0].position[1] + self.buttons[0].width > pygame.mouse.get_pos()[1] > self.buttons[0].position[1]:

                    t0 = time.time()
                    path = AStarSearch(self, block_size, grid, start, end)  # calling A*, and timing it
                    t1 = time.time()

                    for x in range(1, len(path) - 1):  # makes the path blue, except for start/end nodes
                        step = path[x]
                        grid[step[0]][step[1]] = 4  # the change to blue (4 = blue)

                    searched = True
                    print("path found!")  # fun stats :D
                    print("the path is " + str(len(path) - 1) + " steps.")
                    print("the search took " + str("{:.3f}".format(t1 - t0)) + " seconds.")

                # if clicked in "reset" box then reset the thing
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                        and self.buttons[1].position[0] + self.game_screen.get_width() + self.buttons[1].length > pygame.mouse.get_pos()[0] > self.buttons[1].position[0] + self.game_screen.get_width() \
                        and self.buttons[1].position[1] + self.buttons[1].width > pygame.mouse.get_pos()[1] > self.buttons[1].position[1]:

                    grid = [[0 for i in range(self.grid_size)] for j in range(self.grid_size)]  # makes new grid
                    grid[0][0] = 2  # places start point (2 = green)
                    grid[self.grid_size - 1][self.grid_size - 1] = 3  # places end point (3 = red)
                    start = [0, 0]  # store start
                    end = [self.grid_size - 1, self.grid_size - 1]  # store end
                    searched = False  # clear search state

                # for keyboard presses (some buttons repeated but for keyboard now)
                elif event.type == pygame.KEYDOWN:
                    # space key will reset everything to default
                    if event.key == pygame.K_SPACE:
                        grid = [[0 for i in range(self.grid_size)] for j in range(self.grid_size)]  # makes new grid
                        grid[0][0] = 2  # places start point (2 = green)
                        grid[self.grid_size - 1][self.grid_size - 1] = 3  # places end point (3 = red)
                        start = [0, 0]  # store start
                        end = [self.grid_size - 1, self.grid_size - 1]  # store end
                        searched = False  # clear search state

                    # enter key will preform the A* search
                    elif event.key == pygame.K_RETURN and not searched:
                        t0 = time.time()
                        path = AStarSearch(self, block_size, grid, start, end)  # calling A*, and timing it
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
                            and (pygame.mouse.get_pos()[0] // block_size) < self.grid_size \
                            and (pygame.mouse.get_pos()[1] // block_size) < self.grid_size:
                        pos = pygame.mouse.get_pos()
                        col = pos[0] // block_size
                        row = pos[1] // block_size
                        if [col, row] != end:  # if new point isnt the end point
                            grid[start[0]][start[1]] = 0  # changes previous start to a 0
                            grid[row][col] = 2  # assigns new start position (2 = green)
                            start = [row, col]  # store new start

                    # the "2" key moves end point
                    elif event.key == pygame.K_2 \
                            and (pygame.mouse.get_pos()[0] // block_size) < self.grid_size \
                            and (pygame.mouse.get_pos()[1] // block_size) < self.grid_size:
                        pos = pygame.mouse.get_pos()
                        col = pos[0] // block_size
                        row = pos[1] // block_size
                        if [col, row] != start:  # if new point isnt start point
                            grid[end[0]][end[1]] = 0  # changes previous end to a 0
                            grid[row][col] = 3  # assigns new end position (3 = red)
                            end = [row, col]  # store new end


if __name__ == '__main__':
    pygame.init()
    length = 1000                      # height of window, width will be larger to fit side menu
    width = 750
    rel_menu_size = 0.25
    gridSize = 20                     # size of grid, x by x blocks
    window = Window(length, width, rel_menu_size, gridSize)
