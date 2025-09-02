import sys
import os
import re
import shutil
import logging

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

# The location for the log file. This is essential for troubleshooting.
LOG_FILE = "C:/Users/YourUser/Downloads/sorter_log.txt"

# List of video file extensions to look for when processing folders.
VIDEO_EXTENSIONS = ['.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv']


# --- LOGGING SETUP ---
# This helps with debugging. qBittorrent will run this script in the background,
# so print statements won't be visible. A log file is essential.
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# --- HELPER FUNCTIONS ---

def get_media_info(torrent_name):
    """
    Analyzes the torrent name to determine its category and destination path.
    Returns a tuple: (category, destination_path)
    Categories: 'episode', 'season_pack', 'movie', 'unclassified'
    """
    # 1. Check for single TV episode (e.g., S01E01, 1x01)
    tv_episode_pattern = re.compile(r'(.+?)[. _-][Ss](\d{1,2})[EeXx](\d{1,2})', re.IGNORECASE)
    episode_match = tv_episode_pattern.search(torrent_name)
    if episode_match:
        show_name = episode_match.group(1).replace('.', ' ').strip()
        season_number = int(episode_match.group(2))
        show_name = re.sub(r'\(\d{4}\)', '', show_name).strip()  # Clean up year
        logging.info(f"Detected TV Episode: {show_name}, Season: {season_number}")
        dest_path = os.path.join(TV_SHOWS_DIR, show_name, f"Season {season_number:02d}")
        return 'episode', dest_path

    # 2. Check for a full TV season pack (e.g., Season.01, S02)
    tv_season_pattern = re.compile(r'(.+?)[. _-]([Ss]eason[. _-]?)(\d{1,2})', re.IGNORECASE)
    season_match = tv_season_pattern.search(torrent_name)
    if season_match:
        show_name = season_match.group(1).replace('.', ' ').strip()
        season_number = int(season_match.group(3))  # Extract season number
        show_name = re.sub(r'\(\d{4}\)', '', show_name).strip()  # Clean up year
        logging.info(f"Detected TV Season Pack: {show_name}, Season: {season_number}")
        dest_path = os.path.join(TV_SHOWS_DIR, show_name, f"Season {season_number}")
        return 'season_pack', dest_path

    # 3. Check for a movie (often with a year)
    movie_pattern = re.compile(r'(.+?)[. _-](\d{4})', re.IGNORECASE)
    movie_match = movie_pattern.search(torrent_name)
    if movie_match:
        # Extra check to avoid misclassifying TV shows that have a year
        if 'season' not in torrent_name.lower() and 'episode' not in torrent_name.lower():
            movie_title = movie_match.group(1).replace('.', ' ').strip()
            year = movie_match.group(2)
            logging.info(f"Detected Movie: {movie_title} ({year})")
            dest_path = os.path.join(MOVIES_DIR, f"{movie_title} ({year})")
            return 'movie', dest_path

    # 4. If nothing matches, classify as unsorted
    logging.warning(f"Could not categorize '{torrent_name}'. Placing in Unsorted.")
    return 'unclassified', UNSORTED_DIR


def main():
    """
    Main function to handle the sorting logic.
    """
    logging.info("--- Sorter script started ---")
    if len(sys.argv) < 3:
        logging.error("Error: Script needs torrent name and content path arguments.")
        sys.exit(1)

    torrent_name = sys.argv[1]
    content_path = sys.argv[2]  # Full path to the downloaded file or folder
    logging.info(f"Processing Torrent: '{torrent_name}' at '{content_path}'")

    if not os.path.exists(content_path):
        logging.error(f"Source path does not exist: '{content_path}'")
        sys.exit(1)

    category, dest_path = get_media_info(torrent_name)

    try:
        # For season packs, the parent directory needs to be created, not the final path itself
        if category == 'season_pack':
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        else:
            os.makedirs(dest_path, exist_ok=True)
    except OSError as e:
        logging.error(f"Error creating directory {dest_path}: {e}")
        sys.exit(1)

    try:
        # --- LOGIC FOR HANDLING DIFFERENT CATEGORIES ---
        if category in ['movie', 'episode']:
            if os.path.isdir(content_path):
                # It's a folder, find the largest video file inside and move it
                logging.info(f"Content is a directory. Searching for video files...")
                video_file = None
                max_size = -1
                for root, _, files in os.walk(content_path):
                    for f in files:
                        if any(f.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                            file_path = os.path.join(root, f)
                            file_size = os.path.getsize(file_path)
                            if file_size > max_size:
                                max_size = file_size
                                video_file = file_path

                if video_file:
                    logging.info(f"Found largest video file: '{video_file}'")
                    shutil.move(video_file, os.path.join(dest_path, os.path.basename(video_file)))
                    logging.info(f"Moved video file to '{dest_path}'.")
                    # Clean up the original folder if it's now empty
                    try:
                        os.rmdir(content_path)
                        logging.info(f"Removed empty source directory: '{content_path}'")
                    except OSError:
                        logging.warning(f"Source directory '{content_path}' was not empty. Not removing.")
                else:
                    logging.warning("No video files found in directory. Moving entire folder to Unsorted.")
                    shutil.move(content_path, os.path.join(UNSORTED_DIR, os.path.basename(content_path)))

            else:  # It's a single file
                logging.info("Content is a single file. Moving...")
                shutil.move(content_path, os.path.join(dest_path, os.path.basename(content_path)))

        elif category == 'season_pack':
            # Move and rename the entire folder to the specific season directory
            logging.info(f"Moving and renaming season pack folder to '{dest_path}'")
            shutil.move(content_path, dest_path)

        else:  # 'unclassified'
            logging.info(f"Moving unclassified content to '{dest_path}'")
            shutil.move(content_path, os.path.join(dest_path, os.path.basename(content_path)))

        logging.info("Move successful!")

    except Exception as e:
        logging.error(f"Failed to move content: {e}")
        sys.exit(1)

    logging.info("--- Sorter script finished ---")


if __name__ == "__main__":
    main()

