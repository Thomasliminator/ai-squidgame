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
        opp_pos = grid.find(3 - self.player_num)
        neighbors = grid.get_neighbors(opp_pos, only_available = True)
        if len(neighbors) == 1:
            #print("WEAKNESS DETECTED, case 1")
            #print("NEIGHBORS:", neighbors)
            if opp_pos in grid.get_neighbors(neighbors[0], only_available = True):
                return neighbors[0]
        if len(neighbors) == 2:
            ##print("WEAKNESS DETECTED, case 2")
            #print("NEIGHBORS:", neighbors)
            for neigh in neighbors:
                #print("neighbors of", neigh, grid.get_neighbors(neigh, only_available = True))
                if opp_pos in grid.get_neighbors(neigh, only_available = True) and opp_pos not in neighbors:
                    #print("NEIGH:", neigh)
                    return neigh
        result, _ = self.max_move(grid, self.pos, 1, -math.inf, math.inf, False)
        return result

    def max_move(self, grid, pos, i, a, b, off):
        if i >= 5:
            return None, self.h(grid, self.player_num, off)
        maxChild, maxUtility = None, -math.inf
        neighbors = grid.get_neighbors(pos, only_available = True)
        if len(neighbors) == 0:
            return None, self.h(grid, self.player_num, off) # heuristic
        for child_pos in neighbors:
            child_grid = grid.clone()
            child_grid.move(child_pos, self.player_num)
            _, utility = self.min_move(child_grid, child_pos, i + 1, a, b, off)
            if utility > maxUtility:
                maxChild, maxUtility = child_pos, utility
            if maxUtility >= b:
                break
            if maxUtility > a:
                a = maxUtility
        return maxChild, maxUtility

    def min_move(self, grid, pos, i, a, b, off):
        if i >= 5:
            return None, 1
        minChild, minUtility = None, math.inf
        opp_pos = grid.find(3 - self.player_num)
        for child_pos in grid.getAvailableCells():
            child_grid = grid.clone()
            child_grid.trap(child_pos)
            _, utility = self.max_move(child_grid, pos, i + 1, a, b, off)
            utility *= self.prob(opp_pos, child_pos)
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
        opp_pos = grid.find(3 - self.player_num)
        neighbors = grid.get_neighbors(opp_pos, only_available = True)
        if len(neighbors) == 1:
            return neighbors[0]
        result, _ = self.max_trap(grid, grid.find(3 - self.player_num), 1, -math.inf, math.inf, True)
        #print("RESULT:", result)
        return result

    def max_trap(self, grid, pos, i, a, b, off):
        if self.paths2(grid, 3 - self.player_num) == 1:
            return grid.get_neighbors(pos, only_available = True)[0], math.inf
        if i >= 5:
            return None, self.h(grid, self.player_num, off)
        maxChild, maxUtility = None, -math.inf
        for child_pos in grid.getAvailableCells():
            child_grid = grid.clone()
            child_grid.trap(child_pos)
            _, utility = self.min_trap(child_grid, pos, i + 1, a, b, off)
            utility *= self.prob(self.pos, child_pos)
            if utility > maxUtility:
                maxChild, maxUtility = child_pos, utility
            if maxUtility >= b:
                break
            if maxUtility > a:
                a = maxUtility
        return maxChild, maxUtility

    def min_trap(self, grid, pos, i, a, b, off):
        minChild, minUtility = None, math.inf
        for child_pos in grid.get_neighbors(pos, only_available = True):
            child_grid = grid.clone()
            child_grid.move(child_pos, 3 - self.player_num)
            _, utility = self.max_trap(child_grid, child_pos, i + 1, a, b, off)
            if utility < minUtility:
                minChild, minUtility = child_pos, utility
            if minUtility <= a:
                break
            if minUtility < b:
                b = minUtility
        return minChild, minUtility

    # heuristics
    def h(self, grid : Grid, player_num, off):
        player_moves = self.paths2(grid, self.player_num)
        opp_moves = -self.paths2(grid, 3 - self.player_num)
        if opp_moves == 0:
            return math.inf
        if grid.get_neighbors(grid.find(self.player_num), only_available = True) == 1:
            return -math.inf
        if off:
            return player_moves + 1.5 * opp_moves
        return 1.5 * player_moves + opp_moves

    def paths2(self, grid, player_num):
        count = 0
        x,y = grid.find(player_num)
        valid_range1 = lambda t: range(max(t-1, 0), min(t+2, grid.dim))
        neighbors1 = list({(a,b) for a in valid_range1(x) for b in valid_range1(y) if grid.map[(a, b)] == 0} - {(x,y)})
        neighbors1_set = set(neighbors1)
        count += 2.5 * len(neighbors1_set)
        for n in neighbors1:
            p = n[0]
            q = n[1]
            count += len({(a, b) for a in valid_range1(p) for b in valid_range1(q) if grid.map[(a, b)] == 0} - neighbors1_set)
        return count

    def m_dist(self, p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) 
    
    def prob(self, pos, target):
        return 1 - 0.05*(self.m_dist(pos, target) - 1)
