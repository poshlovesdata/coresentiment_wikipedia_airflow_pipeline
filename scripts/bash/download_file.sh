#!/bin/bash

echo "Downloading Wikipedia pageviews data..."
dir_name="output"
base_dir="/opt/airflow"


gzipped_file_name="wiki_pages.gz"
unzipped_file_name="wiki_pages"
wiki_url="https://dsumps.wikimedia.org/other/pageviews/2025/2025-10/pageviews-20251010-090000.gz"

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