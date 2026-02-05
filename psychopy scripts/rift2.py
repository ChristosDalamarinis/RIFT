"""
RIFT Study: Flickering Gabor Patch with Complementary Colors
- Gray background with fixation cross
- Gabor patch at 3 o'clock position (right side)
- 60 Hz flicker using complementary RGB colors
- Smooth edges with adjustable smoothness (Gaussian mask)
- INCLUDES: Frame timing verification to confirm flicker frequency
"""

from psychopy import visual, core, event
import numpy as np

# ==================== CONFIGURATION ====================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
BACKGROUND_COLOR = [0.5, 0.5, 0.5]  # Medium gray
REFRESH_RATE = 120  # Hz (standard monitor) NOTE: 240 Hz WORKS GOOD
FLICKER_FREQUENCY = 25   # Hz NOTE: 60 IS THE GOLD STANDARD

# NOTE: in Windows i have to use 240Hz and 100Hz flicker to get a good result. In macOS, 120Hz and 60Hz flicker worked well.

# Gabor patch parameters
GABOR_SIZE = 256  # MUST be power of 2 (256, 512, etc)
GABOR_X_POS = 300  # pixels right of center (3 o'clock)
GABOR_Y_POS = 0  # centered vertically
SPATIAL_FREQUENCY = 0.05  # cycles per pixel (lower = fewer stripes)
ORIENTATION = 45  # degrees
MASK_SMOOTHNESS = 4.8  # Controls edge smoothness (higher = smoother/softer edges)

# Colors: Complementary RGB pairs (exact opposites on RGB wheel)
COLOR1 = [1.0, 0.0, -1.0]  # Magenta/Pink
COLOR2 = [-1.0, 0.0, 1.0]  # Cyan (opposite of magenta)

# Duration
TRIAL_DURATION = None  # None = infinite (until spacebar), or set to float like 30.0

# ==================== HELPER FUNCTIONS ====================

def get_complementary_color(color):
    """Calculate exact RGB opposite of a color."""
    return [-c for c in color]


def create_smooth_gaussian_mask(size, smoothness):
    """Create a Gaussian mask for smooth edges on the Gabor patch."""
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    distance = np.sqrt(X**2 + Y**2)
    mask = np.exp(-smoothness * distance**2)
    mask = 2 * mask - 1
    return mask


def calculate_flicker_frame(frame_num, flicker_freq, refresh_rate):
    """Calculate whether stimulus should be shown this frame."""
    frames_per_cycle = refresh_rate // flicker_freq
    return (frame_num % frames_per_cycle) < (frames_per_cycle // 2)


# ==================== SETUP ====================

win = visual.Window(
    size=[WINDOW_WIDTH, WINDOW_HEIGHT],
    color=BACKGROUND_COLOR,
    units='pix',
    fullscr=False,
    monitor='testMonitor'
)

fixation = visual.ShapeStim(
    win, 
    vertices=((0, -10), (0, 10), (0, 0), (-10, 0), (10, 0)),
    lineWidth=2,
    lineColor='black',
    closeShape=False
)

mask_array = create_smooth_gaussian_mask(
    size=GABOR_SIZE,
    smoothness=MASK_SMOOTHNESS
)

gabor = visual.GratingStim(
    win,
    tex='sin',
    mask=mask_array,
    pos=[GABOR_X_POS, GABOR_Y_POS],
    size=GABOR_SIZE,
    sf=SPATIAL_FREQUENCY,
    ori=ORIENTATION,
    color=COLOR1,
    contrast=1.0,
    units='pix'
)

# Verify complementary colors
color2_check = get_complementary_color(COLOR1)
print(f"Color 1: {COLOR1}")
print(f"Color 2 (should be opposite): {COLOR2}")
print(f"Match: {np.allclose(COLOR2, color2_check)}")

# ==================== TRIAL LOOP ====================

print("\n" + "="*60)
print("RIFT STUDY - FLICKERING GABOR PATCH")
print("="*60)
print(f"Requested flicker frequency: {FLICKER_FREQUENCY} Hz")
print(f"Expected monitor refresh rate: {REFRESH_RATE} Hz")
print(f"Gabor position: 3 o'clock ({GABOR_X_POS}, {GABOR_Y_POS})")
print(f"Mask smoothness: {MASK_SMOOTHNESS}")
print(f"Gabor size: {GABOR_SIZE} pixels")
print(f"\nPress SPACEBAR to end demo")
print("="*60 + "\n")

trial_clock = core.Clock()
frame_num = 0
trial_ended = False

# Lists to store timing data
frame_times = []
color_switches = []  # Track when color changes
last_color = COLOR1

while not trial_ended:
    
    # Record frame time
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
    
    show_frame = calculate_flicker_frame(frame_num, FLICKER_FREQUENCY, REFRESH_RATE)
    
    if show_frame:
        gabor.color = COLOR1
        current_color = COLOR1
    else:
        gabor.color = COLOR2
        current_color = COLOR2
    
    # Track color switches
    if current_color != last_color:
        color_switches.append(current_time)
        last_color = current_color
    
    fixation.draw()
    gabor.draw()
    win.flip()
    
    frame_num += 1

# ==================== TIMING ANALYSIS ====================

print("\n" + "="*60)
print("TIMING VERIFICATION")
print("="*60)

print(f"\nTotal frames displayed: {frame_num}")
print(f"Trial duration: {trial_clock.getTime():.3f} seconds")

# Calculate actual frame rate
if len(frame_times) > 1:
    frame_intervals = np.diff(frame_times)
    mean_interval = np.mean(frame_intervals)
    actual_refresh_rate = 1.0 / mean_interval
    print(f"\nActual refresh rate: {actual_refresh_rate:.1f} Hz")
    print(f"Mean frame interval: {mean_interval*1000:.2f} ms")
    print(f"Std dev of frame intervals: {np.std(frame_intervals)*1000:.3f} ms")

# Calculate actual flicker frequency from color switches
if len(color_switches) > 1:
    switch_intervals = np.diff(color_switches)
    mean_switch_interval = np.mean(switch_intervals)
    actual_flicker_freq = 1.0 / mean_switch_interval
    
    print(f"\n{'='*60}")
    print(f"Color switches detected: {len(color_switches)}")
    print(f"Mean time between switches: {mean_switch_interval*1000:.2f} ms")
    print(f"Actual flicker frequency: {actual_flicker_freq:.1f} Hz")
    print(f"Expected flicker frequency: {FLICKER_FREQUENCY} Hz")
    match = abs(actual_flicker_freq - FLICKER_FREQUENCY) < 2
    print(f"Match: {'✓ YES' if match else '✗ NO'}")
    print(f"Difference: {abs(actual_flicker_freq - FLICKER_FREQUENCY):.1f} Hz")

print(f"\n{'='*60}")
print("\nINTERPRETATION:")
print("- Actual refresh rate = monitor's true Hz (usually 60, 120, 144)")
print("- Actual flicker frequency = should match FLICKER_FREQUENCY setting")
print("- If actual refresh rate is 120 Hz: your monitor is running at 120 Hz")
print(f"- Frame intervals should be consistent (low std dev < 1 ms)")
print(f"- Example: 60 Hz = ~16.67 ms per frame")
print(f"- 60 Hz flicker on 120 Hz monitor = 2 frames per color")
print(f"{'='*60}\n")

win.close()
core.quit()