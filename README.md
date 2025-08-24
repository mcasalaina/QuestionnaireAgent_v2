# Questionnaire Multiagent Application

A windowed application that orchestrates three Azure AI Foundry agents to answer questions with fact-checking and link validation. Features both individual question processing and Excel import/export functionality, with a legacy command-line interface also available.

## Overview

This tool implements a multi-agent system that:

1. **Question Answerer**: Searches the web for evidence and synthesizes a candidate answer
2. **Answer Checker**: Validates factual correctness, completeness, and consistency
3. **Link Checker**: Verifies that every URL cited in the answer is reachable and relevant

If either checker rejects the answer, the Question Answerer reformulates and the cycle repeats up to 25 attempts.

## Features

- **Windowed GUI**: User-friendly interface built with Python tkinter
- **Excel Integration**: Import questions from Excel files and export results
- **Real-time Progress**: Live reasoning display showing agent workflow
- **Character Limit Control**: Configurable answer length with automatic retries
- **Web Grounding**: All agents use Bing search via Azure AI Foundry
- **Multi-agent Validation**: Three-stage validation ensures answer quality
- **Source Verification**: All cited URLs are checked for reachability and relevance
- **Legacy CLI Support**: Command-line interface still available for automation

## Installation

### Prerequisites

- Python 3.8 or higher
- Azure subscription with AI Foundry project
- Azure CLI installed and authenticated (`az login`)
- Bing Search resource connected to your AI Foundry project

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Build the Project

```bash
pip install -e .
```

## Usage

### Primary GUI Application

Run the main windowed application:

```bash
python question_answerer.py
```

**Single Question Mode:**
1. Enter your context (default: "Microsoft Azure AI")
2. Set character limit (default: 2000)
3. Type your question and click "Ask!"
4. Monitor progress in the Reasoning tab
5. View results in Answer and Documentation tabs

**Excel Import Mode:**
1. Click "Import From Excel" button
2. Select Excel file with questions
3. System auto-detects question columns
4. Monitor real-time processing progress
5. Choose save location when complete

### Legacy CLI Interface

For automation and scripting:

```bash
python main.py "Why is the sky blue?"
```

With verbose logging:
```bash
python main.py "What are the benefits of renewable energy?" --verbose
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

Create a `.env` file in the project root with your Azure AI Foundry configuration:

```bash
AZURE_OPENAI_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4.1
BING_CONNECTION_ID=your-bing-connection-name
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/;LiveEndpoint=https://your-region.livediagnostics.monitor.azure.com/;ApplicationId=your-app-id
```

**Finding your values:**
- `AZURE_OPENAI_ENDPOINT`: Found in Azure AI Foundry portal under project overview
- `AZURE_OPENAI_MODEL_DEPLOYMENT`: Your model deployment name from Models + Endpoints  
- `BING_CONNECTION_ID`: Connection name (not ID) from Connected Resources in your project
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Found in Azure Portal > Application Insights > Overview. Enables Azure AI Foundry tracing to monitor application performance, track agent interactions, and debug issues. Optional but recommended for production monitoring.

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
QuestionnaireAgent_v2/
├── question_answerer.py         # Main GUI application
├── main.py                      # Legacy CLI entry point
├── agents/                      # Agent implementations
│   ├── __init__.py
│   ├── question_answerer.py
│   ├── answer_checker.py
│   └── link_checker.py
├── utils/                       # Shared utilities
│   ├── __init__.py
│   ├── logger.py
│   ├── resource_manager.py      # Azure AI Foundry resource management
│   └── web_search.py
├── tests/                       # Test suite
├── requirements.txt             # Python dependencies
├── setup.py                     # Installation script
├── README.md                    # This documentation
└── README_Questionnaire_UI.md   # Detailed UI documentation
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
