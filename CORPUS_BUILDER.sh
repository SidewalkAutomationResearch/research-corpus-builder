#!/bin/bash
# ===========================================
# Universal Corpus Builder
# A general-purpose tool for building research corpora
# ===========================================

# Usage: ./CORPUS_BUILDER.sh <config.json>
# Example config.json:
# {
#   "name": "ai_psychosis",
#   "sections": {
#     "academic": {
#       "papers": ["https://arxiv.org/pdf/123.pdf"],
#       "research": ["https://university.edu/paper.pdf"]
#     },
#     "news": {
#       "articles": ["https://news.com/story.html"]
#     }
#   }
# }

# Configuration
if [ -z "$1" ]; then
    echo "Error: Please provide a config JSON file"
    echo "Usage: ./CORPUS_BUILDER.sh <config.json>"
    exit 1
fi

CONFIG_FILE=$1
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    echo "Please install jq first:"
    echo "  macOS: brew install jq"
    echo "  Linux: sudo apt-get install jq"
    exit 1
fi

# Extract corpus name from config
CORPUS_NAME=$(jq -r '.name' "$CONFIG_FILE")
if [ -z "$CORPUS_NAME" ] || [ "$CORPUS_NAME" = "null" ]; then
    echo "Error: No corpus name found in config"
    exit 1
fi

echo "Building corpus: $CORPUS_NAME"
echo "===================="

# Create base directory
CORPUS_DIR="${CORPUS_NAME}_CORPUS"
mkdir -p "$CORPUS_DIR"

# Function to safely create directories from config
create_directories() {
    local section=$1
    echo "Creating $section directories..."
    
    # Get all subsections and their URLs from config
    jq -r --arg section "$section" '.sections[$section] | keys[]' "$CONFIG_FILE" | while read subsection; do
        mkdir -p "$CORPUS_DIR/$section/$subsection"
        echo "✓ Created $CORPUS_DIR/$section/$subsection"
    done
}

# Function to download content
download_content() {
    local section=$1
    local subsection=$2
    local url=$3
    local filename=$(basename "$url")
    local target="$CORPUS_DIR/$section/$subsection/$filename"
    
    echo "Downloading $url to $target"
    curl -s -L -o "$target" "$url"
    
    if [ -f "$target" ]; then
        echo "✓ Downloaded $filename"
        return 0
    else
        echo "✗ Failed to download $filename"
        return 1
    fi
}

# Process each section in config
jq -r '.sections | keys[]' "$CONFIG_FILE" | while read section; do
    create_directories "$section"
    
    # Get subsections and URLs
    jq -r --arg section "$section" '.sections[$section] | to_entries[] | "\(.key) \(.value[])"' "$CONFIG_FILE" | while read subsection url; do
        download_content "$section" "$subsection" "$url"
    done
done

# Create manifest with jq
echo "Creating manifest..."
jq -n \
  --arg name "$CORPUS_NAME" \
  --arg created "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  --arg total "$(find "$CORPUS_DIR" -type f | grep -v manifest.json | wc -l | tr -d ' ')" \
  '{
    name: $name,
    created: $created,
    statistics: {
      total_files: $total | tonumber,
      sections: {}
    }
  }' > "$CORPUS_DIR/manifest.json.tmp"

# Add section statistics to manifest
jq -r '.sections | keys[]' "$CONFIG_FILE" | while read section; do
    files=$(find "$CORPUS_DIR/$section" -type f | wc -l | tr -d ' ')
    size=$(du -sh "$CORPUS_DIR/$section" 2>/dev/null | cut -f1)
    size=${size:-"0B"}
    
    jq \
      --arg section "$section" \
      --arg files "$files" \
      --arg size "$size" \
      '.statistics.sections += {($section): {files: ($files | tonumber), size: $size}}' \
      "$CORPUS_DIR/manifest.json.tmp" > "$CORPUS_DIR/manifest.json.tmp2" \
    && mv "$CORPUS_DIR/manifest.json.tmp2" "$CORPUS_DIR/manifest.json.tmp"
done

mv "$CORPUS_DIR/manifest.json.tmp" "$CORPUS_DIR/manifest.json"

echo "✓ Created manifest"

# Print statistics
echo -e "\nCorpus Statistics:"
echo "Total files: $(find "$CORPUS_DIR" -type f | wc -l)"
for section in $sections; do
    count=$(find "$CORPUS_DIR/$section" -type f | wc -l)
    size=$(du -sh "$CORPUS_DIR/$section" | cut -f1)
    echo "$section: $count files ($size)"
done

echo -e "\nCorpus built at: $CORPUS_DIR"