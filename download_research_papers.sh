#!/bin/bash

# Download research papers and technical resources
echo "Building voice synthesis research corpus..."

mkdir -p CORPUS/{papers,tools,models,techniques}/{rvc,tts,synthesis,effects}

# Research Papers
echo "Downloading research papers..."

# RVC Papers
papers=(
  "https://arxiv.org/pdf/2305.13470.pdf"  # RVC main paper
  "https://arxiv.org/pdf/2306.15412.pdf"  # Voice conversion survey
  "https://arxiv.org/pdf/2304.05632.pdf"  # Neural voice synthesis
  "https://arxiv.org/pdf/2306.17005.pdf"  # Low-resource voice conversion
)

for paper in "${papers[@]}"; do
  wget -q -P CORPUS/papers/rvc "$paper"
done

# Tools and Techniques
echo "Gathering tools and techniques..."

# Voice processing tools
tools=(
  "https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI"
  "https://github.com/NVIDIA/tacotron2"
  "https://github.com/resemble-ai/Resemblyzer"
  "https://github.com/CorentinJ/Real-Time-Voice-Cloning"
)

for tool in "${tools[@]}"; do
  git clone --depth 1 "$tool" "CORPUS/tools/$(basename $tool)"
done

# Model architectures
mkdir -p CORPUS/models/{hubert,wavenet,tacotron,gans}

# Download pre-trained base models
wget -q -O CORPUS/models/hubert/hubert_base.pt "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt"

# Audio processing techniques
mkdir -p CORPUS/techniques/{pitch,timbre,prosody,compression}

# Effect chains and processing
mkdir -p CORPUS/techniques/effects/{reverb,compression,eq,spatial}

echo "Research corpus built!"

# Show statistics
echo -e "\nCorpus Statistics:"
echo "Papers: $(find CORPUS/papers -type f | wc -l)"
echo "Tools: $(find CORPUS/tools -type d -mindepth 1 | wc -l)"
echo "Models: $(find CORPUS/models -type f | wc -l)"
echo "Techniques: $(find CORPUS/techniques -type d -mindepth 1 | wc -l)"