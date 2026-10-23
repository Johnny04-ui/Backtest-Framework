class Position:
    """"
    具有如下属性：
        code
        average_cost
        quantity
        available_quantity
        market_price
    有如下方法:
        today_buy_quantity              今天的买入量
        cost_value                      返回总成本
        market_value                    返回总市值
        unrealized_pnl                  返回浮动盈亏
        update_market_price             更新市场价
        add_buy                         新增买入仓位，会改变average_cost, quantity, 
        reduce_sell                     删掉卖出的仓位， 会改变quantity和available_quantity
        settle                          更新available_quantity为quantity
    """
    def __init__(
            self,
            code : str,
            average_cost : float,
            quantity : int,
            available_quantity : int | None = None,
            market_price : float | None = None,
            ):
        if not code:
            raise ValueError("股票代码不能为空")
        if average_cost <= 0 :
            raise ValueError("平均成本价必须大于0")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("持仓数量必须是正整数")
        if market_price is not None and market_price <= 0:
            raise ValueError("市场价格必须大于 0")

        self.code = code
        self.average_cost = float(average_cost)
        self.quantity = quantity
        self.available_quantity = quantity if available_quantity is None else available_quantity
        self.market_price = self.average_cost if market_price is None else float(market_price)


    @property
    def today_buy_quantity(self) :
        return(
            self.quantity - self.available_quantity
        )

    @property
    def cost_value(self) :
        return(
            self.average_cost * self.quantity
        )

    @property
    def market_value(self) : 
        return(
            self.market_price * self.quantity
        )

    @property
    def unrealized_pnl(self) : 
        return (
            self.market_value-self.cost_value
            )
    
    def update_market_price(
            self,
            new_price : float
    ):
        if new_price <= 0 :
            raise ValueError("市场价格必须大于0")
        self.market_price = float(new_price)
    
    def add_buy(
            self,
            price : float,
            quantity : int,
            fee : float
    ):
        if price <= 0:
            raise ValueError("买入价格必须大于 0")

        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("买入数量必须是正整数")

        if fee < 0:
            raise ValueError("手续费不能小于 0")

        old_cost_value = (
            self.average_cost * self.quantity
        )
        new_cost_value = (
            price * quantity + fee
        )

        new_quantity = (
            self.quantity + quantity
        )
        self.average_cost = (
            old_cost_value + new_cost_value
        )/new_quantity

        self.quantity = new_quantity
        self.market_price = float(price)

    def reduce_sell(
            self, 
            quantity : int,

    ):
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("卖出数量必须是正整数")

        if quantity > self.available_quantity:
            raise ValueError(
                f"可卖数量不足："
                f"想卖 {quantity} 股，"
                f"实际只能卖 {self.available_quantity} 股"
            )
        self.quantity -= quantity
        self.available_quantity -= quantity

    def settle(self) :
        #进入下一个交易日后执行结算。
        self.available_quantity = self.quantity

class Trade:
    """
    具有如下属性
        trade_date
        code
        side
        price
        quantity
        fee
        realized_pnl
        cash_after
    有如下方法
        __repr__        阅读这一条交易记录
    """
    def __init__(
            self,
            trade_date : str,
            code : str,
            side : str,
            price : float,
            quantity: int,
            fee : float,
            realized_pnl : float,
            cash_after : float
    ):
        side = side.upper()

        if side not in ("BUY", "SELL"):
            raise ValueError(
                "side 只能是 BUY 或 SELL"
            )
        self.trade_date = trade_date
        self.code = code
        self.side = side
        self.price = float(price)
        self.quantity = quantity

        self.amount = (self.price * self.quantity)
        self.fee = float(fee)
        self.realized_pnl = float(realized_pnl)
        self.cash_after = float(cash_after)
    
    def __repr__(self) -> str:
        """
        当你 print(trade) 时，
        返回一段容易阅读的文字。
        """
        return (
            f"Trade("
            f"date={self.trade_date}, "
            f"code={self.code}, "
            f"side={self.side}, "
            f"price={self.price:.2f}, "
            f"quantity={self.quantity}, "
            f"fee={self.fee:.2f}, "
            f"realized_pnl={self.realized_pnl:.2f}, "
            f"cash_after={self.cash_after:.2f}"
            f")"
        )

def transaction_cost(amount : float, side : str):
    """
    当前包括：
    1. 佣金commission
    2. 过户费transfer fee
    3. 卖出时的印花税stamp_duty
    """
    commission = max(5, amount* 0.0003)
    transfer_fee = amount * 0.00001
    if side == "SELL":
        stamp_duty = (
            amount * 0.0005
        )
    else:
        stamp_duty = 0.0

    return (
        commission
        + transfer_fee
        + stamp_duty
    )

class Account:
    """
    具有如下属性
        initial balance
        cash
        positions
        trade_records
    具有如下方法
        total_unrealized_pnl
        total_realized_pnl
        buy                             立即购买，同时改变average_cost, available_quantity
        sell
        settle                          更新所有持仓的available_quantity为quantity
        update_market_price             更新持仓中某只股票的最新价格
        total_asset                     返回当前账户的总资产
        nav                             返回当前账户的净值

    
    """
    def __init__(self, 
                 initial_balance : float = 0.0,
                 cash : float | None = None,
                 positions : dict[str, Position] | None = None,
                 trade_records : list[Trade] | None = None
                 ):
        self.initial_balance = float(initial_balance)
        self.positions = {} if positions is None else positions
        self.cash = initial_balance if cash is None else cash
        self.trade_records = trade_records if trade_records else []
        self.total_fee = sum(trade.fee for trade in self.trade_records)
    @property
    def total_unrealized_pnl(self):
        """账户全部持仓的浮动盈亏。"""
        return sum(position.unrealized_pnl for position in self.positions.values())   
    @property
    def total_realized_pnl(self):
        """账户所有已完成卖出的实际盈亏。"""
        return sum(trade.realized_pnl for trade in self.trade_records if trade.side == 'SELL')
    def buy(
            self,
            trade_date : str,
            code : str,
            price : float,
            quantity : int
    ) -> Trade :
        if price <= 0: raise ValueError("买入价格必须大于 0")
        if not isinstance(quantity, int) or quantity <= 0: raise ValueError("买入数量必须是正整数")

        amount = price * quantity
        fee = transaction_cost(amount = amount, side = "BUY")

        total_payment = amount + fee
        if self.cash < total_payment :
            raise ValueError(
                f"现金不足："
                f"需要 {total_payment:.2f} 元，"
                f"实际只有 {self.cash:.2f} 元"
            )

        self.cash -= total_payment
        self.total_fee += fee

        if code in self.positions:
            self.positions[code].add_buy(
                price = price,
                quantity = quantity,
                fee = fee
            )
        else :
            average_cost = total_payment / quantity
            self.positions[code]  = Position(code = code, 
                                             average_cost = average_cost,
                                             quantity = quantity,
                                             available_quantity = 0,
                                             market_price = price)
        #交易记录
        trade = Trade(
            trade_date = trade_date,
            code = code,
            side = "BUY",
            price = price,
            quantity = quantity,
            fee = fee,
            realized_pnl = 0.0,
            cash_after = self.cash
        )
        self.trade_records.append(trade)
        return trade
    def sell(
        self,
        trade_date: str,
        code: str,
        price: float,
        quantity: int | None = None,
    ) -> Trade:
        """
        立即卖出股票。
        quantity=None 表示卖出全部可卖持仓。
        """
        if code not in self.positions:
            raise ValueError(
                f"账户中没有 {code} 的持仓"
            )
        if price <= 0:
            raise ValueError("卖出价格必须大于 0")
        position = self.positions[code]
        # 没有填写数量时，默认全部卖出。
        if quantity is None:
            quantity = position.available_quantity
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError(
                "没有可卖持仓，或者卖出数量不正确"
            )
        if quantity > position.available_quantity:raise ValueError(
                f"可卖数量不足："
                f"想卖 {quantity} 股，"
                f"实际只能卖 "
                f"{position.available_quantity} 股"
            )
        amount = price * quantity
        fee = transaction_cost(amount=amount,side="SELL")
        # 平均成本中已经包含了买入手续费。
        sold_cost = position.average_cost* quantity
        realized_pnl = amount- fee- sold_cost
        self.cash += amount - fee
        self.total_fee += fee
        # 先更新市场价，再扣除持仓数量。
        position.update_market_price(price)
        position.reduce_sell(quantity)

        trade = Trade(
            trade_date=trade_date,
            code=code,
            side="SELL",
            price=price,
            quantity=quantity,
            fee=fee,
            realized_pnl=realized_pnl,
            cash_after=self.cash,
        )
        self.trade_records.append(trade)

        # 全部卖完后，从持仓字典中删除
        if position.quantity == 0:
            del self.positions[code]

        return trade
    def settle(self):
        for position in self.positions.values():
            position.settle()
    def update_market_price(
        self,
        code: str,
        price: float,
    ) -> None:
        """更新某只持仓的最新价格。"""
        if code not in self.positions:
            return

        self.positions[code].update_market_price(
            price
        )
    def total_asset(self) -> float:
        total_market_value = sum(position.market_value for position in self.positions.values())
        return (self.cash + total_market_value)
    def nav(self) -> float:
        return (self.total_asset() / self.initial_balance)



#测试代码
if __name__ == "__main__" : 
    current_positions = Position('510500.SH', 10, 100)
    current_account = Account(1, 10000, current_balance = None, positions = {current_positions.code : current_positions})
    print(current_account.nav())


    