# Questionnaire Multiagent UI

A windowed application that orchestrates three Azure AI Foundry agents to answer questions with fact-checking and link validation. Supports both individual questions and Excel import/export functionality.

## Features

- **Three-Agent Workflow**: Question Answerer, Answer Checker, and Link Checker work in sequence
- **Character Limit Enforcement**: Configurable character limits with automatic retries
- **Link Validation**: Validates URLs for reachability and relevance
- **Excel Integration**: Import questions from Excel files and export results
- **Real-time Feedback**: Live reasoning display showing agent progress
- **Azure AI Foundry Integration**: Uses Azure AI Foundry Agent Service with Bing grounding

## Architecture

### Agents

1. **Question Answerer**
   - Searches the web using Bing grounding
   - Synthesizes comprehensive answers with citations
   - Respects context and character limits

2. **Answer Checker** 
   - Validates factual correctness and completeness
   - Uses web search to verify claims
   - Provides approval/rejection feedback

3. **Link Checker**
   - Tests URL reachability using HTTP requests
   - Validates link relevance to the question
   - Filters out broken or irrelevant links

### Workflow

For single questions:
1. User enters question, context, and character limit
2. Question Answerer generates candidate answer
3. Links and citations are extracted and cleaned
4. Answer Checker validates the response
5. Link Checker verifies all URLs
6. Process repeats up to 3 times if validation fails
7. Final answer and documentation links are displayed

For Excel files:
1. System analyzes Excel structure to identify columns
2. Each question is processed through the full workflow
3. Results are saved to answer and documentation columns
4. User chooses save location for processed file

## Setup

### Prerequisites

- Python 3.8+
- Azure subscription with AI Foundry project
- Azure CLI installed and authenticated (`az login`)
- Bing Search resource connected to your AI Foundry project

### Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure your `.env` file is properly configured (see Environment Variables section)

### Environment Variables

The `.env` file should contain:

```bash
AZURE_OPENAI_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4.1
BING_CONNECTION_ID=your-bing-connection-name
```

**Finding your values:**
- `AZURE_OPENAI_ENDPOINT`: Found in Azure AI Foundry portal under project overview
- `AZURE_OPENAI_MODEL_DEPLOYMENT`: Your model deployment name from Models + Endpoints
- `BING_CONNECTION_ID`: Connection **name** (not ID) from Connected Resources in your project. The application will automatically retrieve the actual connection ID from this name.

## Usage

### Running the Application

```bash
python question_answerer.py
```

### Single Question Mode

1. Enter your context (default: "Microsoft Azure AI")
2. Set character limit (default: 2000)
3. Type your question
4. Click "Ask!" button
5. Monitor progress in the Reasoning tab
6. View results in Answer and Documentation tabs

### Excel Import Mode

1. Click "Import From Excel" button
2. Select an Excel file with questions
3. System automatically identifies question columns
4. Processing begins with real-time progress updates
5. Choose save location when complete

**Excel File Format:**
- Questions can be in any column (system auto-detects)
- Answer and documentation columns will be created if missing
- Supports multiple sheets
- Preserves original formatting

## Testing

Run the core functionality test:

```bash
python test_core_functionality.py
```

This tests:
- Environment variable configuration
- Import dependencies 
- Azure authentication
- Basic functionality

## Troubleshooting

### Common Issues

**"Failed to connect to Azure AI Foundry"**
- Run `az login` to authenticate with Azure
- Verify your endpoint URL in the .env file
- Check that you have access to the AI Foundry project

**"BING_CONNECTION_ID not found"**
- Verify Bing Search resource is connected to your project
- Check the connection name in Azure AI Foundry portal

**"No module named '_tkinter'"**
- tkinter is required for the GUI
- On Ubuntu/Debian: `sudo apt-get install python3-tk`
- On macOS with Homebrew: tkinter should be included
- Consider using a different Python installation if issues persist

**"Character limit exceeded"**
- The system automatically retries with stricter prompts
- Reduce the character limit for shorter answers
- Check the reasoning tab for retry attempts

### Performance Notes

- Each question requires multiple agent calls (3+ API requests)
- Excel processing time depends on number of questions
- Large Excel files may take several minutes to process
- Network connectivity affects Bing search performance

## File Structure

```
├── question_answerer.py          # Main UI application
├── test_core_functionality.py    # Core functionality tests
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (not tracked)
├── .gitignore                    # Git ignore rules
└── README_Questionnaire_UI.md    # This documentation
```

## Dependencies

Key packages:
- `azure-ai-projects`: Azure AI Foundry Agent Service SDK
- `azure-identity`: Azure authentication
- `azure-ai-agents`: Agent models and tools
- `pandas`: Excel file processing
- `openpyxl`: Excel format support
- `requests`: HTTP requests for link checking
- `python-dotenv`: Environment variable management

## Security Notes

- The `.env` file contains sensitive credentials and is excluded from git
- Never commit API keys or connection strings to version control
- Use Azure managed identities in production environments
- Link validation involves making external HTTP requests

## Limitations

- Maximum 3 retry attempts per question
- GUI requires tkinter support in Python environment
- Bing search results depend on external service availability
- Excel processing is sequential (not parallelized)
- Link checking uses simple HTTP HEAD requests

## Support

For issues related to:
- Azure AI Foundry: Check Azure documentation and support channels
- Application bugs: Review error messages in the Reasoning tab
- Excel processing: Ensure proper file format and permissions
- Authentication: Verify Azure CLI login and permissions

---

Built with Azure AI Foundry Agent Service and Python tkinter.