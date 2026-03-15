try:
    from deepface import DeepFace
    import numpy as np
    dummy = np.zeros((48,48,3), dtype=np.uint8)
    res = DeepFace.analyze(dummy, actions=['emotion'], enforce_detection=False, silent=True)
    print('DeepFace Success:', res)
except Exception as e:
    import traceback
    traceback.print_exc()
