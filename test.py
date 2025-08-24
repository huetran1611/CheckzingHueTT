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


solution = [[[[0, [1, 2, 4, 5, 3, 6, 7, 8, 9, 10]], [1, []], [2, []], [4, []], [5, []], [3, []], [6, []], [7, []], [8, []], [10, []], [9, []]]], []]       
# print(sample)
print(Function.fitness(solution))
# a = Data.release_date[2] + Data.manhattan_move_matrix[0, 2] +Data.manhattan_move_matrix[2, 0]
# print(a)
# print(Data.release_date[15]+Data.euclid_flight_matrix[0,2])

# c = Neighborhood.addNewTripInDroneRoute(sample, [12], 0, 3)
# print(c[0])
# aa = [[2, [11]]]
# d = Function.cal_time_fly_a_trip(aa)
# d, e = Function.determine_start_end(sample, 0, 5)
# print(d,"    ", e)

# c = Neighborhood.findLocationForDropPackage(solution, 0, 6)
# c = Function.fitness(solution)

# print(c)
# nei = Neighborhood_drone.Neighborghood_change_drone_route_max_pro_plus(solution)
# c = Function.fitness(solution)
# print(c)
