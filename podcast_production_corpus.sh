#!/bin/bash
# Comprehensive Podcast Production Corpus Builder

echo "Building comprehensive podcast production corpus..."

# Create podcast corpus structure
mkdir -p CORPUS/podcasts/production/{recording,editing,mastering,hosting}
mkdir -p CORPUS/podcasts/formats/{interview,narrative,conversational,educational,comedy,true_crime}
mkdir -p CORPUS/podcasts/equipment/{microphones,interfaces,software,acoustic_treatment}
mkdir -p CORPUS/podcasts/distribution/{rss,platforms,syndication,analytics}
mkdir -p CORPUS/podcasts/monetization/{sponsorship,patreon,premium,merchandise}
mkdir -p CORPUS/podcasts/voices/{hosts,guests,narrators,voice_actors}
mkdir -p CORPUS/podcasts/music/{intro,outro,beds,stingers,transitions}
mkdir -p CORPUS/podcasts/templates/{show_notes,transcripts,contracts,releases}

# Technical specifications
cat > CORPUS/podcasts/production/technical_specs.json << 'EOF'
{
  "audio_standards": {
    "sample_rate": "48000Hz",
    "bit_depth": "24-bit",
    "format": "WAV for editing, MP3/M4A for distribution",
    "loudness": "-16 LUFS stereo, -19 LUFS mono",
    "true_peak": "-1 dBFS maximum",
    "dynamic_range": "7-10 LU"
  },
  "file_formats": {
    "master": "WAV 48kHz 24-bit",
    "distribution_high": "MP3 320kbps CBR",
    "distribution_standard": "MP3 128kbps CBR",
    "distribution_spoken": "MP3 64kbps mono",
    "video_podcast": "MP4 H.264 + AAC"
  },
  "episode_lengths": {
    "micro": "1-5 minutes",
    "short": "10-20 minutes",
    "standard": "30-45 minutes",
    "long_form": "60-120 minutes",
    "marathon": "3+ hours"
  }
}
EOF

# Recording setup guide
cat > CORPUS/podcasts/production/recording_setup.md << 'EOF'
# Professional Podcast Recording Setup

## Recording Environment
- Room treatment: Acoustic panels, bass traps
- Noise floor: Below -60dB
- RT60: Under 0.3 seconds
- Background noise control

## Signal Chain
1. Microphone -> Preamp -> Interface -> DAW
2. Monitoring: Closed-back headphones
3. Backup recording: Always run redundant recording

## Recording Best Practices
- 48kHz 24-bit minimum
- Leave headroom (-12 to -6 dB peaks)
- Record room tone (30 seconds)
- Clap sync for multi-track
- Use pop filter / windscreen
- Monitor in real-time
- Save projects with timestamps

## Remote Recording
- Double-ender technique
- Platform options: Riverside, SquadCast, Zencastr
- Local backup always
- Sync methods: Timecode, clap sync
EOF

# Editing workflow
cat > CORPUS/podcasts/production/editing_workflow.md << 'EOF'
# Podcast Editing Workflow

## Pre-Production
1. Script/outline review
2. Music/SFX selection
3. Template setup
4. Guest prep

## Editing Process
1. **Assembly Edit**
   - Sync tracks
   - Remove false starts
   - Basic arrangement

2. **Content Edit**
   - Remove filler words (um, uh)
   - Tighten pacing
   - Remove tangents
   - Balance conversation flow

3. **Audio Processing**
   - EQ (high-pass 80Hz, presence boost)
   - Compression (3:1 ratio, -20dB threshold)
   - De-essing
   - Noise reduction
   - Level matching

4. **Sweetening**
   - Add music beds
   - Insert transitions
   - Room tone fill
   - Crossfades

5. **Mastering**
   - Final EQ
   - Multiband compression
   - Limiting to -16 LUFS
   - True peak limiting -1dB
   - Dithering for MP3

## Quality Control
- Listen on multiple systems
- Check mono compatibility
- Verify loudness standards
- Review transcript
EOF

# Popular podcast formats
cat > CORPUS/podcasts/formats/format_templates.yaml << 'EOF'
interview_format:
  structure:
    - cold_open: 30s teaser
    - intro_music: 15s
    - host_intro: 1-2min
    - guest_intro: 2-3min
    - main_interview: 30-45min
    - rapid_fire: 5min
    - closing: 2min
    - outro_music: 15s
  
narrative_format:
  structure:
    - hook: 1min
    - theme_music: 30s
    - act_1: 15min
    - midroll_break: 2min
    - act_2: 15min
    - climax: 5min
    - resolution: 5min
    - credits: 1min

conversational_format:
  structure:
    - banter: 5min
    - topic_intro: 2min
    - discussion: 35min
    - listener_questions: 10min
    - recommendations: 5min
    - preview_next: 1min

true_crime_format:
  structure:
    - case_teaser: 2min
    - intro_music: 30s
    - background: 10min
    - investigation: 20min
    - evidence: 15min
    - theories: 10min
    - conclusion: 5min
    - updates: 3min
EOF

# Distribution setup
cat > CORPUS/podcasts/distribution/platform_specs.json << 'EOF'
{
  "apple_podcasts": {
    "format": "M4A AAC or MP3",
    "bitrate": "128kbps recommended",
    "artwork": "3000x3000px minimum",
    "rss_namespace": "itunes",
    "categories": 100,
    "explicit_tag": true
  },
  "spotify": {
    "format": "MP3",
    "bitrate": "96-320kbps",
    "artwork": "1400x1400px minimum",
    "video": "MP4 supported",
    "music_segments": "Licensed only",
    "analytics": "Spotify for Podcasters"
  },
  "youtube": {
    "format": "MP4 video required",
    "audio_codec": "AAC",
    "resolution": "1920x1080 recommended",
    "thumbnail": "1280x720px",
    "chapters": "Supported via timestamps",
    "monetization": "YouTube Partner Program"
  },
  "hosting_platforms": {
    "buzzsprout": {"price": "$12+/mo", "analytics": "advanced"},
    "libsyn": {"price": "$15+/mo", "oldest": true},
    "anchor": {"price": "free", "spotify_owned": true},
    "transistor": {"price": "$19+/mo", "multiple_shows": true},
    "podbean": {"price": "$9+/mo", "monetization": "built-in"}
  }
}
EOF

# Podcast SEO and growth
cat > CORPUS/podcasts/distribution/growth_strategy.md << 'EOF'
# Podcast Growth & SEO Strategy

## Podcast SEO
1. **Title Optimization**
   - Include keywords in show title
   - Episode titles: Descriptive + Guest Name
   - Avoid clickbait

2. **Description Optimization**
   - First 125 characters crucial
   - Include keywords naturally
   - Episode timestamps
   - Links to resources

3. **Transcripts**
   - Full transcripts for SEO
   - Key quotes highlighted
   - Timestamp markers
   - Searchable content

## Growth Tactics
- Guest swapping
- Audiogram creation
- Newsletter integration
- Social media clips
- Community building
- Review campaigns
- Cross-promotion
- Paid advertising

## Analytics to Track
- Downloads vs unique listeners
- Completion rate
- Platform distribution
- Geographic data
- Device types
- Episode performance
- Subscriber growth
EOF

# Monetization strategies
cat > CORPUS/podcasts/monetization/revenue_models.json << 'EOF'
{
  "sponsorship": {
    "cpm_rates": {
      "pre_roll": "$15-25",
      "mid_roll": "$25-35",
      "post_roll": "$10-15"
    },
    "minimum_downloads": "5000 per episode",
    "platforms": ["Podcorn", "AdvertiseCast", "Podcast One"]
  },
  "premium_content": {
    "platforms": ["Patreon", "Supercast", "Supporting Cast"],
    "tier_suggestions": ["$3", "$5", "$10", "$25"],
    "perks": ["Ad-free", "Bonus episodes", "Early access", "Community"]
  },
  "direct_support": {
    "one_time": ["Buy Me a Coffee", "PayPal", "Venmo"],
    "recurring": ["Memberful", "Ghost", "Substack"]
  },
  "products": {
    "merchandise": ["Teespring", "Printful", "Redbubble"],
    "courses": ["Teachable", "Thinkific", "Kajabi"],
    "books": ["Amazon KDP", "IngramSpark", "Lulu"]
  },
  "services": {
    "consulting": "$100-500/hour",
    "speaking": "$1000-10000/event",
    "workshops": "$500-5000/session"
  }
}
EOF

# Voice processing for podcasts
cat > CORPUS/podcasts/voices/voice_processing.md << 'EOF'
# Podcast Voice Processing Guide

## Voice EQ Settings
### Male Voice
- High-pass: 80-100Hz (24dB/oct)
- Mud cut: -3dB at 200-400Hz
- Presence: +2-3dB at 3-5kHz
- Air: +1-2dB shelf at 10kHz

### Female Voice
- High-pass: 100-120Hz (24dB/oct)
- Warmth: +1-2dB at 200-300Hz
- Clarity: +2-3dB at 4-6kHz
- Brightness: +1dB shelf at 12kHz

## Compression Settings
- Ratio: 3:1 to 4:1
- Threshold: -20 to -15dB
- Attack: 2-5ms
- Release: 50-100ms
- Makeup gain: As needed
- Knee: Soft (2-3dB)

## De-essing
- Frequency: 5-8kHz
- Threshold: -25 to -20dB
- Ratio: 8:1
- Listen mode for tuning

## Noise Reduction
1. Capture noise profile (room tone)
2. Reduction: 6-12dB
3. Sensitivity: 6-8
4. Frequency smoothing: 3-5
5. Attack/Release: 0ms/100ms

## Gate Settings
- Threshold: -40 to -35dB
- Ratio: 10:1
- Attack: 1ms
- Hold: 10-30ms
- Release: 100-300ms
- Range: -10 to -20dB
EOF

# Create RSS feed template
cat > CORPUS/podcasts/distribution/rss_template.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:podcast="https://podcastindex.org/namespace/1.0">
  <channel>
    <title>Podcast Title</title>
    <link>https://example.com</link>
    <description>Podcast Description</description>
    <language>en-us</language>
    <copyright>© 2024</copyright>
    <itunes:author>Author Name</itunes:author>
    <itunes:summary>Detailed Summary</itunes:summary>
    <itunes:owner>
      <itunes:name>Owner Name</itunes:name>
      <itunes:email>email@example.com</itunes:email>
    </itunes:owner>
    <itunes:image href="https://example.com/artwork.jpg"/>
    <itunes:category text="Technology"/>
    <itunes:explicit>false</itunes:explicit>
    <podcast:funding url="https://example.com/support">Support the show</podcast:funding>
    
    <item>
      <title>Episode Title</title>
      <description>Episode Description</description>
      <pubDate>Wed, 15 Jun 2024 19:00:00 GMT</pubDate>
      <enclosure url="https://example.com/episode.mp3" type="audio/mpeg" length="25000000"/>
      <guid>unique-episode-id</guid>
      <itunes:duration>1801</itunes:duration>
      <itunes:episode>1</itunes:episode>
      <itunes:season>1</itunes:season>
      <podcast:transcript url="https://example.com/transcript.srt" type="application/srt"/>
    </item>
  </channel>
</rss>
EOF

echo "Podcast corpus created with:"
echo "✓ Production workflows"
echo "✓ Technical specifications"
echo "✓ Format templates"
echo "✓ Distribution guides"
echo "✓ Monetization strategies"
echo "✓ Voice processing settings"
echo "✓ RSS feed templates"
echo "✓ Growth strategies"