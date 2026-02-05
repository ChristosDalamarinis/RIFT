"""
RIFT Study: Flickering Gabor Patch with Complementary Colors
- Gray background with fixation cross
- Gabor patch at 3 o'clock position (right side)
- 60 Hz flicker using complementary RGB colors
- Smooth edges with adjustable smoothness (Gaussian mask)
"""

from psychopy import visual, core, event
import numpy as np

# ==================== CONFIGURATION ====================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
BACKGROUND_COLOR = [0.5, 0.5, 0.5]  # Medium gray
REFRESH_RATE = 60  # Hz (standard monitor)
FLICKER_FREQUENCY = 30  # Hz

# Gabor patch parameters
GABOR_SIZE = 256  # pixels
GABOR_X_POS = 300  # pixels right of center (3 o'clock)
GABOR_Y_POS = 0  # centered vertically
SPATIAL_FREQUENCY = 0.05  # cycles per pixel (lower = fewer stripes)
ORIENTATION = 45  # degrees
MASK_TYPE = 'gauss'  # 'gauss' for smooth circular edges
MASK_SMOOTHNESS = 4.0  # Controls edge smoothness (higher = smoother/softer edges)

# Colors: Complementary RGB pairs (exact opposites on RGB wheel)
# PsychoPy uses RGB scale from -1 to 1
# For complementary colors: flip all channels (R->-R, G->-G, B->-B)
COLOR1 = [1.0, 0.0, -1.0]  # Magenta/Pink
COLOR2 = [-1.0, 0.0, 1.0]  # Cyan (opposite of magenta)

# Duration
TRIAL_DURATION = None  # seconds

# ==================== HELPER FUNCTIONS ====================

def get_complementary_color(color):
    """Calculate exact RGB opposite of a color."""
    return [-c for c in color]


def create_smooth_gaussian_mask(size, smoothness):
    """
    Create a Gaussian mask for smooth edges on the Gabor patch.
    
    Parameters:
    -----------
    size : int
        Size of the mask in pixels
    smoothness : float
        Smoothness factor. Higher values = smoother/more spread-out edges
        - 1.0: sharp edges
        - 2.0-3.0: moderately smooth
        - 5.0+: very smooth blur
    
    Returns:
    --------
    mask : numpy array (normalized to -1 to 1 range for PsychoPy)
    """
    # Create coordinate grid centered at 0
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    
    # Calculate distance from center
    distance = np.sqrt(X**2 + Y**2)
    
    # Create Gaussian: exp(-smoothness * distance^2)
    # Higher smoothness = faster falloff from center
    mask = np.exp(-smoothness * distance**2)
    
    # Scale to PsychoPy range (-1 to 1)
    # 1 = fully opaque, -1 = fully transparent
    mask = 2 * mask - 1
    
    return mask


def calculate_flicker_frame(frame_num, flicker_freq, refresh_rate):
    """
    Calculate whether stimulus should be shown this frame.
    
    For 60 Hz flicker on 60 Hz monitor:
    - Frame period = 60 / 60 = 1 frame
    - Shows: 1 frame on, 1 frame off, alternating
    
    Parameters:
    -----------
    frame_num : int
        Current frame number
    flicker_freq : int
        Desired flicker frequency in Hz
    refresh_rate : int
        Monitor refresh rate in Hz
    
    Returns:
    --------
    bool : True if stimulus should be drawn, False if not
    """
    frames_per_cycle = refresh_rate // flicker_freq
    return (frame_num % frames_per_cycle) < (frames_per_cycle // 2)


# ==================== SETUP ====================

# Create window
win = visual.Window(
    size=[WINDOW_WIDTH, WINDOW_HEIGHT],
    color=BACKGROUND_COLOR,
    units='pix',
    fullscr=False,
    monitor='testMonitor'
)

# Create fixation cross (at center)
fixation = visual.ShapeStim(
    win, 
    vertices=((0, -10), (0, 10), (0, 0), (-10, 0), (10, 0)),  # Vertical and horizontal lines
    lineWidth=2,
    lineColor='black',
    closeShape=False
)

# Create Gaussian mask for smooth edges
mask_array = create_smooth_gaussian_mask(
    size=GABOR_SIZE,
    smoothness=MASK_SMOOTHNESS
)

# Create Gabor patch (grating stimulus)
gabor = visual.GratingStim(
    win,
    tex='sin',  # Sine wave grating (Gabor pattern)
    mask=mask_array,  # Apply smooth Gaussian mask
    pos=[GABOR_X_POS, GABOR_Y_POS],  # 3 o'clock position
    size=GABOR_SIZE,
    sf=SPATIAL_FREQUENCY,
    ori=ORIENTATION,
    color=COLOR1,  # Start with first color
    contrast=1.0,
    units='pix'
)

# Verify complementary colors
color2_check = get_complementary_color(COLOR1)
print(f"Color 1: {COLOR1}")
print(f"Color 2 (should be opposite): {COLOR2}")
print(f"Verification - Calculated opposite of Color1: {color2_check}")
print(f"Match: {np.allclose(COLOR2, color2_check)}")

# ==================== TRIAL LOOP ====================

# Clock for timing
clock = core.Clock()
frame_num = 0

print("\n" + "="*60)
print("RIFT STUDY - FLICKERING GABOR PATCH")
print("="*60)
print(f"Duration: {TRIAL_DURATION} seconds")
print(f"Flicker frequency: {FLICKER_FREQUENCY} Hz")
print(f"Monitor refresh rate: {REFRESH_RATE} Hz")
print(f"Gabor position: 3 o'clock ({GABOR_X_POS}, {GABOR_Y_POS})")
print(f"Mask smoothness: {MASK_SMOOTHNESS}")
print(f"\nPress 'q' to quit early")
print("="*60 + "\n")

# Trial loop
trial_clock = core.Clock()
frame_num = 0
trial_ended = False
while not trial_ended:
    
    # Check for quit key
    keys = event.getKeys()
    if 'space' in keys:
        print(f"Trial stopped at {trial_clock.getTime():.2f}s (spacebar pressed)")
        trial_ended = True
        break
    
    # Determine which color to show based on flicker
    show_frame = calculate_flicker_frame(frame_num, FLICKER_FREQUENCY, REFRESH_RATE)
    
    if show_frame:
        gabor.color = COLOR1
    else:
        gabor.color = COLOR2
    
    # Draw stimuli
    fixation.draw()
    gabor.draw()
    
    # Flip to display
    win.flip()
    
    frame_num += 1

# ==================== CLEANUP ====================

print(f"\nTotal frames displayed: {frame_num}")
print(f"Actual duration: {trial_clock.getTime():.3f} seconds")
expected_frames = TRIAL_DURATION * REFRESH_RATE
print(f"Expected frames: ~{expected_frames:.0f}")
print(f"Difference: {frame_num - expected_frames:.0f} frames")

win.close()
core.quit()