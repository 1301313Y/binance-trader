from behavior.Advice import Advice

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
            for b in self.behavior_list:
                action = b.on_action(symbol)
                if action == Advice.BUY:
                    count_buy += 1
                elif action == Advice.SELL:
                    count_sell += 1
                elif action == Advice.HOLD:
                    count_hold += 1
            highest = max(count_hold, max(count_buy, count_sell))
            if count_buy == count_sell:
                return Advice.HOLD
            if highest == count_buy:
                return Advice.BUY
            elif highest == count_sell:
                return Advice.SELL
            else:
                return Advice.HOLD
