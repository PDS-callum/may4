import random
import math

class Event:
    def __init__(self, name, probability, duration, speed_modifier, lethal=False):
        self.name = name
        self.probability = probability
        self.duration = duration
        self.speed_modifier = speed_modifier
        self.lethal = lethal  # This will now only affect speed, not destroy directly