from behavior.Advice import Advice
import pandas as pd

class BehaviorManager:
    behavior_list = list()

    def submit(self, behaviors):
        for b in behaviors:
            self.behavior_list.append(b)

    def popular_advice(self, symbol):
        if len(self.behavior_list) > 0:
            count_hold = 0
            count_buy = 0
            count_sell = 0
            buy_behaviors = list()
            sell_behaviors = list()
            neutral_behaviors = list()
            for b in self.behavior_list:
                action = b.on_action(symbol)
                if action == Advice.STRONG_BUY:
                    count_buy += 2 * b.weight()
                    buy_behaviors.append(b.__class__.__name__)
                elif action == Advice.STRONG_SELL:
                    count_sell += 2 * b.weight()
                    sell_behaviors.append(b.__class__.__name__)
                elif action == Advice.BUY:
                    count_buy += b.weight()
                    buy_behaviors.append(b.__class__.__name__)
                elif action == Advice.SELL:
                    count_sell += b.weight()
                    sell_behaviors.append(b.__class__.__name__)
                elif action == Advice.HOLD:
                    count_hold += b.weight()
                    neutral_behaviors.append(b.__class__.__name__)
            highest = max(count_hold, max(count_buy, count_sell))
            if count_buy == count_sell:
                advice = Advice.HOLD
            elif highest == count_buy:
                advice = Advice.BUY
            elif highest == count_sell:
                advice = Advice.SELL
            else:
                advice = Advice.HOLD
            print('Tick Results: [')
            buy_title = '\tBuy:  %d | %s' % (count_buy, buy_behaviors)
            sell_title = '\tSell: %d | %s' % (count_sell, sell_behaviors)
            hold_title = '\tHold: %d | %s' % (count_hold, neutral_behaviors)
            print(buy_title)
            print(sell_title)
            print(hold_title)
            print('\tAdvice: %s' % advice.name)
            print(']')
            return advice
