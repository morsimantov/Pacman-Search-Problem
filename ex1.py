import search
import math
import utils

id="No numbers - I'm special!"

""" Rules """
RED = 20
BLUE = 30
YELLOW = 40
GREEN = 50
PACMAN = 77
WALL = 99
PILL = 11
EMPTY = 10
PACMAN_EATEN = 88
RED_PILL = 21
BLUE_PILL = 31
YELLOW_PILL = 41
GREEN_PILL = 51
PACMAN_POSITION = 7
RED_POSITION = 2
BLUE_POSITION = 3
YELLOW_POSITION = 4
GREEN_POSITION = 5
UP = 'U'
DOWN = 'D'
RIGHT = 'R'
LEFT = 'L'

class PacmanProblem(search.Problem):
    """This class implements a pacman problem"""
    def __init__(self, initial):
        """ Magic numbers for ghosts and Packman: 
        2 - red, 3 - blue, 4 - yellow, 5 - green and 7 - Packman.""" 

        self.locations = dict.fromkeys((7, 2, 3, 4, 5))
        self.dead_end = False

        self.update_locations(initial)

        """ Constructor only needs the initial state.
        Don't forget to set the goal or implement the goal test"""
        search.Problem.__init__(self, initial)

    def successor(self, state):
        """ Generates the successor state """
        successors = []
        # Update locations of the ghost and pacman
        self.update_locations(state)
        # Get the pacman location
        pacman_x, pacman_y = self.get_pacman_position()
        if pacman_x is None or pacman_y is None:
            return tuple(successors)
        # Define possible moves
        moves = [(pacman_x - 1, pacman_y, UP), (pacman_x + 1, pacman_y, DOWN), (pacman_x, pacman_y - 1, LEFT),
                 (pacman_x, pacman_y + 1, RIGHT)]
        # If the pacman is eaten in the given state, don't expand that state
        if state[pacman_x][pacman_y] == PACMAN_EATEN:
            self.dead_end = True
            return tuple(successors)
        # Go through each possible move
        for move in moves:
            new_x, new_y, action = move
            # If the move is valid
            if self.is_valid_move_pacman(state, (new_x, new_y)):
                # Generate the new state after the move
                new_state = self.result(state, (new_x, new_y))
                # Append the move if it's not None
                if new_state is not None:
                    successors.append((action, tuple(map(tuple, new_state))))

        return tuple(successors)

    def result(self, state, move):
        """given state and an action and return a new state"""
        # Coordinates of the new position of pacman after the move
        new_pacman_x, new_pacman_y = move
        # Set a new state similar to the old state
        new_state = [list(row) for row in state]
        # Move pacman to the new position
        new_state = self.move_pacman(move, state, new_state)
        # Return the new state with the eaten pacman without expanding it
        if new_state[new_pacman_x][new_pacman_y] == PACMAN_EATEN:
            return new_state
        # Update the state after moving pacman
        state = [list(row) for row in new_state]
        # Move the ghosts one nby one after move of pacman
        new_state = self.move_ghosts(move, state, new_state)
        # Check if the new position of pacman contains a ghost after ghost moves
        if new_state[new_pacman_x][new_pacman_y] in (RED, BLUE, YELLOW, GREEN, RED_PILL, BLUE_PILL, GREEN_PILL,
                                                     YELLOW_PILL):
            # Pacman is eaten by a ghost (=88)
            new_state[new_pacman_x][new_pacman_y] = PACMAN_EATEN
        # Return the new state
        return tuple(tuple(row) for row in new_state)

    def goal_test(self, state):
        """ given a state, checks if this is the goal state, compares to the created goal state"""
        for row in state:
            for cell in row:
                # If there's a pill in this cell
                if cell in (PILL, RED_PILL, BLUE_PILL, GREEN_PILL, YELLOW_PILL, PACMAN_EATEN):
                    # There are still tiles with pills left
                    return False
        # All tiles with pills have been consumed
        return True

    def h(self, node):
        """ This is the heuristic. It get a node (not a state)
        and returns a goal distance estimate"""
        # Find the coordinates of the nearest pill
        nearest_pill_coordinates = self.find_nearest_pill(node.state)
        pacman_position = self.get_pacman_position()
        if pacman_position is not None and nearest_pill_coordinates is not None:
            x, y = pacman_position
            # Calculate the Manhattan distance between the current state and the nearest pill
            return abs(x - nearest_pill_coordinates[0]) + abs(y - nearest_pill_coordinates[1])
        else:
            # Handle the case where either pacman_position or nearest_pill_coordinates is None
            return 0

    def find_nearest_pill(self, state):
        """Find the coordinates of the nearest pill in the given state"""
        nearest_pill_coordinates = None
        # Initialize nearest_distance to positive infinity
        nearest_distance = float('inf')

        for i in range(len(state)):
            for j in range(len(state[i])):
                # Check if the current cell contains a pill
                if state[i][j] in (PILL, RED_PILL, BLUE_PILL, GREEN_PILL, YELLOW_PILL):
                    # Calculate Manhattan distance from Pacman's position to the pill
                    distance = abs(i - self.locations[7][0]) + abs(j - self.locations[7][1])
                    # If the calculated distance is smaller than the current nearest_distance, update it
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_pill_coordinates = (i, j)

        return nearest_pill_coordinates

    def is_valid_move_pacman(self, state, move):
        """ Helper function to check if a move is valid for Pacman"""
        x, y = move

        # Check if the move is within the bounds of the matrix
        if 0 <= x < len(state) and 0 <= y < len(state[0]):
            # Check if the new position is not a wall
            if state[x][y] != WALL:
                return True

        return False

    def is_valid_move_ghost(self, state, move):
        """ Helper function to check if a move is valid for a ghost"""
        x, y = move

        # Check if the move is within the bounds of the matrix
        if 0 <= x < len(state) and 0 <= y < len(state[0]):
            # Check if the new position is not a wall (value 99) or another ghost (values 2, 3, 4, 5)
            if state[x][y] not in (WALL, RED, BLUE, GREEN, YELLOW, RED_PILL, BLUE_PILL, GREEN_PILL, YELLOW_PILL,
                                   PACMAN_EATEN):
                return True

        return False

    def move_pacman(self, move, state, new_state):
        """Move Pacman to the new position in the given new state"""
        # Coordinates of the new state of pacman after the move
        new_pacman_x, new_pacman_y = move
        # Get the current position of pacman
        pacman_x, pacman_y = self.get_pacman_position()
        if pacman_x is None or pacman_y is None:
            return new_state
        # Set the old position to empty
        new_state[pacman_x][pacman_y] = EMPTY
        # If in the new position of Pacman there is a ghost
        if state[new_pacman_x][new_pacman_y] in (RED, BLUE, GREEN, YELLOW, RED_PILL, BLUE_PILL, GREEN_PILL,
                                                 YELLOW_PILL):
            new_state[new_pacman_x][new_pacman_y] = PACMAN_EATEN
        else:
            new_state[new_pacman_x][new_pacman_y] = PACMAN
        return new_state

    def move_ghosts(self, move, state, new_state):
        """Move ghosts by order to a new position in the given new state"""
        # Coordinates of the new state of pacman
        new_pacman_x, new_pacman_y = move
        # Set the order of the ghosts
        ghost_order = [RED_POSITION, BLUE_POSITION, YELLOW_POSITION, GREEN_POSITION]
        # Go through all ghosts by order
        for ghost in ghost_order:
            # Get the current location of the ghost
            ghost_x, ghost_y = self.get_ghost_position(ghost)
            if ghost_x is None or ghost_y is None:
                continue

            # Define the possible moves for the ghost
            ghost_moves = [(ghost_x, ghost_y + 1, RIGHT), (ghost_x + 1, ghost_y, DOWN), (ghost_x, ghost_y - 1, LEFT),
                           (ghost_x - 1, ghost_y, UP)]

            # Sort the ghost moves based on the Manhattan distance to Pacman
            ghost_moves.sort(key=lambda g_move: abs(new_pacman_x - g_move[0]) + abs(new_pacman_y - g_move[1]))

            # Go through the moves of a ghost
            for ghost_move in ghost_moves:
                ghost_new_x, ghost_new_y, ghost_action = ghost_move
                # If the ghost's move is valid (not into a wall or into another ghost)
                if self.is_valid_move_ghost(state, (ghost_new_x, ghost_new_y)):
                    # Move the ghost to the new position
                    new_state = self.move_ghost(state, new_state, (ghost_x, ghost_y), (ghost_new_x, ghost_new_y))
                    # If the new position of the ghost contains a pill, update the ghost to a ghost with a pill
                    if state[ghost_new_x][ghost_new_y] == PILL:
                        new_state = self.update_ghost_with_pill(new_state, (ghost_new_x, ghost_new_y),
                                                                state[ghost_x][ghost_y])
                    break
            # Update the state after a ghost move
            state = [list(row) for row in new_state]
        return new_state

    def move_ghost(self, state, new_state, old_position, new_position):
        """Move the ghost from old position to new position in the given new state"""
        ghost_x, ghost_y = old_position
        ghost_new_x, ghost_new_y = new_position

        # If the old position contained a pill, update it to the corresponding color
        if state[ghost_x][ghost_y] == RED_PILL:
            new_state[ghost_x][ghost_y] = PILL
            new_state[ghost_new_x][ghost_new_y] = RED
        elif state[ghost_x][ghost_y] == BLUE_PILL:
            new_state[ghost_x][ghost_y] = PILL
            new_state[ghost_new_x][ghost_new_y] = BLUE
        elif state[ghost_x][ghost_y] == YELLOW_PILL:
            new_state[ghost_x][ghost_y] = PILL
            new_state[ghost_new_x][ghost_new_y] = YELLOW
        elif state[ghost_x][ghost_y] == GREEN_PILL:
            new_state[ghost_x][ghost_y] = PILL
            new_state[ghost_new_x][ghost_new_y] = GREEN

        # If the old position was empty
        else:
            new_state[ghost_x][ghost_y] = EMPTY
            new_state[ghost_new_x][ghost_new_y] = state[ghost_x][ghost_y]

        return new_state

    def update_ghost_with_pill(self, new_state, pill_position, color):
        """Update the ghost position to be with a pill in the given new state based on its color"""
        x, y = pill_position
        if color == RED:
            new_state[x][y] = RED_PILL
        elif color == BLUE:
            new_state[x][y] = BLUE_PILL
        elif color == YELLOW:
            new_state[x][y] = YELLOW_PILL
        elif color == GREEN:
            new_state[x][y] = GREEN_PILL
        return new_state

    def get_pacman_position(self):
        """Return the current pacman position"""
        x, y = None, None
        pacman_position = self.locations.get(PACMAN_POSITION)
        if pacman_position is not None:
            x, y = pacman_position
        return x, y

    def get_ghost_position(self, ghost_position_number):
        """Return the current ghost position by its number"""
        x, y = None, None
        ghost_position = self.locations.get(ghost_position_number)
        if ghost_position is not None:
            x, y = ghost_position
        return x, y

    def update_locations(self, state):
        """Update the locations dictionary based on the given state"""
        for i in range(len(state)):
            for j in range(len(state[i])):
                # Check if the current cell contains a red ghost
                if state[i][j] in (RED, RED_PILL):
                    self.locations[RED_POSITION] = (i, j)
                # Check if the current cell contains a blue ghost
                elif state[i][j] in (BLUE, BLUE_PILL):
                    self.locations[BLUE_POSITION] = (i, j)
                # Check if the current cell contains a yellow ghost
                elif state[i][j] in (YELLOW, YELLOW_PILL):
                    self.locations[YELLOW_POSITION] = (i, j)
                # Check if the current cell contains a green ghost
                elif state[i][j] in (GREEN, GREEN_PILL):
                    self.locations[GREEN_POSITION] = (i, j)
                # Check if the current cell contains Pacman
                elif state[i][j] in (PACMAN, PACMAN_EATEN):
                    self.locations[PACMAN_POSITION] = (i, j)


def create_pacman_problem(game):
    print ("<<create_pacman_problem")
    """ Create a pacman problem, based on the description.
    game - matrix as it was described in the pdf file"""
    return PacmanProblem(game)

game =()


create_pacman_problem(game)