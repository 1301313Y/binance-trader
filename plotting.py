import sys
from BinanceAPI import BinanceAPI
import config

from app.behavior.StochOscillator import StochOscillator
from app.behavior.Burst import Burst
from app.behavior.MACD import MACD
from app.behavior.RSI import RSI
from app.behavior.WilliamsPR import WilliamsPR

sys.path.insert(0, './app')


class Plotting:

    def __init__(self, options):
        self.options = options
        self.client = BinanceAPI(config.api_key, config.api_secret)
        behavior = options.p_behavior
        if behavior is not None:
            self.behavior = self.get_behavior(options, behavior.split('_', 1) if '_' in behavior else behavior)
        else:
            self.behavior = StochOscillator(options)
        print(behavior)

    def plot(self):
        self.behavior.on_plot(self.options.symbol)

    @staticmethod
    def get_behavior(options, behavior):
        behavior_list = list()
        # Behaviors
        i = len(behavior)
        print(i)
        oscillator = StochOscillator(options)
        if i == 5:
            behavior_list.append(oscillator)
            behavior_list.append(Burst(options))
        elif i == 4:
            behavior_list.append(WilliamsPR(options))
            behavior_list.append(MACD(options))
        elif i == 3:
            behavior_list.append(RSI(options))
        print(behavior_list)
        if len(behavior_list) > 0:
            for b in behavior_list:
                if b.__class__.__name__[:i].upper() == behavior.upper():
                    return b

        return oscillator
