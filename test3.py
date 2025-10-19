import Data
import Function
import Neighborhood
import time
import random
import csv
import Neighborhood11
import Neighborhood10
import Neighborhood_drone
import copy
import numpy as np

global LOOP
global tabu_tenure
# global best_sol
# global best_fitness
global Tabu_Structure
global current_neighborhood
global LOOP_IMPROVED
global SET_LAST_10
global BEST
global start_time
global Data1

epsilon = (-1)*0.00001


solution = [[[[0, [1]], [6, [6, 9, 8, 10]], [9, []], [8, []], [10, []], [7, [7, 2, 4, 3]], 
              [0, []], 
              [0, [5]], [2, []], [1, []], [4, []], [3, []], [5, []], 
              [0, []]]], 
            [[[6, [6, 9, 8, 10]]], [[7, [7, 2, 4, 3]]]]]

solution2 = [[[[0, [2, 14]], [14, []], [2, []], [11, [11, 5]], [5, [14]], [3, [3, 9]], [9, []], [15, [15, 7, 13, 1]], [13, []], [1, []], [7, []]], 
              [[0, []], [4, [10, 4]], [10, []], [8, [8, 12, 6]], [6, []], [12, []]]], 
             [[[4, [10, 4]]], [[11, [11, 5]]], [[8, [6]]], [[8, [8, 12]]], [[3, [3, 9]]], [[15, [7, 13]]], [[15, [15, 1]]]]]

solution3 = [[[[0, []], [8, [8]], [5, [5, 3]], [1, [1, 7]], [7, []], [3, []]], [[0, [9]], [2, [2, 4]], [6, [6, 10]], [4, []], [10, []], [9, []]]], [[[8, [8]]], [[2, [2, 4]]], [[5, [5, 3]]], [[6, [6, 10]]], [[1, [1, 7]]]]]

# print(Function.max_release_date([6]))
# print(Data.manhattan_move_matrix[4][7])
# print(Data.manhattan_move_matrix[10][3])
# print(Data.euclid_flight_matrix[0][5])

# a, b = Function.determine_start_end(solution3, 1, solution[0][index_truck][index_city+2][0])

# # print(Data.city[10])

# print("-----------------")
print(Function.fitness(solution3)[0])
# print(Function.fitness(solution3)[1][0])
# print(Function.fitness(solution3)[1][1])


# Nei=Neighborhood10.Neighborhood_one_opt_standard(solution3)

# sol = Neighborhood.Split_two_truck_term(solution3, 1, 5)
# print(sol[0][1])

# Nei = Neighborhood.Neighborhood_split_two_truck_term(solution3)
# print(Nei[0][0])
# for i in range(len(Nei)):
#         print("-----------------------", i)
#         print(Nei[i][0][0][0])
#         print(Nei[i][0][0][1])
#         print(Nei[i][0][1])
# print(solution3[0][0])
# print(solution3[0][1])
# print(solution3[1])
# print(Data.number_of_cities)
# print(Data.city)
# print(Data.release_date)

# print(Function.fitness(solution3))