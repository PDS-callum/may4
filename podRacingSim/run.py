import tkinter as tk
from tkinter import ttk
import pygame.mixer
from utils.raceWindow import RaceWindow
from utils.race import Race

def main():
    root = tk.Tk()
    race_window = RaceWindow(root)
    
    racers = [f"Pod {i+1}" for i in range(6)]  # Create 6 racers
    race = Race(25000, racers, race_window)  # Updated to 25,000 meters
    
    def update_race():
        if not race.started or not race.is_race_finished():
            race.update()
            root.after(1400 if race.countdown >= 0 else 20, update_race)  # Even faster update rate
        else:
            print("\nRace finished!")
            # Show all racers in final standings
            race_window.draw_podium(race.finished_racers)
            # Print full results
            for i, racer in enumerate(race.finished_racers, 1):
                print(f"{i}. {racer.name}")

    try:
        update_race()
        root.mainloop()
    finally:
        pygame.mixer.quit()  # Clean up pygame mixer

if __name__ == "__main__":
    main()
