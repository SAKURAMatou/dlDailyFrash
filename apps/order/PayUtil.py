import decimal


class PayUtil(object):
    '''请求支付的工具类'''
    payWay = ""  # 支付方式
    totalPrice = decimal.Decimal()  # 总价
    tradeNo = ''  # 交易编号

    def __init__(self, payWay, totalPrice, tradeNo):
        self.payWay = payWay
        self.totalPrice = totalPrice
        self.tradeNo = tradeNo

    def handlePay(self):
        '''具体执行支付的方法,暂时只做演示'''
        print(f"支付订单{self.tradeNo}，通过{self.payWay}方式共支付金额{self.totalPrice}")
