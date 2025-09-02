# qBittorrent Automatic Media Sorter

A simple but powerful Python script that automatically sorts your completed qBittorrent downloads into designated movie and TV show folders, keeping your media library clean and organized.
Features

    Intelligent Categorization: Uses regular expressions to identify movies, single TV episodes, and full TV season packs from the torrent name.

    Flexible Content Handling: Correctly processes both single-file torrents and torrents that contain a folder.

    Smart Extraction: For movies or single episodes within a folder, it finds the main video file, moves it, and cleans up the original empty folder.

    Season Pack Renaming: Moves and renames full season pack folders to a clean format (e.g., Some Show/Season 3).

    Detailed Logging: Creates a log file (sorter_log.txt) to record all its actions, making troubleshooting simple.

    Customizable: Easily configure your source and destination folders at the top of the script.

Requirements

    Python 3 installed on your system.

    qBittorrent.

1. Script Configuration

Before using the script, you must edit the configuration section at the top of qbittorrent_sorter.py to match your system's folder structure.

Open qbittorrent_sorter.py in a text editor and modify the following paths:

# --- CONFIGURATION ---
# IMPORTANT: EDIT THESE PATHS TO MATCH YOUR FOLDER STRUCTURE
# Use forward slashes '/' even on Windows.

# The directory where qBittorrent places completed downloads.
DOWNLOADS_DIR = "C:/Users/YourUser/Downloads/Completed"

# The root directory for your movie library.
MOVIES_DIR = "D:/Media/Movies"

# The root directory for your TV show library.
TV_SHOWS_DIR = "D:/Media/TV Shows"

# A folder for anything that couldn't be categorized.
UNSORTED_DIR = "D:/Media/Unsorted"

# The location for the log file. A good place is near your downloads.
LOG_FILE = "C:/Users/YourUser/Downloads/sorter_log.txt"

2. qBittorrent Setup

Next, configure qBittorrent to run the script automatically when a download finishes.

    In qBittorrent, go to Tools -> Options... (or Alt+O).

    Select the Downloads tab on the left.

    Scroll down to the section "Run external program on torrent completion".

    Check the box to enable it.

    In the text box, enter the command to run the script. The command must include the full path to your Python executable and the script, followed by the qBittorrent arguments "%N" and "%F".

    The command format is: full/path/to/python.exe "full/path/to/your/script.py" "%N" "%F"

    What the arguments mean:

        %N: Passes the name of the torrent.

        %F: Passes the full path to the downloaded file or folder.

    Example (Windows):

    "C:/Python39/python.exe" "D:/Scripts/qbittorrent_sorter.py" "%N" "%F"

    Example (Linux/macOS):

    /usr/bin/python3 "/home/user/scripts/qbittorrent_sorter.py" "%N" "%F"

    Note: Remember to use quotes around the paths to handle any spaces.

    Click Apply and OK.

3. Testing & Troubleshooting

It is highly recommended to test the script manually before letting qBittorrent run it automatically.
Manual Test

    Create some fake test files and folders in a temporary directory (e.g., C:/Temp/test_downloads).

    Open a command prompt or terminal.

    Run the script with pretend torrent info:

    python qbittorrent_sorter.py "My.Movie.2023.1080p" "C:/Temp/test_downloads/My.Movie.2023.1080p"

    Check your media folders to see if the files were moved correctly.

Troubleshooting

If a download finishes but isn't sorted, your first step is to check the log file (sorter_log.txt at the path you configured). It will tell you:

    When the script started.

    What torrent it tried to process.

    How it categorized the media.

    The source and destination paths.

    Any errors that occurred during the process.

Common issues are incorrect paths in the script's configuration or a mistake in the command entered into qBittorrent.