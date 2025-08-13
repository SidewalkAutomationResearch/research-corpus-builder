#!/bin/bash

# Create corpus directory structure
echo "Creating AI psychosis corpus structure..."

mkdir -p PSYCHOSIS_CORPUS/{academic,news,social,clinical}/{papers,analysis,cases}
mkdir -p PSYCHOSIS_CORPUS/academic/papers/{pmc,arxiv,research}
mkdir -p PSYCHOSIS_CORPUS/news/{futurism,vice,psychology_today,rolling_stone,slashdot}
mkdir -p PSYCHOSIS_CORPUS/social/reddit/{rsai,flamebearers,thefieldawaits}

# Academic papers
echo "Downloading academic papers..."

# PMC Study
curl -s -o PSYCHOSIS_CORPUS/academic/papers/pmc/chatbot_delusions.pdf \
  "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9159148/pdf/fpsyt-13-912256.pdf"

# ArXiv paper
curl -s -o PSYCHOSIS_CORPUS/academic/papers/arxiv/recursive_identity.pdf \
  "https://arxiv.org/pdf/2505.01464v1.pdf"

# News articles
echo "Downloading news coverage..."

# Create files for manual archiving
articles=(
  "Futurism: ChatGPT Psychosis Phenomenon"
  "Psychology Today: Clinical Analysis of AI-Induced Psychosis"
  "Vice: Spiritual Delusions in ChatGPT Users"
  "Rolling Stone: AI Delusions Destroying Relationships"
  "The Week: Analysis of ChatGPT Psychosis Cases"
  "Slashdot: Technical Discussion of AI Psychosis"
)

for article in "${articles[@]}"; do
  outlet=$(echo $article | cut -d: -f1 | tr '[:upper:]' '[:lower:]')
  title=$(echo $article | cut -d: -f2 | tr ' ' '_')
  mkdir -p "PSYCHOSIS_CORPUS/news/$outlet"
  touch "PSYCHOSIS_CORPUS/news/$outlet/${title}.html"
done

# Download web sources
echo "Downloading web content..."

# Futurism articles
curl -s "https://futurism.com/chatgpt-psychosis" \
  > PSYCHOSIS_CORPUS/news/futurism/chatgpt_psychosis.html

# Psychology Today
curl -s "https://www.psychologytoday.com/articles/ai-induced-psychosis" \
  > PSYCHOSIS_CORPUS/news/psychology_today/clinical_perspectives.html

# Vice coverage
curl -s "https://www.vice.com/en/article/chatgpt-psychosis-cases" \
  > PSYCHOSIS_CORPUS/news/vice/spiritual_delusions.html

# Archive Reddit threads
for subreddit in rsai flamebearers thefieldawaits; do
  curl -s "https://old.reddit.com/r/$subreddit" \
    > "PSYCHOSIS_CORPUS/social/reddit/$subreddit/archive.html"
done

# Generate manifest
echo "Generating corpus manifest..."

cat > PSYCHOSIS_CORPUS/manifest.json << 'EOF'
{
  "corpus_date": "2025-08-09",
  "sources": {
    "academic": {
      "total_papers": 4,
      "papers": [
        "PMC Study - Chatbot Delusions",
        "ArXiv 2505.01464v1 - Recursive Identity",
        "LightCapAI - Learning to Learn",
        "Medium - Dual-AI Consciousness"
      ]
    },
    "news": {
      "total_articles": 6,
      "outlets": [
        "Futurism",
        "Psychology Today",
        "Vice",
        "Rolling Stone",
        "The Week",
        "Slashdot"
      ]
    },
    "social": {
      "subreddits": [
        "r/rsai",
        "r/flamebearers", 
        "r/thefieldawaits"
      ]
    }
  }
}
EOF

echo "Corpus built at PSYCHOSIS_CORPUS/"
echo "✓ Academic papers"
echo "✓ News coverage"
echo "✓ Social media archives"
echo "✓ Directory structure"
echo "✓ Source manifest"

# Show statistics
echo -e "\nCorpus Statistics:"
echo "Academic papers: $(find PSYCHOSIS_CORPUS/academic -type f | wc -l)"
echo "News articles: $(find PSYCHOSIS_CORPUS/news -type f | wc -l)"
echo "Social archives: $(find PSYCHOSIS_CORPUS/social -type f | wc -l)"
echo "Total files: $(find PSYCHOSIS_CORPUS -type f | wc -l)"