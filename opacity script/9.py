"""
Docstring for 9.py

THIS SCRIPT IS MODULATING OPACITY
BE CAUTIOUS -> MIGHT NOT BE ENOUGH TO INDUCE EEG RESPONSES

THIS SCRIPT WONT INDUCE ANY EEG RESPONSES AS IT FLICKERS BETWEEN OPACITY LEVELS
BUT NO LUMINANCE CHANGE IS OCCURRING, THEREFORE NO RETINAL MODULATION HAPPENS
"""

from psychopy import visual, core, event
import numpy as np

# ============ CONFIGURATION ============
refresh_rate = 60  # SET YOUR MONITOR'S REFRESH RATE HERE 
flicker_freq = 2  # Choose flicker frequency in Hz
duration = None  # Present until ESC is pressed

# Simple window setup
win = visual.Window(
    [1200, 900], # Set to your screen resolution
    color=[-1, 0, 0], # Background colour
    units='pix',
    fullscr=False  # Windowed mode for testing
)

print(f"Using refresh rate: {refresh_rate} Hz")

# Create a simple circle
circle = visual.Circle(
    win,
    radius=100,
    pos=[0, 0], # Center of the screen
    fillColor=[0, 0, 0],  # Colour of the circle flickering in the middle of the screen
    units='pix' # Use pixel units for consistent size across different screen resolutions
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
