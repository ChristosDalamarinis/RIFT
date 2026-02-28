from psychopy import visual, event, core
import numpy as np

# Get the PsychoPy window
win = exp.window

# General settings
duration = 10
frame_rate = win.getActualFrameRate() or 60
n_frames = int(duration * frame_rate)

# ESC key to quit
escape_key = 'escape'

# Screen dimensions
screen_width = 1920
screen_height = 1080
square_size = 200
triangle_size = square_size * 3 / 4
move_factor = 0.8

# Define frequencies for each row
row_frequencies = [56, 60, 64]

# Define square positions
positions = {
    "topLeft": (-screen_width / 2 * move_factor + square_size / 2, 
                screen_height / 2 * move_factor - square_size / 2),
    "topRight": (screen_width / 2 * move_factor - square_size / 2, 
                 screen_height / 2 * move_factor - square_size / 2),
    "middleLeft": (-screen_width / 2 * move_factor + square_size / 2, 0),
    "middleRight": (screen_width / 2 * move_factor - square_size / 2, 0),
    "bottomLeft": (-screen_width / 2 * move_factor + square_size / 2, 
                   -screen_height / 2 * move_factor + square_size / 2),
    "bottomRight": (screen_width / 2 * move_factor - square_size / 2, 
                    -screen_height / 2 * move_factor + square_size / 2),
}

# Assign frequencies to rows
square_frequencies = {
    "topLeft": row_frequencies[0],
    "topRight": row_frequencies[0],
    "middleLeft": row_frequencies[1],
    "middleRight": row_frequencies[1],
    "bottomLeft": row_frequencies[2],
    "bottomRight": row_frequencies[2],
}

# Create square stimuli
squares = {name: visual.Rect(win, width=square_size, height=square_size, 
                              units="pix", pos=pos) 
           for name, pos in positions.items()}

# Create triangle
triangle_vertices = [
    (-screen_width / 2, -screen_height / 2),
    (-screen_width / 2 + triangle_size, -screen_height / 2),
    (-screen_width / 2, -screen_height / 2 + triangle_size),
]
triangle = visual.ShapeStim(win, vertices=triangle_vertices, 
                            fillColor=[0.5]*3, lineColor=[0.5]*3)

# Create text stimuli
row_texts = {
    "top": visual.TextStim(win, text=f"{row_frequencies[0]} Hz", 
                          pos=(0, screen_height / 2 * move_factor - square_size), 
                          color="white", height=30),
    "middle": visual.TextStim(win, text=f"{row_frequencies[1]} Hz", 
                             pos=(0, 0), color="white", height=30),
    "bottom": visual.TextStim(win, text=f"{row_frequencies[2]} Hz", 
                             pos=(0, -screen_height / 2 * move_factor + square_size), 
                             color="white", height=30),
}

# ===== PRE-COMPUTE ALL LUMINANCE VALUES =====
time = np.arange(n_frames) / frame_rate  # Time for each frame
luminance_values = {}
for name, freq in square_frequencies.items():
    # Pre-compute entire luminance trajectory
    luminance_values[name] = 0.58 + 0.3 * np.sin(2 * np.pi * freq * time)

# Set background once
win.color = [0.8, 0.8, 0.8]

# Create clock for timing
clock = core.Clock()

#! ===== MAIN LOOP =====
for i in range(n_frames):
    # Check for ESC
    if escape_key in event.getKeys():
        break
    
    # Update square colors from pre-computed values
    for name, square in squares.items():
        lum = luminance_values[name][i]
        square.fillColor = [lum, lum, lum]
        square.lineColor = [lum, lum, lum]
        square.draw()
    
    # Draw triangle (color already set)
    triangle.draw()
    
    # Draw text
    for text in row_texts.values():
        text.draw()
    
    # Flip
    win.flip()

# Clean up
core.quit()
