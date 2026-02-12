"""
8 Gabor Patches - ADAPTIVE Frame-Based SINE-WAVE Flicker (7_sine.py)

NEW FEATURES:
- Sine-wave modulation instead of square-wave
- Smooth gradual color transitions
- Maintains perfect temporal averaging to gray
- Compatible with both opponent colors and black/white

SINE-WAVE ARCHITECTURE:
Instead of:     GREEN (100%) → MAGENTA (100%) → repeat
Now:           GREEN (100%) → blend (71%) → gray (0%) → 
               blend (71%) → MAGENTA (100%) → blend (71%) → 
               gray (0%) → blend (71%) → repeat

Both average to gray, but sine-wave provides smoother transitions.

================================================================================
"""

# NOTE: this script has a sine-wave architecture for the flickering between opposite colours or black and white.
# NOTE: this is the 1st script employing the algorithm but you can choose between a SINE or SQUARE wave for flickering.

from psychopy import visual, core, event
import numpy as np
from fractions import Fraction

# ========================= CONFIGURATION ========================
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
BACKGROUND_COLOR = [0.0, 0.0, 0.0]
REFRESH_RATE = 240  # Hz

# ================== FLICKER CONFIGURATION ========================
NINE_OCLOCK_FLICKER_FREQUENCY = 60  # Hz
ENABLE_NINE_OCLOCK_FLICKER = True

THREE_OCLOCK_FLICKER_FREQUENCY = 1  # Hz
ENABLE_THREE_OCLOCK_FLICKER = True

# ================== FLICKER MODE CONFIGURATION ========================
# Choose flicker mode: 'SQUARE' or 'SINE'
FLICKER_MODE = 'SQUARE'  # Options: 'SQUARE', 'SINE'                       NOTE: use square if 120hz monitor and 60hz flicker is used

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

# ==================== ADAPTIVE FLICKER CLASS WITH SINE ====================
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

        # Generate sine wave: starts at 0, goes to +1, back to 0, to -1, back to 0
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
        # sine = -1 → blend_factor = 0 → full color_b (MAGENTA)
        # sine = 0  → blend_factor = 0.5 → mid-gray
        # sine = +1 → blend_factor = 1 → full color_a (GREEN)
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
print(f"ADAPTIVE FRAME-BASED {FLICKER_MODE}-WAVE FLICKER")
print(f"{'='*70}")
print(f"Monitor refresh rate: {REFRESH_RATE} Hz")

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
GABOR_SIZE = 1500
CIRCLE_RADIUS = 300
GABOR_SF = 0.05 # 0.05 by default
GABOR_CONTRAST = 1.0
GABOR_OPACITY = 1.0
GABOR_PHASE = 0.5

GABOR_SMOOTHNESS_DEFAULT = 0.05  # 0.05 be default
GABOR_SMOOTHNESS_9_OCLOCK = 0.05 # 0.05 by default
GABOR_SMOOTHNESS_3_OCLOCK = 0.05 # 0.05 by default

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
COLOR_A = [-1.0, -1.0, -1.0]  # BLACK
COLOR_B = [1.0, 1.0, 1.0]     # WHITE

# Option 3: Red/Cyan opponent colors - UNCOMMENT TO USE
# GRAY_COLOR = [0.5, 0.5, 0.5]
# COLOR_A = [1.0, -1.0, -1.0]   # RED
# COLOR_B = [-1.0, 1.0, 1.0]    # CYAN

# Option 4: Blue/Yellow opponent colors - UNCOMMENT TO USE
# GRAY_COLOR = [0.5, 0.5, 0.5]
# COLOR_A = [-1.0, -1.0, 1.0]   # BLUE
# COLOR_B = [1.0, 1.0, -1.0]    # YELLOW

ENABLE_LUMINANCE_SCALING = True
LUMINANCE_MULTIPLIER = 0.7

ENABLE_SATURATION_CONTROL = True
SATURATION_LEVEL = 0.7

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
print(f"\nWith {FLICKER_MODE}-wave modulation:")
if FLICKER_MODE == 'SINE':
    print(f"  Colors blend smoothly through intermediate values")
    print(f"  Temporal average: [0, 0, 0] (mid-gray)")
else:
    print(f"  Colors switch abruptly between extremes")
    print(f"  Temporal average: [0, 0, 0] (mid-gray)")
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
    fullscr=False,
    monitor='testMonitor',
    waitBlanking=True
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
clock_positions = [12, 1.5, 3, 4.5, 6, 7.5, 9, 10.5]   # NOTE: by default -> clock_positions = [12, 1.5, 3, 4.5, 6, 7.5, 9, 10.5]

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

    custom_mask = create_custom_mask(size=256, sigma=smoothness) # NOTE: 256 by default

    gabors[hour] = visual.GratingStim(
        win,
        tex='sqr', # Sinusoidal grating = "sin", OR "sqr" for sharper edges. Other options: 'sin', 'sqr', 'cross', 'saw', 'none' NOTE: "sin" is not very good 
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
print(f"8 GABOR PATCHES - {FLICKER_MODE}-WAVE ADAPTIVE FLICKER")
print("="*70)
print(f"Press SPACEBAR to end demo")
print("="*70 + "\n")

trial_clock = core.Clock()
frame_num = 0
trial_ended = False

frame_times = []
color_samples_9 = []  # Store color values for sine verification
color_samples_3 = []

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
            # Get color using sine or square wave
            current_color = pattern_9.get_color(frame_num, COLOR_A_FINAL, COLOR_B_FINAL)
            gabors[hour].color = current_color

            # Store for verification (only first few cycles)
            if frame_num < 100:
                color_samples_9.append((frame_num, current_color))

            gabors[hour].draw()

        elif hour == 3 and ENABLE_THREE_OCLOCK_FLICKER:
            # Get color using sine or square wave
            current_color = pattern_3.get_color(frame_num, COLOR_A_FINAL, COLOR_B_FINAL)
            gabors[hour].color = current_color

            # Store for verification
            if frame_num < 100:
                color_samples_3.append((frame_num, current_color))

            gabors[hour].draw()
        else:
            gabors[hour].draw()

    win.flip()
    frame_num += 1

# ==================== TIMING VERIFICATION ====================
print("\n" + "="*70)
print("TIMING & COLOR VERIFICATION")
print("="*70)

if len(frame_times) > 1:
    frame_intervals = np.diff(frame_times)
    mean_frame_interval = np.mean(frame_intervals)
    actual_refresh_rate = 1.0 / mean_frame_interval

    print(f"\n*** MONITOR REFRESH RATE ***")
    print(f"  Expected: {REFRESH_RATE} Hz")
    print(f"  Actual: {actual_refresh_rate:.2f} Hz")
    print(f"  Match: {'✓ YES' if abs(actual_refresh_rate - REFRESH_RATE) < 5 else '✗ NO'}")

# Verify sine-wave color averaging
if FLICKER_MODE == 'SINE' and len(color_samples_9) > 0:
    print(f"\n*** SINE-WAVE COLOR AVERAGING (9 o'clock) ***")
    colors_array = np.array([c[1] for c in color_samples_9])
    average_color = np.mean(colors_array, axis=0)
    print(f"  Samples: {len(color_samples_9)} frames")
    print(f"  Temporal average: [{average_color[0]:.6f}, {average_color[1]:.6f}, {average_color[2]:.6f}]")
    print(f"  Averages to gray: {'✓ YES' if np.allclose(average_color, [0, 0, 0], atol=0.1) else '✗ NO'}")

    # Show color range
    min_color = np.min(colors_array, axis=0)
    max_color = np.max(colors_array, axis=0)
    print(f"  Color range: [{min_color[0]:.3f}, {min_color[1]:.3f}, {min_color[2]:.3f}] to")
    print(f"               [{max_color[0]:.3f}, {max_color[1]:.3f}, {max_color[2]:.3f}]")

print("="*70 + "\n")

win.close()
core.quit()