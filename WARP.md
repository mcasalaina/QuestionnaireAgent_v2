# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project: Web-Based Questionnaire Answering Agent (CLI Prototype)

What this repo provides
- A CLI that orchestrates three Azure AI Foundry-powered agents (question answering → answer checking → link checking) with retries until acceptance.
- Robust resource management for Azure AI Foundry agent/thread lifecycle via a context manager to prevent leaks.
- Pytest-based unit tests focused on the orchestrator flow and resource cleanup guarantees.

Common commands (PowerShell on Windows)
- Create and activate a virtual environment, install deps, and build a dev install:
  ```pwsh path=null start=null
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  pip install -e .
  # Dev-only dependency for tests
  pip install pytest
  ```
- Environment configuration (the code loads .env via python-dotenv, but you can also export directly in the shell). At minimum, set a Foundry endpoint:
  ```pwsh path=null start=null
  # Required for both running and testing; can be a dummy URL for unit tests
  $env:AZURE_OPENAI_ENDPOINT = "http://localhost"
  # Optional; defaults vary by agent (see Architecture). Set explicitly to keep behavior consistent.
  $env:AZURE_OPENAI_MODEL_DEPLOYMENT = "gpt-4o-mini"
  # Optional (used by utils/web_search.py)
  $env:BING_CONNECTION_ID = "bing_grounding"
  ```
- Run the CLI (direct and via console script after install):
  ```pwsh path=null start=null
  # Direct
  python .\main.py "Why is the sky blue?" -v
  python .\main.py "What are the benefits of renewable energy?" --debug --log-file .\debug.log

  # After `pip install -e .` (console script is generated)
  questionnaire-agent "Why is the sky blue?"
  ```
- Run the installation smoke test (imports + CLI help):
  ```pwsh path=null start=null
  python .\test_installation.py
  ```
- Run all tests (note: set AZURE_OPENAI_ENDPOINT as above so agent constructors don’t raise):
  ```pwsh path=null start=null
  pytest -q
  ```
- Run a single test or filtered subset:
  ```pwsh path=null start=null
  # Single test method
  pytest .\tests\test_questionnaire_agent.py::TestQuestionnaireAgent::test_happy_path_all_agents_succeed -q
  
  # By test name pattern
  pytest -k "cleanup" -q
  
  # Specific class in a file
  pytest .\tests\test_resource_cleanup.py::TestFoundryAgentSessionCleanup -q
  ```
- Linting/formatting
  - No linter/formatter config is present in this repo (no ruff/flake8/black configs found).

Repository-specific guardrails
- .env files are intentionally ignored by .gitignore; do not stage or commit them.
- __pycache__/ and *.pyc are ignored; do not stage or commit them.

High-level architecture and structure
- Entry point and orchestration
  - main.py defines QuestionnaireAgent and CLI. The orchestrator runs three agents in sequence:
    1) QuestionAnswerer.generate_answer(question)
    2) AnswerChecker.validate_answer(question, candidate_answer)
    3) LinkChecker.validate_links(candidate_answer)
  - Control flow: If AnswerChecker or LinkChecker rejects, the loop retries with a new candidate until MAX_ATTEMPTS is reached; success prints a “FINAL ANSWER” block.
  - MAX_ATTEMPTS is set to 10 in code. Note: README and CLI spec documents mention 25 attempts; tests assert 10. Keep this in mind if changing behavior—update both docs and tests together.
  - Logging levels are wired via utils.logger.setup_logger. --debug enables Azure SDK HTTP logging; --verbose is INFO-level; default is ERROR.

- Agents (Azure AI Foundry via azure-ai-projects)
  - Shared behavior:
    - All agents use DefaultAzureCredential() with AIProjectClient(endpoint=$env:AZURE_OPENAI_ENDPOINT). No connection is made at construction; but AZURE_OPENAI_ENDPOINT must be set or constructors raise.
    - All agent calls are wrapped in FoundryAgentSession to ensure agent/thread resources are created and then deleted, even on exceptions.
    - Responses are obtained by writing a user message to the thread, then create_and_process a run, then scanning assistant messages for text content.
  - QuestionAnswerer (agents/question_answerer.py)
    - Default model via env: AZURE_OPENAI_MODEL_DEPLOYMENT (default 'gpt-4o-mini').
    - Uses long instructions that strictly enforce third-person answers, no follow-up questions, and citation requirements.
    - Produces a synthesized candidate answer grounded by web search (via Foundry’s Bing grounding under the hood of the agent service).
  - AnswerChecker (agents/answer_checker.py)
    - Default model: env AZURE_OPENAI_MODEL_DEPLOYMENT or fallback 'gpt-4.1'.
    - Validates factual accuracy (with grounding), completeness, proper citations, strict third-person style, and forbids follow-up prompts. Expects validation output of the form ‘VALID’ or ‘INVALID: ...’ and parses accordingly.
  - LinkChecker (agents/link_checker.py)
    - Default model: env AZURE_OPENAI_MODEL_DEPLOYMENT or fallback 'gpt-4.1'.
    - Extracts URLs from the candidate answer (markdown and plain links), cleans trailing punctuation, and validates via an agent prompt. Returns a VALID/INVALID judgment with feedback. A requests.Session exists for direct HTTP checks but current validation logic relies on the Foundry agent response.

- Resource management (utils/resource_manager.py)
  - FoundryAgentSession is a context manager that:
    - Creates an agent (client.agents.create_agent(...)) and a thread (client.agents.threads.create(...)) on enter, returning (agent, thread).
    - Stores IDs robustly whether the SDK returns objects with .id, dictionaries with 'id', or direct string IDs.
    - On exit, always attempts to delete thread first, then agent, suppressing cleanup exceptions so they do not mask the original error. Cleanup is attempted even if construction partially failed.
    - get_agent_id/get_thread_id are available for diagnostics across the context lifetime.

- Web search helper (utils/web_search.py)
  - AzureAIFoundrySearcher uses BingGroundingTool (azure.ai.agents.models) by constructing an agent with tool definitions/resources and then performing a run. It parses assistant text for URLs (regex) to structure results.
  - BING_CONNECTION_ID defaults to 'bing_grounding'.
  - The module also offers a get_page_content method that requests an agent summarize the URL content through the same mechanism. If Bing grounding is unavailable, methods fall back to simple stubbed results.

- Tests
  - tests/test_questionnaire_agent.py: Mocks sub-agents to verify orchestrator success path, fail-fast on exception, retry acceptance on second attempt, and MAX_ATTEMPTS == 10.
  - tests/test_resource_cleanup.py: Thoroughly validates FoundryAgentSession cleanup semantics across success/failure cases, partial failures, and various return formats (object/dict/string IDs).
  - test_installation.py: Smoke test ensuring imports and CLI help work.
  - Important for local runs: Ensure AZURE_OPENAI_ENDPOINT is set (a dummy URL is acceptable) so agent constructors in QuestionnaireAgent.__init__ do not raise.

Important documents in repo (summarized)
- README.md: Provides overview, usage examples, environment variables, and a component/workflow description consistent with the code. Values to note:
  - Required envs: AZURE_OPENAI_ENDPOINT; AZURE_OPENAI_MODEL_DEPLOYMENT recommended.
  - After install, console script questionnaire-agent is available.
- QuestionnaireAgent-CLI-spec.md: Mirrors the core design and workflow expectations of the CLI agent system.
- Questionnaire_UI_Agent_spec.md: A future/alternate UI direction. It states AzureCliCredential, while the current code uses DefaultAzureCredential—align credential strategy if building the UI.

Conventions and gotchas
- Credentials: DefaultAzureCredential is used by all agents. For real calls (beyond unit tests), ensure az login or equivalent environment credentials are available for the SDK to acquire a token.
- Model selection: Defaults differ across agents (QuestionAnswerer defaults to gpt-4o-mini; checker/link checker default to gpt-4.1). Set AZURE_OPENAI_MODEL_DEPLOYMENT to the same deployment to keep behavior consistent across agents.
- Attempt limit: The code uses 10; docs reference 25. Update code, docs, and tests together if changing.
- Cleanup: Always instantiate agents within FoundryAgentSession to avoid stranding Foundry resources.

