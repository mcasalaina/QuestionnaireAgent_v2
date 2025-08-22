#!/usr/bin/env python3
"""
Questionnaire Multiagent - UI Application

A windowed application that orchestrates three Azure AI Foundry agents to answer questions
with fact-checking and link validation. Supports both individual questions and Excel import/export.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import tempfile
import asyncio
import logging
from typing import Tuple, Optional, List, Dict, Any
from pathlib import Path

import pandas as pd
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import BingGroundingTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QuestionnaireAgentUI:
    """Main UI application for the Questionnaire Agent."""
    
    def __init__(self):
        # Setup logging first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.root = tk.Tk()
        self.root.title("Questionnaire Multiagent")
        self.root.geometry("1200x800")
        
        # Initialize Azure AI Project Client
        self.project_client = None
        self.init_azure_client()
        
        # Agent IDs will be set when agents are created
        self.question_answerer_id = None
        self.answer_checker_id = None
        self.link_checker_id = None
        
        # Setup UI
        self.setup_ui()
        
    def init_azure_client(self):
        """Initialize Azure AI Project Client with credentials from .env file."""
        try:
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            if not endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT not found in environment variables")
            
            credential = DefaultAzureCredential()
            self.project_client = AIProjectClient(
                endpoint=endpoint,
                credential=credential
            )
            self.logger.info("Azure AI Project Client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure client: {e}")
            messagebox.showerror("Azure Connection Error", 
                               f"Failed to connect to Azure AI Foundry:\n{e}\n\nPlease check your .env file and Azure credentials.")
    
    def setup_ui(self):
        """Setup the main UI layout."""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right panel
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
        
    def setup_left_panel(self, parent):
        """Setup the left panel with input controls."""
        # Context section
        context_label = ttk.Label(parent, text="Context")
        context_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.context_entry = tk.Entry(parent, width=40)
        self.context_entry.insert(0, "Microsoft Azure AI")  # Default value
        self.context_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Character Limit section
        limit_label = ttk.Label(parent, text="Character Limit")
        limit_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.limit_entry = tk.Entry(parent, width=40)
        self.limit_entry.insert(0, "2000")  # Default value
        self.limit_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Question section
        question_label = ttk.Label(parent, text="Question")
        question_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.question_text = scrolledtext.ScrolledText(parent, height=8, width=40)
        self.question_text.insert(tk.END, "Does your service offer video generative AI?")  # Default value
        self.question_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.ask_button = tk.Button(button_frame, text="Ask!", bg="lightgray", fg="black", 
                                  height=2, command=self.on_ask_clicked)
        self.ask_button.pack(fill=tk.X, pady=(0, 10))
        
        self.import_button = tk.Button(button_frame, text="📊 Import From Excel", 
                                     command=self.on_import_excel_clicked)
        self.import_button.pack(fill=tk.X)
        
    def setup_right_panel(self, parent):
        """Setup the right panel with output sections."""
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Answer tab
        answer_frame = ttk.Frame(self.notebook)
        self.notebook.add(answer_frame, text="Answer")
        
        answer_label = ttk.Label(answer_frame, text="Answer")
        answer_label.pack(anchor=tk.W, pady=(5, 5))
        
        self.answer_text = scrolledtext.ScrolledText(answer_frame, wrap=tk.WORD)
        self.answer_text.insert(tk.END, "Response will appear here after clicking Ask!")
        self.answer_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Documentation tab
        docs_frame = ttk.Frame(self.notebook)
        self.notebook.add(docs_frame, text="Documentation")
        
        docs_label = ttk.Label(docs_frame, text="Documentation")
        docs_label.pack(anchor=tk.W, pady=(5, 5))
        
        self.docs_text = scrolledtext.ScrolledText(docs_frame, wrap=tk.WORD)
        self.docs_text.insert(tk.END, "Documentation will appear here...")
        self.docs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Reasoning tab
        reasoning_frame = ttk.Frame(self.notebook)
        self.notebook.add(reasoning_frame, text="Reasoning")
        
        reasoning_label = ttk.Label(reasoning_frame, text="Reasoning")
        reasoning_label.pack(anchor=tk.W, pady=(5, 5))
        
        self.reasoning_text = scrolledtext.ScrolledText(reasoning_frame, wrap=tk.WORD)
        self.reasoning_text.insert(tk.END, "Reasoning will appear here...")
        self.reasoning_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
    def log_reasoning(self, message: str):
        """Add a message to the reasoning text area."""
        self.reasoning_text.insert(tk.END, f"{message}\n")
        self.reasoning_text.see(tk.END)
        self.root.update_idletasks()
        
    def on_ask_clicked(self):
        """Handle the Ask button click."""
        # Disable button during processing
        self.ask_button.config(state=tk.DISABLED)
        
        # Switch to Reasoning tab immediately
        self.notebook.select(2)  # Index 2 is the Reasoning tab (Answer=0, Documentation=1, Reasoning=2)
        
        # Clear previous results
        self.answer_text.delete(1.0, tk.END)
        self.docs_text.delete(1.0, tk.END)
        self.reasoning_text.delete(1.0, tk.END)
        
        # Get input values
        question = self.question_text.get(1.0, tk.END).strip()
        context = self.context_entry.get().strip()
        char_limit = int(self.limit_entry.get()) if self.limit_entry.get().isdigit() else 2000
        
        if not question:
            messagebox.showwarning("Input Required", "Please enter a question.")
            self.ask_button.config(state=tk.NORMAL)
            return
            
        # Run processing in separate thread
        thread = threading.Thread(target=self.process_single_question, 
                                args=(question, context, char_limit))
        thread.daemon = True
        thread.start()
        
    def process_single_question(self, question: str, context: str, char_limit: int):
        """Process a single question using the three-agent workflow."""
        try:
            self.log_reasoning("Starting question processing...")
            
            # Create agents if not already created
            if not all([self.question_answerer_id, self.answer_checker_id, self.link_checker_id]):
                self.create_agents()
            
            attempt = 1
            max_attempts = 3
            
            while attempt <= max_attempts:
                self.log_reasoning(f"Attempt {attempt}/{max_attempts}")
                
                # Step 1: Generate answer
                self.log_reasoning("Question Answerer: Generating answer...")
                candidate_answer, doc_urls = self.generate_answer(question, context, char_limit)
                
                if not candidate_answer:
                    self.log_reasoning("Question Answerer failed to generate an answer")
                    break
                
                # Log the raw answer before processing
                self.log_reasoning("=== RAW ANSWER FROM QUESTION ANSWERER ===")
                self.log_reasoning(candidate_answer)
                self.log_reasoning("=== END RAW ANSWER ===")
                
                # Remove links and citations, save links for documentation
                clean_answer, text_links = self.extract_links_and_clean(candidate_answer)
                
                self.log_reasoning("=== CLEANED ANSWER AFTER URL EXTRACTION ===")
                self.log_reasoning(clean_answer)
                self.log_reasoning("=== END CLEANED ANSWER ===")
                
                self.log_reasoning(f"Extracted {len(text_links)} URLs from answer text")
                for link in text_links:
                    self.log_reasoning(f"  Text URL: {link}")
                
                # Combine documentation URLs from run steps with any URLs found in text
                all_links = list(set(doc_urls + text_links))  # Remove duplicates
                self.log_reasoning(f"Total combined URLs: {len(all_links)}")
                for link in all_links:
                    self.log_reasoning(f"  Combined URL: {link}")
                
                # Check character limit
                if len(clean_answer) > char_limit:
                    self.log_reasoning(f"Answer exceeds character limit ({len(clean_answer)} > {char_limit}). Retrying...")
                    attempt += 1
                    continue
                
                # Step 2: Validate answer
                self.log_reasoning("Answer Checker: Validating answer...")
                answer_valid, answer_feedback = self.validate_answer(question, clean_answer)
                
                if not answer_valid:
                    self.log_reasoning(f"Answer Checker rejected: {answer_feedback}")
                    attempt += 1
                    continue
                
                # Step 3: Validate links
                self.log_reasoning("Link Checker: Verifying URLs...")
                links_valid, valid_links, link_feedback = self.validate_links(all_links)
                
                if not links_valid:
                    self.log_reasoning(f"Link Checker rejected: {link_feedback}")
                    attempt += 1
                    continue
                
                # All checks passed
                self.log_reasoning("All agents approved the answer!")
                
                # Update UI with results
                self.root.after(0, lambda: self.update_results(clean_answer, valid_links))
                break
                
            else:
                # Max attempts reached
                self.log_reasoning(f"Failed to generate acceptable answer after {max_attempts} attempts")
                self.root.after(0, lambda: messagebox.showerror("Processing Failed", 
                    f"Could not generate an acceptable answer after {max_attempts} attempts."))
                
        except Exception as e:
            self.logger.error(f"Error processing question: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
        finally:
            # Re-enable button
            self.root.after(0, lambda: self.ask_button.config(state=tk.NORMAL))
            
    def update_results(self, answer: str, links: List[str]):
        """Update the UI with the final answer and documentation."""
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, answer)
        
        self.docs_text.delete(1.0, tk.END)
        if links:
            self.docs_text.insert(tk.END, "Documentation links:\n\n")
            for link in links:
                self.docs_text.insert(tk.END, f"• {link}\n")
        else:
            self.docs_text.insert(tk.END, "No documentation links found.")
            
    def create_agents(self):
        """Create the three Azure AI Foundry agents."""
        try:
            self.log_reasoning("Creating Azure AI Foundry agents...")
            
            # Get model deployment name from environment
            model_deployment = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT", "gpt-4.1")
            bing_resource_name = os.getenv("BING_CONNECTION_ID")
            
            if not bing_resource_name:
                raise ValueError("BING_CONNECTION_ID not found in environment variables")
            
            # Get the actual connection ID from the resource name
            self.log_reasoning(f"Getting connection ID for resource: {bing_resource_name}")
            connection = self.project_client.connections.get(name=bing_resource_name)
            conn_id = connection.id
            self.log_reasoning(f"Retrieved connection ID: {conn_id}")
            
            # Create Bing grounding tool
            bing_tool = BingGroundingTool(connection_id=conn_id)
            
            # Create Question Answerer agent
            question_answerer = self.project_client.agents.create_agent(
                model=model_deployment,
                name="Question Answerer",
                instructions="You are a question answering agent. You MUST search the web extensively for evidence and synthesize accurate answers. Your answer must be based on current web search results. IMPORTANT: You must include the actual source URLs directly in your answer text. Write the full URLs (like https://docs.microsoft.com/example) in your response text where you reference information. Do not use citation markers like [1], (source), or 【†source】 - instead include the actual URLs. Write in plain text without formatting. Your answer must end with a period and contain only complete sentences. Do not include any closing phrases like 'Learn more:', 'References:', questions, or calls-to-action at the end. Always use the Bing grounding tool to search for current information.",
                tools=bing_tool.definitions
            )
            self.question_answerer_id = question_answerer.id
            
            # Create Answer Checker agent
            answer_checker = self.project_client.agents.create_agent(
                model=model_deployment,
                name="Answer Checker",
                instructions="You are an answer validation agent. Review candidate answers for factual correctness, completeness, and consistency. Use web search to verify claims. Respond with 'VALID' if the answer is acceptable or 'INVALID: [reason]' if not.",
                tools=bing_tool.definitions
            )
            self.answer_checker_id = answer_checker.id
            
            # Create Link Checker agent
            link_checker = self.project_client.agents.create_agent(
                model=model_deployment,
                name="Link Checker",
                instructions="You are a link validation agent. Verify that URLs are reachable and relevant to the given question. Report any issues with links.",
                tools=[]  # Will use requests/playwright for link checking
            )
            self.link_checker_id = link_checker.id
            
            self.log_reasoning("All agents created successfully!")
            
        except Exception as e:
            self.logger.error(f"Failed to create agents: {e}")
            raise
            
    def generate_answer(self, question: str, context: str, char_limit: int) -> Tuple[Optional[str], List[str]]:
        """Generate an answer using the Question Answerer agent."""
        try:
            # Create thread
            thread = self.project_client.agents.threads.create()
            self.log_reasoning(f"Created thread: {thread.id}")
            
            # Create message
            message = self.project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"Context: {context}\n\nQuestion: {question}\n\nPlease provide a comprehensive answer with supporting evidence and citations. Keep it under {char_limit} characters."
            )
            self.log_reasoning(f"Created message: {message.id}")
            
            # Create and process run
            run = self.project_client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=self.question_answerer_id
            )
            
            self.log_reasoning(f"Run finished with status: {run.status}")
            
            # Check if the run failed
            if run.status == "failed":
                error_msg = f"Run failed: {run.last_error.message if run.last_error else 'Unknown error'}"
                self.log_reasoning(error_msg)
                self.logger.error(error_msg)
                return None
            
            # Get messages
            messages = self.project_client.agents.messages.list(thread_id=thread.id)
            
            # Find the assistant's response
            for msg in messages:
                if msg.role == "assistant" and msg.content:
                    response = msg.content[0].text.value
                    self.log_reasoning(f"Got response: {response[:100]}...")
                    
                    # Extract actual source URLs from message annotations
                    doc_urls = []
                    if hasattr(msg.content[0], 'annotations') and msg.content[0].annotations:
                        self.log_reasoning(f"Found {len(msg.content[0].annotations)} annotations")
                        for annotation in msg.content[0].annotations:
                            if hasattr(annotation, 'uri_citation') and annotation.uri_citation:
                                url = annotation.uri_citation.uri
                                # Only include actual website URLs, not Bing API URLs
                                if url and not url.startswith('https://api.bing.microsoft.com'):
                                    doc_urls.append(url)
                                    self.log_reasoning(f"Found source URL: {url}")
                    
                    if not doc_urls:
                        self.log_reasoning("No annotations found, trying run steps...")
                        doc_urls = self.extract_documentation_urls(thread.id, run.id)
                    
                    return response, doc_urls
                    
            self.log_reasoning("No assistant response found in messages")
            return None, []
            
        except Exception as e:
            error_msg = f"Error generating answer: {e}"
            self.logger.error(error_msg)
            self.log_reasoning(error_msg)
            return None, []
            
    def extract_documentation_urls(self, thread_id: str, run_id: str) -> List[str]:
        """Extract documentation URLs from run steps."""
        try:
            run_steps = self.project_client.agents.run_steps.list(thread_id=thread_id, run_id=run_id)
            documentation_urls = []
            
            for step in run_steps:
                self.log_reasoning(f"Checking run step: {step.id}")
                
                # Check if there are tool calls in the step details
                if hasattr(step, 'step_details') and step.step_details:
                    step_details = step.step_details
                    if hasattr(step_details, 'tool_calls') and step_details.tool_calls:
                        self.log_reasoning(f"Found {len(step_details.tool_calls)} tool calls")
                        
                        for call in step_details.tool_calls:
                            # Look for any tool call output that might contain URLs
                            if hasattr(call, 'bing_grounding') and call.bing_grounding:
                                self.log_reasoning(f"Examining bing_grounding data: {type(call.bing_grounding)}")
                                
                                # Handle different data structures
                                if isinstance(call.bing_grounding, dict):
                                    for key, value in call.bing_grounding.items():
                                        self.log_reasoning(f"  Key: {key}, Value type: {type(value)}")
                                        if isinstance(value, str) and value.startswith('http') and not value.startswith('https://api.bing.microsoft.com'):
                                            documentation_urls.append(value)
                                            self.log_reasoning(f"Found documentation URL from dict: {value}")
                                elif isinstance(call.bing_grounding, list):
                                    for item in call.bing_grounding:
                                        if isinstance(item, dict):
                                            for key, value in item.items():
                                                if isinstance(value, str) and value.startswith('http') and not value.startswith('https://api.bing.microsoft.com'):
                                                    documentation_urls.append(value)
                                                    self.log_reasoning(f"Found documentation URL from list: {value}")
                                        elif isinstance(item, str) and item.startswith('http') and not item.startswith('https://api.bing.microsoft.com'):
                                            documentation_urls.append(item)
                                            self.log_reasoning(f"Found documentation URL from list item: {item}")
            
            if documentation_urls:
                self.log_reasoning(f"Extracted {len(documentation_urls)} documentation URLs")
            else:
                self.log_reasoning("No documentation URLs found in run steps")
                
            return list(set(documentation_urls))  # Remove duplicates
            
        except Exception as e:
            self.log_reasoning(f"Error extracting documentation URLs: {e}")
            return []
            
    def validate_answer(self, question: str, answer: str) -> Tuple[bool, str]:
        """Validate an answer using the Answer Checker agent."""
        try:
            # Create thread
            thread = self.project_client.agents.threads.create()
            
            # Create message
            message = self.project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"Question: {question}\n\nCandidate Answer: {answer}\n\nPlease validate this answer for factual correctness, completeness, and consistency. Respond with 'VALID' if acceptable or 'INVALID: [reason]' if not."
            )
            
            # Create and process run
            run = self.project_client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=self.answer_checker_id
            )
            
            # Get messages
            messages = self.project_client.agents.messages.list(thread_id=thread.id)
            
            # Find the assistant's response
            for msg in messages:
                if msg.role == "assistant" and msg.content:
                    response = msg.content[0].text.value
                    if "VALID" in response.upper() and "INVALID" not in response.upper():
                        return True, response
                    else:
                        return False, response
                        
            return False, "No response from Answer Checker"
            
        except Exception as e:
            self.logger.error(f"Error validating answer: {e}")
            return False, f"Error: {e}"
            
    def validate_links(self, links: List[str]) -> Tuple[bool, List[str], str]:
        """Validate links using CURL and Link Checker agent."""
        import requests
        
        # First check: Must have at least one URL
        if not links or len(links) == 0:
            self.log_reasoning("Link Checker: No documentation URLs found - this is a failure condition")
            return False, [], "No documentation URLs provided. All answers must include source links."
        
        self.log_reasoning(f"Link Checker: Validating {len(links)} URLs")
        
        valid_links = []
        invalid_links = []
        
        # Check if links are reachable using requests
        for link in links:
            try:
                response = requests.head(link, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    valid_links.append(link)
                    self.log_reasoning(f"Link Checker: ✓ {link} (HTTP 200)")
                else:
                    invalid_links.append(f"{link} (HTTP {response.status_code})")
                    self.log_reasoning(f"Link Checker: ✗ {link} (HTTP {response.status_code})")
            except Exception as e:
                invalid_links.append(f"{link} (Error: {e})")
                self.log_reasoning(f"Link Checker: ✗ {link} (Error: {e})")
        
        # If we have at least one valid link, that's success
        if valid_links:
            if invalid_links:
                self.log_reasoning(f"Link Checker: Removed {len(invalid_links)} invalid URLs, keeping {len(valid_links)} valid ones")
                return True, valid_links, f"Found {len(valid_links)} valid links (removed {len(invalid_links)} invalid)"
            else:
                return True, valid_links, f"All {len(valid_links)} links are valid"
        else:
            return False, [], "No valid documentation URLs found after validation"
        
    def extract_links_and_clean(self, text: str) -> Tuple[str, List[str]]:
        """Extract URLs from text and return cleaned text and list of URLs."""
        import re
        
        self.log_reasoning(f"Extracting URLs from text (length: {len(text)})")
        self.log_reasoning(f"Text preview: {text[:200]}...")
        
        # Find URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        self.log_reasoning(f"URL regex found {len(urls)} URLs")
        
        # Remove URLs from text
        clean_text = re.sub(url_pattern, '', text)
        
        # Remove various citation formats
        clean_text = re.sub(r'\[\d+\]', '', clean_text)  # Remove [1], [2], etc.
        clean_text = re.sub(r'【[^】]*】', '', clean_text)  # Remove 【3:3†source】 style citations
        clean_text = re.sub(r'\(\d+\)', '', clean_text)  # Remove (1), (2), etc.
        clean_text = re.sub(r'\[\d+:\d+[^]]*\]', '', clean_text)  # Remove [3:3†source] style
        
        # Remove markdown formatting
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_text)  # Remove **bold**
        clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)  # Remove *italic*
        clean_text = re.sub(r'`(.*?)`', r'\1', clean_text)  # Remove `code`
        clean_text = re.sub(r'#{1,6}\s*', '', clean_text)  # Remove # headers
        
        # Remove numbered list formatting
        clean_text = re.sub(r'^\d+\.\s*\*\*[^*]*\*\*:\s*', '', clean_text, flags=re.MULTILINE)  # Remove "1. **Title**:"
        clean_text = re.sub(r'^\d+\.\s*', '', clean_text, flags=re.MULTILINE)  # Remove "1. "
        
        # Remove bullet points
        clean_text = re.sub(r'^\s*[-•]\s*', '', clean_text, flags=re.MULTILINE)
        
        # Remove "References:" at the end
        clean_text = re.sub(r'\s*References?:\s*$', '', clean_text, flags=re.IGNORECASE)
        
        # Clean up whitespace and line breaks
        clean_text = re.sub(r'\n\s*\n', ' ', clean_text)  # Replace multiple newlines with space
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # Clean up multiple spaces
        
        return clean_text, urls
        
    def on_import_excel_clicked(self):
        """Handle the Import From Excel button click."""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            # Process Excel file in separate thread
            thread = threading.Thread(target=self.process_excel_file, args=(file_path,))
            thread.daemon = True
            thread.start()
            
    def process_excel_file(self, file_path: str):
        """Process an Excel file with questions."""
        try:
            self.log_reasoning(f"Processing Excel file: {file_path}")
            
            # Create agents if not already created
            if not all([self.question_answerer_id, self.answer_checker_id, self.link_checker_id]):
                self.create_agents()
            
            # Create temporary copy
            temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Copy original file
            import shutil
            shutil.copy2(file_path, temp_path)
            
            # Read Excel file
            excel_file = pd.ExcelFile(temp_path)
            context = self.context_entry.get().strip()
            char_limit = int(self.limit_entry.get()) if self.limit_entry.get().isdigit() else 2000
            
            for sheet_name in excel_file.sheet_names:
                self.log_reasoning(f"Processing sheet: {sheet_name}")
                df = pd.read_excel(temp_path, sheet_name=sheet_name)
                
                # Identify columns using LLM
                question_col, answer_col, docs_col = self.identify_columns_with_llm(df)
                
                # Ensure answer and docs columns exist
                if answer_col not in df.columns:
                    df[answer_col] = ""
                if docs_col not in df.columns:
                    df[docs_col] = ""
                
                # Process each question
                for idx, row in df.iterrows():
                    if pd.notna(row[question_col]) and str(row[question_col]).strip():
                        question = str(row[question_col]).strip()
                        self.log_reasoning(f"Processing question {idx + 1}: {question[:50]}...")
                        
                        # Process question using the same workflow as single questions
                        success, answer, links = self.process_question_with_agents(question, context, char_limit)
                        
                        if success:
                            # Update the dataframe
                            df.at[idx, answer_col] = answer
                            if links:
                                df.at[idx, docs_col] = '\n'.join(links)
                            else:
                                df.at[idx, docs_col] = "No documentation links found"
                            
                            self.log_reasoning(f"Successfully processed question {idx + 1}")
                        else:
                            self.log_reasoning(f"Failed to process question {idx + 1}: {answer}")
                            df.at[idx, answer_col] = f"Error: {answer}"
                            df.at[idx, docs_col] = "Could not generate documentation"
                
                # Save updated sheet
                with pd.ExcelWriter(temp_path, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Ask user where to save
            self.root.after(0, lambda: self.save_processed_excel(temp_path))
                
        except Exception as e:
            self.logger.error(f"Error processing Excel file: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to process Excel file:\n{e}"))
            
    def save_processed_excel(self, temp_path: str):
        """Save the processed Excel file."""
        try:
            save_path = filedialog.asksaveasfilename(
                title="Save Processed Excel File",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if save_path:
                import shutil
                shutil.move(temp_path, save_path)
                messagebox.showinfo("Success", f"File processed and saved to:\n{save_path}")
            else:
                os.unlink(temp_path)
        except Exception as e:
            self.logger.error(f"Error saving Excel file: {e}")
            messagebox.showerror("Error", f"Failed to save Excel file:\n{e}")
            
    def identify_columns_with_llm(self, df: pd.DataFrame) -> Tuple[str, str, str]:
        """Use LLM to identify question, answer, and documentation columns."""
        try:
            # Create a prompt with column names and sample data
            column_info = []
            for col in df.columns:
                sample_data = df[col].dropna().head(3).tolist()
                column_info.append(f"Column '{col}': {sample_data}")
            
            prompt = f"""Analyze the following Excel columns and identify which column contains:
1. Questions (to be answered)
2. Expected answers (where AI responses should go)
3. Documentation/links (where reference links should go)

Columns:
{chr(10).join(column_info)}

Respond in this exact format:
Question Column: [column_name]
Answer Column: [column_name]
Documentation Column: [column_name]

If a column doesn't exist, suggest a name for it."""

            # Use the Question Answerer agent to analyze columns
            thread = self.project_client.agents.threads.create()
            message = self.project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            
            run = self.project_client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=self.question_answerer_id
            )
            
            messages = self.project_client.agents.messages.list(thread_id=thread.id)
            
            # Parse the response
            for msg in messages.data:
                if msg.role == "assistant" and msg.content:
                    response = msg.content[0].text.value
                    question_col = self.extract_column_name(response, "Question Column:")
                    answer_col = self.extract_column_name(response, "Answer Column:")
                    docs_col = self.extract_column_name(response, "Documentation Column:")
                    
                    # Fallback to simple logic if parsing fails
                    if not question_col:
                        question_col = self.identify_question_column(df)
                    if not answer_col:
                        answer_col = self.identify_answer_column(df)
                    if not docs_col:
                        docs_col = self.identify_docs_column(df)
                    
                    return question_col, answer_col, docs_col
            
            # Fallback to simple logic
            return (self.identify_question_column(df), 
                   self.identify_answer_column(df), 
                   self.identify_docs_column(df))
            
        except Exception as e:
            self.logger.error(f"Error identifying columns with LLM: {e}")
            # Fallback to simple logic
            return (self.identify_question_column(df), 
                   self.identify_answer_column(df), 
                   self.identify_docs_column(df))
                   
    def extract_column_name(self, text: str, prefix: str) -> Optional[str]:
        """Extract column name from LLM response."""
        import re
        pattern = f"{re.escape(prefix)}\\s*(.+?)(?:\\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
        
    def process_question_with_agents(self, question: str, context: str, char_limit: int) -> Tuple[bool, str, List[str]]:
        """Process a single question using the three-agent workflow."""
        try:
            attempt = 1
            max_attempts = 3
            
            while attempt <= max_attempts:
                # Step 1: Generate answer
                candidate_answer = self.generate_answer(question, context, char_limit)
                
                if not candidate_answer:
                    return False, "Question Answerer failed to generate an answer", []
                
                # Remove links and citations, save links for documentation
                clean_answer, links = self.extract_links_and_clean(candidate_answer)
                
                # Check character limit
                if len(clean_answer) > char_limit:
                    attempt += 1
                    continue
                
                # Step 2: Validate answer
                answer_valid, answer_feedback = self.validate_answer(question, clean_answer)
                
                if not answer_valid:
                    attempt += 1
                    continue
                
                # Step 3: Validate links
                links_valid, valid_links, link_feedback = self.validate_links(links)
                
                if not links_valid:
                    attempt += 1
                    continue
                
                # All checks passed
                return True, clean_answer, valid_links
                
            # Max attempts reached
            return False, f"Failed to generate acceptable answer after {max_attempts} attempts", []
            
        except Exception as e:
            self.logger.error(f"Error processing question with agents: {e}")
            return False, f"Error: {e}", []
            
    def identify_question_column(self, df: pd.DataFrame) -> str:
        """Identify the column containing questions."""
        # Simplified logic - look for columns with "question" in the name
        for col in df.columns:
            if 'question' in str(col).lower():
                return col
        return df.columns[0]  # Default to first column
        
    def identify_answer_column(self, df: pd.DataFrame) -> str:
        """Identify the column for answers."""
        for col in df.columns:
            if 'answer' in str(col).lower():
                return col
        return df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
    def identify_docs_column(self, df: pd.DataFrame) -> str:
        """Identify the column for documentation."""
        for col in df.columns:
            if any(word in str(col).lower() for word in ['doc', 'link', 'reference']):
                return col
        return df.columns[2] if len(df.columns) > 2 else df.columns[0]
        
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    try:
        app = QuestionnaireAgentUI()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{e}")


if __name__ == "__main__":
    main()