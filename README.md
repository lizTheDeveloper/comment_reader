# Comment Reader - AI Complaint Analysis System

A data analysis project that processes social media comments to identify and categorize complaints about AI technology. The system uses LLM (Large Language Model) analysis to normalize complaints and create vote tallies based on comment engagement.

## Project Overview

This project analyzes comments from Instagram and TikTok to understand public sentiment and concerns about AI technology. It processes raw comment data, normalizes complaints using LLM analysis, and creates weighted vote tallies based on comment engagement (likes).

## Key Modules

### 1. Data Processing Modules

#### `instagram_comment_parser.py`
- **Purpose**: Parses Instagram comments from markdown files into individual thread-based files
- **Functionality**: 
  - Extracts usernames, content, timestamps, and engagement data
  - Groups consecutive comments from the same user into threads
  - Handles markdown formatting and profile pictures
  - Creates sanitized filenames with content previews
- **Usage**: `python instagram_comment_parser.py <input_file>`

#### `parse_into_comments_tiktok.py`
- **Purpose**: Parses TikTok comments from markdown files into individual comment files
- **Functionality**:
  - Extracts usernames, content, timestamps, and like counts
  - Handles TikTok-specific markdown formatting
  - Creates individual files for each comment
- **Usage**: `python parse_into_comments_tiktok.py <input_file>`

### 2. LLM Analysis Modules

#### `comment_reading_llm_local.py`
- **Purpose**: Primary complaint normalization and categorization system
- **Functionality**:
  - Connects to local LM Studio instance for LLM processing
  - Normalizes complaints across different comment variations
  - Maintains a growing list of unique complaints
  - Handles token limits by chunking long comments
  - Saves progress to JSON files for persistence

#### `comment_like_voter_llm.py`
- **Purpose**: Advanced complaint analysis with like-weighted voting
- **Functionality**:
  - Uses LLM tool calling for structured vote recording
  - Extracts like counts from comments to weight complaint importance
  - Records votes for each normalized complaint
  - Implements robust logging for all operations
  - Handles edge cases and error recovery

### 3. Data Storage

#### JSON Files
- `complaints.json`: Master complaint list with vote tallies
- `comments_to_complaints.json`: Mapping of comments to their normalized complaints
- `like_weighted_complaints.json`: Like-weighted complaint tallies
- `current_vote_tally.json`: Real-time vote tracking

## Project Structure

```
comment_reader/
├── comments/
│   ├── instagram/          # Parsed Instagram comment files
│   └── tiktok/            # Parsed TikTok comment files
├── plans/
│   ├── requirements.md     # Project requirements
│   └── plan.md           # Development plan
├── comment_reading_llm_local.py    # Main LLM analysis
├── comment_like_voter_llm.py       # Like-weighted voting
├── instagram_comment_parser.py     # Instagram parser
├── parse_into_comments_tiktok.py   # TikTok parser
├── complaints.json                 # Complaint tallies
└── README.md                      # This file
```

## How It Works

### 1. Data Ingestion
- Raw comment data is parsed from markdown files using platform-specific parsers
- Comments are split into individual files with metadata extraction
- Files are organized by platform (Instagram/TikTok)

### 2. LLM Analysis
- Each comment is processed by an LLM (via LM Studio) to normalize complaints
- The LLM identifies complaints and maps them to existing categories or creates new ones
- Long comments are chunked to handle token limits

### 3. Vote Tallying
- Complaints are weighted by comment engagement (likes)
- The system maintains running tallies of complaint frequencies
- Progress is saved incrementally to prevent data loss

### 4. Output Generation
- Final complaint tallies are saved to JSON files
- Results can be used for content creation prioritization
- Data supports trend analysis and sentiment tracking

## Getting Started

### Prerequisites
- Python 3.7+
- LM Studio running locally on port 1234
- Virtual environment (recommended)

### Setup

1. **Clone and navigate to the project**:
   ```bash
   cd comment_reader
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install openai tiktoken
   ```

4. **Start LM Studio**:
   - Launch LM Studio
   - Load a model (e.g., qwq-32b-mlx)
   - Start the local server on port 1234

### Usage

1. **Parse raw comment data**:
   ```bash
   # Parse Instagram comments
   python instagram_comment_parser.py <instagram_markdown_file>
   
   # Parse TikTok comments
   python parse_into_comments_tiktok.py <tiktok_markdown_file>
   ```

2. **Run LLM analysis**:
   ```bash
   # Basic complaint normalization
   python comment_reading_llm_local.py
   
   # Like-weighted voting (recommended)
   python comment_like_voter_llm.py
   ```

3. **Check results**:
   - View `complaints.json` for final tallies
   - Check `like_weighted_complaints.json` for engagement-weighted results

## Current Results

The system has processed hundreds of comments and identified key AI-related concerns:

**Top Complaints (by frequency)**:
- AI art theft (15 votes)
- Environmental cost of AI (9 votes)
- AI development under capitalism (8 votes)
- AI-generated low-quality content (8 votes)
- AI's inconsistent behavior (7 votes)

## Next Steps

### Immediate Improvements
1. **Error Handling**: Implement more robust error recovery for LLM failures
2. **Performance**: Add batch processing for large comment datasets
3. **Validation**: Add data validation and quality checks
4. **Visualization**: Create dashboards for complaint trends

### Feature Enhancements
1. **Multi-language Support**: Process comments in different languages
2. **Sentiment Analysis**: Add sentiment scoring to complaints
3. **Trend Detection**: Identify emerging complaint patterns over time
4. **Export Options**: Add CSV/Excel export for external analysis

### Infrastructure
1. **Database Integration**: Move from JSON files to proper database
2. **API Development**: Create REST API for real-time analysis
3. **Web Interface**: Build web dashboard for results visualization
4. **Automation**: Set up scheduled processing for new comments

### Content Creation Integration
1. **Video Prioritization**: Use complaint tallies to prioritize content topics
2. **Response Generation**: Create AI-assisted response content
3. **Engagement Tracking**: Monitor how content addresses specific complaints

## Technical Notes

- **Token Management**: Comments over 4096 tokens are automatically chunked
- **Progress Persistence**: All processing saves progress to prevent data loss
- **Logging**: Comprehensive logging in `comment_like_voter_llm.log`
- **Error Recovery**: System continues processing even if individual comments fail

## Contributing

This is a data analysis project focused on understanding AI sentiment. Contributions should maintain the existing functionality while adding new analysis capabilities or improving data processing efficiency.

## License

This project is for data analysis purposes. Please ensure compliance with platform terms of service when collecting comment data. 