import torch
import torchaudio

# Cargar el modelo español (v3 es la última)
device = torch.device('cpu')
model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                     model='silero_tts',
                                     language='es',
                                     speaker='es_0')
model.to(device)

# Texto a sintetizar
text = "Hola, soy FerdoNAN. Mi voz ahora es natural y completamente local."

# Generar audio
audio = model.apply_tts(text=text,
                         speaker='es_0',
                         sample_rate=48000)

# Guardar y reproducir
torchaudio.save('output.wav', audio.unsqueeze(0), 48000)
# Reproducir (necesitas aplay o similar)
import subprocess
subprocess.run(['aplay', 'output.wav'])
