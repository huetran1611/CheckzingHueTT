import Data
import Function
import Neighborhood
import time
import random
import csv
import Neighborhood11
import Neighborhood10
import Neighborhood_drone

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


# solution = [[[[0, []], [1, [1]], [0, []], [6, [6, 7, 8]], [7, []], [8, []]],
#              [[0, []], [5, [5]], [0, []], [2, [2, 3, 4]], [3, []], [4, []]]],
#             [[[1, [1]]], [[5, [5]]], [[2, [2, 3, 4]]], [[6, [6, 7, 8]]]]]

solution = [[[[0, []], [1, [1]], [0, []], [6, [6, 7, 8]], [7, []], [8, []],
             [0, []], [2, [2, 3, 4]], [3, []], [4, []]]], 
             [[[1, [1]]], [[6, [6, 7, 8]]], [[2, [2, 3, 4]]]]]


solution = [[[[0, []], [1, [1]], [0, [6, 7, 8]], [6, []], [7, []], [8, []],
             [0, []], [2, [2, 3, 4]], [3, []], [4, []]]], 
             [[[1, [1]]], [[2, [2, 3, 4]]]]]

solution = [[[[0, [1, 13]], [4, [4, 5, 10, 14]], [5, []], [3, []], [1, []], [2, [2, 11]], [7, []], [6, []], [8, []], [12, [12, 9, 15]], [10, []], [11, []], [9, []], [13, []], [15, []], [14, []], [0, []]]], 
            [[[2, [2, 11]]], [[4, [4, 5, 10, 14]]], [[12, [12, 9, 15]]]]]

# nei = Neighborhood_drone.Neighborghood_change_drone_route_max_pro_plus(solution)

# print(Function.fitness(solution))
# print(solution[0][0])
print(Function.Check_if_feasible(solution))

# nei = Neighborhood.Neighborhood_split_two_truck_term(solution)
# solution = Neighborhood.Split_two_truck_term(solution, 0, 1)
# print(solution[0][0])
# print(solution[1])
# init = Function.initial_solution7()
# print(init)
# print("------")
# init = Neighborhood.Turn_single_to_multi_trip(init)

# nei = Neighborhood11.Neighborhood_move_2_1(init)
# print(init)
print(Function.fitness(solution))

