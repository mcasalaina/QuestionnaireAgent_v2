## Web-Based Questionnaire Answering Agent (CLI Prototype)

### 1. Overview
A command-line tool that accepts a natural-language question and orchestrates three agents in sequence:  
1. **Question Answerer**  
2. **Answer Checker**  
3. **Link Checker**  

Each agent uses web grounding to perform its task. If either checker rejects the answer, the Question Answerer reformulates and the cycle repeats up to 25 attempts.

---

### 2. Components

| Component               | Responsibility                                                                 | Grounding Source    |
|-------------------------|--------------------------------------------------------------------------------|---------------------|
| **Question Answerer**   | Searches the web for evidence, synthesizes a candidate answer                  | Web search API      |
| **Answer Checker**      | Validates factual correctness, completeness, and consistency of the candidate  | Web search API      |
| **Link Checker**        | Verifies that every URL cited in the answer is reachable and relevant          | HTTP requests + web search |

---

### 3. Workflow

1. **Read Input**  
   - Accept a question from the command line.  
   - Initialize an attempt counter at 1.

2. **Answer Generation**  
   - Question Answerer retrieves evidence and produces a draft answer.

3. **Validation**  
   - Answer Checker reviews the draft for accuracy and completeness.  
   - Link Checker tests all cited URLs for reachability and relevance.

4. **Decision**  
   - **If both checkers approve:**  
     - Output the final answer and terminate successfully.  
   - **If either checker rejects:**  
     - Log rejection reasons.  
     - Increment the attempt counter.  
     - If attempts ≤ 25, return to step 2; otherwise, terminate with an error indicating maximum retries reached.

---

### 4. CLI Usage

- **Installation**  
  1. Install dependencies.  
  2. Build the project.

- **Run**  
  ```bash or whatever shell you're using
  $ questionnaire-agent "Why is the sky blue?"
