import yt_dlp
import os

def list_and_download_combined_formats(video_url):
    """
    Lists only formats that contain both video+audio already merged (progressive formats).
    Then lets the user select one to download.
    """

    # Create the downloads directory
    os.makedirs('./downloads', exist_ok=True)

    try:
        # Extract formats info
        ydl_info_opts = {
            'quiet': True,
            'skip_download': True,
            'nocheckcertificate': True,
        }

        with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        title = info.get("title", "video").replace("/", "_").replace("\\", "_")
        formats = info.get("formats", [])

        print(f"\n### Combined Video + Audio Formats for: {title} ###\n")
        print("CODE | EXT | RESOLUTION | SIZE (MB)")
        print("-----|-----|------------|----------")

        available = {}
        found = False

        for f in formats:
            # Must have both video & audio
            if f.get("vcodec") == "none" or f.get("acodec") == "none":
                continue

            fmt_id = f.get("format_id")
            ext = f.get("ext")

            # Determine resolution
            height = f.get("height")
            width = f.get("width")
            resolution = f"{width}x{height}" if width and height else f.get("format_note", "Unknown")

            # Size
            size = f.get("filesize")
            if size:
                size_mb = f"{size / (1024*1024):.1f}"
            else:
                size_mb = "N/A"

            print(f"{fmt_id:<4} | {ext:<3} | {resolution:<10} | {size_mb:<10}")

            available[fmt_id] = f
            found = True

        if not found:
            print("\nNo progressive (video+audio) formats found.")
            return

        selected = input("\nEnter the CODE to download: ").strip()
        if selected not in available:
            print("Invalid selection.")
            return

        # Download options
        download_opts = {
            'format': selected,
            'outtmpl': f'./downloads/{title}.%(ext)s',
            'nocheckcertificate': True
        }

        print(f"\nDownloading format {selected}...")
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([video_url])

        print(f"\n✔ Download complete! Saved as: ./downloads/{title}.{available[selected]['ext']}")

    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    url = input("Enter YouTube URL: ").strip()
    if url:
        list_and_download_combined_formats(url)
    else:
        print("Invalid URL.")
