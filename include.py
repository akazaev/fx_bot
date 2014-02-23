from copy import copy, deepcopy

class Bot:

    def __init__(self, quotes, deposit = 10000, spread = 0.0001):
        self.quotes = quotes
        self.init_deposit = deposit
        self.deposit = deposit
        self.spread = spread
        self.orders = []
        self.deposit_array = []

    def start(self, params, full_output = False):
        self.deposit = self.init_deposit
        deposit_by_orders = 0

        if type(params) == list:
            volume = int(params[0]) # объем ордера после "плеча"
            back_steps = int(params[1]) # проверяется цена на back_steps назад
            len_orders = int(params[2]) # максимальное количество одновременно открываемых ордеров
            order_live = int(params[3]) # сколько живут максимум ордера
            change = float(params[4]) # изменение, на которое реагирует бот
            alfa_positive = float(params[5]) # коэффициент, на который умножаем change, чтобы снять прибыль
            spread = self.spread
            change_negative = float(params[6]) # отрицательное изменение, при котором закрываем ордер
        elif type(params) == dict:
            volume = params["volume"]
            back_steps = params["back_steps"]
            len_orders = params["len_orders"]
            order_live = params["order_live"]
            change = params["change"]
            alfa_positive = params["alfa_positive"]
            spread = self.spread
            change_negative = params["change_negative"]

        self.orders = []
        quotes = self.quotes

        sum = 0
        max_drawdown = 99999
        max_orders = 0
        all_orders = 0
        max_profit = 0

        if back_steps > 240 or back_steps < 1:
            return(-99999)
        #if volume*len_orders > self.deposit*0.9 or volume < 1 or len_orders < 1:
        #    return(-99999)
        if order_live > 1000 or order_live < 1:
            return(-99999)
        if change > 0.99 or order_live < 0.00001:
            return(-99999)
        if alfa_positive > 99 or alfa_positive < 0.00001:
            return(-99999)
        if change_negative > 0.99 or change_negative < 0.00001:
            return(-99999)

        # volume = self.deposit*0.8/len_orders

        for i in range(back_steps, len(quotes)):
            row = quotes[i]
            row_back = quotes[i - back_steps]
            close = float(row[5])
            close_back = float(row_back[5])
            if((close - close_back)/close_back >= change): # если цена выросла, то sell
                if len(self.orders) < len_orders:
                    self.orders.append({
                        'type': 'sell',
                        'price': close - spread,
                        'delta': (close - close_back)/close_back,
                        'steps': 0
                    })
                    all_orders += 1
            if((close_back - close)/close_back >= change): # если цена упала, то buy
                if len(self.orders) < len_orders:
                    self.orders.append({
                        'type': 'buy',
                        'price': close + spread,
                        'delta': (close_back - close)/close_back,
                        'steps': 0
                    })
                    all_orders += 1

            for order in self.orders:
                order["steps"] += 1

            if len(self.orders) > max_orders:
                max_orders = len(self.orders)


            _deposit = 0
            deposit_by_orders = 0
            for order in self.orders:
                order_type, price, delta, steps = order['type'], order['price'], order['delta'], order['steps']
                if order_type == 'sell':
                    # _deposit += volume*(price - close)/price
                    _deposit += volume*price/close
                if order_type == 'buy':
                    # _deposit += volume*(close - price)/price
                    _deposit += volume*close/price
            deposit_by_orders = self.deposit + _deposit - volume*len(self.orders)
            if deposit_by_orders - self.init_deposit < max_drawdown:
                max_drawdown = deposit_by_orders - self.init_deposit
            if deposit_by_orders - self.init_deposit > max_profit:
                max_profit = deposit_by_orders - self.init_deposit

            for_remove = []
            for order in self.orders:
                order_type, price, delta, steps = order['type'], order['price'], order['delta'], order['steps']
                if order_type == 'sell' and (price - close)/price >= alfa_positive*delta:
                    for_remove.append(order)
                    sum += price - close
                    self.deposit += volume*(price - close)/price
                if order_type == 'buy' and (close - price)/price >= alfa_positive*delta:
                    for_remove.append(order)
                    sum += close - price
                    self.deposit += volume*(close - price)/price
                # просроченные ордера
                if steps > order_live or order_type == 'sell' and (price - close)/price <= -change_negative\
                    or order_type == 'buy' and (close - price)/price <= -change_negative:
                    if order_type == 'sell':
                        sum += price - close
                        self.deposit += volume*(price - close)/price
                    if order_type == 'buy':
                        sum += close - price
                        self.deposit += volume*(close - price)/price
                    for_remove.append(order)

            for order in for_remove:
                if order in self.orders:
                    self.orders.remove(order)

            orders_sum = 0
            for order in self.orders:
                order_type, price, delta, steps = order['type'], order['price'], order['delta'], order['steps']
                if order_type == 'sell':
                    orders_sum += (price - close)/price
                if order_type == 'buy':
                    orders_sum += (close - price)/price

            # if deposit_pre < deposit:
            # volume = deposit2*0.9/len_orders
            # volume = deposit*0.9/len_orders
            #len_orders = deposit*0.9/volume

            self.deposit_array.append(deposit_by_orders)

        orders_sum = 0
        for order in self.orders:
            row = quotes[-1]
            close = float(row[5])
            order_type, price, delta, steps = order['type'], order['price'], order['delta'], order['steps']
            if order_type == 'sell':
                orders_sum += price - close
                self.deposit += volume*(price - close)/price
            if order_type == 'buy':
                orders_sum += close - price
                self.deposit += volume*(close - price)/price

        # max_profit

        if full_output:
            return((deposit_by_orders, max_profit, len(self.quotes), self.deposit_array))
        else:
            return(deposit_by_orders)

    def optimize(self, params):
        optimized = False
        value = self.start(params)
        print(value)
        final_params = []

        bounds = [
            (1, 1000, 1),
            (2, 240, 1),
            (1, 200, 1),
            (10, 1000, 1),
            (0.0009, 0.1, 0.0001),
            (0.1, 10.0, 0.1),
            (0.001, 0.1, 0.001)
        ]

        step = 0
        while not optimized:
            changed = False
            for i in range(len(params)):
                var = params[i]
                new_params = deepcopy(params)
                new_params[i] = var + bounds[i][2]
                in_bounds = True
                if var + bounds[i][2] > bounds[i][1] or new_params[0]*new_params[2] > self.init_deposit*0.9:
                    in_bounds = False
                if in_bounds:
                    new_value = self.start(new_params)
                if in_bounds and new_value > value:
                    value = new_value
                    params = new_params
                    final_params = new_params
                    changed = True
                    print(step, params, value)
                    step += 1
                else:
                    new_value = params
                    new_params[i] = var - bounds[i][2]
                    in_bounds = True
                    if var - bounds[i][2] < bounds[i][0] or new_params[0]*new_params[2] > self.init_deposit*0.9:
                        in_bounds = False
                    if in_bounds:
                        new_value = self.start(new_params)
                    if in_bounds and new_value > value:
                        value = new_value
                        params = new_params
                        changed = True
                        print(step, params, value)
                        step += 1
            if not changed:
                print("optimized", in_bounds)
                break

        return(final_params)
