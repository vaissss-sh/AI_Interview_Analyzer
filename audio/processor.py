import whisper
import time

class AudioTranscriber:
    def __init__(self, model_size="base"):
        # We assume Streamlit will handle the caching of this model instance
        # but the actual loading happens dynamically or via app.py
        self.model = whisper.load_model(model_size)
        
    def transcribe(self, audio_path):
        """
        Transcribes the audio file and extracts word-level timestamps.
        Calculates WPM and Hesitation Gaps (> 1.5s).
        """
        result = self.model.transcribe(audio_path, word_timestamps=True)
        
        transcript = result.get("text", "").strip()
        words_data = []
        for segment in result.get("segments", []):
            for word in segment.get("words", []):
                words_data.append(word)
                
        # Calculate WPM
        total_words = len(words_data)
        if total_words > 0:
            duration_minutes = words_data[-1]["end"] / 60.0
            wpm = total_words / duration_minutes if duration_minutes > 0 else 0
        else:
            wpm = 0.0
            
        # Calculate Hesitation gaps
        hesitation_pauses_seconds = 0.0
        for i in range(1, len(words_data)):
            prev_word = words_data[i-1]
            curr_word = words_data[i]
            
            gap = curr_word["start"] - prev_word["end"]
            if gap > 1.5:
                hesitation_pauses_seconds += gap
                
        return {
            "transcript": transcript,
            "wpm": wpm,
            "pauses_seconds": hesitation_pauses_seconds,
            "words": words_data
        }
