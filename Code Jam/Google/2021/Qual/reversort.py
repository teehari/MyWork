# -*- coding: utf-8 -*-
#import itertools

def find_seq(m,cost):

    def max_cost(n):
        if n == 1:
            return 0
        cost = max_cost(n - 1) + n
        return cost

    def reversort(l):
        cost = 0
        for i in range(0,len(l) - 1):
            min_l = l.index(min(l[i:]))
            if i > 0:
                rev_list = l[min_l:i-1:-1]
            else:
                rev_list = l[min_l::-1]
            cost += len(rev_list)
            l = l[:i] + rev_list + l[i+len(rev_list):]
        return cost

    min_cost = m - 1
    max_cost = max_cost(m)
    min_max_list = list(range(m - 1,0,-1))
    min_max_cum_list = [sum(min_max_list[0:x:1]) for x in range(1, len(min_max_list)+1)]

    if (cost > max_cost) or (cost < min_cost):
        return "IMPOSSIBLE"

    n = cost - min_cost
    cost_range = 0
    cost_index = 0
    base_list = list(range(1,m + 1))

    if cost == min_cost:
        return " ".join([str(s) for s in base_list])

    st = -1
    en = m
    prev_cost = 0

    for cost_index, cost_item in enumerate(min_max_cum_list):
        if n <= cost_item:
            diff_range = n - prev_cost
            find_ind = base_list.index(cost_index + 1)
            if cost_index % 2 == 0:
                base_list[find_ind:find_ind + diff_range + 1] = list(reversed(base_list[find_ind:find_ind + diff_range + 1]))
            else:
                base_list[find_ind - diff_range:find_ind + 1] = list(reversed(base_list[find_ind - diff_range:find_ind + 1]))
            break
        else:
            if cost_index % 2 == 0:
                st += 1
            else:
                en -= 1
            if st == 0:
                base_list[:en] = list(reversed(base_list[:en]))
            else:
                base_list[st:en] = list(reversed(base_list[st:en]))
        prev_cost = cost_item


    return " ".join([str(s) for s in base_list])


test_cases = int(input())

for case in range(test_cases):
    str_n_cost = input().split(" ")
    n = int(str_n_cost[0])
    cost = int(str_n_cost[1])
    seq = find_seq(n,cost)
    print("Case #" + str(case + 1) + ": ", seq)

