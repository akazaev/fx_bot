from include import Bot
from scipy.optimize import minimize, fmin_l_bfgs_b, anneal
import numpy as np
import matplotlib.pyplot as plt

import csv
import sqlite3 as lite
from copy import copy, deepcopy

con = lite.connect('quotes.db')
cur = con.cursor()
interval = (23600, 27600)
cur.execute('select date, time, open, high, low, close from quotes_1min where id >= %s and id <= %s' % interval)

quotes = cur.fetchall()

deposit = 10000
spread = 0.0001

bot = Bot(quotes, deposit, spread)

# volume, back_steps, len_orders, order_live, change, alfa_positive, change_negative
params = [288, 21, 27, 259, 0.00084517, 1.82448557, 0.25164]
params = [1, 20, 18, 263, 0.0009451700000000001, 1.72448557, 0.25164]

value = bot.start(params, True)
print(value[:-1])
deposit_array = value[-1]

print(len(deposit_array))
steps = np.arange(len(deposit_array))
start_deposit = np.arange(len(deposit_array))
start_deposit.fill(deposit)

plt.figure(0)
fig, ax = plt.subplots()
ax.plot(
    steps,
    deposit_array
)
ax.plot(
    steps,
    start_deposit
)
plt.show()

#print(bot.optimize(params))