#!/bin/bash
# Download and decompress one hourly Wikimedia pageviews dump inside Airflow container.
# Update `wiki_url` to target the desired hour; timestamp refers to end of window.

echo "Downloading Wikipedia pageviews data..."
dir_name="output"
base_dir="/opt/airflow"

# Output filenames inside the container
gzipped_file_name="wiki_pages.gz"
unzipped_file_name="wiki_pages"

# Configure the desired hour/day here for convenience
year="2025"
month="10"
day="10"
end_hour="10"

# Zero-pad to two digits for URL correctness
month=$(printf "%02d" "$month")
day=$(printf "%02d" "$day")
end_hour=$(printf "%02d" "$end_hour")

wiki_url="https://dumps.wikimedia.org/other/pageviews/${year}/${year}-${month}/pageviews-${year}${month}${day}-${end_hour}0000.gz"

# Define the full paths
gzipped_file_path="$base_dir/$dir_name/$gzipped_file_name"
unzipped_file_path="$base_dir/$dir_name/$unzipped_file_name"

echo "Creating directory if it doesn't exist..."
mkdir -p "$base_dir/$dir_name"

# Remove old files if they already exist
if [ -f "$gzipped_file_path" ]; then
  echo "Removing old gzipped file: $gzipped_file_path"
  rm -f "$gzipped_file_path"
fi

if [ -f "$unzipped_file_path" ]; then
  echo "Removing old unzipped file: $unzipped_file_path"
  rm -f "$unzipped_file_path"
fi

# Download the new file
echo "Downloading file..."
curl -L -o "$gzipped_file_path" "$wiki_url"

# Decompress the file
echo "Decompressing the file..."
gunzip -f "$gzipped_file_path"

echo "File downloaded and decompressed successfully."

# Output the path to the unzipped file for XCom
echo "$unzipped_file_path"