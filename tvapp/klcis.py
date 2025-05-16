import requests
import json

# Base API URLs
CHANNELS_API = "https://int.klcis.cc/api/channels"
STREAM_API_TEMPLATE = "https://int.klcis.cc/api/stream/{}?quality={}"

# Output M3U file
OUTPUT_FILE = "klcis.m3u"

def fetch_channels():
    """Fetch channel data from the channels API."""
    try:
        response = requests.get(CHANNELS_API)
        response.raise_for_status()
        return response.json().get("channels", [])
    except requests.RequestException as e:
        print(f"Error fetching channels: {e}")
        return []

def fetch_stream_url(channel_id, quality="hd"):
    """Fetch stream URL for a given channel ID and quality."""
    try:
        url = STREAM_API_TEMPLATE.format(channel_id, quality)
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("stream_url")
    except requests.RequestException as e:
        print(f"  Error fetching {quality} stream for {channel_id}: {e}")
        return None

def clean_title(title):
    """Remove specified words and commas from the title."""
    words_to_remove = [
        "US Eastern Feed",
        "US East",
        "Eastern Feed",
        "HD",
        "HD East",
        "Eastern",
        "SD",
        "SD East"
    ]
    cleaned_title = title
    for word in words_to_remove:
        cleaned_title = cleaned_title.replace(word, "").strip()
    # Remove commas
    cleaned_title = cleaned_title.replace(",", "").strip()
    # Remove any extra spaces
    cleaned_title = " ".join(cleaned_title.split())
    return cleaned_title

def generate_m3u():
    """Generate M3U playlist from channel data."""
    channels = fetch_channels()
    if not channels:
        print("No channels found.")
        return

    # Write M3U header
    m3u_content = ["#EXTM3U"]

    for channel in channels:
        channel_id = channel.get("id")
        title = channel.get("title")
        category = channel.get("category")

        if not channel_id or not title or not category:
            print(f"Processing channel: {title or 'Unknown'} ({channel_id or 'No ID'}) - Failure (missing data)")
            continue

        # Clean the title for both tvg-name and channel name
        cleaned_title = clean_title(title)
        print(f"Processing channel: {cleaned_title} ({channel_id})")

        # Fetch stream URL (try HD first)
        stream_url = fetch_stream_url(channel_id, "hd")

        # If HD stream contains "fallback" or is None, try SD
        if stream_url and "fallback" in stream_url.lower():
            print(f"  HD stream contains 'fallback', switching to SD")
            stream_url = fetch_stream_url(channel_id, "sd")
        elif not stream_url:
            print(f"  HD stream failed, trying SD")
            stream_url = fetch_stream_url(channel_id, "sd")

        if not stream_url:
            print(f"  Result: Failure (no valid stream URL)")
            continue

        print(f"  Result: Success (stream URL obtained)")
        # Add channel to M3U with cleaned title and tvg-logo
        m3u_content.append(
            f'#EXTINF:-1 tvg-name="{cleaned_title}" tvg-logo="" group-title="{category}",{cleaned_title}\n{stream_url}'
        )

    # Write to M3U file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_content))
    print(f"\nM3U playlist generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_m3u()