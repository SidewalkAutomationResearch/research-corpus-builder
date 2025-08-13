#!/bin/bash

# Download professional voice samples for analysis
echo "Building professional voice corpus..."

mkdir -p CORPUS/professional/{radio,podcast,documentary,interview}/{raw,processed}

# Radio announcer samples
mkdir -p CORPUS/professional/radio/{news,talk,commercial}

# Podcast host styles
mkdir -p CORPUS/professional/podcast/{interview,solo,panel}

# Documentary narration
mkdir -p CORPUS/professional/documentary/{nature,science,history}

# Interview voices
mkdir -p CORPUS/professional/interview/{host,guest,moderator}

# Process voices to 8-bit for storage
echo "Processing voice samples..."

# Function to process audio file to 8-bit
process_to_8bit() {
  input=$1
  output="${input%.wav}_8bit.wav"
  sox "$input" -r 22050 -b 8 -c 1 "$output" \
    compand 0.3,1 6:-70,-60,-20 -5 -90 0.2
  rm "$input"
}

# Process each directory
for dir in $(find CORPUS/professional -type d); do
  if [ -d "$dir/raw" ]; then
    for file in "$dir/raw"/*.wav; do
      if [ -f "$file" ]; then
        process_to_8bit "$file"
        mv "${file%.wav}_8bit.wav" "$dir/processed/"
      fi
    done
  fi
done

echo "Voice corpus processed!"

# Show storage stats
echo -e "\nCorpus Statistics:"
echo "Raw samples: $(find CORPUS/professional -name '*.wav' -path '*/raw/*' | wc -l)"
echo "Processed samples: $(find CORPUS/professional -name '*_8bit.wav' -path '*/processed/*' | wc -l)"
echo "Total size: $(du -sh CORPUS/professional | cut -f1)"