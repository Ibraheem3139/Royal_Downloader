import os
import re
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pytube import Playlist
import threading
import queue
from pytube import YouTube

# Function to download a single video with a numbered prefix
def download_video(video_url, folder_name, result_queue, index):
    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        video_filename = "{:02d}. {}.mp4".format(index + 1, re.sub(r'[\/:*?\"<>|]', '', yt.title))
        save_path = os.path.join(folder_name, video_filename)
        stream.download(output_path=folder_name, filename=video_filename)
        result_queue.put(video_filename)
    except Exception as e:
        result_queue.put(None)

# Function to download the entire playlist with numbered videos
def download_playlist(playlist, folder_name, result_queue):
    # Download each video in the playlist with a numbered prefix
    for index, video_url in enumerate(playlist.video_urls):
        download_video(video_url, folder_name, result_queue, index)

# Function to check download progress and update the progress bar
def check_download_progress(result_queue, folder_name, total_videos):
    completed_videos = 0

    while completed_videos < total_videos:
        video_filename = result_queue.get()
        if video_filename is not None:
            completed_videos += 1
            progress_var.set(completed_videos * 100 // total_videos)
        if completed_videos == total_videos:
            messagebox.showinfo("Download Complete", "Playlist download is complete!")
            break

# Function to handle playlist download
def handle_download():
    playlist_url = entry.get()
    try:
        playlist = Playlist(playlist_url)
        total_videos = len(playlist.video_urls)
        playlist_title = re.sub(r'[\/:*?"<>|]', '', playlist.title)
        folder_name = playlist_title.replace(' ', '_')
        os.makedirs(folder_name, exist_ok=True)

        result_queue = queue.Queue()

        # Create a separate thread for downloading videos
        download_thread = threading.Thread(target=download_playlist, args=(playlist, folder_name, result_queue))
        download_thread.start()

        # Create a thread to check download progress
        progress_thread = threading.Thread(target=check_download_progress, args=(result_queue, folder_name, total_videos))
        progress_thread.start()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create a GUI window
root = tk.Tk()
root.title("Royal Downloader")

# Create a label indicating "Royal Downloader" as a title (bold and in Times New Roman)
title_label = tk.Label(root, text="Royal Downloader", font=("Times New Roman", 16, "bold"))
title_label.pack(pady=10)  # Add vertical space (10 pixels) below the title

# Create a label indicating to enter the playlist URL
instruction_label = tk.Label(root, text="Enter the YouTube Playlist URL below:")
instruction_label.pack()

# Create an entry field for URL
entry = tk.Entry(root, width=60)
entry.pack()
# ...
# Create a download button
download_button = tk.Button(root, text="Download Playlist", command=handle_download)
download_button.pack(pady=20)  # Add padding (20 pixels) to create space between the button and the progress bar

# Create a progress bar with a longer length
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=300)  # Adjust the length as needed
progress_bar.pack()

# Start the GUI main loop
root.mainloop()
