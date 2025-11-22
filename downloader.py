import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, ttk # Added ttk for Combobox
import subprocess
import sys
import os
import importlib.util
//smk
# --- 1. Automated Dependency Check and Installation ---

REQUIRED_LIBRARIES = ['yt-dlp']
FFMPEG_URL = "https://ffmpeg.org/download.html" # Link for user info

def install_missing_libraries(libraries):
    """Checks for and installs missing Python libraries using pip."""
    missing = []
    for lib in libraries:
        # Check if the module is importable
        if importlib.util.find_spec(lib) is None:
            missing.append(lib)
    
    if not missing:
        return True, "All required Python libraries are installed."

    # Installation attempt
    try:
        pip_command = [sys.executable, "-m", "pip", "install"] + missing
        subprocess.check_call(pip_command, 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True)
        return True, f"Successfully installed: {', '.join(missing)}"
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to install libraries: {', '.join(missing)}. Error: {e.stderr.strip()}"
        return False, error_msg
    except Exception as e:
        return False, f"An unexpected error occurred during installation: {e}"

# --- 2. Main Application Class with GUI (Tkinter) ---

class VideoDownloaderGUI:
    # Define quality options for the dropdown and their corresponding yt-dlp format strings
    QUALITY_OPTIONS = {
        "Best Available (Requires FFmpeg)": 'bestvideo+bestaudio/best',
        "High (1080p if available)": 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        "Medium (720p)": 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        "Standard (480p)": 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        "Audio Only (MP3)": 'bestaudio/best',
    }

    def __init__(self, master):
        self.master = master
        master.title(" yt-dlp GUI Downloader")
        master.geometry("600x500") # Increased size for new controls

        # Variables
        self.url_var = tk.StringVar()
        self.path_var = tk.StringVar(value=os.path.join(os.getcwd(), 'downloads'))
        self.quality_var = tk.StringVar(value=list(self.QUALITY_OPTIONS.keys())[0]) # Default to "Best Available"
        
        # Check and Install Libraries
        success, message = install_missing_libraries(REQUIRED_LIBRARIES)
        self.setup_complete = success
        
        self.create_widgets()
        self.log_message(f"SETUP STATUS: {message}")
        if not self.setup_complete:
            messagebox.showerror("Setup Failed", message + "\nPlease restart the application after fixing the issue.")

    def create_widgets(self):
        # --- Input Frame ---
        input_frame = tk.Frame(self.master, padx=10, pady=10)
        input_frame.pack(fill='x')

        # URL Label and Entry
        tk.Label(input_frame, text="Video URL:").grid(row=0, column=0, sticky='w', pady=5)
        url_entry = tk.Entry(input_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=0, column=1, padx=5, sticky='ew', columnspan=2)

        # Output Path Label and Entry/Button
        tk.Label(input_frame, text="Save To:").grid(row=1, column=0, sticky='w', pady=5)
        path_entry = tk.Entry(input_frame, textvariable=self.path_var, width=40, state='readonly')
        path_entry.grid(row=1, column=1, padx=5, sticky='ew')
        tk.Button(input_frame, text="Browse", command=self.browse_path).grid(row=1, column=2, sticky='e')

        # --- NEW: Quality Selection ---
        tk.Label(input_frame, text="Quality:").grid(row=2, column=0, sticky='w', pady=5)
        quality_combobox = ttk.Combobox(
            input_frame, 
            textvariable=self.quality_var, 
            values=list(self.QUALITY_OPTIONS.keys()),
            state='readonly',
            width=30
        )
        quality_combobox.grid(row=2, column=1, padx=5, sticky='ew', columnspan=2)
        
        # Download Button
        tk.Button(input_frame, text=" START DOWNLOAD ", command=self.start_download, 
                  state=tk.NORMAL if self.setup_complete else tk.DISABLED,
                  bg='#4CAF50', fg='white', font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=3, pady=15)

        # Configure grid column weights for resizing
        input_frame.grid_columnconfigure(1, weight=1)

        # --- Log Output Frame ---
        log_frame = tk.Frame(self.master, padx=10, pady=5)
        log_frame.pack(fill='both', expand=True)

        tk.Label(log_frame, text="Log/Status:").pack(anchor='w')
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True)

        # --- Footer ---
        footer_frame = tk.Frame(self.master, padx=10, pady=5)
        footer_frame.pack(fill='x')
        tk.Label(footer_frame, text=f"NOTE: Merging video/audio requires FFmpeg. Get it here: {FFMPEG_URL}", fg='gray').pack(anchor='w')


    def log_message(self, message):
        """Appends a message to the GUI log area."""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # Auto-scroll to the bottom
        self.log_text.config(state='disabled')
        self.master.update() # Force GUI refresh

    def browse_path(self):
        """Opens a directory selection dialog."""
        new_path = filedialog.askdirectory(initialdir=self.path_var.get())
        if new_path:
            self.path_var.set(new_path)

    def start_download(self):
        """Validates input and starts the download process."""
        video_url = self.url_var.get().strip()
        download_path = self.path_var.get().strip()
        selected_quality_name = self.quality_var.get()
        
        if not video_url:
            messagebox.showerror("Input Error", "Please enter a valid video URL.")
            return
        if not download_path:
            messagebox.showerror("Path Error", "Download path cannot be empty.")
            return

        # Create the directory if it doesn't exist
        os.makedirs(download_path, exist_ok=True)
        
        # Determine the yt-dlp format string based on user selection
        format_string = self.QUALITY_OPTIONS.get(selected_quality_name, self.QUALITY_OPTIONS["Best Available (Requires FFmpeg)"])

        # Simple non-threaded download execution (blocks GUI temporarily)
        self.log_message("\n--- Starting Download ---")
        self.log_message(f"URL: {video_url}")
        self.log_message(f"Destination: {download_path}")
        self.log_message(f"Selected Quality: {selected_quality_name} (Format: {format_string})")


        try:
            self.download_video_yt_dlp(video_url, download_path, format_string, selected_quality_name)
        except Exception as e:
            self.log_message(f"!!! CRITICAL ERROR: {e}")
            messagebox.showerror("Download Failed", f"An unexpected error occurred: {e}")

    def progress_hook_gui(self, d):
        """Progress hook updated for GUI logging."""
        if d['status'] == 'downloading':
            try:
                # Use _total_bytes_str for a more robust progress display
                total_size = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str', 'N/A')
                msg = f"Downloading: {d['_percent_str']} of {total_size} at {d['_speed_str']} - ETA: {d['_eta_str']}"
                
                # Overwrite the previous log line for a 'live' update effect
                self.log_text.config(state='normal')
                self.log_text.delete("end-2l", "end-1c") # Remove last line
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state='disabled')
                self.master.update()
            except Exception:
                # Fallback for initial stages or errors
                pass
        elif d['status'] == 'finished':
            # This status often reports the final step, like merging
            self.log_message(f"Download/Processing complete: {d.get('filename', 'Unknown File')}")
        elif d['status'] == 'error':
            self.log_message(f"ERROR: {d['error']}")

    def download_video_yt_dlp(self, video_url, download_path, format_string, selected_quality_name):
        """Performs the video download using yt-dlp with selected quality."""
        
        # Filename template is '%(title)s.%(ext)s' placed in the custom download_path
        output_path_template = os.path.join(download_path, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': format_string,                 # Uses the quality selected by the user
            'merge_output_format': 'mp4',            # Required for merging separate video/audio streams
            'outtmpl': output_path_template,
            'noplaylist': True,
            'progress_hooks': [self.progress_hook_gui], # Use the GUI hook
            'verbose': False,
            'ignoreerrors': False,
            'no_warnings': True,
        }
        
        # If 'Audio Only' is selected, change the merge format to mp3 or m4a
        if "Audio Only" in selected_quality_name:
            # Tell yt-dlp to extract the audio and convert it to mp3
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', # High quality
            }]
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['merge_output_format'] = None # No merging needed, just extraction

        try:
            self.log_message(f"Starting download with format: {format_string}...")
            if "Audio Only" not in selected_quality_name:
                self.log_message("Checking for FFmpeg to merge video/audio...")
            
            # The download is performed here
            import yt_dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            self.log_message("\n*** Download and Processing Finished Successfully! ***")

        except yt_dlp.DownloadError as e:
            error_msg = str(e)
            if ("requested format" in error_msg.lower() and "ffmpeg" in error_msg.lower()) or "no such file or directory" in error_msg.lower() and "ffmpeg" in error_msg.lower():
                self.log_message("\n!!! ERROR: Download failed, likely because **FFmpeg is not installed or not in PATH**.")
                self.log_message("FFmpeg is required for merging high-quality video/audio or for audio conversion.")
                self.log_message(f"Get FFmpeg here: {FFMPEG_URL}")
                messagebox.showerror("Download Error (FFmpeg Missing)", "Download failed. Please check the log for FFmpeg installation details.")
            else:
                self.log_message(f"\n!!! An error occurred during download: {error_msg}")
                messagebox.showerror("Download Error", "A yt-dlp download error occurred. Check the log for details.")
        except Exception as e:
            self.log_message(f"\n!!! An unexpected error occurred: {e}")
            messagebox.showerror("General Error", f"An unexpected error occurred: {e}")


# --- 3. Execution Block ---

if __name__ == "__main__":
    # Check for Tkinter availability
    try:
        root = tk.Tk()
        app = VideoDownloaderGUI(root)
        root.mainloop()
    except tk.TclError:
        print("--- Tkinter Error ---")
        print("It looks like Tkinter (the GUI library) is not available in your Python environment.")
        print("On some systems (like Linux), you may need to install it manually (e.g., 'sudo apt install python3-tk').")
        # Proceed with library install check only
        install_missing_libraries(REQUIRED_LIBRARIES)
