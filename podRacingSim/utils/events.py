import random
import math

class Event:
    def __init__(self, name, probability, duration, speed_modifier, lethal=False):
        self.name = name
        self.probability = probability
        self.duration = duration
        self.speed_modifier = speed_modifier
        self.lethal = lethal  # This will now only affect speed, not destroy directly

class Obstacle:
    def __init__(self, x_pos, y_pos, size=20):
        self.x_pos = x_pos
        self.y_pos = (random.randint(0, 1000) / 1000) * y_pos
        self.size = random.randint(20, 35)
        self.speed = 15
        self.y_offset = random.choice([-0.6, -0.3, 0, 0.3, 0.6])
        self.points = self._generate_shape()
        self.color = random.choice(['#8B4513', '#A0522D', '#6B4423'])  # Earth tones

    def _generate_shape(self):
        num_points = random.randint(6, 8)
        points = []
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            radius = self.size * (0.8 + random.uniform(0, 0.3))
            points.append((math.cos(angle) * radius, math.sin(angle) * radius))
        return points

    def get_shape_points(self):
        y = self.y_pos  # Use y_pos for vertical location
        return [(self.x_pos + dx, y + dy) for dx, dy in self.points]

    def update(self):
        self.x_pos -= self.speed
        return self.x_pos > -self.size  # Return False when off screen

class SpeedGate:
    def __init__(self, x_pos, y_pos, size=30):
        self.x_pos = x_pos
        self.y_pos = (random.randint(0, 1000) / 1000) * y_pos
        self.size = size
        self.speed = 15  # Same speed as obstacles
        self.y_offset = random.choice([-0.3, 0, 0.3])
        self.activated = False  # Track if a racer has used this gate
        
    def update(self):
        self.x_pos -= self.speed
        return self.x_pos > -self.size