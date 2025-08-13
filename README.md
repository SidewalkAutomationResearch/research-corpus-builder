# Research Corpus Builder Module

**Version**: 2.0.0  
**Self-contained, portable research corpus management system**

## Overview

Complete toolkit for building, expanding, and managing research corpora with local AI integration. Designed for academic research, AI safety studies, and interdisciplinary analysis.

## Features

- **Automated Reference Expansion**: Extract and download papers from citations
- **Archive Integration**: Merge historical research collections  
- **Local AI Processing**: Offline analysis with Ollama models
- **Multi-format Support**: PDFs, JSON, Markdown, plain text
- **Comprehensive Analysis**: Generate research summaries and insights
- **Modular Design**: Self-contained, portable components

## Quick Start

### Installation

```bash
# Clone or copy the CORPUS-BUILDER-MODULE directory
cd CORPUS-BUILDER-MODULE

# Install dependencies
pip install -r requirements.txt

# Verify Ollama installation (for local AI)
ollama --version
```

### Basic Usage

```python
# Import the module
from CORPUS_BUILDER_MODULE import *

# Quick corpus expansion
expand_corpus("path/to/corpus", max_downloads=25)

# Generate summary
summary = summarize_corpus("path/to/corpus", model="qwen-research")

# Integrate archives
integrate_archives("archive_config.json")
```

### Command Line Interface

```bash
# Expand corpus references
python reference_expander.py ../AI_SAFETY_CORPUS --max-downloads 25

# Execute expansion plan
python execute_expansion_plan.py --plan corpus_expansion_plan.json

# Generate corpus summary
python corpus_summarizer.py ../ --model qwen-research

# Integrate archives
python archive_integrator.py archived_integration_config.json
```

## Core Components

### 1. Reference Expander (`reference_expander.py`)
Extracts citations from research papers and automatically downloads referenced works.

**Features:**
- DOI resolution and download
- arXiv paper extraction
- Citation pattern recognition
- Deduplication and tracking
- SQLite database logging

**Usage:**
```python
from reference_expander import ReferenceExpander

expander = ReferenceExpander("corpus_path")
results = expander.expand_corpus({"max_downloads": 50})
```

### 2. Archive Integrator (`archive_integrator.py`)
Merges archived research collections into main corpus.

**Features:**
- Multi-source integration
- File deduplication
- Metadata preservation
- Integration manifests
- Quality validation

**Usage:**
```python
from archive_integrator import ArchiveIntegrator

integrator = ArchiveIntegrator("config.json")
manifest = integrator.integrate_archives()
```

### 3. Corpus Summarizer (`corpus_summarizer.py`)
Generates comprehensive analysis using local AI models.

**Features:**
- Section-by-section analysis
- Research pattern detection
- Cross-domain insights
- Statistical summaries
- Markdown reports

**Usage:**
```python
from corpus_summarizer import CorpusSummarizer

summarizer = CorpusSummarizer("corpus_path", "qwen-research")
summary = summarizer.create_comprehensive_summary()
```

### 4. Expansion Executor (`execute_expansion_plan.py`)
Orchestrates multi-phase corpus expansion campaigns.

**Features:**
- Phased expansion planning
- Rate limiting and error handling
- Progress tracking
- Success criteria validation
- Comprehensive reporting

**Usage:**
```python
from execute_expansion_plan import CorpusExpansionExecutor

executor = CorpusExpansionExecutor("plan.json", "corpus_path")
results = executor.execute_expansion_plan()
```

## Configuration

### Basic Configuration (`example_config.json`)
```json
{
  "name": "research_corpus",
  "sections": {
    "academic": {
      "papers": ["https://arxiv.org/pdf/123.pdf"]
    },
    "clinical": {
      "studies": ["https://pubmed.ncbi.nlm.nih.gov/study.pdf"]
    }
  }
}
```

### Expansion Plan (`corpus_expansion_plan.json`)
```json
{
  "expansion_plan": {
    "phase_1": {
      "priority": "high",
      "target_sections": ["AI_SAFETY_CORPUS"],
      "download_limit": 30
    }
  },
  "execution_strategy": {
    "model": "qwen-research",
    "rate_limiting": "0.5s_between_downloads"
  }
}
```

## Local AI Integration

### Supported Models
- **qwen-research**: Optimized for research analysis
- **qwen2.5-coder:7b**: Technical document processing
- **llama3.1:8b**: General reasoning and analysis
- **deepseek-coder:6.7b**: Code and technical content

### Model Management
```bash
# List available models
ollama list

# Install new model
ollama pull qwen-research

# Test model
ollama run qwen-research "Analyze this research abstract..."
```

## Advanced Features

### 1. Multi-Phase Expansion
Execute complex expansion strategies across multiple corpus sections:

```python
# Create expansion plan
plan = {
    "phase_1_clinical": {"target_sections": ["PSYCHOSIS_CORPUS"], "download_limit": 25},
    "phase_2_ai_safety": {"target_sections": ["AI_SAFETY_CORPUS"], "download_limit": 50}
}

# Execute plan
executor = CorpusExpansionExecutor(plan, corpus_base)
results = executor.execute_expansion_plan()
```

### 2. Cross-Domain Analysis
Generate insights across research domains:

```python
# Analyze connections between AI safety and psychology
summarizer = CorpusSummarizer(corpus_base, "qwen-research")
cross_analysis = summarizer.analyze_cross_domain_patterns()
```

### 3. Quality Validation
Ensure corpus integrity and quality:

```python
# Validate downloaded papers
expander = ReferenceExpander(corpus_path)
validation_report = expander.validate_corpus_quality()
```

## File Structure

```
CORPUS-BUILDER-MODULE/
├── __init__.py                 # Module interface
├── reference_expander.py       # Citation extraction & download
├── archive_integrator.py       # Archive integration
├── corpus_summarizer.py        # AI-powered analysis
├── execute_expansion_plan.py   # Multi-phase expansion
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── docs/                       # Additional documentation
└── examples/                   # Usage examples
    ├── basic_expansion.py
    ├── archive_integration.py
    └── analysis_pipeline.py
```

## Output Files

### Expansion Results
- `references.db`: SQLite database of all citations
- `expansion_log.json`: Detailed expansion logs
- `EXPANDED_REFERENCES/`: Downloaded papers directory

### Analysis Results
- `corpus_summary_YYYYMMDD_HHMMSS.json`: Comprehensive analysis
- `corpus_summary_YYYYMMDD_HHMMSS.md`: Human-readable report

### Integration Results
- `integration_manifest.json`: Archive integration details
- `INTEGRATED_ARCHIVES/`: Merged research collections

## Performance

### Recommended Specifications
- **RAM**: 16GB minimum (for local AI models)
- **Storage**: 50GB+ for large corpora
- **Network**: Stable connection for downloads
- **CPU**: Multi-core recommended for parallel processing

### Optimization Tips
- Use SSD storage for better I/O performance
- Configure rate limiting to respect server policies
- Monitor disk space during large expansions
- Use local AI models for offline analysis

## Troubleshooting

### Common Issues

**1. PDF extraction fails**
```bash
pip install pdfplumber pypdf pymupdf
```

**2. Local AI timeout**
```python
# Increase timeout in query
result = manager.query_model(prompt, timeout=300)
```

**3. Download failures**
- Check network connectivity
- Verify DOI/arXiv URLs
- Review rate limiting settings

**4. Memory issues with large corpora**
- Process in smaller batches
- Use streaming analysis
- Monitor system resources

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# All operations will show detailed logs
```

## Integration Examples

### With Jupyter Notebooks
```python
# In notebook cell
from CORPUS_BUILDER_MODULE import *

# Interactive corpus exploration
corpus_stats = get_corpus_statistics("../research_corpus")
display(corpus_stats)

# Generate visualizations
plot_corpus_growth_over_time(corpus_stats)
```

### With Research Pipelines
```python
# Automated research pipeline
def research_pipeline(query_topic):
    # 1. Expand relevant corpus sections
    expand_corpus(f"corpus/{query_topic}", max_downloads=30)
    
    # 2. Generate topic analysis
    analysis = summarize_corpus(f"corpus/{query_topic}")
    
    # 3. Extract key insights
    insights = generate_research_insights(query_topic, analysis)
    
    return insights
```

## License

Open source research tool. See individual component licenses for details.

## Support

For issues, feature requests, or questions:
1. Check troubleshooting section
2. Review component documentation
3. Test with minimal examples
4. Verify local AI model availability

## Changelog

### Version 2.0.0
- Complete modular redesign
- Local AI integration
- Multi-phase expansion
- Enhanced error handling
- Comprehensive documentation
- Self-contained portability

### Version 1.0.0
- Initial implementation
- Basic reference expansion
- Archive integration
- Simple analysis tools