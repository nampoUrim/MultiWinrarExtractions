
from pathlib import Path
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import queue


# ==============================
# EXTRACTION FUNCTIONS
# ==============================

def find_winrar():
    # Check the default WinRAR installation path
    directory = Path("C:/Program Files") / "WinRAR" / "WinRAR.exe"

    if directory.exists():
        return directory
    return None


def find_archives(folder):
    # Find supported archive formats in the selected folder
    for item in folder.iterdir():
        if item.is_file() and item.suffix.lower() in [".zip", ".rar", ".7z"]:
            yield item


def extract_archive(archive_path, winrar_path):
    # Create an output folder using the archive's name
    output_folder = archive_path.parent / archive_path.stem

    # Skip extraction if the output folder already exists
    if output_folder.exists():
        return None

    try:
        output_folder.mkdir(parents=True)

        # Build the WinRAR extraction command
        command = [
            str(winrar_path),
            "x",
            "-y",
            "-o-",
            str(archive_path),
            str(output_folder) + "\\"
        ]

        # Run WinRAR and retrieve its exit code
        result = subprocess.run(command, check=False)

        if result.returncode == 0:
            return True
        return False

    except OSError:
        return False


# ==============================
# GRAPHICAL INTERFACE
# ==============================

class ArchiveExtractor:

    def __init__(self, root):
        self.root = root
        self.root.title("Archive Extractor")
        self.root.geometry("650x520")
        self.root.minsize(550, 450)

        # Initialize application settings
        self.winrar_path = find_winrar()
        self.selected_folder = None

        # Queue used to communicate with the main thread
        self.progress_queue = queue.Queue()

        # Extraction statistics
        self.success_count = 0
        self.failure_count = 0
        self.skipped_count = 0

        self.create_widgets()

        # Close the application if WinRAR is not installed
        if not self.winrar_path:
            messagebox.showerror(
                "WinRAR not found",
                "WinRAR is not installed in the default location."
            )
            self.root.after(100, self.root.destroy)

    def create_widgets(self):

        # Main container
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Application title
        title = ttk.Label(
            main_frame,
            text="Archive Extractor",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(pady=(0, 20))

        # Folder selection section
        folder_frame = ttk.LabelFrame(
            main_frame,
            text="Select archive folder",
            padding=10
        )
        folder_frame.pack(fill="x", pady=5)

        self.folder_label = ttk.Label(
            folder_frame,
            text="No folder selected",
            wraplength=430
        )
        self.folder_label.pack(side="left", fill="x", expand=True, padx=5)

        self.browse_button = ttk.Button(
            folder_frame,
            text="Browse",
            command=self.select_folder
        )
        self.browse_button.pack(side="right")

        # Start extraction button
        self.start_button = ttk.Button(
            main_frame,
            text="Start Extraction",
            command=self.start_extraction
        )
        self.start_button.pack(pady=15)

        # Extraction progress section
        progress_frame = ttk.LabelFrame(
            main_frame,
            text="Extraction Progress",
            padding=10
        )
        progress_frame.pack(fill="x", pady=5)

        self.progress_label = ttk.Label(
            progress_frame,
            text="Waiting..."
        )
        self.progress_label.pack(anchor="w", pady=5)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100
        )
        self.progress_bar.pack(fill="x", pady=5)

        self.percentage_label = ttk.Label(
            progress_frame,
            text="0%"
        )
        self.percentage_label.pack(anchor="e")

        # Extraction statistics section
        stats_frame = ttk.LabelFrame(
            main_frame,
            text="Extraction Summary",
            padding=10
        )
        stats_frame.pack(fill="x", pady=10)

        self.success_label = ttk.Label(
            stats_frame,
            text="Successful: 0"
        )
        self.success_label.pack(side="left", expand=True)

        self.failure_label = ttk.Label(
            stats_frame,
            text="Failed: 0"
        )
        self.failure_label.pack(side="left", expand=True)

        self.skipped_label = ttk.Label(
            stats_frame,
            text="Skipped: 0"
        )
        self.skipped_label.pack(side="left", expand=True)

        # Activity log section
        log_frame = ttk.LabelFrame(
            main_frame,
            text="Activity Log",
            padding=10
        )
        log_frame.pack(fill="both", expand=True, pady=5)

        self.log_text = tk.Text(
            log_frame,
            height=8,
            state="disabled",
            wrap="word",
            font=("Consolas", 9)
        )
        self.log_text.pack(fill="both", expand=True)

    # ==============================
    # INTERFACE METHODS
    # ==============================

    def log(self, message):
        # Temporarily enable the text widget to insert a message
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def select_folder(self):

        # Open the folder selection dialog
        folder = filedialog.askdirectory(
            title="Select folder containing archives"
        )

        if folder:
            self.selected_folder = Path(folder)
            self.folder_label.config(text=str(self.selected_folder))

            self.log(f"Selected folder: {folder}")

    def start_extraction(self):

        # Check whether a folder has been selected
        if not self.selected_folder:
            messagebox.showwarning(
                "No folder selected",
                "Please select a folder first."
            )
            return

        # Check whether the selected folder still exists
        if not self.selected_folder.exists():
            messagebox.showerror(
                "Invalid folder",
                "The selected folder no longer exists."
            )
            return

        # Collect all supported archives
        archives = list(find_archives(self.selected_folder))

        if not archives:
            messagebox.showinfo(
                "No archives",
                "No ZIP, RAR or 7Z archives were found in this folder."
            )
            return

        # Reset statistics before starting a new extraction
        self.success_count = 0
        self.failure_count = 0
        self.skipped_count = 0

        self.progress_bar["value"] = 0
        self.percentage_label.config(text="0%")

        self.success_label.config(text="Successful: 0")
        self.failure_label.config(text="Failed: 0")
        self.skipped_label.config(text="Skipped: 0")

        # Prevent new actions during extraction
        self.start_button.config(state="disabled")
        self.browse_button.config(state="disabled")

        self.progress_label.config(text="Extraction in progress...")

        self.log(f"Found {len(archives)} archive(s).")

        # Run extraction in a separate thread
        worker = threading.Thread(
            target=self.extraction_worker,
            args=(archives,),
            daemon=True
        )
        worker.start()

        # Start checking for worker messages
        self.root.after(100, self.check_progress)

    # ==============================
    # EXTRACTION WORKER
    # ==============================

    def extraction_worker(self, archives):

        total = len(archives)

        for index, archive in enumerate(archives, start=1):

            # Notify the main thread about the current archive
            self.progress_queue.put(
                ("log", f"Extracting: {archive.name}")
            )

            result = extract_archive(
                archive,
                self.winrar_path
            )

            # Update the appropriate statistic
            if result is True:
                self.success_count += 1
                message = f"Successful: {archive.name}"

            elif result is False:
                self.failure_count += 1
                message = f"Failed: {archive.name}"

            else:
                self.skipped_count += 1
                message = f"Skipped: {archive.name}"

            # Send extraction results to the main thread
            self.progress_queue.put(
                ("result", (
                    index,
                    total,
                    self.success_count,
                    self.failure_count,
                    self.skipped_count,
                    message
                ))
            )

        # Notify the main thread that extraction is finished
        self.progress_queue.put(("finished", None))

    # ==============================
    # PROGRESS UPDATES
    # ==============================

    def check_progress(self):

        try:
            # Process all available messages in the queue
            while True:
                event, data = self.progress_queue.get_nowait()

                if event == "log":
                    self.log(data)

                elif event == "result":

                    (
                        current,
                        total,
                        success,
                        failure,
                        skipped,
                        message
                    ) = data

                    # Calculate extraction progress
                    percentage = current / total * 100

                    self.progress_bar["value"] = percentage
                    self.percentage_label.config(
                        text=f"{percentage:.0f}%"
                    )

                    self.progress_label.config(
                        text=f"Processed {current} / {total} archives"
                    )

                    # Update statistics displayed in the interface
                    self.success_label.config(
                        text=f"Successful: {success}"
                    )

                    self.failure_label.config(
                        text=f"Failed: {failure}"
                    )

                    self.skipped_label.config(
                        text=f"Skipped: {skipped}"
                    )

                    self.log(message)

                elif event == "finished":

                    # Re-enable buttons after extraction
                    self.start_button.config(state="normal")
                    self.browse_button.config(state="normal")

                    self.progress_label.config(
                        text="Extraction completed!"
                    )

                    self.log("All extraction tasks completed.")

                    # Display the final extraction summary
                    messagebox.showinfo(
                        "Extraction completed",
                        f"Successful: {self.success_count}\n"
                        f"Failed: {self.failure_count}\n"
                        f"Skipped: {self.skipped_count}"
                    )

                    return

        except queue.Empty:
            pass

        # Check the queue again after 100 milliseconds
        self.root.after(100, self.check_progress)


# ==============================
# APPLICATION ENTRY POINT
# ==============================

if __name__ == "__main__":

    # Create the main Tkinter window
    root = tk.Tk()

    # Initialize the application
    app = ArchiveExtractor(root)

    # Start the Tkinter event loop
    root.mainloop()
