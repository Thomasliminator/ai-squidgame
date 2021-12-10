import numpy as np
import random
import time
import sys
import os 
import math
from BaseAI import BaseAI
from Grid import Grid

# TO BE IMPLEMENTED
# 
class PlayerAI(BaseAI):

    def __init__(self) -> None:
        # You may choose to add attributes to your player - up to you!
        super().__init__()
        self.pos = None
        self.player_num = None
    
    def getPosition(self):
        return self.pos

    def setPosition(self, new_position):
        self.pos = new_position 

    def getPlayerNum(self):
        return self.player_num

    def setPlayerNum(self, num):
        self.player_num = num

    def getMove(self, grid: Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player moves.

        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Trap* actions, 
        taking into account the probabilities of them landing in the positions you believe they'd throw to.

        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
        result, _ = self.max_move(grid, self.pos, 1, -math.inf, math.inf)
        return result

    '''
    def getAvailableMoves(self, grid, pos):
        x,y = pos
        valid_range = lambda t: range(max(t-1, 0), min(t+2, grid.dim))
        return list({(a,b) for a in valid_range(x) for b in valid_range(y) if grid.map[(a, b)] == 0} - {(x,y)})
    '''

    def max_move(self, grid, pos, i, a, b):
        if i >= 7:
            return None, self.DEF(grid, self.player_num) # heuristic
        maxChild, maxUtility = None, -math.inf
        neighbors = grid.get_neighbors(pos, only_available = True)
        if len(neighbors) == 0:
            return None, self.DEF(grid, self.player_num) # heuristic
        for child_pos in neighbors:
            child_grid = grid.clone()
            child_grid.move(child_pos, self.player_num)
            _, utility = self.min_move(child_grid, child_pos, i + 1, a, b)
            if utility > maxUtility:
                maxChild, maxUtility = child_pos, utility
            if maxUtility >= b:
                break
            if maxUtility > a:
                a = maxUtility
        return maxChild, maxUtility

    def min_move(self, grid, pos, i, a, b):
        if i >= 5:
            return None, 1
        minChild, minUtility = None, math.inf
        for child_pos in grid.getAvailableCells():
            child_grid = grid.clone()
            child_grid.trap(child_pos)
            _, utility = self.max_move(child_grid, pos, i + 1, a, b)
            if utility < minUtility:
                minChild, minUtility = child_pos, utility
            if minUtility <= a:
                break
            if minUtility < b:
                b = minUtility
        return minChild, minUtility

    def getTrap(self, grid : Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player *WANTS* to throw the trap.
        
        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Move* actions, 
        taking into account the probabilities of it landing in the positions you want. 
        
        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
        result, _ = self.max_trap(grid, grid.find(3 - self.player_num), 1, -math.inf, math.inf)
        return result

    def max_trap(self, grid, pos, i, a, b):
        if i >= 3:
            return None, -self.HM(grid, 3 - self.player_num) # heuristic
        maxChild, maxUtility = None, -math.inf
        for child_pos in grid.getAvailableCells():
            child_grid = grid.clone()
            child_grid.trap(child_pos)
            _, utility = self.min_trap(child_grid, pos, i + 1, a, b)
            if utility > maxUtility:
                maxChild, maxUtility = child_pos, utility
            if maxUtility >= b:
                break
            if maxUtility > a:
                a = maxUtility
        return maxChild, maxUtility

    def min_trap(self, grid, pos, i, a, b):
        minChild, minUtility = None, math.inf
        for child_pos in grid.get_neighbors(pos, only_available = True):
            child_grid = grid.clone()
            child_grid.move(child_pos, 3 - self.player_num)
            _, utility = self.max_trap(child_grid, child_pos, i + 1, a, b)
            if utility < minUtility:
                minChild, minUtility = child_pos, utility
            if minUtility <= a:
                break
            if minUtility < b:
                b = minUtility
        return minChild, minUtility

    # heuristics
    def DEF(self, grid : Grid, player_num):
        player_moves = len(self.get_n(grid, grid.find(player_num), 1, only_available = True))
        opp_moves = len(self.get_n(grid, grid.find(3 - player_num), 1, only_available = True))
        return 2 * player_moves - opp_moves

    def OFF(self, grid : Grid, player_num):
        player_moves = len(self.get_n(grid, grid.find(player_num), 1, only_available = True))
        opp_moves = len(self.get_n(grid, grid.find(3 - player_num), 1, only_available = True))
        return -opp_moves

    def HM(self, grid : Grid, player_num):
        pos = grid.find(player_num)
        return (1 * len(self.get_n(grid, pos, 1, only_available = True))) + (1.5 * len(self.get_n(grid, pos, 2, only_available = True))) + (2 * len(self.get_n(grid, pos, 3, only_available = True)))

    def get_n(self, grid, pos, n, only_available = False):
        x,y = pos
        valid_range = lambda t: range(max(t-n, 0), min(t+n+1, grid.dim))
        neighbors = list({(a,b) for a in valid_range(x) for b in valid_range(y)} - {(x,y)})
        if only_available:
            return [neighbor for neighbor in neighbors if grid.map[neighbor] == 0]
        return neighbors
    
    def paths(self, grid, player_num):
        x,y = pos
        valid_range = lambda t: range(max(t-1, 0), min(t+2, grid.dim))
        neighbors = list({(a,b) for a in valid_range(x) for b in valid_range(y)} - {(x,y)})
