from include import Bot
from scipy.optimize import minimize, fmin_l_bfgs_b, anneal
from numpy import arange
import timeit
from random import uniform

import csv

quote_file = open('quote.csv', 'r')
reader = csv.reader(quote_file, delimiter=';')

account_file = open('bruteforce\\account.csv', 'w', newline='')
account_writer = csv.writer(account_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

deposit = 10000
spread = 0.0001

quotes = []
count = 0
for row in reader:
    if count > 0:
        quotes.append(row)
    count += 1

quote_file.close()

bot = Bot(quotes, deposit, spread)
#print(bot.start(params))

params = [300, 30, 30, 240, 0.001, 1.5, 0.1]

#t = timeit.timeit('bot.start(params)', number=1, setup='from __main__ import bot, params')

params = [
    (1, 320, 40),       # volume
    (1, 60, 10),        # back_steps
    (1, 200, 50),      # len_orders
    (1, 600, 60),      # order_live
    (0.001, 0.01, 0.001), # change
    (1, 5, 0.1),        # alfa_poisitve
    (0.001, 0.5, 0.1)     # change_negative
]


def get_param(j):
    return(uniform(params[j][0], params[j][1]))

c = 0
for i in range(45000):
    volume = get_param(0)
    len_orders = get_param(2)
    if volume*len_orders > deposit*0.9:
        volume = deposit*0.9/len_orders
    bot_params = [
        volume,
        get_param(1),
        len_orders,
        get_param(3),
        get_param(4),
        get_param(5),
        get_param(6)
    ]
    result = bot.start(bot_params)
    #print(c, ";", bot_params, ";", result)
    print(c)
    c += 1
    account_writer.writerow([
        c,
        bot_params,
        result
    ])

account_file.close()
