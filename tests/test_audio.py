import pytest
import os
import wave
from utils.config import TEMP_DIR, SAMPLE_RATE
from audio.processor import detect_filler_words

@pytest.fixture
def dummy_wav():
    """Fixture to create and return a path to a dummy 1-second WAV file."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    path = os.path.join(TEMP_DIR, "test_dummy.wav")
    
    # Create empty wave
    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2) # 16-bit
    wf.setframerate(SAMPLE_RATE)
    # Write 1 second of silence
    wf.writeframes(b'\x00' * (SAMPLE_RATE * 2))
    wf.close()
    
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)

def test_detect_filler_words():
    """Test the static filler word regex function."""
    text = "Um, I think that basically, like, you know, we should literally do this."
    counts = detect_filler_words(text)
    
    assert counts.get("um") == 1
    assert counts.get("basically") == 1
    assert counts.get("like") == 1
    assert counts.get("you know") == 1
    assert counts.get("literally") == 1
    assert "uh" not in counts
    
    text2 = "No fillers here at all."
    assert len(detect_filler_words(text2)) == 0

def test_silence_ratio_with_dummy(dummy_wav):
    """Test the librosa silence ratio against pure silence."""
    from audio.processor import get_silence_ratio
    # Should be entirely silent
    ratio = get_silence_ratio(dummy_wav)
    assert ratio >= 0.99
