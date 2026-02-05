"""
Singleton Visual Search Paradigm with Flickering SSVEP Stimuli

- Gray background with fixation cross at center
- 8 stimuli arranged in a circle around fixation (clock positions)
- 3 o'clock: RED/CYAN GRATING (distractor) - flickers independently
- 9 o'clock: GREEN/MAGENTA GRATING (target) - flickers independently
- Other positions: GREEN CIRCLES with sharp edges (solid, no flicker)
"""

from psychopy import visual, core, event
import numpy as np

# ==================== CONFIGURATION ====================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
BACKGROUND_COLOR = [0.5, 0.5, 0.5]  # Medium gray
REFRESH_RATE = 240  # Hz - set to your monitor's actual refresh rate

# Flicker settings for TARGET and DISTRACTOR
TARGET_FLICKER_FREQUENCY = 30  # Hz - Green/magenta grating at 9 o'clock
DISTRACTOR_FLICKER_FREQUENCY = 60  # Hz - Red/cyan grating at 3 o'clock

# Enable/disable flicker for each stimulus
ENABLE_TARGET_FLICKER = True
ENABLE_DISTRACTOR_FLICKER = True

# Stimulus parameters
STIMULUS_SIZE = 120  # pixels (for gratings and circles)
CIRCLE_RADIUS = 400  # Distance from center to each stimulus
MASK_SMOOTHNESS = 4.0  # Edge smoothness for gratings only

# Colors (PsychoPy uses RGB -1 to 1)
RED_COLOR = [1.0, -1.0, -1.0]  # Red for distractor grating
CYAN_COLOR = [-1.0, 1.0, 1.0]  # Cyan (inverted red) for distractor
GREEN_COLOR = [-1.0, 1.0, -1.0]  # Green for target grating and circles
MAGENTA_COLOR = [1.0, -1.0, 1.0]  # Magenta (inverted green) for target

# Grating parameters
GRATING_SPATIAL_FREQUENCY = 0.05  # Cycles per pixel
GRATING_ORIENTATION = 45  # Degrees (diagonal stripes)

# Duration
TRIAL_DURATION = None  # None = infinite (until spacebar)

# ==================== HELPER FUNCTIONS ====================
def create_smooth_gaussian_mask(size, smoothness):
    """Create a Gaussian mask for smooth edges on gratings."""
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    distance = np.sqrt(X**2 + Y**2)
    mask = np.exp(-smoothness * distance**2)
    mask = 2 * mask - 1
    return mask

def calculate_flicker_frame(frame_num, flicker_freq, refresh_rate):
    """Calculate whether stimulus should flicker this frame."""
    frames_per_cycle = refresh_rate // flicker_freq
    return (frame_num % frames_per_cycle) < (frames_per_cycle // 2)

def get_clock_position(hour, radius):
    """
    Get (x, y) coordinates for a clock position.
    hour: 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
    radius: distance from center
    """
    angle = (hour / 12.0) * 2 * np.pi - np.pi / 2  # Convert to radians, 12 o'clock = top
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    return [x, y]

# ==================== SETUP ====================
win = visual.Window(
    size=[WINDOW_WIDTH, WINDOW_HEIGHT],
    color=BACKGROUND_COLOR,
    units='pix',
    fullscr=False,
    monitor='testMonitor',
    waitBlanking=True  # Sync to vertical blank for stable timing
)

# Create fixation cross (at center)
fixation = visual.ShapeStim(
    win,
    vertices=((0, -10), (0, 10), (0, 0), (-10, 0), (10, 0)),
    lineWidth=2,
    lineColor='black',
    closeShape=False
)

# Create mask for gratings only (smooth edges)
grating_mask = create_smooth_gaussian_mask(
    size=256,
    smoothness=MASK_SMOOTHNESS
)

# ==================== CREATE STIMULI ====================
# Dictionary to hold all stimuli
stimuli = {}

# Create 8 stimuli at clock positions
clock_positions = {
    12: "circle",      # Top
    1.5: "circle",     # Top-right (between 1 and 2)
    3: "distractor",   # Right (RED/CYAN GRATING)
    4.5: "circle",     # Bottom-right
    6: "circle",       # Bottom
    7.5: "circle",     # Bottom-left
    9: "target",       # Left (GREEN/MAGENTA GRATING)
    10.5: "circle"     # Top-left
}

for hour, stim_type in clock_positions.items():
    pos = get_clock_position(hour, CIRCLE_RADIUS)
    
    if stim_type == "target":
        # Green/magenta grating at 9 o'clock (with smooth mask)
        stimuli[hour] = visual.GratingStim(
            win,
            tex='sin',
            mask=grating_mask,
            pos=pos,
            size=STIMULUS_SIZE,
            sf=GRATING_SPATIAL_FREQUENCY,
            ori=GRATING_ORIENTATION,
            color=GREEN_COLOR,
            contrast=1.0,
            units='pix'
        )
    elif stim_type == "distractor":
        # Red/cyan grating at 3 o'clock (with smooth mask)
        stimuli[hour] = visual.GratingStim(
            win,
            tex='sin',
            mask=grating_mask,
            pos=pos,
            size=STIMULUS_SIZE,
            sf=GRATING_SPATIAL_FREQUENCY,
            ori=GRATING_ORIENTATION,
            color=RED_COLOR,
            contrast=1.0,
            units='pix'
        )
    else:  # circle
        # Green circle with SHARP edges (no mask, using Circle shape)
        stimuli[hour] = visual.Circle(
            win,
            radius=STIMULUS_SIZE / 2,
            pos=pos,
            fillColor=GREEN_COLOR,
            lineColor=GREEN_COLOR,
            units='pix'
        )

# ==================== TRIAL LOOP ====================
print("\n" + "="*70)
print("SINGLETON VISUAL SEARCH PARADIGM - FLICKERING SSVEP GRATINGS")
print("="*70)
print(f"Monitor refresh rate: {REFRESH_RATE} Hz")
print(f"Target (9 o'clock, GREEN/MAGENTA GRATING): {TARGET_FLICKER_FREQUENCY} Hz {'(ENABLED)' if ENABLE_TARGET_FLICKER else '(DISABLED)'}")
print(f"Distractor (3 o'clock, RED/CYAN GRATING): {DISTRACTOR_FLICKER_FREQUENCY} Hz {'(ENABLED)' if ENABLE_DISTRACTOR_FLICKER else '(DISABLED)'}")
print(f"Other positions: Static GREEN circles (sharp edges)")
print(f"\nStimulus layout:")
print(f"  - 8 positions around fixation cross")
print(f"  - Target (GREEN/MAGENTA GRATING) at 9 o'clock (LEFT)")
print(f"  - Distractor (RED/CYAN GRATING) at 3 o'clock (RIGHT)")
print(f"  - Neutral (GREEN CIRCLES with sharp edges) at other positions")
print(f"\nPress SPACEBAR to end demo")
print("="*70 + "\n")

trial_clock = core.Clock()
frame_num = 0
trial_ended = False

# Lists to store timing data
frame_times = []
target_switches = []
distractor_switches = []
last_target_color = GREEN_COLOR
last_distractor_color = RED_COLOR

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
    
    # Draw fixation cross
    fixation.draw()
    
    # Draw all stimuli with independent flicker control
    for hour, stim in stimuli.items():
        if hour == 9:  # TARGET (green/magenta grating)
            if ENABLE_TARGET_FLICKER:
                show_frame = calculate_flicker_frame(frame_num, TARGET_FLICKER_FREQUENCY, REFRESH_RATE)
                if show_frame:
                    stim.color = GREEN_COLOR
                    current_color = GREEN_COLOR
                else:
                    stim.color = MAGENTA_COLOR  # Inverted green
                    current_color = MAGENTA_COLOR
                
                # Track color switches
                if current_color != last_target_color:
                    target_switches.append(current_time)
                    last_target_color = current_color
            stim.draw()
            
        elif hour == 3:  # DISTRACTOR (red/cyan grating)
            if ENABLE_DISTRACTOR_FLICKER:
                show_frame = calculate_flicker_frame(frame_num, DISTRACTOR_FLICKER_FREQUENCY, REFRESH_RATE)
                if show_frame:
                    stim.color = RED_COLOR
                    current_color = RED_COLOR
                else:
                    stim.color = CYAN_COLOR  # Inverted red
                    current_color = CYAN_COLOR
                
                # Track color switches
                if current_color != last_distractor_color:
                    distractor_switches.append(current_time)
                    last_distractor_color = current_color
            stim.draw()
            
        else:  # NEUTRAL circles (green, no flicker, sharp edges)
            stim.draw()
    
    # Flip to display
    win.flip()
    frame_num += 1

# ==================== TIMING ANALYSIS ====================
print("\n" + "="*70)
print("TIMING VERIFICATION")
print("="*70)
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

# Calculate actual flicker frequency for TARGET
if len(target_switches) > 1:
    switch_intervals = np.diff(target_switches)
    mean_switch_interval = np.mean(switch_intervals)
    actual_target_freq = 1.0 / mean_switch_interval
    print(f"\n{'='*70}")
    print(f"TARGET (GREEN/MAGENTA GRATING, 9 o'clock):")
    print(f"  Color switches detected: {len(target_switches)}")
    print(f"  Actual flicker frequency: {actual_target_freq:.1f} Hz")
    print(f"  Expected: {TARGET_FLICKER_FREQUENCY} Hz")
    match = abs(actual_target_freq - TARGET_FLICKER_FREQUENCY) < 2
    print(f"  Match: {'✓ YES' if match else '✗ NO'}")

# Calculate actual flicker frequency for DISTRACTOR
if len(distractor_switches) > 1:
    switch_intervals = np.diff(distractor_switches)
    mean_switch_interval = np.mean(switch_intervals)
    actual_distractor_freq = 1.0 / mean_switch_interval
    print(f"\n{'='*70}")
    print(f"DISTRACTOR (RED/CYAN GRATING, 3 o'clock):")
    print(f"  Color switches detected: {len(distractor_switches)}")
    print(f"  Actual flicker frequency: {actual_distractor_freq:.1f} Hz")
    print(f"  Expected: {DISTRACTOR_FLICKER_FREQUENCY} Hz")
    match = abs(actual_distractor_freq - DISTRACTOR_FLICKER_FREQUENCY) < 2
    print(f"  Match: {'✓ YES' if match else '✗ NO'}")

print(f"\n{'='*70}\n")

win.close()
core.quit()
