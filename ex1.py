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
PLAYER_EATEN = 88
RED_PILL = 21
BLUE_PILL = 31
YELLOW_PILL = 41
GREEN_PILL = 51

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
        self.update_locations(state)
        # Get the pacman location
        # pacman_x, pacman_y = (3, 0)
        pacman_x, pacman_y = self.locations.get(7)
        # Define possible moves (right, down, left, up)
        moves = [(pacman_x - 1, pacman_y, "U"), (pacman_x + 1, pacman_y, "D"), (pacman_x, pacman_y + 1, "R"), (pacman_x, pacman_y - 1, "L")]
        # If the pacman is eaten in the given state
        if state[pacman_x][pacman_y] == 88:
            self.dead_end = True
            return ()
        # Go through each possible move
        for move in moves:
            new_x, new_y, action = move
            # If the move is valid
            if self.is_valid_move_pacman(state, (new_x, new_y)):
                # Generate the new state after the move
                new_state = self.result(state, (new_x, new_y))
                # Append the move if it's not None (=Pacman eaten)
                if new_state is not None:
                    successors.append((action, tuple(map(tuple, new_state))))  # Convert new_state to a tuple

        return tuple(successors)

    def result(self, state, move):
        """given state and an action and return a new state"""
        """ Magic numbers for ghosts and Packman: 
                2 - red, 3 - blue, 4 - yellow, 5 - green and 7 - Packman."""
        # Coordinates of the new state after the move
        new_x, new_y = move
        # Set a new state similar to the old state
        new_state = [list(row) for row in state]
        # Get the current position of pacman
        pacman_position = self.locations.get(7)
        pacman_x, pacman_y = pacman_position
        # Set the old position to empty
        new_state[pacman_x][pacman_y] = EMPTY
        # If in the new position of Pacman there is a ghost
        if state[new_x][new_y] in (RED, BLUE, GREEN, YELLOW, RED_PILL, BLUE_PILL, GREEN_PILL, YELLOW_PILL):
            new_state[new_x][new_y] = PLAYER_EATEN
            # Return the new state with the eaten pacman without expanding it
            return new_state
        else:
            new_state[new_x][new_y] = PACMAN

        # Set the order of the ghosts
        ghost_order = [2, 3, 4, 5]
        # Update the state after moving pacman
        state = [list(row) for row in new_state]
        for ghost in ghost_order:
            ghost_position = self.locations.get(ghost)
            if ghost_position is None:
                continue
            # Get the current location of the ghost
            ghost_x, ghost_y = ghost_position

            # Define the possible moves for the ghost
            ghost_moves = [
                (ghost_x, ghost_y + 1, "R"),
                (ghost_x + 1, ghost_y, "D"),
                (ghost_x, ghost_y - 1, "L"),
                (ghost_x - 1, ghost_y, "U"),
            ]

            # Sort the ghost moves based on the Manhattan distance to Pacman
            ghost_moves.sort(key=lambda g_move: abs(new_x - g_move[0]) +
                                                abs(new_y - g_move[1]))

            # Go through the moves of a ghost
            for g_move in ghost_moves:
                g_new_x, g_new_y, g_action = g_move
                # Check if the new position for the ghost is valid - if so update ghost position in new_state
                if self.is_valid_move_ghost(state, (g_new_x, g_new_y)):
                    # If the old position of the ghost contained a pill
                    if state[ghost_x][ghost_y] == RED_PILL:
                        new_state[ghost_x][ghost_y] = PILL
                        new_state[g_new_x][g_new_y] = RED
                    elif state[ghost_x][ghost_y] == BLUE_PILL:
                        new_state[ghost_x][ghost_y] = PILL
                        new_state[g_new_x][g_new_y] = BLUE
                    elif state[ghost_x][ghost_y] == YELLOW_PILL:
                        new_state[ghost_x][ghost_y] = PILL
                        new_state[g_new_x][g_new_y] = YELLOW
                    elif state[ghost_x][ghost_y] == GREEN_PILL:
                        new_state[ghost_x][ghost_y] = PILL
                        new_state[g_new_x][g_new_y] = GREEN
                    else:
                        # Set the previous ghost position to empty (10)
                        new_state[ghost_x][ghost_y] = EMPTY
                        new_state[g_new_x][g_new_y] = state[ghost_x][ghost_y]
                    # If the new position of the ghost contains a pill
                    if state[g_new_x][g_new_y] == PILL:
                        if new_state[g_new_x][g_new_y] == RED:
                            new_state[g_new_x][g_new_y] = RED_PILL
                        elif new_state[g_new_x][g_new_y] == BLUE:
                            new_state[g_new_x][g_new_y] = BLUE_PILL
                        elif new_state[g_new_x][g_new_y] == YELLOW:
                            new_state[g_new_x][g_new_y] = YELLOW_PILL
                        elif new_state[g_new_x][g_new_y] == GREEN:
                            new_state[g_new_x][g_new_y] = GREEN_PILL
                    break
            # Update the state after a ghost move
            state = [list(row) for row in new_state]

        # Check if the new position contains a ghost after ghost moves
        if new_state[new_x][new_y] in (RED, BLUE, YELLOW, GREEN, RED_PILL, BLUE_PILL, GREEN_PILL, YELLOW_PILL):
            # Player is eaten by a ghost
            new_state[new_x][new_y] = PLAYER_EATEN  # Player is eaten (88)
        # Return the new state
        return tuple(tuple(row) for row in new_state)

    def goal_test(self, state):
        """ given a state, checks if this is the goal state, compares to the created goal state"""
        for row in state:
            for cell in row:
                # If there's a pill in this cell
                if cell in (PILL, RED_PILL, BLUE_PILL, GREEN_PILL, YELLOW_PILL, PLAYER_EATEN):
                    return False  # There are still tiles with pills left
        return True  # All tiles with pills have been consumed

    def h(self, node):
        """ This is the heuristic. It get a node (not a state)
        and returns a goal distance estimate"""
        # Find the coordinates of the nearest pill
        nearest_pill_coordinates = self.find_nearest_pill(node.state)
        pacman_position = self.locations.get(7)
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
            if state[x][y] not in (WALL, RED, BLUE, GREEN, YELLOW, RED_PILL, BLUE_PILL, GREEN_PILL, YELLOW_PILL, PLAYER_EATEN):
                return True

        return False

    def update_locations(self, state):
        """Update the locations dictionary based on the given state"""
        """ Magic numbers for ghosts and Packman: 
                2 - red, 3 - blue, 4 - yellow, 5 - green and 7 - Packman."""
        for i in range(len(state)):
            for j in range(len(state[i])):
                # Check if the current cell contains a red ghost
                if state[i][j] in (RED, RED_PILL):
                    self.locations[2] = (i, j)
                # Check if the current cell contains a blue ghost
                elif state[i][j] in (BLUE, BLUE_PILL):
                    self.locations[3] = (i, j)
                # Check if the current cell contains a yellow ghost
                elif state[i][j] in (YELLOW, YELLOW_PILL):
                    self.locations[4] = (i, j)
                # Check if the current cell contains a green ghost
                elif state[i][j] in (GREEN, GREEN_PILL):
                    self.locations[5] = (i, j)
                # Check if the current cell contains Pacman
                elif state[i][j] in (PACMAN, PLAYER_EATEN):
                    self.locations[7] = (i, j)





def create_pacman_problem(game):
    print ("<<create_pacman_problem")
    """ Create a pacman problem, based on the description.
    game - matrix as it was described in the pdf file"""
    return PacmanProblem(game)

game = (
        (10, 10, 10, 11),
        (10, 99, 10, 50),
        (10, 10, 10, 10),
        (77, 10, 10, 10),)


problem = (
            (10, 10, 10, 11),
            (10, 99, 10, 50),
            (10, 10, 10, 10),
            (77, 10, 10, 10),)

create_pacman_problem(game)
