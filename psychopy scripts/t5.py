"""
Feature Singleton Visual Search Task
- Black background
- Green circles with orientation lines
- One green diamond (singleton) with orientation line
- Diamond positioned at 3 o'clock
"""

from psychopy import visual, core, event
import numpy as np

# ========================= CONFIGURATION ========================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
BACKGROUND_COLOR = [0.4, 0.4, 0.4]  # Gray background = [0.6, 0.6, 0.6]
REFRESH_RATE = 120  # Hz - set to your monitor's actual refresh rate NOTE: 120 Hz WORKS GOOD
# NOTE: IN MACBOOK M3 120 IS THE ONE THAT PROVIDES THE BEST FLICKER
# NOTE: THIS CODE FLICKERS BETWEEN COLORS RATHER THAN ON/OFF

# ================== FLICKER CONFIGURATION ========================
# Flicker settings for 9 o'clock stimulus
NINE_OCLOCK_FLICKER_FREQUENCY = 60 # Hz - Set your desired frequency here NOTE: 60 Hz IS THE GOLD STANDARD
ENABLE_NINE_OCLOCK_FLICKER = True    # Set to False to disable flicker

# Flickering settings for 3 o'clock stimulus
THREE_OCLOCK_FLICKER_FREQUENCY =  60  # Hz - Set frequency here NOTE: 60 Hz IN MACBOOK M3 PROVIDES A GOOD FLICKER
ENABLE_THREE_OCLOCK_FLICKER = True    # Set to False to disable flicker

# Smoothness for flickering stimulus (higher = smoother edges)
FLICKER_STIMULUS_SMOOTHNESS = 5.0    # Edge smoothness for 9 o'clock circle. Higher = smoother edges

# Stimulus parameters
STIMULUS_SIZE = 80  # Radius for circles
CIRCLE_RADIUS = 300  # Distance from center to each stimulus
LINE_LENGTH = 40  # Length of orientation lines inside stimuli
LINE_WIDTH = 4  # Width of orientation lines

# Colors
GREEN_COLOR = [-1.0, 1.0, -1.0]  # Bright green
RED_COLOR = [1.0, -1.0, -1.0]  # Bright red

# New: opponent gray color for gray fusion
COLOR_A = [-1.0, 1.0, -1.0]  # Bright green
COLOR_B = [1.0, -1.0, 1.0]   # Bright magenta

# Optionally: the gray they should average to (not strictly needed for drawing)
GRAY_COLOR = [0.0, 0.0, 0.0]      # Mid-gray in rgb

# Duration
TRIAL_DURATION = None  # None = infinite (until spacebar)

# ==================== COLOR CONFIGURATION ====================
# Set the color for the 9 o'clock stimulus
# Options: GREEN_COLOR or RED_COLOR
NINE_OCLOCK_COLOR = RED_COLOR  # Change to GREEN_COLOR if you want it green
# ============================================================

# ==================== HELPER FUNCTIONS ====================
def get_clock_position(hour, radius):
    """
    Get (x, y) coordinates for a clock position.
    """
    angle = (hour / 12.0) * 2 * np.pi - np.pi / 2  # 12 o'clock = top
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    return [x, y]

def calculate_flicker_frame(frame_num, flicker_freq, refresh_rate):
    """Calculate whether stimulus should be visible this frame for flickering."""
    frames_per_cycle = refresh_rate / flicker_freq  # Full on-off cycle
    return (frame_num %  frames_per_cycle) < (frames_per_cycle / 2)

def create_smooth_gaussian_mask(size, smoothness):
    """Create a Gaussian mask for smooth edges on Flickering stimuli."""
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    distance = np.sqrt(X**2 + Y**2)
    mask = np.exp(-smoothness * distance**2)
    mask = 2 * mask - 1  # Scale to -1 to 1
    return mask

def calculate_color_flicker_frame(frame_num, flicker_freq, refresh_rate, color_a, color_b):
    """
    Return color_a or color_b depending on the phase of the flicker cycle.
    At 60Hz flicker on a 60Hz monitor, this will alternate every frame."""
    frames_per_cycle = refresh_rate / flicker_freq  # Full cycle
    if (frame_num % frames_per_cycle) < (frames_per_cycle / 2):
        return color_a
    else:
        return color_b

# ==================== SETUP ====================
win = visual.Window(
    size=[WINDOW_WIDTH, WINDOW_HEIGHT],
    color=BACKGROUND_COLOR,
    units='pix',
    fullscr=False,
    monitor='testMonitor',
    waitBlanking=True
)

# Create fixation cross
fixation = visual.ShapeStim(
    win,
    vertices=((0, -10), (0, 10), (0, 0), (-10, 0), (10, 0)),
    lineWidth=2,
    lineColor='white',
    closeShape=False
)

# Create smooth mask for flickering stimulus at 9 o'clock
smooth_mask = create_smooth_gaussian_mask(
    size=256,
    smoothness=FLICKER_STIMULUS_SMOOTHNESS
)

# ==================== CREATE STIMULI ====================
stimuli = {}
orientation_lines = {}

# Define positions and types
# At 3 o'clock: diamond (singleton)
# All others: circles
clock_positions = {
    12: ("circle", 90),      # Vertical line
    1.5: ("circle", 0),      # Horizontal line
    3: ("diamond", 0),       # SINGLETON - Diamond with horizontal line
    4.5: ("circle", 0),      # Horizontal line
    6: ("circle", 0),        # Horizontal line
    7.5: ("circle", 90),     # Vertical line
    9: ("circle", 90),       # Vertical line
    10.5: ("circle", 90)     # Vertical line
}

for hour, (stim_type, line_orientation) in clock_positions.items():
    pos = get_clock_position(hour, CIRCLE_RADIUS)

    # Determine color for this stimulus
    if hour == 9:
        stim_color = NINE_OCLOCK_COLOR
    else:
        stim_color = GREEN_COLOR

    if stim_type == "diamond":
        # Create green diamond at 3 o'clock
        diamond_vertices = [
            [pos[0], pos[1] + STIMULUS_SIZE],      # Top
            [pos[0] + STIMULUS_SIZE, pos[1]],      # Right
            [pos[0], pos[1] - STIMULUS_SIZE],      # Bottom
            [pos[0] - STIMULUS_SIZE, pos[1]]       # Left
        ]
        stimuli[hour] = visual.ShapeStim(
            win,
            vertices=diamond_vertices,
            fillColor=None,
            lineColor=stim_color,
            lineWidth=3,
            closeShape=True
        )
    else:
        # Create circle (for all positions including 9 o'clock)
        stimuli[hour] = visual.Circle(
            win,
            radius=STIMULUS_SIZE,
            pos=pos,
            fillColor=None,
            lineColor=stim_color,
            lineWidth=3,
            units='pix'
        )
    
    # Create orientation line inside each stimulus
    if line_orientation == 90:  # Vertical line
        line_start = [pos[0], pos[1] - LINE_LENGTH / 2]
        line_end = [pos[0], pos[1] + LINE_LENGTH / 2]
    else:  # Horizontal line (0 degrees)
        line_start = [pos[0] - LINE_LENGTH / 2, pos[1]]
        line_end = [pos[0] + LINE_LENGTH / 2, pos[1]]
    
    orientation_lines[hour] = visual.Line(
        win,
        start=line_start,
        end=line_end,
        lineColor=stim_color,
        lineWidth=LINE_WIDTH
    )

# ==================== TRIAL LOOP ====================
print("\n" + "="*70)
print("FEATURE SINGLETON VISUAL SEARCH TASK")
print("="*70)
print(f"Background: Black")
print(f"Stimuli: 6 green circles + 1 red circle (9 o'clock) + 1 green diamond (3 o'clock)")
print(f"9 o'clock flicker: {NINE_OCLOCK_FLICKER_FREQUENCY} Hz {'(ENABLED)' if ENABLE_NINE_OCLOCK_FLICKER else '(DISABLED)'}")
print(f"3 o'clock flicker: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz {'(ENABLED)' if ENABLE_THREE_OCLOCK_FLICKER else '(DISABLED)'}")
print(f"Task: Identify the singleton (diamond)")
print(f"\nPress SPACEBAR to end demo")
print("="*70 + "\n")

trial_clock = core.Clock()
frame_num = 0
trial_ended = False

# Lists to store timing data for flicker verification
frame_times = []
flicker_switches_9 = []
flicker_switches_3 = []
last_flicker_state_9 = True
last_flicker_state_3 = True

while not trial_ended:
    current_time = trial_clock.getTime()
    frame_times.append(current_time)

    keys = event.getKeys()
    if 'space' in keys:
        print(f"Trial ended at {trial_clock.getTime():.2f}s (spacebar pressed)\n")
        trial_ended = True
        break
    
    if TRIAL_DURATION is not None and trial_clock.getTime() >= TRIAL_DURATION:
        print(f"Trial ended at {trial_clock.getTime():.2f}s (max duration reached)\n")
        trial_ended = True
        break
    
    # Draw fixation cross
    fixation.draw()
    
    # Draw all stimuli (circles and diamond)
    for hour in stimuli:
        if hour == 9 and ENABLE_NINE_OCLOCK_FLICKER:
            # New: alternative between Color_A and Color_B
            current_color = calculate_color_flicker_frame(
                frame_num,
                NINE_OCLOCK_FLICKER_FREQUENCY,
                REFRESH_RATE,
                COLOR_A,
                COLOR_B
            )
            
            # Apply to both outline and line
            stimuli[hour].lineColor = current_color
            orientation_lines[hour].lineColor = current_color

            # Draw
            stimuli[hour].draw()
            orientation_lines[hour].draw()
        
        elif hour == 3 and ENABLE_THREE_OCLOCK_FLICKER:
             # New: alternative between Color_A and Color_B
            current_color = calculate_color_flicker_frame(
                frame_num,
                THREE_OCLOCK_FLICKER_FREQUENCY,
                REFRESH_RATE,
                COLOR_A,
                COLOR_B
            )
            
            # Apply to both outline and line
            stimuli[hour].lineColor = current_color
            orientation_lines[hour].lineColor = current_color

            # Draw
            stimuli[hour].draw()
            orientation_lines[hour].draw()
            
        else:
            # Draw non-flickering stimuli normally        
            stimuli[hour].draw()
            orientation_lines[hour].draw()
    
    # Flip to display
    win.flip()
    frame_num += 1


# ==================== TIMING VERIFICATION ====================
# Calculate actual flicker frequency for 9 o'clock
if ENABLE_NINE_OCLOCK_FLICKER and len(flicker_switches_9) > 1:
    switch_intervals = np.diff(flicker_switches_9)
    mean_switch_interval = np.mean(switch_intervals)
    actual_flicker_frequency = 1.0 / (2 * mean_switch_interval)
    
    print(f"\n{'='*70}")
    print(f"9 O'CLOCK STIMULUS FLICKER (Red Circle):")
    print(f"  Flicker switches recorded: {len(flicker_switches_9)}")
    print(f"  Actual flicker frequency: {actual_flicker_frequency:.1f} Hz")
    print(f"  Expected: {NINE_OCLOCK_FLICKER_FREQUENCY} Hz")
    match = abs(actual_flicker_frequency - NINE_OCLOCK_FLICKER_FREQUENCY) < 2
    print(f"  Match: {'✓ YES' if match else '✗ NO'}")

# Calculate actual flicker frequency for 3 o'clock
if ENABLE_THREE_OCLOCK_FLICKER and len(flicker_switches_3) > 1:
    switch_intervals = np.diff(flicker_switches_3)
    mean_switch_interval = np.mean(switch_intervals)
    actual_flicker_frequency = 1.0 / (2 * mean_switch_interval)
    
    print(f"\n{'='*70}")
    print(f"3 O'CLOCK STIMULUS FLICKER (Green Diamond):")
    print(f"  Flicker switches recorded: {len(flicker_switches_3)}")
    print(f"  Actual flicker frequency: {actual_flicker_frequency:.1f} Hz")
    print(f"  Expected: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz")
    match = abs(actual_flicker_frequency - THREE_OCLOCK_FLICKER_FREQUENCY) < 2
    print(f"  Match: {'✓ YES' if match else '✗ NO'}")


print("="*70 + "\n")

win.close()
core.quit()




# this script is an iteration of t4.py with added flicker to 3 o'clock stimulus
# this script flickers between colors




