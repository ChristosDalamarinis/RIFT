from psychopy import visual

win = visual.Window([1200, 900], fullscr=True)

# Try to measure
measured_rate = win.getActualFrameRate(nIdentical=60, nMaxFrames=240)

if measured_rate is None:
    print("❌ Auto-detection FAILED - using fallback")
    refresh_rate = 60.0 # Choose the refresh rate of the monitor if it cannot be measured
else:
    print(f"✓ Auto-detected: {measured_rate:.2f} Hz")
    refresh_rate = measured_rate

print(f"Using refresh rate: {refresh_rate} Hz")

win.close()
