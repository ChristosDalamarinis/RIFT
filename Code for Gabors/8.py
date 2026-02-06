""" Compared to 9.py this script attempts toautoamtically determine the refresh rate.
    If it cannot be determined, it defaults to a prespecified refresh rate, definedby the user in line 24. 
    The rest of the code is the same as 9.py
"""

from psychopy import visual, core, event
import numpy as np

# Simple window setup
win = visual.Window(
    [1200, 900], 
    color=[0, 0, 0], # Black background
    units='pix',
    fullscr=False  # Windowed mode for testing
)

# Get actual refresh rate
refresh_rate = win.getActualFrameRate(nIdentical=60, nMaxFrames=120)
if refresh_rate is None:
    refresh_rate = 60.0         # Choose the refresh rate of the monitor if it cannot be measured
print(f"Monitor refresh rate: {refresh_rate} Hz")

# Use VISIBLE flicker for testing (10 Hz)
flicker_freq = 30  # Choose flicker frequency in Hz
duration = None # Present until ESC is pressed

# Create a simple circle
circle = visual.Circle(
    win,
    radius=100,
    pos=[0, 0],
    fillColor=[0, 0, 0],  # Gray circle
    units='pix'
)

fixation = visual.TextStim(win, text='+', color='white', height=30)

print(f"Flickering at {flicker_freq} Hz. Press ESC to exit.")

frame_count = 0
clock = core.Clock()

while True:
    # Current time
    t = clock.getTime()
    
    # Calculate opacity using sine wave
    opacity = 0.5 + 0.5 * np.sin(2 * np.pi * flicker_freq * t)
    
    # Update circle
    circle.opacity = opacity
    circle.draw()
    fixation.draw()
    
    win.flip()
    frame_count += 1
    
    # Exit check
    if event.getKeys(['escape']):
        break

print(f"Showed {frame_count} frames")
win.close()
core.quit()
