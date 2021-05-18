import random
import copy
import timeit
from random import shuffle

class Game(object):
    def __init__(self):
        n=5
        with open("input.txt", 'r') as f:
            lines = f.readlines()

            piece_type = int(lines[0])
            self.piece_type = piece_type
            previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n+1]]
            board = [[int(x) for x in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]

        
        self.N = 5
        self.set_board(previous_board,board)
        
        ans = self.where_to_put_player(board,previous_board,5,piece_type)
        self.writeoutput(ans)

    def set_board(self, previous_board, curr_board):
        
        self.curr_board = curr_board
        self.previous_board = previous_board

    def where_to_put_player(self,current_board,previous_board,board_size,stone_type):
        available_positions = self.find_legal_possible_moves(current_board, previous_board, board_size, stone_type)
        if len(available_positions) == 25 and self.piece_type == 1:
            next_move = (2, 2)

        elif len(available_positions) == 24 and self.piece_type == 2:
            if current_board[2][2]==0:
                next_move = (2, 2)
            
            else:
                next_move = random.choice([(2, 3), (2, 1), (1, 2), (3, 2)])
        else:
            stone_type = self.piece_type
            value, next_move = self.alpha_beta_search(current_board, previous_board, 5, 2, -1000, 1000, stone_type, True)
            x = next_move[0][0]
            y = next_move[0][1]
            next_move = (x,y)

        return next_move
    
    
    def check_Available_Pos(self, grid, row, col, stone_type ):
        result = []
        liberties = set()
        visited = set()
        self.dfs(grid , row, col, stone_type,result,visited)
        for points in result:
            all_neighbors = []
            if points[0] > 0:
                all_neighbors.append((points[0] - 1, points[1]))
            if points[0] < 4:
                all_neighbors.append((points[0] + 1, points[1]))
            if points[1] > 0:
                all_neighbors.append((points[0], points[1] - 1))
            if points[1] < 4:
                all_neighbors.append((points[0], points[1] + 1))
            
            for neighbor in all_neighbors:
                if grid[neighbor[0]][neighbor[1]]==0 and neighbor not in liberties:
                    liberties.add(neighbor)
        
        return list(liberties)

    def dfs(self, grid, i, j,stone_type,result,visited):
        if i<0 or j<0 or i>=len(grid) or j>=len(grid[0]) or grid[i][j] != stone_type or (i,j) in visited:
            return
        result.append((i,j))
        visited.add((i,j))
        self.dfs(grid, i+1, j, stone_type, result, visited)
        self.dfs(grid, i-1, j, stone_type, result, visited)
        self.dfs(grid, i, j+1, stone_type, result, visited)
        self.dfs(grid, i, j-1, stone_type, result, visited)

    def find_legal_possible_moves(self,current_board, previous_board, board_size, stone_type):

        all_possible_moves = [(row,col) for row in range(5) for col in range(5) if current_board[row][col]==0]

        legal_possible_moves = []
        for move in all_possible_moves:
            
            current_board_copy = copy.deepcopy(current_board)
            current_board_copy[move[0]][move[1]] = stone_type
            current_board_copy2 = copy.deepcopy(current_board_copy)
            liberties = self.check_Available_Pos(current_board_copy, move[0], move[1], stone_type)
            if not liberties:
                dead_stones = self.find_dead_stones(3 - stone_type, current_board_copy, board_size)
                if dead_stones:
                    for stone in dead_stones:
                        current_board_copy[stone[0]][stone[1]] = 0
                    
                liberties = self.check_Available_Pos(current_board_copy, move[0], move[1], stone_type)
            if liberties:
                dead_stones = self.find_dead_stones(3 - stone_type, current_board_copy2, board_size)
                if dead_stones:
                    for stone in dead_stones:
                        current_board_copy2[stone[0]][stone[1]] = 0
                    
                if dead_stones and current_board_copy2 == previous_board:
                    continue
                    
                else:
                    legal_possible_moves.append(move)
        return legal_possible_moves


    def alpha_beta_search(self,board_state, previous_board_state, board_size, n, alpha, beta, stone_type,maximizing_player):
        if n == 0:
            return self.calculate_evaluation_value(board_state, previous_board_state, board_size, stone_type), None
        legal_possible_moves = self.find_legal_possible_moves(board_state, previous_board_state, board_size, stone_type)
        shuffle(legal_possible_moves) 

        if not legal_possible_moves:
            current_best_move = ['PASS']
            return 0, current_best_move

        current_best_move = None

        if maximizing_player:
            v = -1000
            for move in legal_possible_moves:
                next_state = self.play_It(board_state, stone_type, move)
                dead_stones = self.find_dead_stones(3 - stone_type, next_state, board_size)
                for stone in dead_stones:
                        next_state[stone[0]][stone[1]] = 0
                
                
                abs_score = self.alpha_beta_search(next_state, board_state, board_size, n - 1, alpha,
                                            beta, 3 - stone_type, False)
                if v < abs_score[0]:
                    v = abs_score[0]
                    alpha = max(alpha, v)
                    current_best_move = [move]
                if alpha >= beta:
                    break
            if current_best_move is None:
                return v, None
            return v, current_best_move
        else:
            v = 1000
            for move in legal_possible_moves:
                next_state = self.play_It(board_state, stone_type, move)
                dead_stones = self.find_dead_stones(3 - stone_type, next_state, board_size)
                for stone in dead_stones:
                        next_state[stone[0]][stone[1]] = 0
                
                abs_score = self.alpha_beta_search(next_state, board_state, board_size, n - 1, alpha,
                                            beta, 3 - stone_type, True)
                if v > abs_score[0]:
                    v = abs_score[0]
                    beta = min(beta, v)
                    current_best_move = [move]
                if alpha >= beta:
                    break
            if current_best_move is None:
                return v, None
            return v, current_best_move


    def play_It(self,current_board, stone_type, move):
        current_board_copy = copy.deepcopy(current_board)
        row = move[0]
        col = move[1]
        current_board_copy[row][col] = stone_type
        return current_board_copy

    def find_dead_stones(self,stone_type, current_board, board_size):
        dead_stones = []
        for row in range(5):
            for col in range(5):
                if current_board[row][col] == stone_type:
                    liberties = self.check_Available_Pos(current_board, row, col, stone_type)
                    if not liberties and (row, col) not in dead_stones:
                        dead_stones.append((row, col))
        return dead_stones

    

    def calculate_evaluation_value(self,current_board, previous_board, board_size, stone_type):
        player_stones, adversary_stones, player_liberties, adversary_liberties = 0, 0, 0, 0
        komi = board_size / 2
        player = self.piece_type
        for row in range(5):
            for col in range(5):
                if current_board[row][col] == player:
                    player_stones = player_stones + 1
                elif current_board[row][col] == 3 - player:
                    adversary_stones = adversary_stones + 1
        player_liberties = len(self.find_liberties(current_board, previous_board, board_size, player))
        adversary_liberties = len(self.find_liberties(current_board, previous_board, board_size, 3 - player))
        return (player_stones + 1 * player_liberties) - (adversary_stones + 2 * adversary_liberties)
        


    def find_liberties(self,current_board, previous_board, board_size, stone_type):
        all_possible_moves = [(row,col) for row in range(5) for col in range(5) if current_board[row][col]==0]

        liberties = []
        for move in all_possible_moves:
            current_board_copy = copy.deepcopy(current_board)
            current_board_copy[move[0]][move[1]] = stone_type
            liberties.append(self.check_Available_Pos(current_board_copy, move[0], move[1], stone_type))
        all_liberties = [lib for sublist in liberties for lib in sublist]
        return all_liberties

    
    def writeoutput(self,ans):
        output = open("output.txt","w")
        if ans  == "PASS":
            output.write("PASS")
        else:
            output.write(str(ans[0])+"," + str(ans[1])) 

ga = Game()