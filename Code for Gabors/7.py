""""
8 Gabor Patches Visual Task - Chromatic Opponent Flicker with Luminance & Saturation Control (g6.py)

Features:
8 Gabor patches in circular layout
- Green/Magenta opponent color flicker (averages to mid-gray)
- OPTIONAL luminance scaling that preserves fusion
- OPTIONAL saturation control that preserves fusion
- Independent smoothness control for 3 and 9 o'clock
- Orientation/tilt control for 3 and 9 o'clock
- Optimized for 60Hz flicker on 120Hz monitor
"""

# NOTE: THIS SCRIPT IS AN TERATION OF 6.PY - THE GOAL IN TO IMPROVE BUFFER EFFICIENCY AT 480Hz AND TAKE INTO ACCOUNT THE SINCE ARCHITECTURE OF FRAMES AND REFRASH RATE. 

from psychopy import visual, core, event
import numpy as np

# ========================= CONFIGURATION ========================

WINDOW_WIDTH = 1200 # 1920
WINDOW_HEIGHT = 900 # 1080

# Background color - Mid-gray for chromatic fusion
BACKGROUND_COLOR = [0.12, 0.12, 0.12]  # Mid-gray (same as t5.py)

REFRESH_RATE = 60  # Hz - CRITICAL: Must match your monitor's actual refresh rate











