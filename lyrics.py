from lyricsgenius import Genius
import json
import os
import re

token = 'ENTER YOUR API TOKEN HERE'
#API Token can be found on the Genius API Website
name_of_the_artist = 'ENTER THE ARTIST YU WANT TO USE HERE'
genius = Genius(token)
artist = genius.search_artist(name_of_the_artist, max_songs=100)

artist.save_lyrics()

def clean_lyrics(lyrics, artist_name):
    # Split into sections
    sections = re.split(r'(\[[^\]]+\])', lyrics)
    cleaned_lines = []
    keep_section = True  # Default to keeping sections for solo songs

    for i, section in enumerate(sections):
        # If it's a header
        if section.startswith('[') and section.endswith(']'):
            # If there's a colon in the header, check the artist
            if ':' in section:
                # Only keep sections with the artist or no artist specified
                artists = section.split(':')[1].split('&')
                # If other artists are specified, only keep if our artist is among them
                keep_section = any(artist_name in artist.strip() for artist in artists)
            # If no colon, this is a solo song section header - keep it
            else:
                keep_section = True
            continue

        # If we're in a section we want to keep
        if keep_section and section.strip():
            cleaned_lines.append(section.strip())

    # Join sections back together
    lyrics = '\n\n'.join(cleaned_lines)
    lyrics = lyrics.strip()

    return lyrics


def process_lyrics_files():
    # Get all JSON files in current directory
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]

    for json_file in json_files:
        try:
            # Read JSON file
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Extract artist name and songs from the data
            artist_name = name_of_the_artist
            if not artist_name:
                print(f"Couldn't find artist name in {json_file}, skipping...")
                continue

            songs = data.get('songs', [])
            if not songs:
                print(f"No songs found in {json_file}, skipping...")
                continue

            # Create output filename
            output_filename = f"{artist_name.replace(' ', '_')}_lyrics.txt"

            print(f"Processing {len(songs)} songs for {artist_name}...")

            # Write to output file
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                songs_processed = 0
                songs_with_lyrics = 0

                for song in songs:
                    songs_processed += 1
                    lyrics = song.get('lyrics', '')
                    if lyrics:
                        # Clean and write the lyrics
                        clean_text = clean_lyrics(lyrics, artist_name)
                        if clean_text:  # Only write if there are lyrics remaining
                            outfile.write(f"{clean_text}\n\n---\n\n")
                            songs_with_lyrics += 1

                    # Print progress every 50 songs
                    if songs_processed % 50 == 0:
                        print(f"Processed {songs_processed}/{len(songs)} songs...")

            print(f"Finished processing {artist_name}:")
            print(f"- Total songs processed: {songs_processed}")
            print(f"- Songs with artist's lyrics: {songs_with_lyrics}")
            print(f"- Output saved to: {output_filename}")
            print()

        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")


if __name__ == "__main__":
    print("Starting lyrics processing...")
    process_lyrics_files()
    print("Done!")
