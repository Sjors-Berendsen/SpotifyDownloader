import os, re, spotipy, yt_dlp, sys
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

# Initialize Spotipy client
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

def clear_screen():
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For Unix-based systems (Linux, macOS, etc.)
    else:
        os.system('clear')

def get_playlist_link():
    print("Please Provide the playlist share link")
    while True:
            spotify_link = input("Playlist:")
            if spotify_link.startswith("https://open.spotify.com/playlist/"):
                break
            print("Invalid Spotify playlist link. Please provide a valid link.")
    return spotify_link

# Function to extract the playlist ID from a Spotify link
def extract_playlist_id(spotify_link):
    pattern = r'playlist/(\w+)\?'
    match = re.search(pattern, spotify_link)
    if match:
        playlist_id = match.group(1)
        return playlist_id
    else:
        raise ValueError("Invalid Spotify playlist link")

def get_fileformat():
    print("Please Choose a file format for the music")
    print("1. MP3")
    print("2. WAV")
    print("3. OGG")

    while True:
        choice = input("Enter your choice (1/2/3): ")
        if choice in {"1", "2", "3"}:
            break
        print("Invalid choice. Please enter 1, 2, or 3.")
    if choice == "1":
        fileformat = "mp3"
    elif choice == "2":
        fileformat = "wav"
    elif choice == "3":
        fileformat = "ogg"
    return fileformat

def get_output_directory():
    print("Please provide the path to the directory you want us to download to")
    print("Defaults to ./results, press enter to use default")
    while True:
        output_directory = input('Provide the path:') or './results'
        try:
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
        except:
            print('')
        if os.path.isdir(output_directory):
            break
        
        print("Invalid directory. Please provide a valid directory path.")
    return output_directory

def confirm_download(playlist_link, file_format, output_dir):
    print("Confirmation:")
    print(f"    Playlist Link:      {playlist_link}")
    print(f"    File Format:        {file_format.upper()}")
    print(f"    Output Directory:   {output_dir}")
    while True:
        confirmation = input("Proceed with the download? (y/n): ").lower()
        if confirmation in {"y", "n"}:
            break
        print("Invalid choice. Please enter 'y' or 'n'.")
    return confirmation == "y"

def get_all_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def download_spotify_playlist(all_tracks, output_dir, fileformat):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': fileformat,
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_dir}/%(title)s - %(uploader)s.%(ext)s',
        'quiet': True,
    }

    failed = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        downloaded_songs = 0
        total_songs = len(all_tracks)
        for track in all_tracks:
            try:
                clear_screen()
                downloaded_songs += 1
                print(f"\rDownloading: {downloaded_songs}/{total_songs} songs")
                track_name = track['track']['name']
                artist_name = track['track']['artists'][0]['name']
                query = f'{track_name} {artist_name}'
                ydl.download([f'ytsearch:{query}'])
            except Exception as e:
                print(f"An error occurred while downloading: {track_name} - {artist_name}. Error: {str(e)}")
                failed.append(query)

    return failed

if __name__ == "__main__":
    try:    
        clear_screen()
        spotify_link = get_playlist_link()
        
        clear_screen()

        fileformat = get_fileformat()
        clear_screen()

        output_directory = get_output_directory()
        clear_screen()

        if confirm_download(spotify_link, fileformat, output_directory):
            playlist_id = extract_playlist_id(spotify_link)
            all_tracks = get_all_playlist_tracks(playlist_id)
            failed_tracks = download_spotify_playlist(all_tracks, output_directory, fileformat)

            if failed_tracks == []:
                print("Playlist downloaded successfully in" + fileformat + "format.")
            else:
                print("Playlist downloaded partially in" + fileformat + "format.")
                print("The following titles failed:")
                print(failed_tracks)
        else:
            print("Download canceled by the user.")
    except Exception as e:
        print(e)
