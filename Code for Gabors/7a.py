"""
8 Gabor Patches - ADAPTIVE Frame-Based Flicker (7.py - Enhanced)

SUPPORTS BOTH:
1. Integer frame counts (60Hz, 80Hz, 120Hz, etc.) - EXACT timing
2. Non-integer frame counts (64Hz, 72Hz, 100Hz, etc.) - ADAPTIVE patterns

ADAPTIVE ALGORITHM:
- For 64Hz on 480Hz (3.75 frames/color): alternates [4,3,4,4] pattern
- For 72Hz on 480Hz (3.33 frames/color): alternates [4,3,3] pattern
- Achieves EXACT target frequency with zero average error

================================================================================
"""

# NOTE: this script uses sqaure-wave architecture for flickering between two colours.


from psychopy import visual, core, event
import numpy as np
from fractions import Fraction

# ========================= CONFIGURATION ========================
WINDOW_WIDTH = 1710
WINDOW_HEIGHT = 1107
BACKGROUND_COLOR = [0.0, 0.0, 0.0] # Mid-gray
REFRESH_RATE = 60  # Hz - Supports: 60, 120, 240, 360, 480

# ================== FLICKER CONFIGURATION ========================
NINE_OCLOCK_FLICKER_FREQUENCY = 64  # Hz - Now supports non-integer!
ENABLE_NINE_OCLOCK_FLICKER = False

THREE_OCLOCK_FLICKER_FREQUENCY = 30 # Hz
ENABLE_THREE_OCLOCK_FLICKER = True

# ==================== ADAPTIVE FLICKER CLASS ====================
class AdaptiveFlickerPattern:
    """
    Manages adaptive frame patterns for any flicker frequency.
    Handles both integer and non-integer frame counts perfectly.
    """

    def __init__(self, refresh_rate, flicker_frequency):
        self.refresh_rate = refresh_rate
        self.flicker_frequency = flicker_frequency

        # Calculate ideal frames per half-cycle
        self.ideal_frames_per_half = refresh_rate / flicker_frequency / 2

        # Get floor and ceiling
        self.frames_low = int(np.floor(self.ideal_frames_per_half))
        self.frames_high = int(np.ceil(self.ideal_frames_per_half))

        # Check if integer (no adaptation needed)
        self.is_integer = (self.frames_low == self.frames_high)

        if self.is_integer:
            self.pattern = [self.frames_low]
            self.pattern_length = 1
        else:
            self.pattern = self._generate_pattern()
            self.pattern_length = len(self.pattern)

        # Pre-calculate cumulative frame boundaries for fast lookup
        self._build_frame_boundaries()

        # Calculate achieved frequency
        total_frames = sum(self.pattern) * 2
        frames_per_cycle = total_frames / self.pattern_length
        self.achieved_frequency = self.refresh_rate / frames_per_cycle
        self.error = self.achieved_frequency - self.flicker_frequency

    def _generate_pattern(self):
        """Generate optimal alternating pattern using fraction reduction."""
        fractional_part = self.ideal_frames_per_half - self.frames_low
        frac = Fraction(fractional_part).limit_denominator(1000)

        pattern_length = frac.denominator
        num_high = frac.numerator

        # Create evenly distributed pattern
        pattern = []
        for i in range(pattern_length):
            if (i * num_high) % pattern_length < num_high:
                pattern.append(self.frames_high)
            else:
                pattern.append(self.frames_low)

        return pattern

    def _build_frame_boundaries(self):
        """Pre-calculate frame boundaries for O(1) color lookup."""
        # Calculate frames for many cycles to cover long experiments
        max_cycles = 10000  # Should cover even long experiments
        self.frame_boundaries = []

        cumulative = 0
        for cycle in range(max_cycles):
            for half_idx, frames in enumerate(self.pattern):
                color_idx = half_idx % 2  # 0 or 1
                self.frame_boundaries.append((cumulative, color_idx))
                cumulative += frames

        self.max_frame = cumulative

    def get_color_fast(self, frame_num, color_a, color_b):
        """
        Fast O(log n) color lookup using pre-calculated boundaries.

        Args:
            frame_num: Current frame number
            color_a: First color (GREEN)
            color_b: Second color (MAGENTA)

        Returns:
            color_a or color_b
        """
        # Handle wraparound for very long experiments
        frame_num = frame_num % self.max_frame

        # Binary search for efficiency (could use linear for simplicity)
        for i, (boundary, color_idx) in enumerate(self.frame_boundaries):
            if i + 1 < len(self.frame_boundaries):
                next_boundary = self.frame_boundaries[i + 1][0]
                if boundary <= frame_num < next_boundary:
                    return color_a if color_idx == 0 else color_b

        # Fallback
        return color_a

    def get_color_simple(self, frame_num, color_a, color_b):
        """
        Simple O(1) color lookup - recalculates position each time.
        More readable, slightly slower but negligible for real-time use.
        """
        # Total frames in one complete pattern cycle
        pattern_cycle_frames = sum(self.pattern) * 2

        # Position within pattern cycle
        pos_in_cycle = frame_num % pattern_cycle_frames

        # Find which half-cycle we're in
        cumulative = 0
        for half_idx in range(self.pattern_length * 2):
            pattern_idx = half_idx % self.pattern_length
            frames_this_half = self.pattern[pattern_idx]

            if pos_in_cycle < cumulative + frames_this_half:
                # We're in this half-cycle
                return color_a if half_idx % 2 == 0 else color_b

            cumulative += frames_this_half

        # Fallback (should never reach)
        return color_a

    def print_info(self):
        """Print diagnostic information."""
        print(f"  Target: {self.flicker_frequency} Hz")
        print(f"  Ideal frames/half-cycle: {self.ideal_frames_per_half:.4f}")

        if self.is_integer:
            print(f"  Mode: EXACT INTEGER")
            print(f"  Pattern: {self.frames_low} frames per color")
        else:
            print(f"  Mode: ADAPTIVE PATTERN")
            print(f"  Pattern: {self.pattern} (length={self.pattern_length})")
            count_low = self.pattern.count(self.frames_low)
            count_high = self.pattern.count(self.frames_high)
            print(f"  Distribution: {count_low}×{self.frames_low}frames, {count_high}×{self.frames_high}frames")

        print(f"  Achieved: {self.achieved_frequency:.6f} Hz")
        print(f"  Error: {self.error:.6f} Hz ({abs(self.error/self.flicker_frequency)*100:.4f}%)")

# ==================== VALIDATION & SETUP ====================
print(f"\n{'='*70}")
print(f"ADAPTIVE FRAME-BASED FLICKER - CONFIGURATION")
print(f"{'='*70}")
print(f"Monitor refresh rate: {REFRESH_RATE} Hz")

# Create adaptive patterns
if ENABLE_NINE_OCLOCK_FLICKER:
    print(f"\n9 o'clock Gabor:")
    pattern_9 = AdaptiveFlickerPattern(REFRESH_RATE, NINE_OCLOCK_FLICKER_FREQUENCY)
    pattern_9.print_info()
else:
    pattern_9 = None
    print(f"\n9 o'clock Gabor: DISABLED")

if ENABLE_THREE_OCLOCK_FLICKER:
    print(f"\n3 o'clock Gabor:")
    pattern_3 = AdaptiveFlickerPattern(REFRESH_RATE, THREE_OCLOCK_FLICKER_FREQUENCY)
    pattern_3.print_info()
else:
    pattern_3 = None
    print(f"\n3 o'clock Gabor: DISABLED")

print(f"{'='*70}\n")

# ================== GABOR PARAMETERS (same as before) ========================
GABOR_SIZE = 2000
CIRCLE_RADIUS = 300
GABOR_SF = 0.05
GABOR_CONTRAST = 1.0
GABOR_OPACITY = 1.0
GABOR_PHASE = 0.5

GABOR_SMOOTHNESS_DEFAULT = 0.05
GABOR_SMOOTHNESS_9_OCLOCK = 0.05
GABOR_SMOOTHNESS_3_OCLOCK = 0.05

ORIENTATION_DEFAULT = 0
ORIENTATION_9_OCLOCK = -20
ORIENTATION_3_OCLOCK = -20

# ================== COLOR CONFIGURATION ========================
GRAY_COLOR = [0.5, 0.5, 0.5] # For static Gabors (non-flickering)

# Flickering between two opposite colors in RGB space (GREEN vs MAGENTA) by default
# COLOR_A = [-1.0, 1.0, -1.0]  # GREEN
# COLOR_B = [1.0, -1.0, 1.0]   # MAGENTA

# Uncomment below to choose flicker betwee white and black and other opposite colours
COLOR_A = [1.0, 1.0, 1.0]      # WHITE
COLOR_B = [-1.0, -1.0, -1.0]   # BLACK

# Uncomment below to choose flicker between red and cyan (opposite on RGB) 
# COLOR_A = [1.0, -1.0, -1.0]   # RED
# COLOR_B = [-1.0, 1.0, 1.0]    # CYAN

# Uncomment below to choose flicker between blue and yellow (opposite on RGB)
# COLOR_A = [-1.0, -1.0, 1.0]   # BLUE
# COLOR_B = [1.0, 1.0, -1.0]    # YELLOW


ENABLE_LUMINANCE_SCALING = True
LUMINANCE_MULTIPLIER = 1.0

ENABLE_SATURATION_CONTROL = True
SATURATION_LEVEL = 1.0

TRIAL_DURATION = None # Set to None for infinite until spacebar, or specify in seconds (e.g., 30.0)

# ==================== COLOR PROCESSING ====================
def desaturate_color(color, saturation, gray_value=0.0):
    return [gray_value + (c - gray_value) * saturation for c in color]

if ENABLE_LUMINANCE_SCALING:
    COLOR_A_LUM = [c * LUMINANCE_MULTIPLIER for c in COLOR_A]
    COLOR_B_LUM = [c * LUMINANCE_MULTIPLIER for c in COLOR_B]
else:
    COLOR_A_LUM = COLOR_A
    COLOR_B_LUM = COLOR_B

if ENABLE_SATURATION_CONTROL:
    COLOR_A_FINAL = desaturate_color(COLOR_A_LUM, SATURATION_LEVEL, BACKGROUND_COLOR[0])
    COLOR_B_FINAL = desaturate_color(COLOR_B_LUM, SATURATION_LEVEL, BACKGROUND_COLOR[0])
else:
    COLOR_A_FINAL = COLOR_A_LUM
    COLOR_B_FINAL = COLOR_B_LUM

# ==================== HELPER FUNCTIONS ====================
def get_clock_position(hour, radius): 
    angle = (hour / 12.0) * 2 * np.pi - np.pi / 2
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    return [x, y]

def create_custom_mask(size, sigma):
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
    fullscr=True, # turn TRUE for full-screen, 
    monitor='testMonitor',
    waitBlanking=True # Ensures sync with monitor refresh
)

fixation = visual.ShapeStim(
    win,
    vertices=((0, -10), (0, 10), (0, 0), (-10, 0), (10, 0)),
    lineWidth=2,
    lineColor='white',
    closeShape=False
)

# ==================== CREATE GABOR STIMULI ====================
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
        tex='sin', # Sinusoidal grating = "sin", OR "sqr" for sharper edges. Other options: 'sin', 'sqr', 'cross', 'saw', 'none'
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

# ==================== TRIAL LOOP ====================
print("\n" + "="*70)
print("8 GABOR PATCHES - ADAPTIVE FLICKER ACTIVE")
print("="*70)
print(f"Press SPACEBAR to end demo")
print("="*70 + "\n")

trial_clock = core.Clock()
frame_num = 0
trial_ended = False

frame_times = []
flicker_switches_9 = []
flicker_switches_3 = []
last_color_9 = None
last_color_3 = None

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
        print(f"\nTrial ended at {trial_clock.getTime():.2f}s (max duration)")
        trial_ended = True
        break

    fixation.draw()

    for hour in clock_positions:
        if hour == 9 and ENABLE_NINE_OCLOCK_FLICKER:
            # Use adaptive pattern
            current_color = pattern_9.get_color_simple(frame_num, COLOR_A_FINAL, COLOR_B_FINAL)
            gabors[hour].color = current_color

            if last_color_9 is not None and current_color != last_color_9:
                flicker_switches_9.append(current_time)
            last_color_9 = current_color

            gabors[hour].draw()

        elif hour == 3 and ENABLE_THREE_OCLOCK_FLICKER:
            # Use adaptive pattern
            current_color = pattern_3.get_color_simple(frame_num, COLOR_A_FINAL, COLOR_B_FINAL)
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
print("TIMING VERIFICATION")
print("="*70)

if len(frame_times) > 1:
    frame_intervals = np.diff(frame_times)
    mean_frame_interval = np.mean(frame_intervals)
    actual_refresh_rate = 1.0 / mean_frame_interval

    print(f"\n*** MONITOR REFRESH RATE ***")
    print(f"  Expected: {REFRESH_RATE} Hz")
    print(f"  Actual: {actual_refresh_rate:.2f} Hz")
    print(f"  Match: {'✓ YES' if abs(actual_refresh_rate - REFRESH_RATE) < 5 else '✗ NO'}")

if ENABLE_NINE_OCLOCK_FLICKER and len(flicker_switches_9) > 1:
    switch_intervals = np.diff(flicker_switches_9)
    mean_switch_interval = np.mean(switch_intervals)
    actual_flicker_frequency = 1.0 / (2 * mean_switch_interval)

    print(f"\n*** 9 O'CLOCK GABOR FLICKER ***")
    print(f"  Expected: {NINE_OCLOCK_FLICKER_FREQUENCY} Hz")
    print(f"  Actual: {actual_flicker_frequency:.2f} Hz")
    print(f"  Match: {'✓ YES' if abs(actual_flicker_frequency - NINE_OCLOCK_FLICKER_FREQUENCY) < 2 else '✗ NO'}")
    print(f"  Pattern type: {'EXACT' if pattern_9.is_integer else 'ADAPTIVE'}")

if ENABLE_THREE_OCLOCK_FLICKER and len(flicker_switches_3) > 1:
    switch_intervals = np.diff(flicker_switches_3)
    mean_switch_interval = np.mean(switch_intervals)
    actual_flicker_frequency = 1.0 / (2 * mean_switch_interval)

    print(f"\n*** 3 O'CLOCK GABOR FLICKER ***")
    print(f"  Expected: {THREE_OCLOCK_FLICKER_FREQUENCY} Hz")
    print(f"  Actual: {actual_flicker_frequency:.2f} Hz")
    print(f"  Match: {'✓ YES' if abs(actual_flicker_frequency - THREE_OCLOCK_FLICKER_FREQUENCY) < 2 else '✗ NO'}")
    print(f"  Pattern type: {'EXACT' if pattern_3.is_integer else 'ADAPTIVE'}")

print("="*70 + "\n")

win.close()
core.quit()