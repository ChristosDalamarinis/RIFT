"""
8 Gabor Patches Visual Task - Chromatic Opponent Flicker with Luminance Control (g5.py)

Features:
- 8 Gabor patches in circular layout
- Green/Magenta opponent color flicker (averages to mid-gray)
- OPTIONAL luminance scaling that preserves fusion
- Independent smoothness control for 3 and 9 o'clock
- Orientation/tilt control for 3 and 9 o'clock
- Optimized for 60Hz flicker on 120Hz monitor
"""

from psychopy import visual, core, event
import numpy as np

# ========================= CONFIGURATION ========================

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900

# Background color - Mid-gray for chromatic fusion
BACKGROUND_COLOR = [-0.01, -0.01, -0.01]  # Mid-gray (same as t5.py)

REFRESH_RATE = 120  # Hz - CRITICAL: Must match your monitor's actual refresh rate
# NOTE: IN MACBOOK M3 120 Hz WORKS GOOD

# ================== FLICKER CONFIGURATION ========================

# Flicker settings for 9 o'clock Gabor
NINE_OCLOCK_FLICKER_FREQUENCY = 0.1  # Hz
ENABLE_NINE_OCLOCK_FLICKER = True  # Set to False to disable flicker

# Flicker settings for 3 o'clock Gabor
THREE_OCLOCK_FLICKER_FREQUENCY = 60  # Hz - GOLD STANDARD for fusion
ENABLE_THREE_OCLOCK_FLICKER = True  # Set to False to disable flicker

# ================== GABOR PARAMETERS ========================

GABOR_SIZE = 1500  # Size in pixels - SMALLER: compact; BIGGER: larger patch
CIRCLE_RADIUS = 300  # Distance from center - SMALLER: closer to fixation; BIGGER: further out
GABOR_SF = 0.05  # Spatial frequency - SMALLER: wider stripes; BIGGER: narrower stripes
GABOR_CONTRAST = 0.210  # Contrast (0-1) - SMALLER: fainter; BIGGER: bolder
GABOR_OPACITY = 0.4  # Opacity (0-1) - SMALLER: transparent; BIGGER: opaque
GABOR_PHASE = 0.5  # Phase offset - shifts stripe position

# ================== SMOOTHNESS CONTROL ========================
# Controls edge smoothness via Gaussian mask sigma
# SMALLER values = sharper edges; BIGGER = smoother blend with background

GABOR_SMOOTHNESS_DEFAULT = 0.05  # Default for all Gabors except 3 and 9 o'clock - default at 0.05
GABOR_SMOOTHNESS_9_OCLOCK = 0.05  # Smoothness for 9 o'clock Gabor - default at 0.05
GABOR_SMOOTHNESS_3_OCLOCK = 0.15  # Smoothness for 3 o'clock Gabor - default at 0.05

# ================== ORIENTATION/TILT CONTROL ========================
# Orientation in degrees (0 = horizontal stripes, 90 = vertical stripes)

ORIENTATION_DEFAULT = 0  # Default orientation for most Gabors
ORIENTATION_9_OCLOCK = 0  # Tilt for 9 o'clock Gabor (in degrees)
ORIENTATION_3_OCLOCK = -20  # Tilt for 3 o'clock Gabor (in degrees)

# ================== COLOR CONFIGURATION ========================

# Static color for NON-flickering Gabors (should be VISIBLE)
GRAY_COLOR = [0.5, 0.5, 0.5]  # Light gray - VISIBLE against mid-gray background

# ===== GREEN vs MAGENTA (opponent colors that average to gray) =====
# These flicker and fuse to mid-gray [0.0, 0.0, 0.0] at high frequency
COLOR_A = [-1.0, 1.0, -1.0]  # Bright green (from t5.py)
COLOR_B = [1.0, -1.0, 1.0]   # Bright magenta (from t5.py)
# Average: ((-1.0+1.0)/2, (1.0-1.0)/2, (-1.0+1.0)/2) = (0.0, 0.0, 0.0) ✓
# At 60Hz, these fuse to invisible mid-gray background!

# ================== LUMINANCE CONTROL ========================
# Optional: Scale brightness/luminance of flickering colors
# This preserves chromatic opponent relationship AND luminance fusion

ENABLE_LUMINANCE_SCALING = True  # Set to False to use full brightness colors

# Luminance multiplier (only used if ENABLE_LUMINANCE_SCALING = True)
LUMINANCE_MULTIPLIER = 1.0  # Range: 0.0 to 1.0
# 1.0 = Full brightness (original colors, maximum chromatic contrast)
# 0.7 = 70% brightness (dimmer, still fuses perfectly)
# 0.5 = 50% brightness (darker, fusion maintained but less chromatic pop)
# 0.3 = 30% brightness (much darker, harder to see flicker)

# WARNING: Values < 0.5 may compromise visibility and fusion quality
# IMPORTANT: Because we scale BOTH colors equally, they still average to [0.0, 0.0, 0.0]
# Mathematical proof: (COLOR_A * k + COLOR_B * k) / 2 = (COLOR_A + COLOR_B) * k / 2 = [0,0,0]

# Apply luminance scaling conditionally
if ENABLE_LUMINANCE_SCALING:
    COLOR_A_SCALED = [COLOR_A[0] * LUMINANCE_MULTIPLIER, 
                      COLOR_A[1] * LUMINANCE_MULTIPLIER, 
                      COLOR_A[2] * LUMINANCE_MULTIPLIER]
    
    COLOR_B_SCALED = [COLOR_B[0] * LUMINANCE_MULTIPLIER, 
                      COLOR_B[1] * LUMINANCE_MULTIPLIER, 
                      COLOR_B[2] * LUMINANCE_MULTIPLIER]
    
    # Verification that luminance scaling preserves fusion
    average_color = [(COLOR_A_SCALED[i] + COLOR_B_SCALED[i])/2 for i in range(3)]
    print(f"\n{'='*70}")
    print(f"LUMINANCE SCALING ENABLED: {LUMINANCE_MULTIPLIER * 100:.0f}%")
    print(f"Scaled GREEN: {[round(c, 2) for c in COLOR_A_SCALED]}")
    print(f"Scaled MAGENTA: {[round(c, 2) for c in COLOR_B_SCALED]}")
    print(f"Average: {[round(c, 3) for c in average_color]}")
    print(f"Background: {BACKGROUND_COLOR}")
    print(f"Will fuse? {'✓ YES' if all(abs(average_color[i] - BACKGROUND_COLOR[i]) < 0.01 for i in range(3)) else '✗ NO'}")
    print(f"{'='*70}\n")
else:
    # Use original colors without scaling
    COLOR_A_SCALED = COLOR_A
    COLOR_B_SCALED = COLOR_B
    print(f"\nLuminance scaling: DISABLED (using full brightness colors)\n")

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
    At 60Hz flicker on a 120Hz monitor, this will alternate every 2 frames.
    """
    frames_per_cycle = refresh_rate / flicker_freq  # Full cycle
    if (frame_num % frames_per_cycle) < (frames_per_cycle / 2):
        return color_a
    else:
        return color_b

def create_custom_mask(size, sigma):
    """
    Create a custom Gaussian mask with adjustable smoothness.
    Smaller sigma = sharper edges; Larger sigma = smoother edges
    """
    # Create coordinate grids
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    
    # Calculate distance from center
    distance = np.sqrt(X**2 + Y**2)
    
    # Apply Gaussian function
    mask = np.exp(-(distance**2) / (2 * sigma**2))
    
    # Scale to -1 to 1 range for PsychoPy
    mask = 2 * mask - 1
    
    return mask

# ==================== SETUP ====================

win = visual.Window(
    size=[WINDOW_WIDTH, WINDOW_HEIGHT],
    color=BACKGROUND_COLOR,
    units='pix',
    fullscr=False,
    monitor='testMonitor',
    waitBlanking=True  # CRITICAL for accurate timing
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
    
    # Determine smoothness for this Gabor
    if hour == 9:
        smoothness = GABOR_SMOOTHNESS_9_OCLOCK
    elif hour == 3:
        smoothness = GABOR_SMOOTHNESS_3_OCLOCK
    else:
        smoothness = GABOR_SMOOTHNESS_DEFAULT
    
    # Determine orientation for this Gabor
    if hour == 9:
        orientation = ORIENTATION_9_OCLOCK
    elif hour == 3:
        orientation = ORIENTATION_3_OCLOCK
    else:
        orientation = ORIENTATION_DEFAULT
    
    # Create custom mask for this Gabor
    custom_mask = create_custom_mask(size=256, sigma=smoothness)
    
    # Create Gabor patch
    gabors[hour] = visual.GratingStim(
        win,
        tex='sin',  # Sinusoidal grating
        mask=custom_mask,  # Custom Gaussian mask
        size=GABOR_SIZE,
        pos=pos,
        sf=GABOR_SF,
        ori=orientation,
        contrast=GABOR_CONTRAST,
        opacity=GABOR_OPACITY,
        phase=GABOR_PHASE,
        color=GRAY_COLOR,  # Start with gray
        units='pix'
    )

# ==================== TRIAL LOOP ====================

print("\n" + "="*70)
print("8 GABOR PATCHES - CHROMATIC OPPONENT FLICKER (g5.py)")
print("="*70)
print(f"Background: Mid-gray {BACKGROUND_COLOR}")
print(f"Flicker colors: GREEN {[round(c, 2) for c in COLOR_A_SCALED]} ↔ MAGENTA {[round(c, 2) for c in COLOR_B_SCALED]}")
print(f"Luminance: {'ENABLED (' + str(int(LUMINANCE_MULTIPLIER * 100)) + '%)' if ENABLE_LUMINANCE_SCALING else 'DISABLED (100%)'}")
print(f"Color average: [0.0, 0.0, 0.0] (matches background for FUSION)")
print(f"Refresh rate: {REFRESH_RATE} Hz")
print(f"9 o'clock: {NINE_OCLOCK_FLICKER_FREQUENCY} Hz {'FLICKER' if ENABLE_NINE_OCLOCK_FLICKER else 'STATIC'}, Tilt: {ORIENTATION_9_OCLOCK}°")
print(f"3 o'clock: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz {'FLICKER' if ENABLE_THREE_OCLOCK_FLICKER else 'STATIC'}, Tilt: {ORIENTATION_3_OCLOCK}°")
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
            # Flicker between GREEN and MAGENTA (scaled opponent colors)
            current_color = calculate_color_flicker_frame(
                frame_num,
                NINE_OCLOCK_FLICKER_FREQUENCY,
                REFRESH_RATE,
                COLOR_A_SCALED,  # Scaled green
                COLOR_B_SCALED   # Scaled magenta
            )
            gabors[hour].color = current_color
            
            # Track flicker switches for verification
            current_state = (frame_num % (REFRESH_RATE / NINE_OCLOCK_FLICKER_FREQUENCY)) < (REFRESH_RATE / NINE_OCLOCK_FLICKER_FREQUENCY / 2)
            if last_flicker_state_9 is not None and current_state != last_flicker_state_9:
                flicker_switches_9.append(current_time)
            last_flicker_state_9 = current_state
            
            gabors[hour].draw()
            
        elif hour == 3 and ENABLE_THREE_OCLOCK_FLICKER:
            # Flicker between GREEN and MAGENTA (scaled opponent colors)
            current_color = calculate_color_flicker_frame(
                frame_num,
                THREE_OCLOCK_FLICKER_FREQUENCY,
                REFRESH_RATE,
                COLOR_A_SCALED,  # Scaled green
                COLOR_B_SCALED   # Scaled magenta
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

print("\n" + "="*70)
print("TIMING VERIFICATION")
print("="*70)

# Calculate frame rate
if len(frame_times) > 1:
    frame_intervals = np.diff(frame_times)
    mean_frame_interval = np.mean(frame_intervals)
    actual_refresh_rate = 1.0 / mean_frame_interval
    print(f"\nActual refresh rate: {actual_refresh_rate:.1f} Hz")
    print(f"Expected: {REFRESH_RATE} Hz")
    print(f"Match: {'✓ YES' if abs(actual_refresh_rate - REFRESH_RATE) < 5 else '✗ NO'}")

# Calculate actual flicker frequency for 9 o'clock
if ENABLE_NINE_OCLOCK_FLICKER and len(flicker_switches_9) > 1:
    switch_intervals = np.diff(flicker_switches_9)
    mean_switch_interval = np.mean(switch_intervals)
    actual_flicker_frequency = 1.0 / (2 * mean_switch_interval)
    
    print(f"\n9 O'CLOCK GABOR FLICKER:")
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
    
    print(f"\n3 O'CLOCK GABOR FLICKER:")
    print(f"  Flicker switches recorded: {len(flicker_switches_3)}")
    print(f"  Actual flicker frequency: {actual_flicker_frequency:.1f} Hz")
    print(f"  Expected: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz")
    match = abs(actual_flicker_frequency - THREE_OCLOCK_FLICKER_FREQUENCY) < 2
    print(f"  Match: {'✓ YES' if match else '✗ NO'}")
    
    # Special check for 60Hz on 120Hz monitor
    if THREE_OCLOCK_FLICKER_FREQUENCY == 60 and REFRESH_RATE == 120:
        frames_per_cycle = REFRESH_RATE / THREE_OCLOCK_FLICKER_FREQUENCY
        print(f"\n  60Hz on 120Hz optimization: {frames_per_cycle:.0f} frames per half-cycle")
        print(f"  Green ↔ Magenta alternates every {frames_per_cycle:.0f} frames")
        print(f"  → CHROMATIC FUSION to invisible gray!")

print("="*70 + "\n")

win.close()
core.quit()





# the only addtion compared to 4.py is the luminance control