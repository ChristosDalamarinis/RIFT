"""
8 Gabor Patches Visual Task

- Gray background
- 8 Gabor patches arranged in circular layout
- Optional flickering at 9 and 3 o'clock positions
- Configurable refresh rate
"""

from psychopy import visual, core, event
import numpy as np

# ========================= CONFIGURATION ========================

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
BACKGROUND_COLOR = [-0.2, -0.2, -0.2]  # Negative values -> darkness
REFRESH_RATE = 360  # Hz - set to your monitor's actual refresh rate

# ================== FLICKER CONFIGURATION ========================

# Flicker settings for 9 o'clock Gabor
NINE_OCLOCK_FLICKER_FREQUENCY = 1  # Hz
ENABLE_NINE_OCLOCK_FLICKER = True  # Set to False to disable flicker

# Flicker settings for 3 o'clock Gabor
THREE_OCLOCK_FLICKER_FREQUENCY = 60  # Hz
ENABLE_THREE_OCLOCK_FLICKER = True  # Set to False to disable flicker

# ================== GABOR PARAMETERS ========================

GABOR_SIZE = 150  # Size in pixels - NOTE -> SMALLER: more compact Gabor patch; BIGGER: larger, more visible Gabor patch
CIRCLE_RADIUS = 300  # Distance from center to each Gabor - NOTE -> SMALLER: Gabors closer to fixation; BIGGER: Gabors further from center
GABOR_SF = 0.05  # Spatial frequency (cycles per pixel) - NOTE -> SMALLER: wider stripes, low frequency; BIGGER: narrower stripes, high frequency, more cycles
GABOR_CONTRAST = 0.8  # Contrast (0-1) - NOTE -> SMALLER: fainter, lower contrast (more washed out); BIGGER: bolder, higher contrast (more visible black/white difference)
GABOR_OPACITY = 1.0  # Opacity (0-1) - NOTE -> SMALLER: more transparent, see-through; BIGGER: more opaque, solid
GABOR_PHASE = 0  # Phase offset - NOTE -> SMALLER: shifts stripes one direction; BIGGER: shifts stripes in opposite direction (position of bright/dark bands)

# Gabor appearance
GRAY_COLOR = [-0.2, -0.2, -0.2]  # Mid-gray for non-flickering Gabors

# Flickering colors (for contrast flickering)
# Color A: lighter gray
COLOR_A = [0.3, 0.3, 0.3]  # Light gray
# Color B: darker gray  
COLOR_B = [-0.7, -0.7, -0.7]  # Dark gray

# Duration
TRIAL_DURATION = None  # None = infinite (until spacebar)

# ==================== HELPER FUNCTIONS ====================

def get_clock_position(hour, radius):
    """
    Get (x, y) coordinates for a clock position.
    """
    angle = (hour / 12.0) * 2 * np.pi - np.pi / 2  # 12 o'clock = top
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    return [x, y]

def calculate_color_flicker_frame(frame_num, flicker_freq, refresh_rate, color_a, color_b):
    """
    Return color_a or color_b depending on the phase of the flicker cycle.
    """
    frames_per_cycle = refresh_rate / flicker_freq  # Full cycle
    if (frame_num % frames_per_cycle) < (frames_per_cycle / 2):
        return color_a
    else:
        return color_b

def calculate_contrast_flicker(frame_num, flicker_freq, refresh_rate, contrast_high, contrast_low):
    """
    Alternate between high and low contrast values for flickering.
    """
    frames_per_cycle = refresh_rate / flicker_freq
    if (frame_num % frames_per_cycle) < (frames_per_cycle / 2):
        return contrast_high
    else:
        return contrast_low

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

# ==================== CREATE GABOR STIMULI ====================

gabors = {}

# Define 8 clock positions
clock_positions = [12, 1.5, 3, 4.5, 6, 7.5, 9, 10.5]

for hour in clock_positions:
    pos = get_clock_position(hour, CIRCLE_RADIUS)
    
    # Create Gabor patch
    gabors[hour] = visual.GratingStim(
        win,
        tex='sin',  # Sinusoidal grating
        mask='gauss',  # Gaussian mask (circular)
        size=GABOR_SIZE,
        pos=pos,
        sf=GABOR_SF,
        ori=0,  # Orientation in degrees (0 = horizontal)
        contrast=GABOR_CONTRAST,
        opacity=GABOR_OPACITY,
        phase=GABOR_PHASE,
        color=GRAY_COLOR,
        units='pix'
    )

# ==================== TRIAL LOOP ====================

print("\n" + "="*70)
print("8 GABOR PATCHES VISUAL TASK")
print("="*70)
print(f"Background: Gray")
print(f"Stimuli: 8 Gabor patches in circular layout")
print(f"Refresh rate: {REFRESH_RATE} Hz")
print(f"9 o'clock flicker: {NINE_OCLOCK_FLICKER_FREQUENCY} Hz {'(ENABLED)' if ENABLE_NINE_OCLOCK_FLICKER else '(DISABLED)'}")
print(f"3 o'clock flicker: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz {'(ENABLED)' if ENABLE_THREE_OCLOCK_FLICKER else '(DISABLED)'}")
print(f"\nPress SPACEBAR to end demo")
print("="*70 + "\n")

trial_clock = core.Clock()
frame_num = 0
trial_ended = False

# Lists to store timing data for flicker verification
frame_times = []
flicker_switches_9 = []
flicker_switches_3 = []
last_flicker_state_9 = None
last_flicker_state_3 = None

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
    
    # Draw all Gabor patches
    for hour in clock_positions:
        if hour == 9 and ENABLE_NINE_OCLOCK_FLICKER:
            # Flicker between two colors
            current_color = calculate_color_flicker_frame(
                frame_num,
                NINE_OCLOCK_FLICKER_FREQUENCY,
                REFRESH_RATE,
                COLOR_A,
                COLOR_B
            )
            gabors[hour].color = current_color
            
            # Track flicker switches for verification
            current_state = (frame_num % (REFRESH_RATE / NINE_OCLOCK_FLICKER_FREQUENCY)) < (REFRESH_RATE / NINE_OCLOCK_FLICKER_FREQUENCY / 2)
            if last_flicker_state_9 is not None and current_state != last_flicker_state_9:
                flicker_switches_9.append(current_time)
            last_flicker_state_9 = current_state
            
            gabors[hour].draw()
            
        elif hour == 3 and ENABLE_THREE_OCLOCK_FLICKER:
            # Flicker between two colors
            current_color = calculate_color_flicker_frame(
                frame_num,
                THREE_OCLOCK_FLICKER_FREQUENCY,
                REFRESH_RATE,
                COLOR_A,
                COLOR_B
            )
            gabors[hour].color = current_color
            
            # Track flicker switches for verification
            current_state = (frame_num % (REFRESH_RATE / THREE_OCLOCK_FLICKER_FREQUENCY)) < (REFRESH_RATE / THREE_OCLOCK_FLICKER_FREQUENCY / 2)
            if last_flicker_state_3 is not None and current_state != last_flicker_state_3:
                flicker_switches_3.append(current_time)
            last_flicker_state_3 = current_state
            
            gabors[hour].draw()
            
        else:
            # Draw non-flickering Gabors normally
            gabors[hour].draw()
    
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
    print(f"9 O'CLOCK GABOR FLICKER:")
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
    print(f"3 O'CLOCK GABOR FLICKER:")
    print(f"  Flicker switches recorded: {len(flicker_switches_3)}")
    print(f"  Actual flicker frequency: {actual_flicker_frequency:.1f} Hz")
    print(f"  Expected: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz")
    match = abs(actual_flicker_frequency - THREE_OCLOCK_FLICKER_FREQUENCY) < 2
    print(f"  Match: {'✓ YES' if match else '✗ NO'}")

print("="*70 + "\n")

win.close()
core.quit()




# This script creates 8 Gabors and the one's at 9 and 3 o'clock flicker at specified frequencies.
# I need to add:
# 1. The ability to choose between color flicker and gray flicker for the flickering Gabors. COLOURS MUST BE OPPOSITE ON THE COLOR WHEEL!
# 2. Timing verification at the end of the trial to confirm actual flicker frequencies. BE CAREFUL HOW IS CALCULATED!
# 3. The ability to tilt a gabor at a specified angle (e.g., 20 degrees) at 12 and 6 o'clock.
