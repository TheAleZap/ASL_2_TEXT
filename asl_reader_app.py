import tkinter as tk
import serial
import threading
import time
from tkinter import font, messagebox, ttk


class ASLReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ASL Reader")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Variables
        self.serial_port = None
        self.is_connected = False
        self.current_letter = ""
        self.current_phrase = ""
        self.running = False
        self.is_paused = False

        # Create fonts
        self.letter_font = font.Font(family="Helvetica", size=120, weight="bold")
        self.phrase_font = font.Font(family="Helvetica", size=24)
        self.button_font = font.Font(family="Helvetica", size=12)
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")

        # Create title frame
        self.title_frame = tk.Frame(root, bg="#f0f0f0")
        self.title_frame.pack(fill=tk.X, padx=20, pady=10)

        # Add title label
        self.title_label = tk.Label(self.title_frame,
                                    text="Mr. Mitten - Adapted ASL to Text",
                                    font=self.title_font,
                                    bg="#f0f0f0")
        self.title_label.pack(pady=5)

        # Create frames
        self.top_frame = tk.Frame(root, bg="#f0f0f0")
        self.top_frame.pack(fill=tk.X, padx=20, pady=10)

        self.letter_frame = tk.Frame(root, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.letter_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.phrase_frame = tk.Frame(root, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.phrase_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.bottom_frame = tk.Frame(root, bg="#f0f0f0")
        self.bottom_frame.pack(fill=tk.X, padx=20, pady=10)

        # Create widgets
        self.setup_connection_widgets()
        self.setup_letter_display()
        self.setup_phrase_display()
        self.setup_control_buttons()

        # Protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_connection_widgets(self):
        # Port selection
        tk.Label(self.top_frame, text="Port:", bg="#f0f0f0", font=self.button_font).pack(side=tk.LEFT, padx=5)

        # On macOS, ports typically start with /dev/cu.usbmodem or /dev/cu.usbserial
        self.port_var = tk.StringVar(value="/dev/cu.usbmodem")
        self.port_entry = tk.Entry(self.top_frame, textvariable=self.port_var, width=20, font=self.button_font)
        self.port_entry.pack(side=tk.LEFT, padx=5)

        # Baud rate selection
        tk.Label(self.top_frame, text="Baud Rate:", bg="#f0f0f0", font=self.button_font).pack(side=tk.LEFT, padx=5)

        self.baud_var = tk.StringVar(value="9600")
        self.baud_combo = ttk.Combobox(self.top_frame, textvariable=self.baud_var, width=10, font=self.button_font)
        self.baud_combo['values'] = ("9600", "19200", "38400", "57600", "115200")
        self.baud_combo.pack(side=tk.LEFT, padx=5)

        # Connect button
        self.connect_button = tk.Button(self.top_frame, text="Connect", command=self.toggle_connection,
                                        bg="#4caf50", fg="black", width=10, font=self.button_font)
        self.connect_button.pack(side=tk.LEFT, padx=10)

        # Pause/Resume button
        self.pause_button = tk.Button(self.top_frame, text="Pause", command=self.toggle_pause,
                                      bg="#2196f3", fg="black", width=10, font=self.button_font,
                                      state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=10)

        # Status indicator
        self.status_label = tk.Label(self.top_frame, text="Disconnected", fg="red", bg="#f0f0f0", font=self.button_font)
        self.status_label.pack(side=tk.LEFT, padx=10)

    def setup_letter_display(self):
        # Big letter display
        self.letter_label = tk.Label(self.letter_frame, text="", font=self.letter_font, bg="#ffffff")
        self.letter_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Letter instruction
        instruction = tk.Label(self.letter_frame, text="Current ASL Letter", font=self.button_font, bg="#ffffff")
        instruction.pack(side=tk.BOTTOM, pady=5)

    def setup_phrase_display(self):
        # Phrase display with scrollbar
        self.phrase_text = tk.Text(self.phrase_frame, wrap=tk.WORD, font=self.phrase_font,
                                   bg="#ffffff", height=3)
        self.phrase_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Make the text widget read-only
        self.phrase_text.config(state=tk.DISABLED)

        # Phrase instruction
        instruction = tk.Label(self.phrase_frame, text="Accumulated Phrase", font=self.button_font, bg="#ffffff")
        instruction.pack(side=tk.BOTTOM, pady=5)

    def setup_control_buttons(self):
        # Clear button
        self.clear_button = tk.Button(self.bottom_frame, text="Clear Phrase", command=self.clear_phrase,
                                      bg="#ff9800", fg="black", width=15, font=self.button_font)
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # Space button
        self.space_button = tk.Button(self.bottom_frame, text="Add Space", command=self.add_space,
                                      bg="#2196f3", fg="black", width=15, font=self.button_font)
        self.space_button.pack(side=tk.LEFT, padx=10)

        # Backspace button
        self.backspace_button = tk.Button(self.bottom_frame, text="Backspace", command=self.backspace,
                                          bg="#f44336", fg="black", width=15, font=self.button_font)
        self.backspace_button.pack(side=tk.LEFT, padx=10)

        # Copy button
        self.copy_button = tk.Button(self.bottom_frame, text="Copy to Clipboard", command=self.copy_to_clipboard,
                                     bg="#673ab7", fg="black", width=15, font=self.button_font)
        self.copy_button.pack(side=tk.RIGHT, padx=10)

    def toggle_connection(self):
        if not self.is_connected:
            self.connect_to_arduino()
        else:
            self.disconnect_from_arduino()

    def toggle_pause(self):
        if not self.is_paused:
            self.is_paused = True
            self.pause_button.config(text="Resume", bg="#8bc34a")
        else:
            self.is_paused = False
            self.pause_button.config(text="Pause", bg="#2196f3")

    def connect_to_arduino(self):
        port = self.port_var.get()
        baud_rate = int(self.baud_var.get())

        try:
            self.serial_port = serial.Serial(port, baud_rate, timeout=1)
            self.is_connected = True
            self.running = True
            self.is_paused = False

            # Update UI
            self.connect_button.config(text="Disconnect", bg="#f44336")
            self.status_label.config(text="Connected", fg="green")
            self.pause_button.config(state=tk.NORMAL, text="Pause", bg="#2196f3")

            # Start reading thread
            self.read_thread = threading.Thread(target=self.read_serial_data)
            self.read_thread.daemon = True
            self.read_thread.start()

        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to Arduino: {str(e)}")

    def disconnect_from_arduino(self):
        if self.serial_port and self.serial_port.is_open:
            self.running = False
            time.sleep(0.5)  # Give the read thread time to exit
            self.serial_port.close()

        self.is_connected = False
        self.connect_button.config(text="Connect", bg="#4caf50")
        self.status_label.config(text="Disconnected", fg="red")
        self.pause_button.config(state=tk.DISABLED)

    def read_serial_data(self):
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0 and not self.is_paused:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line and len(line) > 0:
                        if line != "No match found":
                            self.update_letter(line)
            except Exception as e:
                print(f"Error reading serial data: {str(e)}")
                break
            time.sleep(0.1)

    def update_letter(self, letter):
        # Update UI in the main thread
        self.root.after(0, lambda: self._update_ui(letter))

    def _update_ui(self, letter):
        # Update the current letter display
        self.current_letter = letter

        # Adjust font size based on length of the letter/text
        if len(letter) > 1:
            # Calculate an appropriate font size based on length
            # More characters = smaller font
            new_size = max(30, int(120 / len(letter)))
            self.letter_label.config(font=font.Font(family="Helvetica", size=new_size, weight="bold"))
        else:
            # Reset to default large font for single letters
            self.letter_label.config(font=self.letter_font)

        # Update the display
        self.letter_label.config(text=letter)

        # Handle special case for underscore as space
        if letter == "_":
            self.current_phrase += " "
            self.phrase_text.config(state=tk.NORMAL)
            self.phrase_text.delete(1.0, tk.END)
            self.phrase_text.insert(tk.END, self.current_phrase)
            self.phrase_text.config(state=tk.DISABLED)
        # Append to the phrase if it's a valid single letter
        elif letter and len(letter) == 1:
            self.current_phrase += letter

            # Update the phrase display
            self.phrase_text.config(state=tk.NORMAL)
            self.phrase_text.delete(1.0, tk.END)
            self.phrase_text.insert(tk.END, self.current_phrase)
            self.phrase_text.config(state=tk.DISABLED)

    def clear_phrase(self):
        self.current_phrase = ""
        self.phrase_text.config(state=tk.NORMAL)
        self.phrase_text.delete(1.0, tk.END)
        self.phrase_text.config(state=tk.DISABLED)

    def add_space(self):
        self.current_phrase += " "
        self.phrase_text.config(state=tk.NORMAL)
        self.phrase_text.delete(1.0, tk.END)
        self.phrase_text.insert(tk.END, self.current_phrase)
        self.phrase_text.config(state=tk.DISABLED)

    def backspace(self):
        if self.current_phrase:
            self.current_phrase = self.current_phrase[:-1]
            self.phrase_text.config(state=tk.NORMAL)
            self.phrase_text.delete(1.0, tk.END)
            self.phrase_text.insert(tk.END, self.current_phrase)
            self.phrase_text.config(state=tk.DISABLED)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_phrase)
        messagebox.showinfo("Copied", "Text copied to clipboard!")

    def on_closing(self):
        if self.is_connected:
            self.disconnect_from_arduino()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ASLReaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()