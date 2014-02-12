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

# params = [300, 30, 30, 240, 0.001, 1.5, 0.1]
#
# def start_optimize(params):
#     return(0 - bot.start(params))

bounds=[
    (1, 1000),
    (2, 240),
    (1, 200),
    (10, 1000),
    (0.0009, 0.1),
    (0.1, 10.0),
    (0.001, 0.1)
]

# res = minimize(start_optimize, params, method='Anneal',
#         options={"maxiter": 1000}, tol=0.01)

# res = anneal(start_optimize, params,
#         schedule = 'boltzmann',
#         T0 = 100,
#         Tf = 0,
#         maxiter = 1000)

# print(res)

bounds=[
    (1, 1000, 1),           # 0 volume
    (2, 240, 1),            # 1 back_steps
    (1, 200, 1),            # 2 len_orders
    (10, 1000, 1),          # 3 order_live
    (0.0009, 0.1, 0.0001),  # 4 change
    (0.1, 10.0, 0.1),       # 5 alfa_positive
    (0.001, 0.1, 0.001)     # 6 change_negative
]

# [190, 50, 46, 530, 0.001377, 1.449, 0.38799] 10308.72409440509
# [191, 52, 45, 427, 0.00104575, 1.532, 0.32129] 10253.014045660719
# [288, 21, 27, 259, 0.00084517, 1.82448557, 0.25164] 10336.258335411425
# [217, 42, 39, 275, 0.00117, 1.639866, 0.1962] 10227.924555149137

params = [191, 52, 45, 427, 0.00104575, 1.532, 0.32129]

final_params = []

optimized = False

#value = bot.start(params)
#print(value)

low = 0.001
high = 0.009
prm_step = 0.0005

for prm in arange(low, high, prm_step):
    params[4] = prm
    print(prm, bot.start(params, True))

