import csv

quote_file = open('quote.csv', 'r')
reader = csv.reader(quote_file, delimiter=';')

account_file = open('account.csv', 'w', newline='')
account_writer = csv.writer(account_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

orders_file = open('orders.csv', 'w', newline='')
order_writer = csv.writer(orders_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
#
# deposit = 10000
# deposit2 = deposit
# deposit_pre = deposit
# volume = 300
# back_steps = 30
# len_orders = 30
# order_live = 240
# change = 0.001 # в процентах
# alfa_positive = 1.5 # снимать прибыль в alfa_positive больше, чем change
# spread = 0.0001
# change_negative = 0.1

# [189.77043720350144, 49.25995736617807, 47.425722007210204, 531.3052148598488, 0.0014770595232108767, 1.249316515503771, 0.38999635365856816]
prms = [293, 21, 30, 262, 0.00084517, 1.82448557, 0.25164]
deposit = 10000
deposit2 = deposit
deposit_pre = deposit
volume = prms[0]
back_steps = prms[1]
len_orders = prms[2]
order_live = prms[3]
change = prms[4] # в процентах
alfa_positive = prms[5] # снимать прибыль в alfa_positive больше, чем change
spread = 0.0001
change_negative = prms[6]

# volume = deposit*0.8/len_orders
# volume = 1000
print("объем $", volume)

quotes = [] # выгруженный из файла массив котировок
orders = []

count = 0
for row in reader:
    if count > 0:
        quotes.append(row)
    count += 1


#quotes = quotes[:int(len(quotes)/3)]
#quotes = quotes[int(len(quotes)/3):int(2*len(quotes)/3)]
#quotes = quotes[int(2*len(quotes)/3):]
#quotes = quotes[130000:230000]

print("шагов ", len(quotes))

sum = 0
drawdown = 99999 # просадка
drawdown_abs = 0
drawdown_a = 99999
max_orders = 0
all_orders = 0
max_profit = 0

for i in range(back_steps, len(quotes)):
    row = quotes[i]
    row_back = quotes[i - back_steps]
    close = float(row[5])
    close_back = float(row_back[5])
    if((close - close_back)/close_back >= change): # если цена выросла, то sell
        if len(orders) < len_orders:
            orders.append({'type': 'sell', 'price': close - spread, 'delta': (close - close_back)/close_back, 'steps': 0})
            all_orders += 1
    if((close_back - close)/close_back >= change): # если цена упала, то buy
        if len(orders) < len_orders:
            orders.append({'type': 'buy', 'price': close + spread, 'delta': (close_back - close)/close_back, 'steps': 0})
            all_orders += 1

    for order in orders:
        order["steps"] += 1

    if len(orders) > max_orders:
        max_orders = len(orders)

    _deposit = 0
    deposit2 = 0
    for order in orders:
        type, price, delta, steps = order['type'], order['price'], order['delta'], order['steps']
        if type == 'sell':
            # _deposit += volume*(price - close)/price
            _deposit += volume*price/close
        if type == 'buy':
            # _deposit += volume*(close - price)/price
            _deposit += volume*close/price
    deposit2 = deposit + _deposit - volume*len(orders)
    if deposit2 - deposit_pre < drawdown_a:
        drawdown_a = deposit2 - deposit_pre
    if deposit2 - deposit_pre > max_profit:
        max_profit = deposit2 - deposit_pre

    remove = []
    for order in orders:
        type, price, delta, steps = order['type'], order['price'], order['delta'], order['steps']
        if type == 'sell' and (price - close)/price >= alfa_positive*delta:
            remove.append(order)
            sum += price - close
            deposit += volume*(price - close)/price

            order_writer.writerow([
                "+",
                type,
                price,
                close,
                delta,
                steps
            ])
        if type == 'buy' and (close - price)/price >= alfa_positive*delta:
            remove.append(order)
            sum += close - price
            deposit += volume*(close - price)/price

            order_writer.writerow([
                "+",
                type,
                price,
                close,
                delta,
                steps
            ])
        # просроченные ордера
        if steps > order_live or type == 'sell' and (price - close)/price <= -change_negative\
            or type == 'buy' and (close - price)/price <= -change_negative:
            if type == 'sell':
                sum += price - close
                deposit += volume*(price - close)/price

                order_writer.writerow([
                    "!",
                    type,
                    price,
                    close,
                    delta,
                    steps
                ])
            if type == 'buy':
                sum += close - price
                deposit += volume*(close - price)/price

                order_writer.writerow([
                    "!",
                    type,
                    price,
                    close,
                    delta,
                    steps
                ])
            remove.append(order)

    for order in remove:
        if order in orders:
            orders.remove(order)

    orders_sum = 0
    for order in orders:
        type, price, delta, steps = order['type'], order['price'], order['delta'], order['steps']
        if type == 'sell':
            orders_sum += (price - close)/price
        if type == 'buy':
            orders_sum += (close - price)/price

    if orders_sum < drawdown:
        drawdown = orders_sum
        drawdown_abs = volume*drawdown

    account_writer.writerow([
        sum,
        orders_sum,
        sum + orders_sum,
        deposit2,
        volume
    ])

    # if deposit_pre < deposit:
    # volume = deposit2*0.9/len_orders
    # volume = deposit*0.9/len_orders
    #len_orders = deposit*0.9/volume

orders_sum = 0
for order in orders:
    row = quotes[-1]
    close = float(row[5])
    type, price, delta, steps = order['type'], order['price'], order['delta'], order['steps']
    if type == 'sell':
        orders_sum += price - close
        deposit += volume*(price - close)/price

        order_writer.writerow([
            "-",
            type,
            price,
            close,
            delta,
            steps
        ])
    if type == 'buy':
        orders_sum += close - price
        deposit += volume*(close - price)/price

        order_writer.writerow([
            "-",
            type,
            price,
            close,
            delta,
            steps
        ])


print("набралось в сумме, пункт", sum)
print("осталось ордеров", len(orders))
print("в ордерах, пункт", orders_sum)
print("остается в итоге, пункт", sum + orders_sum)
print("максимальная просадка по открытым ордерам, пункт", drawdown)
print("максимальная просадка по открытым ордерам, $", drawdown_abs)
print("максимально открыто ордеров", max_orders)
print("депозит, $", deposit)
print("прибыль в день, $", (deposit - deposit_pre)/(count/(60*24)))
print("всего ордеров", all_orders)
print("максимальная просадка от начального депозита", drawdown_a)

print("депозит 2, $", deposit2)
print("максимальная прибыль", max_profit)

quote_file.close()
account_file.close()
orders_file.close()