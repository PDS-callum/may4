from utils.racer import Racer
from utils.events import Event
import random

class Race:
    def __init__(self, distance, racers, window):
        self.distance = distance
        self.racers = [Racer(name) for name in racers]
        self.window = window
        for i, racer in enumerate(self.racers):
            racer.set_initial_position(len(self.racers), i, self.window.height)
        self.countdown = 3
        self.started = False
        self.finished_racers = []
        self.preview = True
        self.events = [
            Event("Engine Trouble", 0.005, 50, 0.5),
            Event("Sand Storm", 0.002, 100, 0.7),
            Event("Debris Hit", 0.003, 30, 0.6),
            Event("Critical Failure", 0.0005, 1, 0, True),
        ]

    def update(self):
        if self.preview:
            if self.window.race_started:
                self.preview = False
            else:
                self.window.draw_odds_screen(self.racers)
                return

        if self.countdown >= 0:
            self.window.draw_countdown(self.countdown)
            self.countdown -= 1
            return

        for racer in self.racers:
            if not racer.finished and not racer.destroyed:
                self._update_racer(racer)

        self.window.draw_race(self.racers, self.distance)

    def _update_racer(self, racer):
        delta_time = 0.016  # Assuming 60 FPS
        racer.update(delta_time, self.window.width - 100, self.window.height)
        self._update_racer_state(racer)

    def _update_racer_state(self, racer):
        """Update racer state including events"""
        # Random vertical movement
        if random.random() < 0.02:  # 2% chance each update to change direction
            direction = random.choice([-1, 1])
            racer.move_vertical(direction)
        
        if racer.active_event:
            racer.event_duration -= 1
            if racer.event_duration <= 0:
                racer.active_event = None
        
        if not racer.active_event:
            for event in self.events:
                if random.random() < event.probability:
                    if event.lethal:
                        self.window.play_sound('explosion')
                    elif event.name == "Engine Trouble":
                        self.window.play_sound('engine_trouble')
                    elif event.name == "Sand Storm":
                        self.window.play_sound('sand_storm')
                    elif event.name == "Debris Hit":
                        self.window.play_sound('debris_hit')
                    
                    racer.apply_event(event)
                    self.window.add_event_message(racer.name, event.name, event.lethal)
                    break
        
        base_movement = random.uniform(1.0, 1.2) * racer.velocity_x * 10 * racer.boost_multiplier  # Reduced multiplier from 20 to 10
        
        if racer.active_event:
            base_movement *= racer.active_event.speed_modifier
        
        racer.x += base_movement
        if racer.x >= self.distance:
            if not racer.finished:
                self.window.play_sound('finish')
                racer.finished = True
                racer.x = self.distance
                if racer not in self.finished_racers:
                    self.finished_racers.append(racer)