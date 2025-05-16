import json
import os

# Load JSON file
def load_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)

# Load M3U file
def load_m3u(m3u_file):
    with open(m3u_file, 'r', encoding='utf-8') as file:
        return file.readlines()

# Write new M3U file
def write_m3u(m3u_file, content):
    with open(m3u_file, 'w', encoding='utf-8') as file:
        file.writelines(content)

# Match channels and update M3U
def update_m3u(channellist, channels):
    updated_m3u = []

    for line in channels:
        if line.startswith("#EXTINF"):
            # Extract the channel name after the last comma
            channel_name = line.split(",", 1)[-1].strip()
            
            # Find a matching channel in the channellist
            match = next((item for item in channellist if item["channel-name"] == channel_name), None)

            if match:
                # If a match is found, update the EXTINF line with details from the JSON
                updated_line = (
                    f'#EXTINF:-1 '
                    f'tvg-name="{match["tvg-name"]}" '
                    f'tvg-id="{match["tvg-id"]}" '
                    f'tvg-logo="{match["tvg-logo"]}" '
                    f'group-title="{match["group-title"]}",'
                    f'{match["tvg-name"]}\n'  # Replace channel name with tvg-name
                )
                updated_m3u.append(updated_line)
            else:
                # If no match is found, assign to DLHD-Unmatched with appropriate fields
                updated_line = (
                    f'#EXTINF:-1 '
                    f'tvg-name="{channel_name}" '
                    f'tvg-id="" '
                    f'tvg-logo="" '
                    f'group-title="KLCIS-Unmatched",'
                    f'{channel_name}\n'
                )
                updated_m3u.append(updated_line)
        else:
            # For lines that do not start with #EXTINF, keep them as-is (including stream URLs)
            updated_m3u.append(line)

    return updated_m3u

if __name__ == "__main__":
    # Paths to input files
    json_file = "channellist_klcis.json"
    m3u_file = "klcis.m3u"
    output_file = "klcis_matched.m3u"

    # Remove existing output file if it exists to prevent appending to old data
    if os.path.exists(output_file):
        os.remove(output_file)

    # Load data from JSON and M3U files
    try:
        channellist = load_json(json_file)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file}' not found.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file '{json_file}'. {e}")
        exit(1)

    try:
        channels = load_m3u(m3u_file)
    except FileNotFoundError:
        print(f"Error: M3U file '{m3u_file}' not found.")
        exit(1)

    # Update M3U content with matched and unmatched channels
    updated_m3u = update_m3u(channellist, channels)
    
    # Write the updated M3U content to the output file
    write_m3u(output_file, updated_m3u)

    print(f"Updated M3U file created: {output_file}")
