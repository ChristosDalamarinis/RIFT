from psychopy import visual

win = visual.Window([1710, 1107], fullscr=False)

# Try to measure
measured_rate = win.getActualFrameRate(nIdentical=60, nMaxFrames=120)

if measured_rate is None:
    print("❌ Auto-detection FAILED - using fallback")
    refresh_rate = 60.0
else:
    print(f"✓ Auto-detected: {measured_rate:.2f} Hz")
    refresh_rate = measured_rate

print(f"Using refresh rate: {refresh_rate} Hz")

win.close()
