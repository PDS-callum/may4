import turtle
import random
from courses.default import draw_track
from PIL import ImageGrab
import numpy as np

# Screen setup
screen = turtle.Screen()
screen.setup(width=1.0, height=1.0)  # Sets window to full screen
screen.title("Turtle Race")

# Before drawing track
screen.tracer(0)  # Turn off animation

# Create track drawer first
track_drawer = turtle.Turtle()
track_drawer.speed(0)  # Fastest speed

# After screen setup, add track drawing
track_drawer.penup()
track_drawer.goto(0, 350)
track_drawer.pendown()
track_drawer.color("gray")
track_drawer.width(50)

draw_track(track_drawer)

# After drawing track
screen.update()  # Update screen once track is complete
screen.tracer(1)  # Resume animation for racers

# Racer setup (example with 3 racers)
# racer_colors = ["red", "blue", "green", "purple", "orange", "black"]
racer_colors = ["red"]
racers = []

# Modify racer setup to start at the beginning of the curve
for i in range(len(racer_colors)):
    racer = turtle.Turtle()
    racer.shape("turtle")
    racer.color(racer_colors[i])
    racer.penup()
    racer.goto(0, 350 + i * 10)  # Changed from -80 to 20
    racer.pendown()
    racers.append(racer)

# Race logic
finish_line = -50  # X-coordinate of the finish line

def get_pixel_color(x, y):
    # Convert turtle coordinates to screen coordinates
    canvas = screen.getcanvas()
    root = canvas.winfo_toplevel()
    screen_x = root.winfo_x() + canvas.winfo_width()/2 + x
    screen_y = root.winfo_y() + canvas.winfo_height()/2 - y
    
    # Capture screen at point
    image = ImageGrab.grab(bbox=(screen_x-1, screen_y-1, screen_x+1, screen_y+1))
    pixel = np.array(image)
    color = tuple(pixel[0,0])  # RGB values
    print(color)
    
    # Check if color is close to gray (track color)
    if color == (80,80,80):
        print("here")
        return "gray"
    return None

# Test at track location
# Use coordinates where you know the track is drawn
print(get_pixel_color(track_drawer.xcor(), track_drawer.ycor()))

# Update race logic in main loop to follow curves
def update_racer_direction(racer):
    x, y = racer.pos()
    color = get_pixel_color(x, y)
    if color != "gray":  # If not on track
        racer.right(10)  # Turn to find track
    else:
        x = racer.xcor()
        y = racer.ycor()
        
        # Define track segments and their target directions
        if x < -200:  # Starting straight
            target_angle = 270
        elif -200 <= x < 0:  # First curve
            target_angle = 315
        elif 0 <= x < 200:  # Second curve
            target_angle = 0
        else:  # Final straight
            target_angle = 45
        
        # Gradually adjust heading towards target angle
        current_heading = racer.heading()
        angle_diff = target_angle - current_heading
        
        # Normalize angle difference to -180 to 180 range
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360
            
        # Apply steering with some randomness
        turn_amount = angle_diff * 0.1 + random.uniform(-1, 1)
        racer.right(turn_amount)

# Main race loop
while True:
    for racer in racers:
        distance = random.randint(1, 5)
        update_racer_direction(racer)
        racer.forward(distance)
        
        # # Win condition
        # if racer.xcor() >= finish_line:
        #     print(f"{racer.color()[0]} turtle wins!")
        #     turtle.done()
        #     exit()