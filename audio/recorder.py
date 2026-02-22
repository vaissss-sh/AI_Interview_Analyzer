import pyaudio
import wave
import threading
import time
import os

class AudioRecorder(threading.Thread):
    def __init__(self, controller, output_filename="temp_audio.wav"):
        super().__init__()
        self.controller = controller
        self.output_filename = output_filename
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000 # 16kHz is suitable for Whisper
        self.frames = []
        
    def run(self):
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(format=self.format,
                            channels=self.channels,
                            rate=self.rate,
                            input=True,
                            frames_per_buffer=self.chunk)
            
            self.frames = []
            
            # Wait for the record event to be set
            while self.controller.record_event.is_set():
                data = stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
                
            # Stop and close the stream 
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save audio if frames exist
            if len(self.frames) > 0:
                self.save_audio()
            else:
                print("Warning: No audio frames captured!")
                
        except Exception as e:
            print(f"Audio recording error: {e}")
            p.terminate()
            
    def save_audio(self):
        wf = wave.open(self.output_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
