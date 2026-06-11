def create_tts(provider: str = "mimic3", **kwargs):
    if provider == "mimic3":
        from services.voice.tts.mimic3_tts import Mimic3TTS
        return Mimic3TTS(
            default_voice=kwargs.get("default_voice", "es_ES"),
            speed=kwargs.get("speed", 1.0)
        )
    else:
        # Fallback a espeak-ng (por si acaso)
        from services.voice.tts.espeak_tts import EspeakTTS
        return EspeakTTS(
            default_voice=kwargs.get("default_voice", "es"),
            speed=kwargs.get("speed", 180),
            pitch=kwargs.get("pitch", 65)
        )
