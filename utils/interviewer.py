import os
import time
from gtts import gTTS
import pygame

class Interviewer:
    def __init__(self):
        self.questions = [
            "Welcome! To start us off, could you tell me a little bit about yourself and your background?",
            "What would you say is your greatest professional strength, and how have you used it recently?",
            "Tell me about a time you faced a significant challenge at work. How did you overcome it?",
            "Where do you see your career heading in the next three to five years?",
            "Finally, why are you interested in this position, and what unique value can you bring to the team?"
        ]
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

    def get_question(self, index):
        if 0 <= index < len(self.questions):
            return self.questions[index]
        return None

    def ask_question(self, index, controller):
        """
        Generates TTS for the question, plays it, 
        and then triggers the recording session via the Controller.
        """
        question_text = self.get_question(index)
        if not question_text:
            return False
            
        # Generates TTS Audio File
        temp_audio_file = f"temp_q_{index}.mp3"
        tts = gTTS(text=question_text, lang='en', slow=False)
        tts.save(temp_audio_file)
        
        # Play the audio
        pygame.mixer.music.load(temp_audio_file)
        pygame.mixer.music.play()
        
        controller.update_state(is_speaking=True)
        
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        # Clean up pygame so we can delete the file later if needed
        pygame.mixer.music.unload()
        
        try:
            os.remove(temp_audio_file)
        except OSError:
            pass
            
        controller.update_state(is_speaking=False)
        return True
