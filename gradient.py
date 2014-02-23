from include import Bot
from scipy.optimize import minimize, fmin_l_bfgs_b, anneal
from numpy import arange

import csv
from copy import copy, deepcopy

quote_file = open('quote.csv', 'r')
reader = csv.reader(quote_file, delimiter=';')


deposit = 10000
spread = 0.0001

quotes = []
count = 0
for row in reader:
    if count > 0:
        quotes.append(row)
    count += 1

#quotes = quotes[130000:230000]
quote_file.close()


bot = Bot(quotes, deposit, spread)

bounds=[
    (1, 1000),
    (2, 240),
    (1, 200),
    (10, 1000),
    (0.0009, 0.1),
    (0.1, 10.0),
    (0.001, 0.1)
]

bounds=[
    (1, 1000, 1),
    (2, 240, 1),
    (1, 200, 1),
    (10, 1000, 1),
    (0.0009, 0.1, 0.0001),
    (0.1, 10.0, 0.1),
    (0.001, 0.1, 0.001)
]

# [190, 50, 46, 530, 0.001377, 1.449, 0.38799] 10308.72409440509
# [191, 52, 45, 427, 0.00104575, 1.532, 0.32129] 10253.014045660719
# [288, 21, 27, 259, 0.00084517, 1.82448557, 0.25164] 10336.258335411425
# [217, 42, 39, 275, 0.00117, 1.639866, 0.1962] 10227.924555149137

params = [190, 50, 46, 530, 0.001377, 1.449, 0.38799]
params = [288, 21, 27, 259, 0.00084517, 1.82448557, 0.25164]
final_params = []

#params = [349, 98, 25, 353, 0.003445169999999998, 9.92448556999998, 0.1596399999999999]

optimized = False
value = bot.start(params)
print(value)

#optimized = True
while not optimized:
    changed = False
    for i in range(len(params)):
        var = params[i]
        new_params = deepcopy(params)
        new_params[i] = var + bounds[i][2]
        in_bounds = True
        if var + bounds[i][2] > bounds[i][1] or new_params[0]*new_params[2] > deposit*0.9:
            in_bounds = False
        if in_bounds:
            new_value = bot.start(new_params)
        if in_bounds and new_value > value:
            value = new_value
            params = new_params
            final_params = new_params
            changed = True
            print(params, value)
        else:
            new_value = params
            new_params[i] = var - bounds[i][2]
            in_bounds = True
            if var - bounds[i][2] < bounds[i][0] or new_params[0]*new_params[2] > deposit*0.9:
                in_bounds = False
            if in_bounds:
                new_value = bot.start(new_params)
            if in_bounds and new_value > value:
                value = new_value
                params = new_params
                changed = True
                print(params, value)
    if not changed:
        break

print("final: ", final_params)
print("value: ", value)
