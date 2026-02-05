"""
Feature Singleton Visual Search Task
- Black background
- Green circles with orientation lines
- One green diamond (singleton) with orientation line
- Diamond positioned at 3 o'clock
"""

from psychopy import visual, core, event
import numpy as np

# ==================== CONFIGURATION ====================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
BACKGROUND_COLOR = [-1, -1, -1]  # Black background
REFRESH_RATE = 120 # Hz - set to your monitor's actual refresh rate NOTE: 120 Hz WORKS GOOD

# ==================== FLICKER CONFIGURATION ====================
# Flicker settings for 9 o'clock stimulus
NINE_OCLOCK_FLICKER_FREQUENCY = 60  # Hz - Set your desired frequency here NOTE: 60 Hz IS THE GOLD STANDARD
ENABLE_NINE_OCLOCK_FLICKER = True    # Set to False to disable flicker

# Smoothness for flickering stimulus (higher = smoother edges)
FLICKER_STIMULUS_SMOOTHNESS = 4.0    # Edge smoothness for 9 o'clock circle. Higher = smoother edges

# Stimulus parameters
STIMULUS_SIZE = 80  # Radius for circles
CIRCLE_RADIUS = 300  # Distance from center to each stimulus
LINE_LENGTH = 40  # Length of orientation lines inside stimuli
LINE_WIDTH = 4  # Width of orientation lines

# Colors
GREEN_COLOR = [-1.0, 1.0, -1.0]  # Bright green
RED_COLOR = [1.0, -1.0, -1.0]  # Bright red

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
        # Special handling for 9 o'clock (flickering with smooth edges)
        if hour == 9:
            # Create smooth circle using GratingStim for flickering
            stimuli[hour] = visual.GratingStim(
                win,
                tex="sin",
                mask=smooth_mask,
                pos=pos,
                size=STIMULUS_SIZE * 2, # Diameter
                sf=0,  # No grating = solid circle
                color=stim_color,
                contrast=1.0,
                units='pix'
            )
        # Create green circle
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
print(f"Stimuli: 7 green circles + 1 green diamond (at 3 o'clock)")
print(f"Task: Identify the singleton (diamond)")
print(f"\nPress SPACEBAR to end demo")
print("="*70 + "\n")

trial_clock = core.Clock()
frame_num = 0
trial_ended = False

# Lists to store timing data for flicker verification
frame_times = []
flicker_switches = []
last_flicker_state = True

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
            #apply flicker to 9 o'clock stimulus
            show_frame = calculate_flicker_frame(frame_num, NINE_OCLOCK_FLICKER_FREQUENCY, REFRESH_RATE)

            # Track flicker Switches for verification
            if show_frame != last_flicker_state:
                flicker_switches.append(current_time)
                last_flicker_state = show_frame
            
            if show_frame:
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
print("\n" + "="*70)
print("TIMING VERIFICATION")
print("="*70)
print(f"\nTotal frames displayed: {frame_num}")
print(f"Trial duration: {trial_clock.getTime():.3f} seconds")

# Calculate actual frame rate
if len(frame_times) > 1:
    frame_intervals = np.diff(frame_times)
    mean_interval = np.mean(frame_intervals)
    actual_frame_rate = 1.0 / mean_interval
    print(f"Actual frame rate: {actual_frame_rate:.1f} Hz")
    print(f"Mean frame interval: {mean_interval*1000:.2f} ms")

# Calculate actual flicker frequency for 9 o'clock stimulus
if ENABLE_NINE_OCLOCK_FLICKER and len (flicker_switches) > 1:
    switch_intervals = np.mean(np.diff(flicker_switches))
    mean_switch_interval = np.mean(switch_intervals)
    actual_flicker_frequency = 1.0 / mean_switch_interval
    print(f"\n{'=*70'}")
    print(f"9 o'clock Stimulus Flicker:") 
    print(f"Flicker switches recorded: {len(flicker_switches)}")
    print(f"Actual flicker frequency: {actual_flicker_frequency:.1f} Hz")
    print(f"Expected: {NINE_OCLOCK_FLICKER_FREQUENCY} Hz")
    match = abs(actual_flicker_frequency - NINE_OCLOCK_FLICKER_FREQUENCY) < 2
    print(f"Match: {'✓ YES' if match else '✗ NO'}")


print("="*70 + "\n")

win.close()
core.quit()








# The Verification Is Wrong:
# The current verification code has a flaw:
# actual_flicker_frequency = 1.0 / mean_switch_interval
# This measures transitions per second, 
# which is double the actual flicker frequency because each cycle has 2 transitions (ON→OFF and OFF→ON).


# ALSO:
# and "else" is missing on line 153
# Since this is missing the code reates the GratingSteim for the 9 o'clock position,
# but thne immediately overwrites it with a Circle stimulus, which does not flicker.
# NOTE: SCRIPT T3.PY SOLVES THESE PROBLEMS