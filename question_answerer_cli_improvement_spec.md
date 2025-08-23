# CLI Mode for Question_answerer

Make 'question_answerer.py' have a second mode wherein it's called via the command line. If it is launched with no arguments, then it should open in its UI mode as it presently does. If it is launched with arguments then it should run headlessly on the command line.

## Allowed Arguments

The CLI should expose the same inputs that are available in the UI so users can run the agent headlessly. If any arguments are provided the app will run in CLI/headless mode and should not open the GUI. If no arguments are provided the app opens the existing Tkinter UI.

Usage: 'question_answerer.py [OPTIONS]'

Options:

- '-q', '--question TEXT' : The natural-language question to ask. This maps to the 'Question' text area in the UI. If omitted when not using '--import-excel', the program should exit with an error explaining that a question or an import file is required.
- '-c', '--context TEXT' : Context or topic string to bias the question answering (UI default: 'Microsoft Azure AI'). If omitted the UI default should be applied.
- '--char-limit N' : Integer character limit for the final answer (UI default: '2000'). If the generated answer exceeds this value the agent may retry (matching UI logic). Default: '2000'.
- '--import-excel PATH' : Path to an Excel file to process in batch. When provided the tool should process questions found in the workbook using the same workflow as the UI 'Import From Excel' button. The CLI must not open file dialogs when this option is used.
- '--output-excel PATH' : Path where the processed Excel file will be written. This provides a non-interactive alternative to the save-file dialog used in the UI. If not provided and '--import-excel' is used, the program should write a processed file beside the input file with a '.answered.xlsx' suffix.
- '--verbose' : Enable verbose / reasoning log output to stdout (mirrors the UI reasoning log pane). Useful for debugging headless runs. If not specified, this should default to true.
- '-h', '--help' : Show help and exit.

Examples:

Run a single question headless and print the final answer:

'''bash
python3 question_answerer.py --question "Does your service offer video generative AI?" --context "Microsoft Azure AI" --char-limit 2000
'''

Process an Excel workbook and save results to a provided output path:

'''bash
python3 question_answerer.py --import-excel /path/to/questions.xlsx --output-excel /path/to/questions.processed.xlsx --context "Microsoft Azure AI" --char-limit 2000 --verbose
'''

Notes and implementation considerations:

- The CLI arguments above map directly to the controls in 'question_answerer.py''s UI: the 'Question' field, the 'Context' entry, the 'Character Limit' entry, and the 'Import From Excel' action.
- When running in CLI/headless mode the program should avoid any GUI interactions (no file dialogs, no message boxes). All required inputs must be provided via arguments; if a non-interactive workflow would otherwise require user input the program should fail with a clear error code and message.
- The CLI should preserve the same defaults as the UI ('Context' default: 'Microsoft Azure AI', 'char-limit' default: '2000').
- When '--import-excel' is used, the CLI should perform the same column-detection and sheet processing logic as the UI path and write the processed workbook to '--output-excel' when provided; otherwise write a sibling file with the '.processed.xlsx' suffix.
