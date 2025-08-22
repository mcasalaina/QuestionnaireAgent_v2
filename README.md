# Web-Based Questionnaire Answering Agent (CLI Prototype)

A command-line tool that accepts a natural-language question and orchestrates three agents in sequence to provide a well-researched, fact-checked answer with verified sources.

## Overview

This tool implements a multi-agent system that:

1. **Question Answerer**: Searches the web for evidence and synthesizes a candidate answer
2. **Answer Checker**: Validates factual correctness, completeness, and consistency
3. **Link Checker**: Verifies that every URL cited in the answer is reachable and relevant

If either checker rejects the answer, the Question Answerer reformulates and the cycle repeats up to 25 attempts.

## Features

- **Web Grounding**: All agents use web search to ground their decisions
- **Multi-agent Validation**: Three-stage validation ensures answer quality
- **Retry Logic**: Up to 25 attempts to generate an acceptable answer
- **Source Verification**: All cited URLs are checked for reachability and relevance
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## Installation

### Prerequisites

- Python 3.7 or higher
- Internet connection for web search functionality

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Build the Project

```bash
pip install -e .
```

## Usage

### Basic Usage

```bash
python main.py "Why is the sky blue?"
```

### With Verbose Logging

```bash
python main.py "What are the benefits of renewable energy?" --verbose
```

### Save Logs to File

```bash
python main.py "How does photosynthesis work?" --log-file debug.log
```

### Using as Installed Command

After installation with `pip install -e .`:

```bash
questionnaire-agent "Why is the sky blue?"
```

## Example Output

```
================================================================================
FINAL ANSWER:
================================================================================
Based on web search results, here's what I found:

The sky appears blue due to a phenomenon called Rayleigh scattering. When sunlight enters Earth's atmosphere, it collides with tiny gas molecules. Blue light has a shorter wavelength than other colors, so it gets scattered more in all directions by these molecules. This scattered blue light is what we see when we look at the sky.

Sources:
- [NASA Science](https://science.nasa.gov/earth/earth-atmosphere/why-is-the-sky-blue/)
- [National Weather Service](https://www.weather.gov/jetstream/color)
================================================================================
```

## Architecture

### Components

| Component | Responsibility | Grounding Source |
|-----------|---------------|------------------|
| **Question Answerer** | Searches the web for evidence, synthesizes a candidate answer | Web search API |
| **Answer Checker** | Validates factual correctness, completeness, and consistency | Web search API |
| **Link Checker** | Verifies that every URL cited in the answer is reachable and relevant | HTTP requests + web search |

### Workflow

1. **Read Input**: Accept a question from the command line
2. **Answer Generation**: Question Answerer retrieves evidence and produces a draft answer
3. **Validation**: 
   - Answer Checker reviews the draft for accuracy and completeness
   - Link Checker tests all cited URLs for reachability and relevance
4. **Decision**:
   - If both checkers approve: Output the final answer and terminate successfully
   - If either checker rejects: Log rejection reasons, increment attempt counter, and retry (up to 25 attempts)

## Configuration

### Environment Variables

The application requires Azure AI Foundry credentials configured through environment variables:

```bash
# Required Azure AI Foundry settings
AZURE_OPENAI_ENDPOINT=your-azure-ai-foundry-endpoint
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4o-mini
```

**Important**: Never commit environment files (`.env`) to version control. The `.gitignore` file already excludes these files to prevent accidental commits.

### FoundryAgentSession Helper

The `FoundryAgentSession` class in `utils/resource_manager.py` provides a context manager for safely managing Azure AI Foundry agent and thread resources. This helper is **required** because:

1. **Resource Cleanup**: Azure AI Foundry agents and threads are persistent resources that must be explicitly deleted to avoid resource leaks
2. **Exception Safety**: Ensures cleanup occurs even if exceptions are raised during agent operations
3. **Cost Management**: Prevents accumulation of unused resources that could incur costs

Usage example:
```python
with FoundryAgentSession(client, model="gpt-4o-mini", 
                        name="my-agent", 
                        instructions="You are a helpful assistant") as (agent, thread):
    # Use agent and thread for operations
    # Resources are automatically cleaned up when exiting the context
```

The context manager handles:
- Creating agent and thread resources on entry
- Automatic cleanup on exit (even if exceptions occur)
- Robust error handling during cleanup to prevent masking original exceptions

### API Configuration

The tool uses Azure AI Foundry with integrated Bing search grounding. For alternative search APIs, consider:

- Google Custom Search API
- Bing Search API  
- SerpAPI

## Limitations

- **Demo Implementation**: Uses basic web search and text processing
- **Rate Limiting**: May encounter rate limits with free APIs
- **Language Support**: Optimized for English questions
- **Fact Checking**: Uses heuristic-based validation rather than advanced fact-checking

## Development

### Project Structure

```
questionnaire-agent/
├── main.py                 # CLI entry point
├── agents/                 # Agent implementations
│   ├── __init__.py
│   ├── question_answerer.py
│   ├── answer_checker.py
│   └── link_checker.py
├── utils/                  # Shared utilities
│   ├── __init__.py
│   ├── logger.py
│   └── web_search.py
├── requirements.txt        # Python dependencies
├── setup.py               # Installation script
└── README.md              # This file
```

### Adding New Features

To extend the system:

1. **New Validation**: Add checks to `AnswerChecker`
2. **Better Search**: Upgrade `WebSearcher` with more sophisticated APIs
3. **Advanced NLP**: Integrate language models for better synthesis and validation
4. **Caching**: Add response caching to reduce API calls

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please read the contributing guidelines and submit pull requests for any improvements.
