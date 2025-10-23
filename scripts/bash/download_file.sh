#!/bin/bash

echo "Downloading Wikipedia pageviews data..."
dir_name="output"
base_dir="/opt/airflow"


gzipped_file_name="wiki_pages.gz"
unzipped_file_name="wiki_pages"
wiki_url="https://dumps.wikimedia.org/other/pageviews/2025/2025-10/pageviews-20251010-090000.gz"

# Define the full paths
gzipped_file_path="$base_dir/$dir_name/$gzipped_file_name"
unzipped_file_path="$base_dir/$dir_name/$unzipped_file_name"


echo "Creating directory and downloading file..."
mkdir -p "$base_dir/$dir_name"

# Download the file and save it with the .gz extension
echo "Downloading to: $gzipped_file_path"
curl -L -o "$gzipped_file_path" "$wiki_url"

echo "Decompressing the file..."
gunzip -f "$gzipped_file_path"


echo "File downloaded and decompressed successfully."
# Echo the path to the unzipped file and push to Xcom
echo "$unzipped_file_path"