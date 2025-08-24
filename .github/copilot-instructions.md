# Questionnaire Multiagent Application - GitHub Copilot Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Fixing issues

- If you're in VS Code and you're asked to fix issues, always make a branch first.
- When asked to interact with GitHub, use its CLI if needed.
- Use the existing tests wherever possible. Ask a single question first. Use test_excel_processing_1_sheet.py if you need to test a single sheet.
- Only make a new test class if absolutely necessary.

### Bootstrap and Setup
- Install Python dependencies: `pip install -r requirements.txt` -- takes 2-3 minutes on first install. NEVER CANCEL. Set timeout to 5+ minutes.
- Install GUI support: `sudo apt-get update && sudo apt-get install -y python3-tk` -- takes 3-5 minutes. NEVER CANCEL. Set timeout to 10+ minutes.
- Install testing framework: `pip install pytest` -- takes 30 seconds.
- Install Playwright browsers (optional): `playwright install` -- takes 5-15 minutes and may fail due to download issues. This is OK to skip if it fails.

### Environment Configuration
- Create `.env` file in project root with Azure AI Foundry configuration:
```bash
AZURE_OPENAI_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4o-mini
BING_CONNECTION_ID=your-bing-connection-name
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/
```
- Azure CLI authentication is REQUIRED: `az login` before running the application.
- NEVER commit `.env` files to version control (already in .gitignore).
- If you're in VS Code, there's already a virtual environment present at ./venv. Activate this venv before you do anything.
- If you're in VS Code, you can interact with GitHub if needed using the GitHub CLI.

### Running and Testing
- Run GUI application: `python3 question_answerer.py`
- Run CLI application: `python3 question_answerer.py --question "Your question here" --verbose`
- Check CLI help: `python3 question_answerer.py --help`
- Run tests: `python3 -m pytest tests/test_resource_cleanup.py -v` -- takes 5-10 seconds.
- Run tests with unittest: `python3 -m unittest discover tests/ -v` (note: some tests have import issues due to missing main module)

## Validation

### Dependency Installation Validation
- `pip install -r requirements.txt` should install 50+ packages successfully
- Expected packages: azure-ai-projects, azure-identity, python-dotenv, openpyxl, pandas, playwright, aiohttp, azure-monitor-opentelemetry, opentelemetry-sdk
- Installation time: 2-3 minutes for fresh install, under 2 seconds if already installed

### Application Validation
- Without Azure credentials: Application should exit with error "AZURE_OPENAI_ENDPOINT not found in environment variables"
- With invalid credentials: Application should show Azure authentication warnings and fail gracefully
- GUI mode test: Application starts but will exit if no Azure credentials are configured
- CLI help test: `python3 question_answerer.py --help` should show usage and examples

### Test Validation
- `python3 -m pytest tests/test_resource_cleanup.py -v` should pass all 15 tests in under 1 second
- Tests validate Azure AI Foundry resource cleanup and error handling
- Note: `tests/test_questionnaire_agent.py` has import issues (references non-existent `main` module)

### Manual End-to-End Validation
ALWAYS test actual functionality after making changes:
1. Create valid `.env` file with real Azure credentials
2. Run: `python3 question_answerer.py --question "What is the sky blue?" --verbose`
3. Verify it attempts to connect to Azure AI Foundry
4. Test Excel processing: `python3 question_answerer.py --import-excel sample.xlsx --output-excel results.xlsx`
5. Test GUI mode by running without arguments (requires display)

## Common Tasks

### Timeout Values and Timing Expectations
- **CRITICAL**: Always set appropriate timeouts for long-running operations:
  - Dependency installation: 5+ minutes timeout, typically takes 2-3 minutes
  - System package installation: 10+ minutes timeout, typically takes 3-5 minutes
  - Test execution: 1 minute timeout, typically takes 5-10 seconds
  - Playwright installation: 20+ minutes timeout, typically takes 5-15 minutes (may fail)
- **NEVER CANCEL** any build or installation command before timeout expires

### Repository Structure
```
QuestionnaireAgent_v2/
├── question_answerer.py      # Main application (GUI + CLI modes)
├── requirements.txt          # Python dependencies
├── README.md                # Primary documentation
├── README_Questionnaire_UI.md # UI-specific documentation
├── .gitignore               # Git ignore rules
├── tests/                   # Test suite
│   ├── test_resource_cleanup.py      # Resource management tests (working)
│   ├── test_questionnaire_agent.py   # Main logic tests (broken imports)
│   └── sample_questionnaire.xlsx     # Test data
├── utils/                   # Utility modules
│   ├── resource_manager.py  # Azure resource cleanup
│   ├── web_search.py        # Web search utilities
│   └── logger.py            # Logging configuration
└── .env                     # Environment variables (not in repo)
```

### Project Dependencies
- **Python**: 3.8+ (tested with 3.12.3)
- **Azure Services**: AI Foundry project with Bing Search resource
- **GUI Framework**: tkinter (requires python3-tk package on Linux)
- **Key Libraries**: azure-ai-projects, azure-identity, pandas, openpyxl, playwright

### Known Issues and Workarounds
- `tests/test_questionnaire_agent.py` fails due to missing `main` module import
- Playwright browser installation may fail with download errors - this is OK to skip
- Application requires valid Azure credentials and authentication to function
- GUI mode requires display (use virtual display in headless environments)
- Some Azure SDK libraries generate verbose logging warnings

### Development Guidelines
- Application entry point: `question_answerer.py` (not main.py)
- Main class: `QuestionnaireAgentUI` in question_answerer.py
- No build system configured (no setup.py, Makefile, or pyproject.toml)
- No linting tools configured (flake8, black, etc.)
- Tests use pytest and unittest frameworks
- Resource cleanup is critical (see `utils/resource_manager.py`)
- **Reasoning Log Guidelines**: Never include issue numbers (e.g., "Issue #10 fix:") in reasoning log messages. Users should only see clean, descriptive messages without development references.

### Architecture
The application orchestrates three Azure AI Foundry agents:
1. **Question Answerer**: Searches web and generates draft answers
2. **Answer Checker**: Validates factual correctness and completeness  
3. **Link Checker**: Verifies cited URLs are reachable and relevant

Both GUI (tkinter) and CLI modes are supported. Excel import/export functionality is available for batch processing.

## Debugging and Troubleshooting

### Common Error Messages
- "AZURE_OPENAI_ENDPOINT not found" → Create .env file with Azure configuration
- "Please run 'az login'" → Authenticate with Azure CLI
- "Bing connection 'X' not found" → Check BING_CONNECTION_ID in .env file
- "ModuleNotFoundError: No module named 'tkinter'" → Install python3-tk package
- Test import errors → Some tests reference non-existent main module (known issue)

### Validation Commands
Always run these commands before committing changes:
- `python3 question_answerer.py --help` (should show usage)
- `python3 -m pytest tests/test_resource_cleanup.py -v` (should pass all tests)
- `pip install -r requirements.txt` (should install successfully)

### File Locations
- Main application: `/path/to/repo/question_answerer.py`
- Configuration: `/path/to/repo/.env` (create this file)
- Tests: `/path/to/repo/tests/`
- Documentation: `/path/to/repo/README.md`