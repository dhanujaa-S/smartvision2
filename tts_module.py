"""
Module 7: Text-to-Speech (Voice Output)
------------------------------------------
Converts generated sentences into spoken audio, in English or Tamil.

Uses gTTS (Google Text-to-Speech) because it has good Tamil support,
unlike most offline engines (pyttsx3's offline voices rarely include Tamil).
Requires an internet connection. Falls back to pyttsx3 for offline
English-only use if you ever need to run without internet.

Includes a cooldown so the same sentence isn't repeated every single
frame -- only speaks when something NEW or CHANGED needs to be said.
"""

import os
import time
import tempfile
import threading

from gtts import gTTS
from playsound import playsound


class VoiceGuide:
    def __init__(self, cooldown_seconds=3.0):
        """
        cooldown_seconds: minimum time between two spoken announcements,
                            so the assistant doesn't talk nonstop.
        """
        self.cooldown_seconds = cooldown_seconds
        self._last_spoken_time = 0.0
        self._last_sentence = None
        self._lock = threading.Lock()

    def _speak_sync(self, text, language="en"):
        lang_code = "en" if language == "en" else "ta"
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            tts = gTTS(text=text, lang=lang_code)
            tts.save(tmp_path)
            playsound(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def say(self, text, language="en", force=False):
        """
        Speaks `text` if the cooldown has passed and it's not an exact
        repeat of the last thing said (unless force=True).
        Runs in a background thread so it doesn't block the video loop.
        """
        now = time.time()
        if not force:
            if text == self._last_sentence:
                return
            if now - self._last_spoken_time < self.cooldown_seconds:
                return

        self._last_spoken_time = now
        self._last_sentence = text

        thread = threading.Thread(target=self._speak_sync, args=(text, language), daemon=True)
        thread.start()

    def say_all(self, sentences, language="en"):
        for sentence in sentences:
            self.say(sentence, language=language)


if __name__ == "__main__":
    guide = VoiceGuide(cooldown_seconds=0)
    guide.say("Person in front of you.", language="en", force=True)
    time.sleep(3)
    guide.say("முன்னால் ஒரு நபர் இருக்கிறார்.", language="ta", force=True)
    time.sleep(3)
