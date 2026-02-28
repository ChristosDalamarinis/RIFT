"""
8 Gabor Patches - ADAPTIVE Frame-Based SINE-WAVE Flicker (7_sine_optimized.py)

NEW IN THIS VERSION:
- Pre-computed colors for optimal 240Hz+ performance
- Built-in frame timing diagnostics
- All original sine-wave and adaptive features preserved

OPTIMIZATIONS:
- Colors calculated once before trial (not per-frame)
- Fast array lookup instead of computation
- Detailed timing diagnostics after trial

================================================================================
"""


#! NOTE: this scripts has only some verification and diagnostic additions compared to 7sine.py script. 
# these daignostics hit the root cause of the problem which is dropped frames as the buffer doesn't 
# have enough time to paint things and flip them

from psychopy import visual, core, event
import numpy as np
from fractions import Fraction
import time

# ========================= CONFIGURATION ========================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
BACKGROUND_COLOR = [0.1, 0.1, 0.1] # 0.25 is a good option         0.075 another option
REFRESH_RATE =  480  # Hz - Change to your monitor (60, 120, 240, 360, 480, 500)

# ================== FLICKER CONFIGURATION ========================
NINE_OCLOCK_FLICKER_FREQUENCY = 1  # Hz
ENABLE_NINE_OCLOCK_FLICKER = True

THREE_OCLOCK_FLICKER_FREQUENCY = 60 # Hz
ENABLE_THREE_OCLOCK_FLICKER = True

# ================== FLICKER MODE CONFIGURATION ========================
FLICKER_MODE = 'SINE'  # Options: 'SQUARE', 'SINE'         NOTE: SINE is a very good option

print(f"\n{'='*70}")
print(f"FLICKER MODE: {FLICKER_MODE}-WAVE")
print(f"{'='*70}")
if FLICKER_MODE == 'SINE':
    print("Sine-wave modulation: Smooth gradual color transitions")
    print("Benefits: Smoother perceptual fusion, reduced edge artifacts")
else:
    print("Square-wave modulation: Abrupt color switching (standard RIFT)")
    print("Benefits: Stronger SSVEP response, standard in literature")
print(f"{'='*70}\n")

#! ==================== ADAPTIVE FLICKER CLASS WITH SINE ====================
class AdaptiveFlickerPattern:
    """
    Manages adaptive frame patterns with optional sine-wave modulation.
    Handles both integer and non-integer frame counts perfectly.
    """

    def __init__(self, refresh_rate, flicker_frequency, mode='SQUARE'):
        """
        Args:
            refresh_rate: Monitor refresh rate in Hz
            flicker_frequency: Target flicker frequency in Hz
            mode: 'SQUARE' for abrupt switching, 'SINE' for smooth transitions
        """
        self.refresh_rate = refresh_rate
        self.flicker_frequency = flicker_frequency
        self.mode = mode.upper()

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

        # Calculate frames per full cycle for sine generation
        self.frames_per_cycle = refresh_rate / flicker_frequency

        # Calculate achieved frequency
        total_frames = sum(self.pattern) * 2
        frames_per_cycle_actual = total_frames / self.pattern_length
        self.achieved_frequency = self.refresh_rate / frames_per_cycle_actual
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

    def _get_sine_value(self, frame_num):
        """
        Calculate sine wave value for current frame.

        Returns value from -1 (full MAGENTA) to +1 (full GREEN)
        with 0 being mid-gray.
        """
        # Calculate position within full cycle
        cycle_position = (frame_num % self.frames_per_cycle) / self.frames_per_cycle

        # Generate sine wave
        sine_value = np.sin(2 * np.pi * cycle_position)

        return sine_value

    def _blend_colors(self, color_a, color_b, sine_value):
        """
        Blend two colors based on sine value.

        Args:
            color_a: First color (e.g., GREEN) - corresponds to sine = +1
            color_b: Second color (e.g., MAGENTA) - corresponds to sine = -1
            sine_value: Value from -1 to +1

        Returns:
            Blended color
        """
        # Convert sine value (-1 to +1) to blend factor (0 to 1)
        blend_factor = (sine_value + 1) / 2

        # Linear interpolation
        blended = [
            color_b[i] * (1 - blend_factor) + color_a[i] * blend_factor
            for i in range(3)
        ]

        return blended

    def get_color_square(self, frame_num, color_a, color_b):
        """
        Square-wave flicker (original method).
        Abrupt switching between two colors.
        """
        # Calculate position within pattern cycle
        pattern_cycle_frames = sum(self.pattern) * 2
        pos_in_cycle = frame_num % pattern_cycle_frames

        # Find which half-cycle we're in
        cumulative = 0
        for half_idx in range(self.pattern_length * 2):
            pattern_idx = half_idx % self.pattern_length
            frames_this_half = self.pattern[pattern_idx]

            if pos_in_cycle < cumulative + frames_this_half:
                return color_a if half_idx % 2 == 0 else color_b

            cumulative += frames_this_half

        return color_a

    def get_color_sine(self, frame_num, color_a, color_b):
        """
        Sine-wave flicker (new method).
        Smooth gradual transitions between colors.
        """
        sine_value = self._get_sine_value(frame_num)
        return self._blend_colors(color_a, color_b, sine_value)

    def get_color(self, frame_num, color_a, color_b):
        """
        Get color for current frame based on selected mode.

        Args:
            frame_num: Current frame number
            color_a: First color (GREEN)
            color_b: Second color (MAGENTA)

        Returns:
            Color (list of 3 RGB values)
        """
        if self.mode == 'SINE':
            return self.get_color_sine(frame_num, color_a, color_b)
        else:
            return self.get_color_square(frame_num, color_a, color_b)

    def print_info(self):
        """Print diagnostic information."""
        print(f"  Target: {self.flicker_frequency} Hz")
        print(f"  Mode: {self.mode}-wave")
        print(f"  Ideal frames/half-cycle: {self.ideal_frames_per_half:.4f}")

        if self.is_integer:
            print(f"  Pattern type: EXACT INTEGER")
            print(f"  Pattern: {self.frames_low} frames per half-cycle")
        else:
            print(f"  Pattern type: ADAPTIVE")
            print(f"  Pattern: {self.pattern} (length={self.pattern_length})")

        print(f"  Achieved: {self.achieved_frequency:.6f} Hz")
        print(f"  Error: {self.error:.6f} Hz ({abs(self.error/self.flicker_frequency)*100:.4f}%)")

# ==================== VALIDATION & SETUP ====================
print(f"\n{'='*70}")
print(f"ADAPTIVE FRAME-BASED {FLICKER_MODE}-WAVE FLICKER (OPTIMIZED)")
print(f"{'='*70}")
print(f"Monitor refresh rate: {REFRESH_RATE} Hz")
print(f"Frame budget: {1000/REFRESH_RATE:.3f} ms")

# Create adaptive patterns
if ENABLE_NINE_OCLOCK_FLICKER:
    print(f"\n9 o'clock Gabor:")
    pattern_9 = AdaptiveFlickerPattern(REFRESH_RATE, NINE_OCLOCK_FLICKER_FREQUENCY, FLICKER_MODE)
    pattern_9.print_info()
else:
    pattern_9 = None
    print(f"\n9 o'clock Gabor: DISABLED")

if ENABLE_THREE_OCLOCK_FLICKER:
    print(f"\n3 o'clock Gabor:")
    pattern_3 = AdaptiveFlickerPattern(REFRESH_RATE, THREE_OCLOCK_FLICKER_FREQUENCY, FLICKER_MODE)
    pattern_3.print_info()
else:
    pattern_3 = None
    print(f"\n3 o'clock Gabor: DISABLED")

print(f"{'='*70}\n")

# ================== GABOR PARAMETERS ========================
GABOR_SIZE = 2000
CIRCLE_RADIUS = 500
GABOR_SF = 0.05 # 0.05 by default
GABOR_CONTRAST = 0.7
GABOR_OPACITY = 0.7
GABOR_PHASE = 0.5

GABOR_SMOOTHNESS_DEFAULT = 0.05  # 0.05 by default
GABOR_SMOOTHNESS_9_OCLOCK = 0.05 # 0.05 by default
GABOR_SMOOTHNESS_3_OCLOCK = 0.15 # 0.05 by default

ORIENTATION_DEFAULT = 0
ORIENTATION_9_OCLOCK = -20
ORIENTATION_3_OCLOCK = -20

# ================== COLOR CONFIGURATION ========================
# You can choose any of these color pairs:

# Option 1: Chromatic opponent colors (GREEN/MAGENTA) - CURRENT
GRAY_COLOR = [0.5, 0.5, 0.5] # Mid-gray for static Gabors (non-flickering)

# Flickering between GREEN vs MAGENTA by default
#COLOR_A = [-1.0, 1.0, -1.0]  # GREEN
#COLOR_B = [1.0, -1.0, 1.0]   # MAGENTA

# Option 2: Luminance modulation (BLACK/WHITE) - UNCOMMENT TO USE
# GRAY_COLOR = [0.0, 0.0, 0.0]
# COLOR_A = [-1.0, -1.0, -1.0]  # BLACK
# COLOR_B = [1.0, 1.0, 1.0]     # WHITE

# Option 3: Red/Cyan opponent colors - UNCOMMENT TO USE
# GRAY_COLOR = [0.5, 0.5, 0.5]
# COLOR_A = [1.0, -1.0, -1.0]   # RED
# COLOR_B = [-1.0, 1.0, 1.0]    # CYAN

# Option 4: Blue/Yellow opponent colors - UNCOMMENT TO USE
# GRAY_COLOR = [0.5, 0.5, 0.5]
COLOR_A = [-1.0, -1.0, 1.0]   # BLUE
COLOR_B = [1.0, 1.0, -1.0]    # YELLOW

ENABLE_LUMINANCE_SCALING = True
LUMINANCE_MULTIPLIER = 0.9

ENABLE_SATURATION_CONTROL = True
SATURATION_LEVEL = 0.9

TRIAL_DURATION = None

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

# Print color configuration
print(f"{'='*70}")
print(f"COLOR CONFIGURATION")
print(f"{'='*70}")
print(f"Color A: {COLOR_A}")
print(f"Color B: {COLOR_B}")
print(f"Average: {[(COLOR_A[i] + COLOR_B[i])/2 for i in range(3)]}")
print(f"{'='*70}\n")

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
    fullscr=True, # set to TRUE for fullscreen
    monitor='testMonitor',
    waitBlanking=True # True by default
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
clock_positions = [3, 9]                            # NOTE: by default -> clock_positions = [12, 1.5, 3, 4.5, 6, 7.5, 9, 10.5]

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

    custom_mask = create_custom_mask(size=4096, sigma=smoothness)  # NOTE: 256 by default

    gabors[hour] = visual.GratingStim(
        win,
        tex='none', # Sinusoidal grating = "sin", OR "sqr" for sharper edges. Other options: 'sin', 'sqr', 'cross', 'saw', 'none' NOTE: "sin" is not very good 
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

# ==================== PRE-COMPUTE COLORS (OPTIMIZATION!) ====================
print(f"\n{'='*70}")
print(f"PRE-COMPUTING COLORS FOR OPTIMAL PERFORMANCE")
print(f"{'='*70}")

# Pre-compute colors for 9 o'clock Gabor
if ENABLE_NINE_OCLOCK_FLICKER:
    max_precompute_frames = 10000  # Covers ~21 seconds at 480Hz
    precomputed_colors_9 = []
    print(f"Pre-computing {max_precompute_frames} colors for 9 o'clock...", end='')
    for f in range(max_precompute_frames):
        color = pattern_9.get_color(f, COLOR_A_FINAL, COLOR_B_FINAL)
        precomputed_colors_9.append(color)
    print(f" ✓ Done")
else:
    precomputed_colors_9 = None

# Pre-compute colors for 3 o'clock Gabor  
if ENABLE_THREE_OCLOCK_FLICKER:
    max_precompute_frames = 10000
    precomputed_colors_3 = []
    print(f"Pre-computing {max_precompute_frames} colors for 3 o'clock...", end='')
    for f in range(max_precompute_frames):
        color = pattern_3.get_color(f, COLOR_A_FINAL, COLOR_B_FINAL)
        precomputed_colors_3.append(color)
    print(f" ✓ Done")
else:
    precomputed_colors_3 = None

print(f"Pre-computation complete! Colors will use fast array lookup.")
print(f"{'='*70}\n")

# ==================== TRIAL LOOP ====================
print("\n" + "="*70)
print(f"8 GABOR PATCHES - {FLICKER_MODE}-WAVE ADAPTIVE FLICKER (OPTIMIZED)")
print("="*70)
print(f"Press SPACEBAR to end demo")
print("="*70 + "\n")

trial_clock = core.Clock()
frame_num = 0
trial_ended = False

# Frame timing diagnostics
frame_times = []
frame_durations = []
slow_frames = []
last_frame_time = None

# ==================== MAIN RENDERING LOOP (OPTIMIZED) ====================    
while not trial_ended:
    current_time = trial_clock.getTime()
    frame_times.append(current_time)

    # Poll keyboard every 10 frames (reduces overhead)
    if frame_num % 10 == 0:
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
            # OPTIMIZED: Fast array lookup (no calculation!)
            gabors[hour].color = precomputed_colors_9[frame_num % len(precomputed_colors_9)]
            gabors[hour].draw()

        elif hour == 3 and ENABLE_THREE_OCLOCK_FLICKER:
            # OPTIMIZED: Fast array lookup (no calculation!)
            gabors[hour].color = precomputed_colors_3[frame_num % len(precomputed_colors_3)]
            gabors[hour].draw()
        else:
            gabors[hour].draw()

    win.flip()

    # Frame timing measurement
    frame_end = time.perf_counter()
    if last_frame_time is not None:
        frame_duration = (frame_end - last_frame_time) * 1000  # Convert to ms
        frame_durations.append(frame_duration)

        # Log slow frames
        frame_budget = 1000 / REFRESH_RATE
        if frame_duration > frame_budget * 1.1:  # 10% over budget
            slow_frames.append((frame_num, frame_duration))
            if len(slow_frames) <= 10:  # Only print first 10
                print(f"⚠ Slow frame {frame_num}: {frame_duration:.3f} ms (budget: {frame_budget:.3f} ms)")

    last_frame_time = frame_end
    frame_num += 1

# ==================== FRAME TIMING DIAGNOSTICS ====================
print("\n" + "="*70)
print("FRAME TIMING DIAGNOSTICS")
print("="*70)

if len(frame_durations) > 0:
    mean_duration = np.mean(frame_durations)
    median_duration = np.median(frame_durations)
    max_duration = np.max(frame_durations)
    min_duration = np.min(frame_durations)
    std_duration = np.std(frame_durations)

    frame_budget = 1000 / REFRESH_RATE
    slow_count = len(slow_frames)
    dropped_count = sum(1 for d in frame_durations if d > frame_budget * 1.5)

    print(f"\n*** FRAME DURATION STATISTICS ***")
    print(f"  Mean:   {mean_duration:.3f} ms")
    print(f"  Median: {median_duration:.3f} ms")
    print(f"  Max:    {max_duration:.3f} ms")
    print(f"  Min:    {min_duration:.3f} ms")
    print(f"  Std:    {std_duration:.3f} ms")

    print(f"\n*** FRAME BUDGET ANALYSIS ***")
    print(f"  Target budget: {frame_budget:.3f} ms ({REFRESH_RATE} Hz)")
    print(f"  Mean vs budget: {mean_duration - frame_budget:+.3f} ms")
    print(f"  Slow frames (>10% over): {slow_count} ({slow_count/len(frame_durations)*100:.2f}%)")
    print(f"  Dropped frames (>50% over): {dropped_count} ({dropped_count/len(frame_durations)*100:.2f}%)")

    # Calculate actual refresh rate
    actual_fps = 1000 / mean_duration
    print(f"\n*** ACTUAL REFRESH RATE ***")
    print(f"  Target: {REFRESH_RATE} Hz")
    print(f"  Actual: {actual_fps:.2f} Hz")
    print(f"  Match: {'✓ YES' if abs(actual_fps - REFRESH_RATE) < REFRESH_RATE * 0.05 else '✗ NO'}")

    # Performance assessment
    print(f"\n*** PERFORMANCE ASSESSMENT ***")
    if mean_duration < frame_budget * 0.95 and slow_count < len(frame_durations) * 0.01:
        print(f"  ✓ EXCELLENT: Comfortable margin, < 1% slow frames")
    elif mean_duration < frame_budget and slow_count < len(frame_durations) * 0.05:
        print(f"  ✓ GOOD: Within budget, < 5% slow frames")
    elif mean_duration < frame_budget * 1.05:
        print(f"  △ ACCEPTABLE: Close to budget, may have occasional drops")
    else:
        print(f"  ✗ POOR: Over budget, frequent dropped frames")
        print(f"  → Try: Close background apps, reduce mask size, use SQUARE mode")

    # Detailed slow frame list (if not too many)
    if len(slow_frames) > 0 and len(slow_frames) <= 20:
        print(f"\n*** SLOW FRAMES DETAIL ***")
        for frame_id, duration in slow_frames[:20]:
            print(f"  Frame {frame_id}: {duration:.3f} ms")
        if len(slow_frames) > 20:
            print(f"  ... and {len(slow_frames) - 20} more")

print(f"\n{'='*70}\n")

win.close()
core.quit()