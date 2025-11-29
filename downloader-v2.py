import yt_dlp

def list_and_download_formats(video_url):
    """
    Lists available video formats and prompts the user to select one for download.
    """
    try:
        # 1. Extract info to get all available formats
        # The 'nocheckcertificate': True is sometimes useful to avoid SSL errors.
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'nocheckcertificate': True,
            'listformats': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            video_title = info_dict.get('title', 'Video')
            formats = info_dict.get('formats', [])

        print(f"### Available Formats for: {video_title} ###\n")
        print("CODE | EXT | RESOLUTION | NOTE")
        print("-----|-----|------------|-----")
        
        # 2. List the formats
        available_formats = {}
        for f in formats:
            format_id = f.get('format_id')
            ext = f.get('ext')
            resolution = f.get('resolution')
            note = f.get('format_note')
            
            # Filter out formats with no ID or note, which are typically incomplete or merged streams
            if format_id and (resolution != 'audio only' or 'audio' in note.lower()):
                print(f"{format_id:<4} | {ext:<3} | {resolution:<10} | {note}")
                available_formats[format_id] = f

        # 3. Prompt for selection
        selected_code = input("\nEnter the CODE for the desired quality (e.g., 'best' or a specific format ID): ").strip()

        # 4. Configure download options
        if not selected_code:
             print("No format selected. Aborting.")
             return

        # Use the entered code for the 'format' option
        download_opts = {
            'format': selected_code,
            'outtmpl': f'./downloads/{video_title}.%(ext)s', # Set output directory and filename template
            'merge_output_format': 'mp4', # Force merging to MP4 if separate streams are downloaded
            'nocheckcertificate': True
        }

        # 5. Download the selected format
        print(f"\nStarting download for format CODE: {selected_code}...")
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([video_url])
            print("\nDownload complete!")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

# Example usage
if __name__ == "__main__":
    video_link = input("Enter the YouTube URL: ").strip()
    if video_link:
        list_and_download_formats(video_link)
    else:
        print("Invalid URL provided.")
