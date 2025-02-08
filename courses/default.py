import numpy as np

def draw_track(track_drawer, grid_height=1080, grid_width=1920):
    grid = np.zeros((grid_height, grid_width))

    # Draw complex track
    # First straight
    track_drawer.forward(300)
    print(track_drawer.pos())
    print("a")
    quit()

    # First right
    for _ in range(30):
        track_drawer.forward(10)
        track_drawer.right(5)

    # Straight section
    track_drawer.forward(50)

    # Second right
    for _ in range(30):
        track_drawer.forward(10)
        track_drawer.right(10)

    # Straight section
    track_drawer.forward(100)

    # Left curve
    for _ in range(45):
        track_drawer.forward(5)
        track_drawer.left(2)

    # Right curve
    for _ in range(40):
        track_drawer.forward(8)
        track_drawer.right(5)

    # Straight section
    track_drawer.forward(200)

    # Right curve
    for _ in range(60):
        track_drawer.forward(4)
        track_drawer.right(1)

    # Left curve
    for _ in range(60):
        track_drawer.forward(4)
        track_drawer.left(1)

    # Left curve
    for _ in range(20):
        track_drawer.forward(3)
        track_drawer.left(6)

    # Straight section
    track_drawer.forward(100)

    # Right curve
    for _ in range(40):
        track_drawer.forward(6)
        track_drawer.right(1)

    # Right curve
    for _ in range(20):
        track_drawer.forward(3)
        track_drawer.right(6)

    # Straight section
    track_drawer.forward(100)

    # Left curve
    for _ in range(60):
        track_drawer.forward(4)
        track_drawer.left(1)

    # Right curve
    for _ in range(80):
        track_drawer.forward(3)
        track_drawer.right(2)

    # Left curve
    for _ in range(40):
        track_drawer.forward(4)
        track_drawer.left(2)

    # Straight section
    track_drawer.forward(4)

    # Right curve
    for _ in range(25):
        track_drawer.forward(3)
        track_drawer.right(4)

    # Straight section
    track_drawer.forward(280)

    track_drawer.hideturtle()