import numpy as np
import sounddevice as sd
from plyer import notification
import tkinter as tk
from tkinter import ttk
import time
from playsound import playsound
import threading

#Global Variables

def get_max_loudness(duration=0.1, fs=44100):
    loudness_values = []
    min_db = -60  # Define silence as -60 dB
    max_db = 0    # Define max loudness as 0 dB
    # Record audio in chunks and calculate loudness
    for _ in range(int(duration * fs / 1024)):  # Process in 1024-sample chunks
        audio = sd.rec(1024, samplerate=fs, channels=1, dtype='float64')
        sd.wait()  # Wait until the recording is finished

        # Calculate the RMS value for the chunk
        rms = np.sqrt(np.mean(np.square(audio)))

        # Convert RMS to dB
        loudness = 20 * np.log10(rms) if rms > 0 else min_db
        normalized_loudness = np.clip((loudness - min_db) / (max_db - min_db) * 100, 0, 100)
        loudness_values.append(normalized_loudness)

    # Return the maximum loudness value
    max_loudness = max(loudness_values)
    return max_loudness

def create_ring():
    """Creates a fullscreen red ring window with a transparent center."""
    stroke = 20
    ring = tk.Tk()
    ring.attributes('-topmost', True)  # Always on top
    ring.attributes('-fullscreen', True)  # Make the window fullscreen
    ring.overrideredirect(True)  # Remove window decorations
    ring.wm_attributes('-transparentcolor','#4682B4')
    # Create a canvas that fills the window
    screen_width = ring.winfo_screenwidth()
    screen_height = ring.winfo_screenheight()
    canvas = tk.Canvas(ring, width=screen_width, height=screen_height)
    canvas.pack()

    # Draw a red rectangle to fill the entire canvas
    canvas.create_rectangle(0, 0, screen_width, screen_height, fill='#8B0000', outline='#8B0000')

    # Draw a transparent center (you can adjust the size of the transparent area)
    canvas.create_rectangle(
        0 + stroke, 0 + stroke, screen_width - stroke, screen_height - stroke,
        fill='#4682B4', outline='', width=5
    )

    ring.update()
    return ring

def play_sound(file_path):
    playsound(file_path)

def listen():
    ring = None
    while True:
        max_loudness = get_max_loudness()
        progress_float.set(max_loudness)
        if(max_loudness > scale_float.get()):
            if ring is None:  # Create the ring if it doesn't exist
                sound_thread = threading.Thread(target=play_sound, args=(sound_file,))
                ring = create_ring()               
                sound_thread.start()            
                print(f"Maximum Loudness: {max_loudness:.2f} dB")
                print("You are too loud!!")
            ring.deiconify()  # Show the ring
        else:
            if ring is not None:  # Hide the ring if it exists
                ring.withdraw()
                ring = None
        time.sleep(0.1)

# Example usage
if __name__ == "__main__":
    sound_file = 'shushhh.mp3'
    threshold = 80
    window = tk.Tk()
    window.title("ShushBot")
    scale_float = tk.DoubleVar(value = 80)
    scale = ttk.Scale(window, 
                      command = lambda value: print(scale_float.get()), 
                      from_= 0, 
                      to= 100,
                    variable= scale_float )
    scale.pack()
    progress_float = tk.DoubleVar(value=0)
    progress = ttk.Progressbar(window,
                               variable = progress_float,
                               maximum=  100)
    progress.pack()

    listen_thread = threading.Thread(target=listen)
    listen_thread.start()

    window.mainloop()
            

