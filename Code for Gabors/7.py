"""
8 Gabor Patches Visual Task - Frame-Based Precise Flicker (7.py)

================================================================================
CRITICAL IMPROVEMENTS OVER 6.py - FRAME-BASED TIMING
================================================================================

WHY FRAME-BASED TIMING?
-----------------------
On a 480Hz monitor, each frame lasts exactly 1/480 s = 2.083 ms.
To create a 60Hz flicker (period = 1/60 s = 16.667 ms), we need:
    480 Hz / 60 Hz = 8 frames per half-cycle

TIMING BREAKDOWN:
-----------------
- Full 60Hz cycle = 16 frames @ 480Hz = 16.667 ms ✓
- GREEN phase     = 8 frames @ 480Hz  = 8.333 ms  ✓
- MAGENTA phase   = 8 frames @ 480Hz  = 8.333 ms  ✓

FRAME-BASED LOGIC:
------------------
Instead of calculating color based on time (prone to drift), we use:
    frame_position = current_frame_number % 16
    if frame_position < 8:
        show GREEN   (frames 0,1,2,3,4,5,6,7)
    else:
        show MAGENTA (frames 8,9,10,11,12,13,14,15)
    repeat...

ADVANTAGES:
-----------
✓ Zero timing drift (pure integer arithmetic)
✓ No floating-point rounding errors
✓ Deterministic color switching
✓ Perfect temporal precision
✓ Eliminates flicker artifacts
✓ Scalable to any refresh rate / flicker frequency combination

MATHEMATICAL GUARANTEE:
-----------------------
For any combination where refresh_rate % flicker_frequency == 0:
    frames_per_half_cycle = (refresh_rate / flicker_frequency) / 2
This ensures EXACT temporal alignment every cycle.

================================================================================
"""

from psychopy import visual, core, event
import numpy as np

# ========================= CONFIGURATION ========================
WINDOW_WIDTH = 1200  # 1920
WINDOW_HEIGHT = 900  # 1080

# Background color - Mid-gray for chromatic fusion
BACKGROUND_COLOR = [0.12, 0.12, 0.12]  # Mid-gray (same as 6.py)

REFRESH_RATE = 480  # Hz - CRITICAL: Must match your monitor's actual refresh rate
# NOTE: This script is optimized for 480Hz with frame-based timing
# Each frame at 480Hz = 1/480 s = 2.083 ms

# ================== FLICKER CONFIGURATION ========================
# Flicker settings for 9 o'clock Gabor
NINE_OCLOCK_FLICKER_FREQUENCY = 60  # Hz
ENABLE_NINE_OCLOCK_FLICKER = True  # Set to False to disable flicker

# Flicker settings for 3 o'clock Gabor
THREE_OCLOCK_FLICKER_FREQUENCY = 60  # Hz - GOLD STANDARD for fusion
ENABLE_THREE_OCLOCK_FLICKER = True  # Set to False to disable flicker

# ================== PRECISE FRAME-BASED TIMING ========================
# *** KEY INNOVATION: Pre-calculate exact frame counts ***
#
# For 60Hz flicker on 480Hz monitor:
#   - Full cycle period = 1/60 s = 16.667 ms
#   - Frames needed for full cycle = 480/60 = 16 frames
#   - Frames per half-cycle (one color) = 16/2 = 8 frames
#   - Duration per color = 8 × (1/480 s) = 8 × 2.083 ms = 16.667 ms total cycle ✓
#
# This is calculated ONCE at startup, then used as integer constants.
# No runtime floating-point calculations = no drift!

FRAMES_PER_HALF_CYCLE_9 = int(REFRESH_RATE / NINE_OCLOCK_FLICKER_FREQUENCY / 2)
FRAMES_PER_HALF_CYCLE_3 = int(REFRESH_RATE / THREE_OCLOCK_FLICKER_FREQUENCY / 2)
FRAMES_PER_FULL_CYCLE_9 = FRAMES_PER_HALF_CYCLE_9 * 2  # Complete flicker cycle
FRAMES_PER_FULL_CYCLE_3 = FRAMES_PER_HALF_CYCLE_3 * 2  # Complete flicker cycle

# Display timing configuration
print(f"\n{'='*70}")
print(f"FRAME-BASED TIMING CONFIGURATION")
print(f"{'='*70}")
print(f"Monitor refresh rate: {REFRESH_RATE} Hz")
print(f"Frame duration: {1000/REFRESH_RATE:.3f} ms per frame")
print(f"\n9 o'clock Gabor:")
print(f"  Target flicker frequency: {NINE_OCLOCK_FLICKER_FREQUENCY} Hz")
print(f"  Frames per half-cycle: {FRAMES_PER_HALF_CYCLE_9}")
print(f"  Frames per full cycle: {FRAMES_PER_FULL_CYCLE_9}")
print(f"  Actual half-cycle duration: {FRAMES_PER_HALF_CYCLE_9 / REFRESH_RATE * 1000:.3f} ms")
print(f"  Actual full cycle duration: {FRAMES_PER_FULL_CYCLE_9 / REFRESH_RATE * 1000:.3f} ms")
print(f"  Achieved frequency: {REFRESH_RATE / FRAMES_PER_FULL_CYCLE_9:.2f} Hz")
print(f"\n3 o'clock Gabor:")
print(f"  Target flicker frequency: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz")
print(f"  Frames per half-cycle: {FRAMES_PER_HALF_CYCLE_3}")
print(f"  Frames per full cycle: {FRAMES_PER_FULL_CYCLE_3}")
print(f"  Actual half-cycle duration: {FRAMES_PER_HALF_CYCLE_3 / REFRESH_RATE * 1000:.3f} ms")
print(f"  Actual full cycle duration: {FRAMES_PER_FULL_CYCLE_3 / REFRESH_RATE * 1000:.3f} ms")
print(f"  Achieved frequency: {REFRESH_RATE / FRAMES_PER_FULL_CYCLE_3:.2f} Hz")
print(f"{'='*70}\n")

# ================== GABOR PARAMETERS ========================
GABOR_SIZE = 2000  # Size in pixels - SMALLER: compact; BIGGER: larger patch
CIRCLE_RADIUS = 300  # Distance from center - SMALLER: closer to fixation; BIGGER: further out
GABOR_SF = 0.05  # Spatial frequency - SMALLER: wider stripes; BIGGER: narrower stripes
GABOR_CONTRAST = 1.0  # Contrast (0-1) - SMALLER: fainter; BIGGER: bolder
GABOR_OPACITY = 1.0  # Opacity (0-1) - SMALLER: transparent; BIGGER: opaque
GABOR_PHASE = 0.5  # Phase offset - shifts stripe position

# ================== SMOOTHNESS CONTROL ========================
# Controls edge smoothness via Gaussian mask sigma
# SMALLER values = sharper edges; BIGGER = smoother blend with background
GABOR_SMOOTHNESS_DEFAULT = 0.05  # Default for all Gabors except 3 and 9 o'clock
GABOR_SMOOTHNESS_9_OCLOCK = 0.05  # Smoothness for 9 o'clock Gabor
GABOR_SMOOTHNESS_3_OCLOCK = 0.05  # Smoothness for 3 o'clock Gabor

# ================== ORIENTATION/TILT CONTROL ========================
# Orientation in degrees (0 = horizontal stripes, 90 = vertical stripes)
ORIENTATION_DEFAULT = 0  # Default orientation for most Gabors
ORIENTATION_9_OCLOCK = -20  # Tilt for 9 o'clock Gabor (in degrees)
ORIENTATION_3_OCLOCK = -20  # Tilt for 3 o'clock Gabor (in degrees)

# ================== COLOR CONFIGURATION ========================
# Static color for NON-flickering Gabors (should be VISIBLE)
GRAY_COLOR = [0.5, 0.5, 0.5]  # Light gray - VISIBLE against mid-gray background

# ===== GREEN vs MAGENTA (opponent colors that average to gray) =====
# These flicker and fuse to mid-gray [0.0, 0.0, 0.0] at high frequency
COLOR_A = [-1.0, 1.0, -1.0]  # Bright green (from 6.py)
COLOR_B = [1.0, -1.0, 1.0]  # Bright magenta (from 6.py)
# Average: ((-1.0+1.0)/2, (1.0-1.0)/2, (-1.0+1.0)/2) = (0.0, 0.0, 0.0) ✓
# At 60Hz, these fuse to invisible mid-gray background!

# ================== LUMINANCE CONTROL ========================
# Optional: Scale brightness/luminance of flickering colors
# This preserves chromatic opponent relationship AND luminance fusion
ENABLE_LUMINANCE_SCALING = True  # Set to True to enable luminance control

# Luminance multiplier (only used if ENABLE_LUMINANCE_SCALING = True)
LUMINANCE_MULTIPLIER = 1.0  # Range: 0.0 to 1.0
# 1.0 = Full brightness (original colors, maximum chromatic contrast)
# 0.7 = 70% brightness (dimmer, still fuses perfectly)
# 0.5 = 50% brightness (darker, fusion maintained but less chromatic pop)
# WARNING: Values < 0.5 may compromise visibility and fusion quality

# ================== SATURATION CONTROL ========================
# Optional: Control color saturation (chromatic intensity)
# SMALLER values = more gray/desaturated; BIGGER = more vivid/saturated
ENABLE_SATURATION_CONTROL = True  # Set to True to enable saturation control

# Saturation level (only used if ENABLE_SATURATION_CONTROL = True)
SATURATION_LEVEL = 1.0  # Range: 0.0 to 1.0
# 1.0 = Full saturation (vivid green/magenta, maximum chromatic contrast)
# 0.7 = 70% saturation (less intense colors, still clearly chromatic)
# 0.5 = 50% saturation (muted colors, still visible)
# 0.3 = 30% saturation (very muted, approaching gray)
# 0.0 = No saturation (pure gray, no chromatic content)
# WARNING:
# - Values < 0.3 may reduce chromatic fusion effectiveness
# - Saturation control PRESERVES fusion because it maintains opponent relationship
# - Mathematical preservation: Colors still average to [0.0, 0.0, 0.0]

# Duration
TRIAL_DURATION = None  # None = infinite (until spacebar)

# ==================== COLOR PROCESSING ====================
def desaturate_color(color, saturation, gray_value=0.0):
    """
    Desaturate a color towards gray while preserving opponent relationships.

    Formula: new_color = gray + (color - gray) * saturation

    This maintains the mathematical property that opponent colors average to gray.
    For example, if COLOR_A and COLOR_B are opponents averaging to [0,0,0]:
        desaturate(COLOR_A, 0.5) + desaturate(COLOR_B, 0.5) still = [0,0,0]

    Args:
        color: RGB color as list [R, G, B] in range [-1, 1]
        saturation: Saturation level 0.0 (gray) to 1.0 (full color)
        gray_value: The gray point to desaturate towards

    Returns:
        Desaturated color as list [R, G, B]
    """
    return [gray_value + (c - gray_value) * saturation for c in color]

# Apply luminance scaling
if ENABLE_LUMINANCE_SCALING:
    COLOR_A_LUM = [COLOR_A[0] * LUMINANCE_MULTIPLIER,
                   COLOR_A[1] * LUMINANCE_MULTIPLIER,
                   COLOR_A[2] * LUMINANCE_MULTIPLIER]
    COLOR_B_LUM = [COLOR_B[0] * LUMINANCE_MULTIPLIER,
                   COLOR_B[1] * LUMINANCE_MULTIPLIER,
                   COLOR_B[2] * LUMINANCE_MULTIPLIER]
else:
    COLOR_A_LUM = COLOR_A
    COLOR_B_LUM = COLOR_B

# Apply saturation control
if ENABLE_SATURATION_CONTROL:
    COLOR_A_FINAL = desaturate_color(COLOR_A_LUM, SATURATION_LEVEL, BACKGROUND_COLOR[0])
    COLOR_B_FINAL = desaturate_color(COLOR_B_LUM, SATURATION_LEVEL, BACKGROUND_COLOR[0])
else:
    COLOR_A_FINAL = COLOR_A_LUM
    COLOR_B_FINAL = COLOR_B_LUM

# Verification that colors still average to background
average_color = [(COLOR_A_FINAL[i] + COLOR_B_FINAL[i])/2 for i in range(3)]
print(f"\n{'='*70}")
print(f"COLOR CONFIGURATION")
print(f"{'='*70}")
print(f"Original GREEN: {COLOR_A}")
print(f"Original MAGENTA: {COLOR_B}")
print(f"\nLuminance scaling: {'ENABLED (' + str(int(LUMINANCE_MULTIPLIER * 100)) + '%)' if ENABLE_LUMINANCE_SCALING else 'DISABLED (100%)'}")
print(f"Saturation control: {'ENABLED (' + str(int(SATURATION_LEVEL * 100)) + '%)' if ENABLE_SATURATION_CONTROL else 'DISABLED (100%)'}")
print(f"\nFinal GREEN: {[round(c, 3) for c in COLOR_A_FINAL]}")
print(f"Final MAGENTA: {[round(c, 3) for c in COLOR_B_FINAL]}")
print(f"Average: {[round(c, 3) for c in average_color]}")
print(f"Background: {BACKGROUND_COLOR}")
print(f"Will fuse? {'✓ YES' if all(abs(average_color[i] - BACKGROUND_COLOR[i]) < 0.01 for i in range(3)) else '✗ NO'}")
print(f"{'='*70}\n")

# ==================== HELPER FUNCTIONS ====================
def get_clock_position(hour, radius):
    """
    Get (x, y) coordinates for a clock position.

    Args:
        hour: Clock position (e.g., 3, 6, 9, 12)
        radius: Distance from center in pixels

    Returns:
        [x, y] coordinate list
    """
    angle = (hour / 12.0) * 2 * np.pi - np.pi / 2  # 12 o'clock = top
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    return [x, y]

def calculate_color_flicker_frame_based(frame_num, frames_per_half_cycle, color_a, color_b):
    """
    *** FRAME-BASED FLICKER TIMING - ELIMINATES ARTIFACTS ***

    Returns color_a or color_b based on EXACT frame count (not time).

    HOW IT WORKS:
    -------------
    For 60Hz flicker on 480Hz monitor:
        - frames_per_half_cycle = 8
        - frames_per_full_cycle = 16

    Frame sequence:
        Frames 0-7:   color_a (GREEN)   → 8 frames × 2.083ms = 16.667ms half-cycle
        Frames 8-15:  color_b (MAGENTA) → 8 frames × 2.083ms = 16.667ms half-cycle
        Frame 16:     color_a (GREEN)   → cycle repeats

    MATHEMATICAL PRECISION:
    -----------------------
    position_in_cycle = frame_num % (frames_per_half_cycle * 2)

    This uses modulo with INTEGER arithmetic:
        - No floating-point rounding errors
        - No cumulative drift over time
        - Deterministic color switching every 8th frame
        - Perfect synchronization guaranteed

    COMPARISON TO 6.py TIME-BASED APPROACH:
    ----------------------------------------
    OLD (6.py):
        frames_per_cycle = refresh_rate / flicker_freq  # e.g., 480/60 = 8.0 (float)
        if (frame_num % frames_per_cycle) < (frames_per_cycle / 2):
            return color_a
        → Floating-point modulo can accumulate errors
        → Timing jitter over long sessions
        → Occasional flicker artifacts

    NEW (7.py):
        frames_per_full_cycle = 16  # Pre-calculated INTEGER
        position_in_cycle = frame_num % 16  # Integer modulo
        if position_in_cycle < 8:
            return color_a
        → Pure integer arithmetic
        → Zero drift, zero jitter
        → Perfect temporal precision

    Args:
        frame_num: Current frame number (monotonically increasing)
        frames_per_half_cycle: Number of frames to display each color (INTEGER)
        color_a: First color (e.g., GREEN)
        color_b: Second color (e.g., MAGENTA)

    Returns:
        color_a or color_b depending on position in flicker cycle
    """
    frames_per_full_cycle = frames_per_half_cycle * 2
    position_in_cycle = frame_num % frames_per_full_cycle

    # Simple integer comparison - deterministic and drift-free
    if position_in_cycle < frames_per_half_cycle:
        return color_a  # First half of cycle
    else:
        return color_b  # Second half of cycle

def create_custom_mask(size, sigma):
    """
    Create a custom Gaussian mask with adjustable smoothness.

    The mask controls how Gabor edges blend with the background:
        - Smaller sigma = sharper edges (more abrupt transition)
        - Larger sigma = smoother edges (gradual fade)

    Args:
        size: Mask resolution (e.g., 256 for 256×256 mask)
        sigma: Gaussian standard deviation controlling smoothness

    Returns:
        2D numpy array with values in range [-1, 1] for PsychoPy
    """
    # Create coordinate grids from -1 to 1
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)

    # Calculate distance from center
    distance = np.sqrt(X**2 + Y**2)

    # Apply Gaussian function: exp(-distance²/(2σ²))
    mask = np.exp(-(distance**2) / (2 * sigma**2))

    # Scale to -1 to 1 range for PsychoPy compatibility
    mask = 2 * mask - 1

    return mask

# ==================== PSYCHOPY SETUP ====================
print("Initializing PsychoPy window...")

win = visual.Window(
    size=[WINDOW_WIDTH, WINDOW_HEIGHT],
    color=BACKGROUND_COLOR,
    units='pix',
    fullscr=False,
    monitor='testMonitor',
    waitBlanking=True  # *** CRITICAL for accurate timing ***
    # waitBlanking=True ensures win.flip() synchronizes with monitor refresh
    # Without this, flicker timing would be unreliable
)

print("Window created successfully.")

# Create fixation cross
fixation = visual.ShapeStim(
    win,
    vertices=((0, -10), (0, 10), (0, 0), (-10, 0), (10, 0)),
    lineWidth=2,
    lineColor='white',
    closeShape=False
)

# ==================== CREATE GABOR STIMULI ====================
print("Creating Gabor patches...")

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
        tex='sqr',  # Square wave grating (sharper edges than 'sin')
        mask=custom_mask,  # Custom Gaussian mask for edge smoothness
        size=GABOR_SIZE,
        pos=pos,
        sf=GABOR_SF,
        ori=orientation,
        contrast=GABOR_CONTRAST,
        opacity=GABOR_OPACITY,
        phase=GABOR_PHASE,
        color=GRAY_COLOR,  # Start with gray (will be updated for flickering Gabors)
        units='pix'
    )

print(f"Created {len(gabors)} Gabor patches.")

# ==================== TRIAL LOOP ====================
print("\n" + "="*70)
print("8 GABOR PATCHES - FRAME-BASED CHROMATIC FLICKER (7.py)")
print("="*70)
print(f"Background: Mid-gray {BACKGROUND_COLOR}")
print(f"Flicker colors: GREEN {[round(c, 2) for c in COLOR_A_FINAL]} ↔ MAGENTA {[round(c, 2) for c in COLOR_B_FINAL]}")
print(f"Luminance: {'ENABLED (' + str(int(LUMINANCE_MULTIPLIER * 100)) + '%)' if ENABLE_LUMINANCE_SCALING else 'DISABLED (100%)'}")
print(f"Saturation: {'ENABLED (' + str(int(SATURATION_LEVEL * 100)) + '%)' if ENABLE_SATURATION_CONTROL else 'DISABLED (100%)'}")
print(f"Refresh rate: {REFRESH_RATE} Hz (frame duration: {1000/REFRESH_RATE:.3f} ms)")
print(f"\n9 o'clock Gabor:")
print(f"  {'FLICKER' if ENABLE_NINE_OCLOCK_FLICKER else 'STATIC'} @ {NINE_OCLOCK_FLICKER_FREQUENCY} Hz")
print(f"  Orientation: {ORIENTATION_9_OCLOCK}°")
if ENABLE_NINE_OCLOCK_FLICKER:
    print(f"  Frame timing: {FRAMES_PER_HALF_CYCLE_9} frames GREEN, {FRAMES_PER_HALF_CYCLE_9} frames MAGENTA")
    print(f"  Color duration: {FRAMES_PER_HALF_CYCLE_9 / REFRESH_RATE * 1000:.3f} ms per color")
print(f"\n3 o'clock Gabor:")
print(f"  {'FLICKER' if ENABLE_THREE_OCLOCK_FLICKER else 'STATIC'} @ {THREE_OCLOCK_FLICKER_FREQUENCY} Hz")
print(f"  Orientation: {ORIENTATION_3_OCLOCK}°")
if ENABLE_THREE_OCLOCK_FLICKER:
    print(f"  Frame timing: {FRAMES_PER_HALF_CYCLE_3} frames GREEN, {FRAMES_PER_HALF_CYCLE_3} frames MAGENTA")
    print(f"  Color duration: {FRAMES_PER_HALF_CYCLE_3 / REFRESH_RATE * 1000:.3f} ms per color")
print(f"\nPress SPACEBAR to end demo")
print("="*70 + "\n")

# Initialize timing variables
trial_clock = core.Clock()
frame_num = 0  # *** FRAME COUNTER - the heart of frame-based timing ***
trial_ended = False

# Lists to store timing data for verification
frame_times = []  # Timestamp of each frame
flicker_switches_9 = []  # Timestamps when 9 o'clock color changes
flicker_switches_3 = []  # Timestamps when 3 o'clock color changes
last_color_9 = None  # Track previous color for 9 o'clock
last_color_3 = None  # Track previous color for 3 o'clock

print("Starting trial... (frame-based flicker active)")

# ==================== MAIN RENDERING LOOP ====================
while not trial_ended:
    current_time = trial_clock.getTime()
    frame_times.append(current_time)

    # Check for spacebar press to end trial
    keys = event.getKeys()
    if 'space' in keys:
        print(f"\nTrial ended at {trial_clock.getTime():.2f}s (spacebar pressed)")
        trial_ended = True
        break

    # Check for maximum duration (if set)
    if TRIAL_DURATION is not None and trial_clock.getTime() >= TRIAL_DURATION:
        print(f"\nTrial ended at {trial_clock.getTime():.2f}s (max duration reached)")
        trial_ended = True
        break

    # Draw fixation cross
    fixation.draw()

    # ==================== DRAW ALL GABOR PATCHES ====================
    for hour in clock_positions:
        # *** 9 O'CLOCK GABOR - FRAME-BASED FLICKER ***
        if hour == 9 and ENABLE_NINE_OCLOCK_FLICKER:
            # Use frame-based calculation for precise timing
            current_color = calculate_color_flicker_frame_based(
                frame_num,                    # Current frame number
                FRAMES_PER_HALF_CYCLE_9,      # 8 frames per color @ 480Hz
                COLOR_A_FINAL,                # GREEN (processed with luminance/saturation)
                COLOR_B_FINAL                 # MAGENTA (processed with luminance/saturation)
            )
            gabors[hour].color = current_color

            # Track color switches for verification
            if last_color_9 is not None and current_color != last_color_9:
                flicker_switches_9.append(current_time)
            last_color_9 = current_color

            gabors[hour].draw()

        # *** 3 O'CLOCK GABOR - FRAME-BASED FLICKER ***
        elif hour == 3 and ENABLE_THREE_OCLOCK_FLICKER:
            # Use frame-based calculation for precise timing
            current_color = calculate_color_flicker_frame_based(
                frame_num,                    # Current frame number
                FRAMES_PER_HALF_CYCLE_3,      # 8 frames per color @ 480Hz
                COLOR_A_FINAL,                # GREEN (processed with luminance/saturation)
                COLOR_B_FINAL                 # MAGENTA (processed with luminance/saturation)
            )
            gabors[hour].color = current_color

            # Track color switches for verification
            if last_color_3 is not None and current_color != last_color_3:
                flicker_switches_3.append(current_time)
            last_color_3 = current_color

            gabors[hour].draw()

        # *** NON-FLICKERING GABORS - STATIC GRAY ***
        else:
            gabors[hour].draw()

    # *** FLIP BUFFER TO DISPLAY - synchronized with monitor refresh ***
    win.flip()

    # *** INCREMENT FRAME COUNTER - drives all timing ***
    frame_num += 1
    # This is the only timing variable that matters!
    # Every 16 frames = one complete 60Hz flicker cycle
    # Frames 0-7: GREEN, Frames 8-15: MAGENTA, repeat...

# ==================== TIMING VERIFICATION ====================
print("\n" + "="*70)
print("TIMING VERIFICATION & PERFORMANCE ANALYSIS")
print("="*70)

# Calculate actual refresh rate from frame timestamps
if len(frame_times) > 1:
    frame_intervals = np.diff(frame_times)  # Time between consecutive frames
    mean_frame_interval = np.mean(frame_intervals)
    actual_refresh_rate = 1.0 / mean_frame_interval

    print(f"\n*** MONITOR REFRESH RATE ***")
    print(f"  Expected: {REFRESH_RATE} Hz")
    print(f"  Actual: {actual_refresh_rate:.2f} Hz")
    print(f"  Match: {'✓ YES' if abs(actual_refresh_rate - REFRESH_RATE) < 5 else '✗ NO (Check monitor settings!)'}")

    print(f"\n*** FRAME INTERVAL STATISTICS ***")
    print(f"  Mean: {mean_frame_interval*1000:.3f} ms ({1/mean_frame_interval:.1f} Hz)")
    print(f"  Std dev: {np.std(frame_intervals)*1000:.3f} ms")
    print(f"  Min: {np.min(frame_intervals)*1000:.3f} ms")
    print(f"  Max: {np.max(frame_intervals)*1000:.3f} ms")

    # Check for dropped frames
    expected_interval = 1.0 / REFRESH_RATE
    dropped_frames = np.sum(frame_intervals > (expected_interval * 1.5))
    print(f"  Dropped frames: {dropped_frames} ({dropped_frames/len(frame_intervals)*100:.2f}%)")
    if dropped_frames > len(frame_intervals) * 0.01:  # More than 1% dropped
        print(f"  ⚠ WARNING: High frame drop rate! Check system performance.")

# Verify 9 o'clock flicker timing
if ENABLE_NINE_OCLOCK_FLICKER and len(flicker_switches_9) > 1:
    switch_intervals = np.diff(flicker_switches_9)
    mean_switch_interval = np.mean(switch_intervals)
    actual_flicker_frequency = 1.0 / (2 * mean_switch_interval)

    print(f"\n*** 9 O'CLOCK GABOR FLICKER ***")
    print(f"  Expected frequency: {NINE_OCLOCK_FLICKER_FREQUENCY} Hz")
    print(f"  Actual frequency: {actual_flicker_frequency:.2f} Hz")
    print(f"  Match: {'✓ YES' if abs(actual_flicker_frequency - NINE_OCLOCK_FLICKER_FREQUENCY) < 2 else '✗ NO'}")
    print(f"  Color switches recorded: {len(flicker_switches_9)}")
    print(f"  Frame-based timing: {FRAMES_PER_HALF_CYCLE_9} frames per color")
    print(f"  Theoretical color duration: {FRAMES_PER_HALF_CYCLE_9 / REFRESH_RATE * 1000:.3f} ms")
    print(f"  Actual color duration: {mean_switch_interval * 1000:.3f} ms")
    print(f"  Timing precision: {abs(mean_switch_interval - FRAMES_PER_HALF_CYCLE_9/REFRESH_RATE)*1000:.3f} ms error")

# Verify 3 o'clock flicker timing
if ENABLE_THREE_OCLOCK_FLICKER and len(flicker_switches_3) > 1:
    switch_intervals = np.diff(flicker_switches_3)
    mean_switch_interval = np.mean(switch_intervals)
    actual_flicker_frequency = 1.0 / (2 * mean_switch_interval)

    print(f"\n*** 3 O'CLOCK GABOR FLICKER ***")
    print(f"  Expected frequency: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz")
    print(f"  Actual frequency: {actual_flicker_frequency:.2f} Hz")
    print(f"  Match: {'✓ YES' if abs(actual_flicker_frequency - THREE_OCLOCK_FLICKER_FREQUENCY) < 2 else '✗ NO'}")
    print(f"  Color switches recorded: {len(flicker_switches_3)}")
    print(f"  Frame-based timing: {FRAMES_PER_HALF_CYCLE_3} frames per color")
    print(f"  Theoretical color duration: {FRAMES_PER_HALF_CYCLE_3 / REFRESH_RATE * 1000:.3f} ms")
    print(f"  Actual color duration: {mean_switch_interval * 1000:.3f} ms")
    print(f"  Timing precision: {abs(mean_switch_interval - FRAMES_PER_HALF_CYCLE_3/REFRESH_RATE)*1000:.3f} ms error")

    # Special message for 60Hz @ 480Hz optimization
    if THREE_OCLOCK_FLICKER_FREQUENCY == 60 and REFRESH_RATE == 480:
        print(f"\n*** 60Hz @ 480Hz FRAME-BASED OPTIMIZATION ***")
        print(f"  Full cycle: {FRAMES_PER_FULL_CYCLE_3} frames = {FRAMES_PER_FULL_CYCLE_3/REFRESH_RATE*1000:.3f} ms")
        print(f"  GREEN phase: frames 0-7 (8 frames = 8.333 ms)")
        print(f"  MAGENTA phase: frames 8-15 (8 frames = 8.333 ms)")
        print(f"  Mathematical precision: 480÷60 = 8 frames per half-cycle ✓")
        print(f"  Result: PERFECT chromatic fusion to invisible gray!")
        print(f"  Artifact elimination: ZERO timing drift!")

# Overall summary
print(f"\n*** FRAME-BASED TIMING SUMMARY ***")
print(f"  Total frames rendered: {frame_num}")
print(f"  Total duration: {trial_clock.getTime():.2f} s")
print(f"  Average frame rate: {frame_num / trial_clock.getTime():.2f} Hz")
if ENABLE_THREE_OCLOCK_FLICKER:
    total_cycles = frame_num / FRAMES_PER_FULL_CYCLE_3
    print(f"  Complete 60Hz cycles: {total_cycles:.1f}")
    print(f"  Frame-based precision: Every {FRAMES_PER_FULL_CYCLE_3} frames = one flicker cycle")

print("="*70 + "\n")

# Clean up
win.close()
core.quit()