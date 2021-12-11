import numpy as np
import random
from Grid import Grid
from ComputerAI import ComputerAI
from Displayer import Displayer
from PlayerAI import PlayerAI
from test_players.EasyAI import EasyAI
from test_players.PlayerAI_2 import PlayerAI as offensive
from test_players.PlayerAI_3 import PlayerAI as balanced

from candidates.d_1_1_1_1_T import PlayerAI as d2222
from candidates.d_1_1e5_1e5_1_F import PlayerAI as d2332
from candidates.d_1_1e5_3_1_F import PlayerAI as d2362
from candidates.d_1_2_1_2_T import PlayerAI as d2424
from candidates.d_1_2_2_1_F import PlayerAI as d2442
from candidates.d_1_2e5_2e5_1_F import PlayerAI as d2552
from candidates.d_1_2e5_5_1_F import PlayerAI as d25102
from candidates.d_1_3_2e5_1_F import PlayerAI as d26102
from candidates.d_1_3_3_1_F import PlayerAI as d2662
from candidates.d_1_5_5_1_F import PlayerAI as d210102
from candidates.s_1_1_1_1_T import PlayerAI as s2222
from candidates.s_1_1e5_1e5_1_T import PlayerAI as s2332
from candidates.s_1_2_1_2_T import PlayerAI as s2424
from candidates.s_1_2_2_1_F import PlayerAI as s2442
from candidates.s_1_2_3_1_F import PlayerAI as s2462
from candidates.s_1_3_2_1_F import PlayerAI as s2642


from Utils import *
import time

from test_players.MediumAI import MediumAI

PLAYER_TURN, COMPUTER_TURN = 1,2

# Time Limit Before Losing
timeLimit = 5.0
allowance = 0.05

class Game():
    def __init__(self, playerAI = None, computerAI = None, N = 7, displayer = None):
        '''
        Description
        ----------
        Construct new game given two players, board size and displayer.

        Parameters
        ----------
        playerAI   - Human player AI, of type PlayerAI. default = None 

        computerAI - Human or Computer Opponent. default = None
        
        N  - dimension of grid.

        '''
        self.grid       = Grid(N)
        self.playerAI   = playerAI or ComputerAI() 
        self.computerAI = computerAI or ComputerAI() 
        self.dim        = N
        self.over       = False
        self.displayer = displayer

    def initialize_game(self):

        p1_index, p2_index = (0, self.dim // 2), (self.dim - 1, self.dim // 2)
        
        self.grid.setCellValue(p1_index, 1)
        self.playerAI.setPosition(p1_index)
        self.playerAI.setPlayerNum(1)

        self.grid.setCellValue(p2_index, 2)
        self.computerAI.setPosition(p2_index)
        self.computerAI.setPlayerNum(2)
        
    def is_over(self, turn):
        """Check if game is over, i.e., Player or Opponent has no moves to make"""
        # check if Player has won
        # find available neighbors of player 1
        opponent_neighbors = self.grid.get_neighbors(self.computerAI.getPosition(), only_available=True)
        # if none - win
        if len(opponent_neighbors) == 0:
            self.over = True
            return 1

        # check if Opponent has won
        player_neighbors = self.grid.get_neighbors(self.playerAI.getPosition(), only_available=True)

        if len(player_neighbors) == 0:
            self.over = True
            return 2
        
        elif self.over:
            return turn

        else: 
            return 0

    def is_valid_move(self, grid : Grid, player, move : tuple):

        '''Validate move - cell has to be available and immediate neighbor'''
        
        if grid.getCellValue(move) == 0 and move in grid.get_neighbors(player.getPosition()):
            return True
        
        return False

    def is_valid_trap(self, grid : Grid, trap : tuple):
        '''Validate trap - cell can't be a player'''

        if grid.getCellValue(trap) > 0:
            return False

        return True

    def throw(self, player, grid : Grid, intended_position : tuple) -> tuple:
        '''
        Description
        ----------
        Function returns the coordinates in which the trap lands, given an intended location.

        Parameters
        ----------

        player : the player throwing the trap

        grid : current game Grid

        intended position : the (x,y) coordinates to which the player intends to throw the trap to.

        Returns
        -------
        Position (x_0,y_0) in which the trap landed : tuple

        '''
 
        # find neighboring cells
        neighbors = grid.get_neighbors(intended_position)

        neighbors = [neighbor for neighbor in neighbors if grid.getCellValue(neighbor) <= 0]
        n = len(neighbors)
        
        probs = np.ones(1 + n)
        
        # compute probability of success, p
        p = 1 - 0.05*(manhattan_distance(player.getPosition(), intended_position) - 1)

        probs[0] = p

        probs[1:] = np.ones(len(neighbors)) * ((1-p)/n)

        # add desired coordinates to neighbors
        neighbors.insert(0, intended_position)
        
        # return 
        result = np.random.choice(np.arange(n + 1), p = probs)
        
        return neighbors[result]

    def updateAlarm(self, currTime):
        print("TIME:", currTime - self.prevTime)
        if currTime - self.prevTime > timeLimit + allowance:
            self.over = True
            print("Went over time. Doll Shot!")
        else:
            while time.process_time() - self.prevTime < timeLimit + allowance:
                pass

            self.prevTime = time.process_time()

    def play(self):
        """ DO NOT MODIFY """

        print("AI SQUID GAME")
        self.initialize_game()

        self.displayer.display(self.grid)

        turn = PLAYER_TURN
        
        while not self.over:
            self.prevTime = time.process_time()
            grid_copy = self.grid.clone()

            move = None
            
            if turn == 1:

                print("Player's Turn: ")

                # find best move; should return two coordinates - new position and bombed tile.
                move = self.playerAI.getMove(grid_copy)

                # if move is valid, perform it
                if self.is_valid_move(self.grid, self.playerAI, move):
                    self.grid.move(move, turn)
                    self.playerAI.setPosition(move)
                    print(f"Moving to {move}")
                else:
                    self.over = True
                    print(f"Tried to move to : {move}")
                    print("invalid Player AI move!")
                
                intended_trap = self.playerAI.getTrap(self.grid.clone())

                if self.is_valid_trap(self.grid, intended_trap):
                    trap = self.throw(self.playerAI, self.grid, intended_trap)
                    self.grid.trap(trap, flag=False)
                    print(f"Throwing a trap to: {intended_trap}. Trap landed in {trap}")

                else: 
                    self.over = True
                    print(f"Tried to put trap in {intended_trap}")
                    print("Invalid trap!")

            else:

                print("Opponent's Turn : ")
                
                # make move
                move = self.computerAI.getMove(grid_copy)

                # check if move is valid; perform if it is.
                if self.is_valid_move(self.grid, self.computerAI, move):
                    self.grid.move(move, turn)
                    self.computerAI.setPosition(move)
                    print(f"Moving to {move}")

                else:
                    self.over = True
                    print("invalid Computer AI Move")

                intended_trap = self.computerAI.getTrap(self.grid.clone())

                if self.is_valid_trap(self.grid, intended_trap):
                    trap = self.throw(self.computerAI, self.grid, intended_trap)
                    self.grid.trap(trap)
                    print(f"Throwing a trap to: {intended_trap}. Trap landed in {trap}")
                else: 
                    self.over = True
                    print(f"Tried to put trap in {intended_trap}")
                    print("Invalid trap!")

            if self.is_over(turn):
                self.over = True
            
            self.updateAlarm(time.process_time())
            turn = 3 - turn
            self.displayer.display(self.grid)

        return self.is_over(turn)

def main():
    candidates = {"d2222": d2222(), "d2332": d2332(), "d2362": d2362(), "d2424": d2424(), "d2442": d2442(), "d2552": d2552(), "d25102": d25102(), "d26102": d26102(), "d2662": d2662(), "d210102": d210102(), "s2222": s2222(), "s2332": s2332(), "s2424": s2424(), "s2442": s2442(), "s2462": s2462(), "s2642": s2642()}
    keys = list(candidates.keys())
    random.shuffle(keys)
    
    file = open("output.txt", "w")
    displayer = Displayer()
    
    j = 0
    
    rounds = int(len(candidates)/4)
    
    for j in range(rounds): #number of rounds
        round_num = int(j + 1)
        message = "ROUND " + str(round_num) + " of TOURNAMENT\n"
        file.write(message)
        surviving_candidates = {}
        if round_num != 1:
            keys = list(candidates.keys())
        results = {}
        i = 0
        surviving_candidates.clear()
        for i in range(0, int(len(candidates)), 2): #number of match ups
            #print(keys)
            playerAI = candidates[keys[i]] # change this to PlayerAI() to test your player!
            computerAI = candidates[keys[i + 1]] # change this to a more sophisticated player you've coded
            results.clear()
            results[keys[i]] = 0
            results[keys[i+1]] = 0
        
            for x in range(10): #CHANGE THIS VALUE to dtermine how many times each matchup plays
                game = Game(playerAI = playerAI, computerAI = computerAI, N = 7, displayer=displayer)
                result = game.play()
                
                if result == 1:
                    results[keys[i]] += 1
                elif result == 2:
                    results[keys[i+1]] += 1
                
                if results[keys[i]] >= results[keys[i+1]]:
                    surviving_candidates[keys[i]] = candidates[keys[i]]
                elif results[keys[i]] < results[keys[i+1]]:
                    surviving_candidates[keys[i+1]] = candidates[keys[i+1]]
                    
            output_message = "The " + keys[i] + " player won " + str(results[keys[i]]) + " times and the " + keys[i+1] + " player won " + str(results[keys[i+1]]) + " times.\n"
            file.write(output_message)
        candidates.clear()
        candidates = surviving_candidates

if __name__ == "__main__":
    main()
