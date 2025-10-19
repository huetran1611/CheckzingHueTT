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

# Set up chỉ số -------------------------------------------------------------------
# 15:   50 - 35,    20:    60 - 40    10:   20 - 15     50:     70 - 50
# tabu_tenure = Data.number_of_cities * 1.5
# tabu_tenure1 = tabu_tenure3 = tabu_tenure2 = Data.number_of_cities
# LOOP = Data.number_of_cities * 40
start_time_sub = time.time()
ITE = 10
epsilon = (-1) * 0.00001
# 15:   120,    20:    150
# BREAKLOOP = Data.number_of_cities * 8
LOOP_IMPROVED = 0
SET_LAST_10 = [] 
BEST = []
Data1 = []
solution_pack_len = 5

# Set up chỉ số -------------------------------------------------------------------

check = [[[[0, [10, 4, 1, 5, 2, 3]], [7, [7]], [10, []], [5, []], [3, [6, 9]], [4, []], [1, []], [2, []], [6, []], [9, []], [8, [8]]]], [[[7, [7]]], [[3, [6, 9]]], [[8, [8]]]]]


def Tabu_search(init_solution, tabu_tenure, AA, BB, CC, first_time, Data1, index_consider_elite_set, solution_pack):
    solution_pack_len = 5
    current_fitness, current_truck_time, current_sum_fitness = Function.fitness(init_solution)
    best_sol = init_solution
    best_fitness = current_fitness
    sol_chosen_to_break = init_solution
    fit_of_sol_chosen_to_break = current_fitness
    
    NUMBER_BREAKLOOP = 0
    lennn = [0] * 6
    lenght_i = [0] * 6
    i = 0
    
    checked = [False] * (AA+1)
    Result_print = []
    
    Result = []
    # LOOP = BREAKLOOP * AA
    # print(Data.standard_deviation)
    global current_neighborhood
    global LOOP_IMPROVED
    LOOP_IMPROVED = 0
    global use_optimize_truck_route
    use_optimize_truck_route = False
        
    tabu_tenure = Data.number_of_cities - 1
    tabu_tenure1 = tabu_tenure3 = tabu_tenure2 = Data.number_of_cities - 1
    
    # tabu_tenure1 = tabu_tenure3 = (int)((Data.number_of_cities - 1)/2)
    # tabu_tenure2 = (int)((Data.number_of_cities - 1)/3)
    
    BREAKLOOP = tabu_tenure1 * BB
    Data1 = [['act', 'fitness', 'change1', 'change2', 'solution', 'tabu structue', 'tabu structure1']]
    
    Tabu_Structure = [(tabu_tenure +1) * (-1)] * Data.number_of_cities
    Tabu_Structure1 = [(tabu_tenure +1) * (-1)] * Data.number_of_cities
    Tabu_Structure2 = [(tabu_tenure +1) * (-1)] * Data.number_of_cities
    Tabu_Structure3 = [(tabu_tenure +1) * (-1)] * Data.number_of_cities
    
    current_sol = init_solution
    
    while i - LOOP_IMPROVED < BREAKLOOP:
        # print("------------------",i,"------------------")
        # print("------------------",i,"------------------", LOOP_IMPROVED, "------------------", NUMBER_BREAKLOOP)
        # print(best_fitness,"------------------", fit_of_sol_chosen_to_break, "--------------", current_fitness)
        # current_neighborhood = []
        # print(len(solution_pack), "***********************************")
        # print(solution_pack)
        # if i - LOOP_IMPROVED > BREAKLOOP:
        #     NUMBER_BREAKLOOP += 1
        #     # print("------------------",NUMBER_BREAKLOOP,"-----------break-------")
        #     # print(sol_chosen_to_break)
        #     # print(fit_of_sol_chosen_to_break)
        #     if len(Result) != 0:
        #         if fit_of_sol_chosen_to_break - min(Result) < epsilon:
        #             NUMBER_BREAKLOOP = 0
        #             # print("pass")
        #     Result.append(fit_of_sol_chosen_to_break)
        #     for iiiii in range(AA):
        #         if NUMBER_BREAKLOOP == iiiii + 1 and not checked[iiiii]:
        #             Result_print.append(min(Result))
        #             checked[iiiii] = True
        #     # current_neighborhood5 = Neighborhood.swap_two_array(sol_chosen_to_break)
        #     # print(sol_chosen_to_break)
        #     current_neighborhood10, solution_pack = Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood_with_package(Neighborhood.swap_two_array, sol_chosen_to_break, CC, 3, False, solution_pack=solution_pack, solution_pack_len=solution_pack_len, use_solution_pack=first_time)
        #     # current_neighborhood10 = []
        #     # print(len(current_neighborhood10))
        #     BEST.append(sol_chosen_to_break)
        #     current_neighborhood.append([10, current_neighborhood10])
        #     fit_of_sol_chosen_to_break = 10000000 
            
        #     for j in range(len(Tabu_Structure)):
        #         Tabu_Structure[j] -= tabu_tenure
        #         Tabu_Structure1[j] -= tabu_tenure1
        #         Tabu_Structure2[j] -= tabu_tenure2
        #         Tabu_Structure3[j] -= tabu_tenure3

        a = random.random()
        current_neighborhood = []
        print("---------------", i)
        print(current_sol)
        if a > 0.66:
            current_neighborhood1, solution_pack = Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood_with_tabu_list_with_package(name_of_truck_neiborhood=Neighborhood10.Neighborhood_one_opt_standard, solution=current_sol, number_of_potial_solution=CC, number_of_loop_drone=2, tabu_list=Tabu_Structure, tabu_tenure=tabu_tenure,  index_of_loop=lenght_i[1], best_fitness=best_fitness, kind_of_tabu_structure=1, need_truck_time=False, solution_pack=solution_pack, solution_pack_len=solution_pack_len, use_solution_pack=first_time, index_consider_elite_set=index_consider_elite_set)
            current_neighborhood.append([1, current_neighborhood1])
        else:
            bb = random.random()
            if bb > 0.5:
                current_neighborhood4, solution_pack = Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood_with_tabu_list_with_package(name_of_truck_neiborhood=Neighborhood11.Neighborhood_move_2_1, solution=current_sol, number_of_potial_solution=CC, number_of_loop_drone=2, tabu_list=Tabu_Structure2, tabu_tenure=tabu_tenure2,  index_of_loop=lenght_i[4], best_fitness=best_fitness, kind_of_tabu_structure=4, need_truck_time=False, solution_pack=solution_pack, solution_pack_len=solution_pack_len, use_solution_pack=first_time, index_consider_elite_set=index_consider_elite_set)
                current_neighborhood5, solution_pack = Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood_with_tabu_list_with_package(name_of_truck_neiborhood=Neighborhood11.Neighborhood_two_opt_tue, solution=current_sol, number_of_potial_solution=CC, number_of_loop_drone=2, tabu_list=Tabu_Structure3, tabu_tenure=tabu_tenure3,  index_of_loop=lenght_i[5], best_fitness=best_fitness, kind_of_tabu_structure=5, need_truck_time=False, solution_pack=solution_pack, solution_pack_len=solution_pack_len, use_solution_pack=first_time, index_consider_elite_set=index_consider_elite_set)
                current_neighborhood.append([4, current_neighborhood4])
                current_neighborhood.append([5, current_neighborhood5])
            else:
                current_neighborhood3, solution_pack = Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood_with_tabu_list_with_package(name_of_truck_neiborhood=Neighborhood11.Neighborhood_move_1_1_standard, solution=current_sol, number_of_potial_solution=CC, number_of_loop_drone=2, tabu_list=Tabu_Structure1, tabu_tenure=tabu_tenure1,  index_of_loop=lenght_i[3], best_fitness=best_fitness, kind_of_tabu_structure=3, need_truck_time=False, solution_pack=solution_pack, solution_pack_len=solution_pack_len, use_solution_pack=first_time, index_consider_elite_set=index_consider_elite_set)
                current_neighborhood.append([3, current_neighborhood3])

        # print("hehe")
        #     current_neighborhood3 = Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood_with_tabu_list(name_of_truck_neiborhood=Neighborhood11.Neighborhood_move_1_1_ver2, solution=current_sol, number_of_potial_solution=3, number_of_loop_drone=2, tabu_list=Tabu_Structure1, tabu_tenure=tabu_tenure1,  index_of_loop=i, best_fitness=best_fitness, is_1_0=False)
        #     current_neighborhood.append([3, current_neighborhood3])
        index = [0] * len(current_neighborhood)
        min_nei = [100000] * len(current_neighborhood)
        min_sum = [1000000000] * len(current_neighborhood)
        # print(current_neighborhood)
        for j in range(len(current_neighborhood)):
            if current_neighborhood[j][0] in [1, 2]:
                for k in range(len(current_neighborhood[j][1])):
                    cfnode = current_neighborhood[j][1][k][1][0]
                    if cfnode - best_fitness < epsilon:
                        min_nei[j] = cfnode
                        index[j] = k
                        best_fitness = cfnode
                        best_sol = current_neighborhood[j][1][k][0]
                        LOOP_IMPROVED = i

                    elif cfnode - min_nei[j] < epsilon and Tabu_Structure[current_neighborhood[j][1][k][2]] + tabu_tenure <= lenght_i[1]:
                        min_nei[j] = cfnode
                        index[j] = k
                        min_sum[j] = current_neighborhood[j][1][k][1][2]

                    elif min_nei[j] - epsilon > cfnode and Tabu_Structure[current_neighborhood[j][1][k][2]] + tabu_tenure <= lenght_i[1]:
                        if min_sum[j] > current_neighborhood[j][1][k][1][2]:
                            min_nei[j] = cfnode
                            index[j] = k
                            min_sum[j] = current_neighborhood[j][1][k][1][2]
            elif current_neighborhood[j][0] == 3:
                for k in range(len(current_neighborhood[j][1])):    
                    cfnode = current_neighborhood[j][1][k][1][0]
                    if cfnode - best_fitness < epsilon:
                        min_nei[j] = cfnode
                        index[j] = k
                        best_fitness = cfnode
                        best_sol = current_neighborhood[j][1][k][0]
                        LOOP_IMPROVED = i

                    elif cfnode - min_nei[j] < epsilon and Tabu_Structure1[current_neighborhood[j][1][k][2][0]] + tabu_tenure1 <= lenght_i[3] or Tabu_Structure1[current_neighborhood[j][1][k][2][1]] + tabu_tenure1 <= lenght_i[3]:
                        min_nei[j] = cfnode
                        index[j] = k
                        min_sum[j] = current_neighborhood[j][1][k][1][2]

                    elif cfnode < min_nei[j] - epsilon and Tabu_Structure1[current_neighborhood[j][1][k][2][0]] + tabu_tenure1 <= lenght_i[3] or Tabu_Structure1[current_neighborhood[j][1][k][2][1]] + tabu_tenure1 <= lenght_i[3]:
                        if min_sum[j] > current_neighborhood[j][1][k][1][2]:
                            min_nei[j] = cfnode
                            index[j] = k
                            min_sum[j] = current_neighborhood[j][1][k][1][2]
            elif current_neighborhood[j][0] == 4:
                for k in range(len(current_neighborhood[j][1])):
                    cfnode = current_neighborhood[j][1][k][1][0]
                    if cfnode - best_fitness < epsilon:
                        min_nei[j] = cfnode
                        index[j] = k
                        best_fitness = cfnode
                        best_sol = current_neighborhood[j][1][k][0]
                        LOOP_IMPROVED = i

                    elif cfnode - min_nei[j] < epsilon and Tabu_Structure2[current_neighborhood[j][1][k][2][0]] + tabu_tenure2 <= lenght_i[4] or Tabu_Structure2[current_neighborhood[j][1][k][2][1]] + tabu_tenure2 <= lenght_i[4] or Tabu_Structure2[current_neighborhood[j][1][k][2][2]] + tabu_tenure2 <= lenght_i[4]:
                        min_nei[j] = cfnode
                        index[j] = k
                        min_sum[j] = current_neighborhood[j][1][k][1][2]
                        
                    elif cfnode < min_nei[j] - epsilon and Tabu_Structure2[current_neighborhood[j][1][k][2][0]] + tabu_tenure2 <= lenght_i[4] or Tabu_Structure2[current_neighborhood[j][1][k][2][1]] + tabu_tenure2 <= lenght_i[4] or Tabu_Structure2[current_neighborhood[j][1][k][2][2]] + tabu_tenure2 <= lenght_i[4]:
                        if min_sum[j] > current_neighborhood[j][1][k][1][2]:
                            min_nei[j] = cfnode
                            index[j] = k
                            min_sum[j] = current_neighborhood[j][1][k][1][2]
            elif current_neighborhood[j][0] == 5:
                for k in range(len(current_neighborhood[j][1])):    
                    cfnode = current_neighborhood[j][1][k][1][0]
                    if cfnode - best_fitness < epsilon:
                        min_nei[j] = cfnode
                        index[j] = k
                        best_fitness = cfnode
                        best_sol = current_neighborhood[j][1][k][0]
                        LOOP_IMPROVED = i

                    elif cfnode - min_nei[j] < epsilon and Tabu_Structure3[current_neighborhood[j][1][k][2][0]] + tabu_tenure3 <= lenght_i[5] or Tabu_Structure3[current_neighborhood[j][1][k][2][1]] + tabu_tenure3 <= lenght_i[5]:
                        min_nei[j] = cfnode
                        index[j] = k
                        min_sum[j] = current_neighborhood[j][1][k][1][2]

                    elif cfnode < min_nei[j] - epsilon and Tabu_Structure3[current_neighborhood[j][1][k][2][0]] + tabu_tenure3 <= lenght_i[5] or Tabu_Structure3[current_neighborhood[j][1][k][2][1]] + tabu_tenure3 <= lenght_i[5]:
                        if min_sum[j] > current_neighborhood[j][1][k][1][2]:
                            min_nei[j] = cfnode
                            index[j] = k
                            min_sum[j] = current_neighborhood[j][1][k][1][2]
            else:
                for k in range(len(current_neighborhood[j][1])):
                    cfnode = current_neighborhood[j][1][k][1][0]
                    if cfnode - best_fitness < epsilon:
                        min_nei[j] = cfnode
                        index[j] = k
                        best_fitness = cfnode
                        best_sol = current_neighborhood[j][1][k][0]
                        LOOP_IMPROVED = i
                        
                    elif cfnode - min_nei[j] < epsilon:
                        min_nei[j] = cfnode
                        index[j] = k
                        min_sum[j] = current_neighborhood[j][1][k][1][2]
                        
                    elif cfnode < min_nei[j] - epsilon:
                        if min_sum[j] > current_neighborhood[j][1][k][1][2]:
                            min_nei[j] = cfnode
                            index[j] = k
                            min_sum[j] = current_neighborhood[j][1][k][1][2]
        index_best_nei = 0
        best_fit_in_cur_loop = min_nei[0]
        
        # for j in range(len(min_nei)):
        #     print(min_nei[j])
        #     print(current_neighborhood[j][1][index[j]][0])
        #     print("-------")
        
        for j in range(1, len(min_nei)):
            if min_nei[j] < best_fit_in_cur_loop:
                index_best_nei = j
                best_fit_in_cur_loop = min_nei[j]
        
        i += 1
        if current_neighborhood[index_best_nei][0] in [1, 2]:
            lenght_i[1] += 1
        
        if current_neighborhood[index_best_nei][0] == 3:
            lenght_i[3] += 1
            
        if current_neighborhood[index_best_nei][0] == 4:
            lenght_i[4] += 1
            
        if current_neighborhood[index_best_nei][0] == 5:
            lenght_i[5] += 1
            
        # print(current_neighborhood[index_best_nei][0])
        # print(len(current_neighborhood[index_best_nei][1]))
        # print(current_neighborhood[index_best_nei][1])
        # print(lenght_i[1], " then ", Tabu_Structure)
        # print(lenght_i[3], " then ", Tabu_Structure1)
        # print(lenght_i[4], " then ", Tabu_Structure2)
        # print(lenght_i[5], " then ", Tabu_Structure3)

        if len(current_neighborhood[index_best_nei][1]) == 0:
            # print("hahhaa")
            continue
            
        # print(index[index_best_nei])
        current_sol = current_neighborhood[index_best_nei][1][index[index_best_nei]][0]
        current_fitness = current_neighborhood[index_best_nei][1][index[index_best_nei]][1][0]
        current_truck_time = current_neighborhood[index_best_nei][1][index[index_best_nei]][1][1]
        current_sum_fitness = current_neighborhood[index_best_nei][1][index[index_best_nei]][1][2]
        # SET_LAST_10.append([current_sol, [current_fitness, current_truck_time]])
        # if len(SET_LAST_10) > 10:
        #     SET_LAST_10.pop(0)
        
        if current_neighborhood[index_best_nei][0] in [1, 2]:
            Tabu_Structure[current_neighborhood[index_best_nei][1][index[index_best_nei]][2]] = lenght_i[1] -1
            lennn[current_neighborhood[index_best_nei][0]] += 1
        
        if current_neighborhood[index_best_nei][0] == 3:
            Tabu_Structure1[current_neighborhood[index_best_nei][1][index[index_best_nei]][2][0]] = lenght_i[3] - 1 
            Tabu_Structure1[current_neighborhood[index_best_nei][1][index[index_best_nei]][2][1]] = lenght_i[3] - 1
            lennn[current_neighborhood[index_best_nei][0]] += 1
            
        if current_neighborhood[index_best_nei][0] == 4:
            Tabu_Structure2[current_neighborhood[index_best_nei][1][index[index_best_nei]][2][0]] = lenght_i[4] - 1
            Tabu_Structure2[current_neighborhood[index_best_nei][1][index[index_best_nei]][2][1]] = lenght_i[4] - 1
            Tabu_Structure2[current_neighborhood[index_best_nei][1][index[index_best_nei]][2][2]] = lenght_i[4] - 1
            lennn[current_neighborhood[index_best_nei][0]] += 1
            
        if current_neighborhood[index_best_nei][0] == 5:
            Tabu_Structure3[current_neighborhood[index_best_nei][1][index[index_best_nei]][2][0]] = lenght_i[5] - 1
            Tabu_Structure3[current_neighborhood[index_best_nei][1][index[index_best_nei]][2][1]] = lenght_i[5] - 1
            lennn[current_neighborhood[index_best_nei][0]] += 1
            
        if fit_of_sol_chosen_to_break > current_fitness:
            sol_chosen_to_break = current_sol
            fit_of_sol_chosen_to_break = current_fitness
            LOOP_IMPROVED = i
            
        

        if current_neighborhood[index_best_nei][0] in [1, 2]:
            temp = [current_neighborhood[index_best_nei][0], current_fitness, current_neighborhood[index_best_nei][1][index[index_best_nei]][2], -1, current_sol, Tabu_Structure, Tabu_Structure1]
        elif current_neighborhood[index_best_nei][0] in [3]:
            temp = [current_neighborhood[index_best_nei][0], current_fitness, current_neighborhood[index_best_nei][1][index[index_best_nei]][2][0], current_neighborhood[index_best_nei][1][index[index_best_nei]][2][1], current_sol, Tabu_Structure, Tabu_Structure1]
        else:
            temp = [current_neighborhood[index_best_nei][0], current_fitness, -1, -1, current_sol]
        Data1.append(temp)
        
        # print("------------------",i,"------------------")
        # print(current_sol)
        # print(current_fitness)
        # print(best_fitness)
        # print(current_neighborhood[index_best_nei][0])
        # print(current_neighborhood[index_best_nei][1][index[index_best_nei]][2])
        # print("Best index nei",index_best_nei)
        # print("hehe:  ", index[index_best_nei])
        # print(current_neighborhood[index_best_nei])
        # print(Function.Check_if_feasible(current_sol))
        # print(Function.cal_truck_time(current_sol))
        # print(lenght_i[1], " then ", Tabu_Structure)
        # print(lenght_i[3], " then ", Tabu_Structure1)
        # print(lenght_i[4], " then ", Tabu_Structure2)
        # print(lenght_i[5], " then ", Tabu_Structure3)
        
        end_time_sub = time.time()
        run_time_sub = end_time_sub - start_time_sub
        if run_time_sub > 900:
            print("hehe")
            break
    # print(lennn)    
    # print(lenght_i)
    # print("--before post optimization--")
    # print(best_fitness)
    
    for ii in range(len(BEST)):
        
        option = [Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood, Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood,
                  Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood, Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood,
                  Neighborhood.Neighborhood_combine_truck_and_drone_neighborhood
                ]
        
        bet_fit, best_truck_time, best_sum = Function.fitness(BEST[ii])
        list_neighborhood_change_truck_route = [Neighborhood10.Neighborhood_one_otp, Neighborhood10.Neighborhood_one_otp_plus, 
                                                Neighborhood11.Neighborhood_move_1_1_standard, Neighborhood11.Neighborhood_move_2_1,
                                                Neighborhood11.Neighborhood_two_opt_tue]
        for i in range(len(option)):
            stop = True
            while stop:
                # print(i)
                stop = False
                if i in [0, 1]:
                    neighborhood = option[i](list_neighborhood_change_truck_route[i], BEST[ii], 15, 2, True)
                elif i in [2, 3, 4]:
                    neighborhood = option[i](list_neighborhood_change_truck_route[i], BEST[ii], 15, 2, False)
                else:
                    neighborhood = option[i](BEST[ii])
                for j in range(len(neighborhood)):
                    cfnode = neighborhood[j][1][0]
                    if cfnode - bet_fit < epsilon:
                        # print(i,"----",cfnode)
                        bet_fit = cfnode
                        BEST[ii] = neighborhood[j][0]
                        best_truck_time = neighborhood[j][1][1]
                        stop = True
        if bet_fit - best_fitness < epsilon:
            print("post-opt used")
            print(bet_fit)
            best_sol = BEST[ii]
            best_fitness = bet_fit
    return best_sol, best_fitness, Result_print, solution_pack, Data1
    
# Hai mẫu bị lỗi khi chạy bộ 10 C101 1 that vào ở initial solution để thử 
def Tabu_search_for_CVRP(AA, BB, CC):
    # tabu_tenure = Data.number_of_cities * 1.5
    Data1 = []
    list_init = []
    current_sol7 = Function.initial_solution7()
    current_sol7 = Neighborhood.Turn_single_to_multi_trip(current_sol7)
    list_init.append(current_sol7)
    # print("Fisssssssssssssssss")
    # print(current_sol7)
    solution_pack = []
    
    list_fitness_init = []
    fitness5 = Function.fitness(current_sol7)

    list_fitness_init.append(fitness5)

    
    current_fitness = list_fitness_init[0][0]
    current_sol = list_init[0]
    
    for i in range(1, len(list_fitness_init)):
        if current_fitness > list_fitness_init[i][0]:
            current_sol = list_init[i]
            current_fitness = list_fitness_init[i][0]

    # Initial solution thay ở đây ------------->
    # current_sol = check     # Để dòng này làm comment để tìm initial solution theo tham lam
    # <------------- Initial solution thay ở đây 
    
    # print(best_sol) 
    # print(best_fitness)
    # print(Function.Check_if_feasible(best_sol))
    
    best_sol, best_fitness, result_print, solution_pack, Data1 = Tabu_search(init_solution=current_sol, tabu_tenure=Data.number_of_cities-1, AA=AA, BB=BB, CC=CC, first_time=True, Data1=Data1, index_consider_elite_set=0, solution_pack=solution_pack)
    for pi in range(solution_pack_len):
        # print("Heeee")
        # print(len(solution_pack))
        # print("+++++++++++++++++++++++++",len(solution_pack),"+++++++++++++++++++++++++",)
        # for iiii in range(len(solution_pack)): 
            # print(solution_pack[iiii][0])
            # print(solution_pack[iiii][1][0])
            # print("$$$$$$$$$$$$$$")
        # print("$$$$$$$$$$$$$$")
        if pi < len(solution_pack):
            print(solution_pack[pi][0])
            current_neighborhood5 = Neighborhood.swap_two_array(solution_pack[pi][0])
            
            best_sol_in_brnei = current_neighborhood5[0][0]
            best_fitness_in_brnei = current_neighborhood5[0][1][0]
            for i in range(1, len(current_neighborhood5)):
                cfnode = current_neighborhood5[i][1][0]
                if cfnode - best_fitness_in_brnei < epsilon:
                    best_sol_in_brnei = current_neighborhood5[i][0]
                    best_fitness_in_brnei = cfnode
            temp = ["break", "break", "break", "break", "break", "break", "break"]
            Data1.append(temp)
            best_sol1, best_fitness1, result_print1, solution_pack, Data1 = Tabu_search(init_solution=best_sol_in_brnei, tabu_tenure=Data.number_of_cities-1, AA=AA, BB=BB, CC=CC, first_time=False, Data1=Data1, index_consider_elite_set=pi+1, solution_pack=solution_pack)
            # print("-----------------", pi, "------------------------")
            # print(best_sol1)
            # print(best_fitness1)
            # print(len(solution_pack))
            if best_fitness1 - best_fitness < epsilon:
                best_sol = best_sol1
                best_fitness = best_fitness1
        break
        
    
    
    with open(Data.file_name, mode='w', newline='') as file:
        csv_writer = csv.writer(file)

        # Ghi dòng tiêu đề
        csv_writer.writerow(Data1[0])

        # Ghi dữ liệu
        for row in Data1[1:]:
            csv_writer.writerow(row)

    return best_fitness, best_sol
 
result = []
run_time = []
avg = 0
for i in range(ITE):
    BEST = []
    print("------------------------",i,"------------------------")
    start_time = time.time()
    best_fitness, best_sol = Tabu_search_for_CVRP(2, 4, 1)
    print("---------- RESULT ----------")
    print(best_sol)
    print(best_fitness)
    avg += best_fitness/ITE
    result.append(best_fitness)
    print(Function.Check_if_feasible(best_sol))
    end_time = time.time()
    run = end_time - start_time
    run_time.append(run)
print(result)
print(avg)
print(run_time)
