import pyaudio
import wave
import os
import threading
from utils.config import SAMPLE_RATE, CHUNK_SIZE, TEMP_DIR

class AudioRecorder:
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.frames = []

    def get_audio_devices(self) -> list:
        """Returns a list of available input audio devices."""
        info = self.pa.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        devices = []
        for i in range(0, num_devices):
            if (self.pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                devices.append({
                    "id": i,
                    "name": self.pa.get_device_info_by_host_api_device_index(0, i).get('name')
                })
        return devices

    def save_audio(self, filepath: str, duration: int = None):
        """
        Saves the recorded frames to a WAV file.
        If duration is specified, limits saving to that duration from frames.
        """
        if not self.frames:
            return

        os.makedirs(os.path.dirname(filepath) or TEMP_DIR, exist_ok=True)
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLE_RATE)
        
        # Calculate exactly how many frames to write if duration is provided
        # 1 duration second = SAMPLE_RATE / CHUNK_SIZE chunks
        if duration:
            chunks_to_write = int((SAMPLE_RATE / CHUNK_SIZE) * duration)
            wf.writeframes(b''.join(self.frames[:chunks_to_write]))
        else:
            wf.writeframes(b''.join(self.frames))
        wf.close()

    def record_stream(self, device_index=None):
        """Generator that starts recording and yields audio chunks in real-time."""
        self.is_recording = True
        self.frames = []
        try:
            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK_SIZE
            )
            while self.is_recording:
                data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                self.frames.append(data)
                yield data
        except Exception as e:
            print(f"Error recording stream: {e}")
        finally:
            self.stop_recording()

    def stop_recording(self):
        """Stops an active recording stream."""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

# Global instance for easy access if needed
recorder = AudioRecorder()

def save_audio(filepath: str, duration: int = None):
    recorder.save_audio(filepath, duration)

def record_stream():
    return recorder.record_stream()

def stop_recording():
    recorder.stop_recording()

def get_audio_devices():
    return recorder.get_audio_devices()
