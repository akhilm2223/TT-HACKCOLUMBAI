try:
    import mediapipe.python.solutions.pose as mp_pose
    print("Found mp_pose via explicit import")
except ImportError as e:
    print("Explicit import failed:", e)

import mediapipe as mp
try:
    from mediapipe.python.solutions import pose
    print("Found pose via mediapipe.python.solutions")
except ImportError as e:
    print("Explicit import 2 failed:", e)
