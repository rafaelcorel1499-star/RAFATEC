"""Anuncia los pagos por el altavoz (voz de Windows, sin internet)."""
from __future__ import annotations

import logging
import os
import queue
import subprocess
import sys
import threading

log = logging.getLogger("nequipay")


class VoiceAnnouncer:
    def __init__(self, volume_percent: int = 75):
        self.volume = max(0, min(100, volume_percent)) / 100
        self._q: "queue.Queue[str | None]" = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def set_volume(self, percent: int):
        self.volume = max(0, min(100, percent)) / 100

    def speak(self, text: str):
        self._q.put(text)

    def stop(self):
        self._q.put(None)

    def _run(self):
        try:  # COM para este hilo (necesario para SAPI en Windows)
            import comtypes
            comtypes.CoInitialize()
        except Exception:
            pass
        while True:
            text = self._q.get()
            if text is None:
                break
            try:
                self._say_pyttsx3(text)
            except Exception as exc:
                log.warning("pyttsx3 falló (%s); usando PowerShell", exc)
                try:
                    self._say_powershell(text)
                except Exception as exc2:
                    log.error("No se pudo reproducir la voz: %s", exc2)

    def _say_pyttsx3(self, text: str):
        import pyttsx3
        engine = pyttsx3.init()
        try:
            for v in engine.getProperty("voices"):
                blob = f"{v.name} {v.id}".lower()
                if any(k in blob for k in ("spanish", "español", "es-co", "es-mx", "es-es", "es-us",
                                           "sabina", "helena", "pablo", "laura", "raul", "dalia", "jorge")):
                    engine.setProperty("voice", v.id)
                    break
            engine.setProperty("volume", self.volume)
            engine.setProperty("rate", 165)
            engine.say(text)
            engine.runAndWait()
        finally:
            try:
                engine.stop()
            except Exception:
                pass

    def _say_powershell(self, text: str):
        # El texto va por variable de entorno (nunca dentro del script) -> sin inyección
        script = (
            "Add-Type -AssemblyName System.Speech;"
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            f"$s.Volume = {int(self.volume * 100)};"
            "try { $s.SelectVoiceByHints('NotSet','NotSet',0,[Globalization.CultureInfo]'es-CO') } catch {};"
            "$s.Speak($env:NEQUI_TEXT)"
        )
        env = dict(os.environ, NEQUI_TEXT=text)
        flags = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW
        subprocess.run(["powershell", "-NoProfile", "-Command", script], env=env,
                       creationflags=flags, timeout=30, check=False)
