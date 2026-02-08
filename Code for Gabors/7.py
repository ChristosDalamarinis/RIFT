"""
8 Gabor Patches Visual Task - Frame-Based Precise Flicker (7.py)

================================================================================
            MULTI-REFRESH-RATE SUPPORT - AUTOMATIC VALIDATION
================================================================================

SUPPORTED REFRESH RATES:
------------------------
✓ 480 Hz 
✓ 360 Hz 
✓ 240 Hz 
✓ 120 Hz 
✓ 60 Hz 

AUTOMATIC VALIDATION:
---------------------
The script automatically checks if your flicker frequency is compatible with
your monitor's refresh rate. It ensures that:
    (refresh_rate / flicker_frequency) is evenly divisible

This guarantees INTEGER frame counts with ZERO timing artifacts.

VALID COMBINATIONS:
-------------------
60Hz monitor  → Max 30Hz flicker  (2 frames/cycle minimum)
120Hz monitor → Max 60Hz flicker  (2 frames/cycle minimum)
240Hz monitor → Max 120Hz flicker (2 frames/cycle minimum)
360Hz monitor → Max 180Hz flicker (2 frames/cycle minimum)
480Hz monitor → Max 240Hz flicker (2 frames/cycle minimum)

COMMON VALID FLICKER FREQUENCIES:
----------------------------------
- 60 Hz: Works on 120Hz, 240Hz, 360Hz, 480Hz 
- 30 Hz: Works on ALL refresh rates
- 20 Hz: Works on 60Hz, 120Hz, 240Hz, 360Hz, 480Hz
- 15 Hz: Works on 60Hz, 120Hz, 240Hz, 360Hz, 480Hz
- 10 Hz: Works on ALL refresh rates

================================================================================
"""
# NOTE: the functionalities of 6.py are in line 228 onwards 
# NOTE: incorporatig RGB colours is a bad idea in psychopy as it requires a convertion
# NOTE: focus on this script

from psychopy import visual, core, event
import numpy as np

# ========================= CONFIGURATION ========================
WINDOW_WIDTH = 1200  # 1920
WINDOW_HEIGHT = 900  # 1080

# Background color - Mid-gray for chromatic fusion
BACKGROUND_COLOR = [0.0, 0.0, 0.0]  # Mid-gray

# *** MONITOR REFRESH RATE - MUST MATCH YOUR ACTUAL MONITOR ***
REFRESH_RATE = 60  # Hz - Options: 480, 360, 240, 120, 60
# CRITICAL: Set this to your actual monitor refresh rate!
# To check your monitor: Windows Settings → Display → Advanced Display → Refresh Rate

# ================== FLICKER CONFIGURATION ========================
# Flicker settings for 9 o'clock Gabor
NINE_OCLOCK_FLICKER_FREQUENCY = 60  # Hz 
ENABLE_NINE_OCLOCK_FLICKER = False  # Set to False to disable flicker

# Flicker settings for 3 o'clock Gabor
THREE_OCLOCK_FLICKER_FREQUENCY = 30  # Hz
ENABLE_THREE_OCLOCK_FLICKER = True  # Set to False to disable flicker

# ==================== VALIDATION FUNCTIONS ====================
def validate_refresh_rate(refresh_rate):
    """
    Validate that the refresh rate is one of the supported values.

    Args:
        refresh_rate: Monitor refresh rate in Hz

    Returns:
        bool: True if valid, False otherwise
    """
    supported_rates = [60, 120, 240, 360, 480]
    return refresh_rate in supported_rates

def validate_flicker_frequency(refresh_rate, flicker_frequency):
    """
    Validate that flicker frequency produces INTEGER frame counts.

    For frame-based timing to work perfectly:
    1. flicker_frequency must be ≤ refresh_rate / 2
    2. (refresh_rate / flicker_frequency) must divide evenly

    Args:
        refresh_rate: Monitor refresh rate in Hz
        flicker_frequency: Desired flicker frequency in Hz

    Returns:
        tuple: (is_valid, frames_per_half_cycle, error_message)
    """
    # Check if flicker frequency is too high
    max_flicker = refresh_rate / 2
    if flicker_frequency > max_flicker:
        error_msg = (
            f"Flicker frequency {flicker_frequency} Hz is TOO HIGH for {refresh_rate} Hz monitor.\n"
            f"Maximum flicker frequency: {max_flicker} Hz (half the refresh rate).\n"
            f"Reason: Need at least 2 frames to show both colors."
        )
        return False, 0, error_msg

    # Calculate frames per cycle
    frames_per_cycle = refresh_rate / flicker_frequency
    frames_per_half_cycle = frames_per_cycle / 2

    # Check if frames_per_half_cycle is an integer (or very close due to float precision)
    frames_per_half_cycle_int = int(round(frames_per_half_cycle))

    # Allow tiny floating point errors (< 0.001)
    if abs(frames_per_half_cycle - frames_per_half_cycle_int) > 0.001:
        error_msg = (
            f"Flicker frequency {flicker_frequency} Hz is INCOMPATIBLE with {refresh_rate} Hz monitor.\n"
            f"Frames per half-cycle: {frames_per_half_cycle:.3f} (not an integer!)\n"
            f"Frame-based timing requires INTEGER frame counts.\n\n"
            f"Valid flicker frequencies for {refresh_rate} Hz monitor:\n"
            f"{get_valid_flicker_frequencies(refresh_rate)}"
        )
        return False, 0, error_msg

    return True, frames_per_half_cycle_int, ""

def get_valid_flicker_frequencies(refresh_rate):
    """
    Generate a list of valid flicker frequencies for a given refresh rate.

    A flicker frequency is valid if:
    - It produces an integer number of frames per half-cycle
    - It's ≤ refresh_rate / 2

    Args:
        refresh_rate: Monitor refresh rate in Hz

    Returns:
        str: Formatted string of valid frequencies
    """
    valid_freqs = []
    max_flicker = refresh_rate / 2

    # Check common frequencies
    test_frequencies = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 48, 60, 80, 90, 120, 180, 240]

    for freq in test_frequencies:
        if freq > max_flicker:
            break
        frames_per_half_cycle = (refresh_rate / freq) / 2
        if abs(frames_per_half_cycle - round(frames_per_half_cycle)) < 0.001:
            frames = int(round(frames_per_half_cycle))
            valid_freqs.append(f"  {freq} Hz ({frames} frames/color)")

    if valid_freqs:
        return "\n".join(valid_freqs)
    else:
        return "  No common frequencies found (this shouldn't happen!)"

# ==================== PERFORM VALIDATION ====================
print(f"\n{'='*70}")
print(f"REFRESH RATE & FLICKER FREQUENCY VALIDATION")
print(f"{'='*70}")

# Validate refresh rate
if not validate_refresh_rate(REFRESH_RATE):
    print(f"\n❌ ERROR: Unsupported refresh rate: {REFRESH_RATE} Hz")
    print(f"\nSupported refresh rates: 60, 120, 240, 360, 480 Hz")
    print(f"\nPlease set REFRESH_RATE to one of the supported values.")
    print(f"{'='*70}\n")
    raise ValueError(f"Unsupported refresh rate: {REFRESH_RATE} Hz")

print(f"✓ Refresh rate: {REFRESH_RATE} Hz (supported)")
print(f"  Frame duration: {1000/REFRESH_RATE:.3f} ms")
print(f"  Maximum flicker frequency: {REFRESH_RATE/2} Hz")

# Validate 9 o'clock flicker frequency
if ENABLE_NINE_OCLOCK_FLICKER:
    is_valid_9, frames_9, error_9 = validate_flicker_frequency(REFRESH_RATE, NINE_OCLOCK_FLICKER_FREQUENCY)

    if not is_valid_9:
        print(f"\n❌ ERROR: 9 o'clock Gabor configuration invalid!")
        print(f"{'='*70}")
        print(error_9)
        print(f"{'='*70}\n")
        raise ValueError(f"Invalid 9 o'clock flicker frequency: {NINE_OCLOCK_FLICKER_FREQUENCY} Hz")

    FRAMES_PER_HALF_CYCLE_9 = frames_9
    FRAMES_PER_FULL_CYCLE_9 = frames_9 * 2
    print(f"\n✓ 9 o'clock Gabor: {NINE_OCLOCK_FLICKER_FREQUENCY} Hz (valid)")
    print(f"  Frames per half-cycle: {FRAMES_PER_HALF_CYCLE_9}")
    print(f"  Frames per full cycle: {FRAMES_PER_FULL_CYCLE_9}")
    print(f"  Color duration: {FRAMES_PER_HALF_CYCLE_9 / REFRESH_RATE * 1000:.3f} ms")
else:
    FRAMES_PER_HALF_CYCLE_9 = 0
    FRAMES_PER_FULL_CYCLE_9 = 0
    print(f"\n○ 9 o'clock Gabor: DISABLED (static)")

# Validate 3 o'clock flicker frequency
if ENABLE_THREE_OCLOCK_FLICKER:
    is_valid_3, frames_3, error_3 = validate_flicker_frequency(REFRESH_RATE, THREE_OCLOCK_FLICKER_FREQUENCY)

    if not is_valid_3:
        print(f"\n❌ ERROR: 3 o'clock Gabor configuration invalid!")
        print(f"{'='*70}")
        print(error_3)
        print(f"{'='*70}\n")
        raise ValueError(f"Invalid 3 o'clock flicker frequency: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz")

    FRAMES_PER_HALF_CYCLE_3 = frames_3
    FRAMES_PER_FULL_CYCLE_3 = frames_3 * 2
    print(f"\n✓ 3 o'clock Gabor: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz (valid)")
    print(f"  Frames per half-cycle: {FRAMES_PER_HALF_CYCLE_3}")
    print(f"  Frames per full cycle: {FRAMES_PER_FULL_CYCLE_3}")
    print(f"  Color duration: {FRAMES_PER_HALF_CYCLE_3 / REFRESH_RATE * 1000:.3f} ms")
else:
    FRAMES_PER_HALF_CYCLE_3 = 0
    FRAMES_PER_FULL_CYCLE_3 = 0
    print(f"\n○ 3 o'clock Gabor: DISABLED (static)")

print(f"\n✓ All configurations valid! Frame-based timing will be perfect.")
print(f"{'='*70}\n")

# ================== GABOR PARAMETERS ========================
GABOR_SIZE = 2000  # Size in pixels
CIRCLE_RADIUS = 300  # Distance from center
GABOR_SF = 0.05  # Spatial frequency
GABOR_CONTRAST = 1.0  # Contrast (0-1)
GABOR_OPACITY = 1.0  # Opacity (0-1)
GABOR_PHASE = 0.5  # Phase offset

# ================== SMOOTHNESS CONTROL ========================
GABOR_SMOOTHNESS_DEFAULT = 0.05
GABOR_SMOOTHNESS_9_OCLOCK = 0.05
GABOR_SMOOTHNESS_3_OCLOCK = 0.05

# ================== ORIENTATION/TILT CONTROL ========================
ORIENTATION_DEFAULT = 0
ORIENTATION_9_OCLOCK = -20
ORIENTATION_3_OCLOCK = -20

# ================== COLOR CONFIGURATION ========================
GRAY_COLOR = [0.5, 0.5, 0.5]  # Light gray

# ===== GREEN vs MAGENTA (opponent colors) =====
COLOR_A = [-1.0, 1.0, -1.0]  # Bright green
COLOR_B = [1.0, -1.0, 1.0]  # Bright magenta

# ================== LUMINANCE CONTROL ========================
ENABLE_LUMINANCE_SCALING = True
LUMINANCE_MULTIPLIER = 1.0  # Range: 0.0 to 1.0

# ================== SATURATION CONTROL ========================
ENABLE_SATURATION_CONTROL = True
SATURATION_LEVEL = 1.0  # Range: 0.0 to 1.0

# Duration
TRIAL_DURATION = None  # None = infinite (until spacebar)

# ==================== COLOR PROCESSING ====================
def desaturate_color(color, saturation, gray_value=0.0):
    """Desaturate a color towards gray while preserving opponent relationships."""
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
    """Get (x, y) coordinates for a clock position."""
    angle = (hour / 12.0) * 2 * np.pi - np.pi / 2
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    return [x, y]

def calculate_color_flicker_frame_based(frame_num, frames_per_half_cycle, color_a, color_b):
    """
    FRAME-BASED flicker timing - eliminates artifacts!

    Returns color_a or color_b based on exact frame count.
    Uses pure integer arithmetic for perfect temporal precision.
    """
    frames_per_full_cycle = frames_per_half_cycle * 2
    position_in_cycle = frame_num % frames_per_full_cycle

    if position_in_cycle < frames_per_half_cycle:
        return color_a
    else:
        return color_b

def create_custom_mask(size, sigma):
    """Create a custom Gaussian mask with adjustable smoothness."""
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    distance = np.sqrt(X**2 + Y**2)
    mask = np.exp(-(distance**2) / (2 * sigma**2))
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
    waitBlanking=True  # CRITICAL for accurate timing
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
clock_positions = [12, 1.5, 3, 4.5, 6, 7.5, 9, 10.5]

for hour in clock_positions:
    pos = get_clock_position(hour, CIRCLE_RADIUS)

    if hour == 9:
        smoothness = GABOR_SMOOTHNESS_9_OCLOCK
        orientation = ORIENTATION_9_OCLOCK
    elif hour == 3:
        smoothness = GABOR_SMOOTHNESS_3_OCLOCK
        orientation = ORIENTATION_3_OCLOCK
    else:
        smoothness = GABOR_SMOOTHNESS_DEFAULT
        orientation = ORIENTATION_DEFAULT

    custom_mask = create_custom_mask(size=256, sigma=smoothness)

    gabors[hour] = visual.GratingStim(
        win,
        tex='sqr', # Sinusoidal grating = "sin", OR Square for sharper edges. Other options: 'sin', 'sqr', 'cross', 'saw', 'none'
        mask=custom_mask,
        size=GABOR_SIZE,
        pos=pos,
        sf=GABOR_SF,
        ori=orientation,
        contrast=GABOR_CONTRAST,
        opacity=GABOR_OPACITY,
        phase=GABOR_PHASE,
        color=GRAY_COLOR,
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

trial_clock = core.Clock()
frame_num = 0
trial_ended = False

# Lists to store timing data for verification
frame_times = []
flicker_switches_9 = []
flicker_switches_3 = []
last_color_9 = None
last_color_3 = None

print("Starting trial... (frame-based flicker active)")

# ==================== MAIN RENDERING LOOP ====================
while not trial_ended:
    current_time = trial_clock.getTime()
    frame_times.append(current_time)

    keys = event.getKeys()
    if 'space' in keys:
        print(f"\nTrial ended at {trial_clock.getTime():.2f}s (spacebar pressed)")
        trial_ended = True
        break

    if TRIAL_DURATION is not None and trial_clock.getTime() >= TRIAL_DURATION:
        print(f"\nTrial ended at {trial_clock.getTime():.2f}s (max duration reached)")
        trial_ended = True
        break

    fixation.draw()

    for hour in clock_positions:
        if hour == 9 and ENABLE_NINE_OCLOCK_FLICKER:
            current_color = calculate_color_flicker_frame_based(
                frame_num,
                FRAMES_PER_HALF_CYCLE_9,
                COLOR_A_FINAL,
                COLOR_B_FINAL
            )
            gabors[hour].color = current_color

            if last_color_9 is not None and current_color != last_color_9:
                flicker_switches_9.append(current_time)
            last_color_9 = current_color

            gabors[hour].draw()

        elif hour == 3 and ENABLE_THREE_OCLOCK_FLICKER:
            current_color = calculate_color_flicker_frame_based(
                frame_num,
                FRAMES_PER_HALF_CYCLE_3,
                COLOR_A_FINAL,
                COLOR_B_FINAL
            )
            gabors[hour].color = current_color

            if last_color_3 is not None and current_color != last_color_3:
                flicker_switches_3.append(current_time)
            last_color_3 = current_color

            gabors[hour].draw()
        else:
            gabors[hour].draw()

    win.flip()
    frame_num += 1

# ==================== TIMING VERIFICATION ====================
print("\n" + "="*70)
print("TIMING VERIFICATION & PERFORMANCE ANALYSIS")
print("="*70)

if len(frame_times) > 1:
    frame_intervals = np.diff(frame_times)
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

    expected_interval = 1.0 / REFRESH_RATE
    dropped_frames = np.sum(frame_intervals > (expected_interval * 1.5))
    print(f"  Dropped frames: {dropped_frames} ({dropped_frames/len(frame_intervals)*100:.2f}%)")
    if dropped_frames > len(frame_intervals) * 0.01:
        print(f"  ⚠ WARNING: High frame drop rate! Check system performance.")

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

print(f"\n*** FRAME-BASED TIMING SUMMARY ***")
print(f"  Total frames rendered: {frame_num}")
print(f"  Total duration: {trial_clock.getTime():.2f} s")
print(f"  Average frame rate: {frame_num / trial_clock.getTime():.2f} Hz")
if ENABLE_THREE_OCLOCK_FLICKER and FRAMES_PER_FULL_CYCLE_3 > 0:
    total_cycles = frame_num / FRAMES_PER_FULL_CYCLE_3
    print(f"  Complete flicker cycles: {total_cycles:.1f}")
    print(f"  Frame-based precision: Every {FRAMES_PER_FULL_CYCLE_3} frames = one flicker cycle")

print("="*70 + "\n")

win.close()
core.quit()