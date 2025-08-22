## Questionnaire Answering Agent UI spec

You will use Python for this project. You will use the Azure AI Foundry Agent Service and SDK. You have the Microsoft Docs MCP server - use it to look up any details about this project or these SDKs. You will use AzureCliCredential to authenticate to this service.

This folder contains a .env file which has all the information you need to use the Azure AI Foundry Agent Service, including the Foundry project URL. You will never try to stage or commit an .env file, it should always remain in the .gitignore.

You will produce a windowed user interface written in Python that looks like .\questionnaire_ui_prototype.png. It will be in a file called question_answerer.py.

The default value in the Context box should be "Microsoft Azure AI" and the default Character Limit should be 2000.

### 1. Overview

This is a tool that accepts a natural-language question, or a spreadsheet of questions, and orchestrates three agents in sequence:  
1. **Question Answerer**  
2. **Answer Checker**  
3. **Link Checker**

These agents work similarly to those in main.py, which is an earlier CLI version of this concept. It provides good sample code for this spec.

If a question is given in the Question box, then the question answerer only answers that one question. Once the question is answered, any citations or links in the answer should be removed. Links should be saved for the Documentation box. If, after links and citations are removed, the answer is longer than the character limit, then the question answerer agent should be re-run with a revised prompt exhorting it to stay below that character limit. This cycle can repeat up to 3 times.

If the user presses the Import From Excel button, then a File Open dialog is displayed from which the user can select an .xls or .xlsx file. Once this file is opened, the system analyzes it. For each tab in this Excel sheet, it uses the specified LLM - the same one it's using for the agents - to determine what column contains the question, which contains the expected answer, and which contains the documentation. It then produces a new Excel file with exactly the 

---

### Agents

These agents are already defined in this codebase, but modify them as needed to implement this specification.

**Question Answerer**

*Responsibility*

Searches the web for evidence and synthesizes a candidate answer of no longer than the character limit, with its system message set such that it writes answers in the context given in the Context box.

*Tools*

Grounding with Bing Search

**Answer Checker**

*Responsibility*

Validates factual correctness, completeness, and consistency of the candidate

*Tools*

Grounding with Bing Search

**Link Checker**

*Responsibility*

Verifies that every URL cited in the answer is reachable (using CURL or the Python equivalent) and relevant (using Playwright to get the page and analyze its content)

*Tools*

Playwright
CURL should not be provided as a tool to the agent itself - it should be run before this agent runs to verify that each link is even reachable. If a link results in a 404 error or any other kind of error, it should immediately report this error.

---

### Workflow From Direct User Question

All output of all agents are logged to the Reasoning box.

**Read Input**  
   - Accept a question from the Question box.  
   - Initialize an attempt counter at 1.

**Answer Generation**  
   - Question Answerer retrieves evidence and produces a draft answer. The answer is then sanitized to remove links and citations; any links are saved to be vetted by the Link Checker, and if they are valid, to be emitted in the Documentation box.

**Validation**  
   - Answer Checker reviews the draft for accuracy and completeness.  
   - Link Checker tests all cited URLs with CURL first to verify the page is reachable and then with Playwright to ensure it is relevant to the question.

**Decision**  
   - **If both checkers approve:**  
     - Output the final answer and terminate successfully.  
   - **If either checker rejects:**  
     - Log rejection reasons in the Reasoning box.  
     - Increment the attempt counter.  
     - If attempts ≤ the maximum, return to step 2; otherwise, terminate with an error indicating maximum retries reached.
	 
### Workflow From Import From Excel

All output of all agents are logged to the Reasoning box. Each agent will identify itself (with a prefix like "Question Answerer:") in the Reasoning box.

**Read Input File**  
   - Read the file 
   - For each tab, determine which column contains the question, which contains the expected answer, and which contains the documentation.
   
**Create Temporary Copy of Input File**
	- Create a temporary copy of the input file in which to write the answers and documentation links.
	- This copy should be identical to the original, with identical formatting.
   
*For each identified question*:

**Answer Generation**  
   - Initialize an attempt counter at 1.
   - Question Answerer retrieves evidence and produces a draft answer.

**Validation**  
   - Answer Checker reviews the draft for accuracy and completeness.  
   - Link Checker tests all cited URLs with CURL first to verify the page is reachable and then with Playwright to ensure it is relevant to the question.

**Decision**  
   - **If both checkers approve:**  
     - Write the answer to the appropriate cell of the spreadsheet, and the documentation links to the corresponding documentation cell.  
   - **If either checker rejects:**  
     - Log rejection reasons in the Reasoning box.  
     - Increment the attempt counter.  
     - If attempts ≤ the maximum, return to step 2; otherwise, terminate with an error indicating maximum retries reached.
	 
*When all questions are answered*
	- Present a File Save dialog box to the user. Save a copy of the temporary Excel file to the location the user chooses. Delete the temporary file.

---

### Technical specs

Use Azure AI and Azure AI Foundry exclusively. Use the included .env file to access the necessary resources.

You have the Microsoft Docs MCP server - use it to look up any details about this project or these SDKs. You will use AzureCliCredential to authenticate to this service.

- **Infrastructure**
	1. Each agent should be defined as an Azure AI Foundry agent.
	2. For any agent that requires grounding, use the Grounding with Bing Search tool using the Bing resource name provided in the .env file.
	3. Do not use a reasoning model in this version.
