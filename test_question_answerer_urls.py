#!/usr/bin/env python3
"""
Test script to examine raw Question Answerer output and URL extraction
"""

import os
import sys
import logging
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import BingGroundingTool

# Load environment variables
load_dotenv()

def test_question_answerer_raw_output():
    """Test the Question Answerer agent and examine raw output for URLs."""
    
    print("=" * 80)
    print("TESTING QUESTION ANSWERER RAW OUTPUT FOR URL EXTRACTION")
    print("=" * 80)
    
    try:
        # Initialize Azure client
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        credential = DefaultAzureCredential()
        project_client = AIProjectClient(endpoint=endpoint, credential=credential)
        print(f"✓ Connected to Azure AI Project: {endpoint}")
        
        # Get connection details
        model_deployment = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT", "gpt-4.1")
        bing_resource_name = os.getenv("BING_CONNECTION_ID")
        
        print(f"✓ Model deployment: {model_deployment}")
        print(f"✓ Bing resource name: {bing_resource_name}")
        
        # Get connection ID
        connection = project_client.connections.get(name=bing_resource_name)
        conn_id = connection.id
        print(f"✓ Retrieved connection ID: {conn_id}")
        
        # Create Bing grounding tool
        bing_tool = BingGroundingTool(connection_id=conn_id)
        print("✓ Created Bing grounding tool")
        
        # Create Question Answerer agent
        question_answerer = project_client.agents.create_agent(
            model=model_deployment,
            name="URL Test Question Answerer",
            instructions="Search the web for evidence and provide detailed answers with sources. Include all relevant citations and source links.",
            tools=bing_tool.definitions
        )
        print(f"✓ Created Question Answerer agent: {question_answerer.id}")
        
        # Test question
        test_question = "Does your service offer video generative AI?"
        test_context = "Microsoft Azure AI"
        
        print(f"\n📝 Testing question: {test_question}")
        print(f"📝 Context: {test_context}")
        
        # Create thread and message
        thread = project_client.agents.threads.create()
        print(f"✓ Created thread: {thread.id}")
        
        message = project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Context: {test_context}\n\nQuestion: {test_question}\n\nPlease provide a comprehensive answer with supporting evidence and citations."
        )
        print(f"✓ Created message: {message.id}")
        
        # Create and process run
        print("\n🔄 Running Question Answerer agent...")
        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=question_answerer.id
        )
        
        print(f"✓ Run completed with status: {run.status}")
        
        if run.status == "failed":
            print(f"❌ Run failed: {run.last_error.message if run.last_error else 'Unknown error'}")
            return False
        
        # Get messages and examine raw content
        messages = project_client.agents.messages.list(thread_id=thread.id)
        
        print("\n" + "="*80)
        print("RAW MESSAGE ANALYSIS")
        print("="*80)
        
        for i, msg in enumerate(messages):
            print(f"\nMessage {i+1}:")
            print(f"  Role: {msg.role}")
            print(f"  Content items: {len(msg.content) if msg.content else 0}")
            
            if msg.role == "assistant" and msg.content:
                for j, content_item in enumerate(msg.content):
                    print(f"\n  Content Item {j+1}:")
                    print(f"    Type: {type(content_item)}")
                    
                    if hasattr(content_item, 'text'):
                        text_content = content_item.text.value
                        print(f"    Text length: {len(text_content)}")
                        print(f"    Text preview: {text_content[:200]}...")
                        
                        # Check for URLs in text
                        import re
                        urls_in_text = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text_content)
                        print(f"    URLs found in text: {len(urls_in_text)}")
                        for url in urls_in_text[:5]:  # Show first 5
                            print(f"      - {url}")
                        if len(urls_in_text) > 5:
                            print(f"      ... and {len(urls_in_text) - 5} more")
                    
                    # Check for annotations
                    if hasattr(content_item, 'annotations'):
                        annotations = content_item.annotations
                        print(f"    Annotations: {len(annotations) if annotations else 0}")
                        
                        if annotations:
                            for k, annotation in enumerate(annotations):
                                print(f"      Annotation {k+1}:")
                                print(f"        Type: {type(annotation)}")
                                
                                if hasattr(annotation, 'uri_citation'):
                                    uri_citation = annotation.uri_citation
                                    if uri_citation:
                                        print(f"        URI Citation: {uri_citation.uri}")
                                        print(f"        Title: {getattr(uri_citation, 'title', 'N/A')}")
                                        
                                        # Check if it's a Bing API URL
                                        if uri_citation.uri and uri_citation.uri.startswith('https://api.bing.microsoft.com'):
                                            print(f"        ❌ This is a Bing API URL (not useful)")
                                        else:
                                            print(f"        ✓ This looks like a real source URL")
                                    else:
                                        print(f"        No URI citation data")
                                else:
                                    print(f"        No uri_citation attribute")
        
        # Examine run steps for tool outputs
        print("\n" + "="*80)
        print("RUN STEPS ANALYSIS")
        print("="*80)
        
        try:
            run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)
            
            for i, step in enumerate(run_steps):
                print(f"\nRun Step {i+1}:")
                print(f"  ID: {step.id}")
                print(f"  Type: {step.type}")
                print(f"  Status: {step.status}")
                
                if hasattr(step, 'step_details') and step.step_details:
                    step_details = step.step_details
                    print(f"  Step details type: {type(step_details)}")
                    
                    if hasattr(step_details, 'tool_calls') and step_details.tool_calls:
                        print(f"  Tool calls: {len(step_details.tool_calls)}")
                        
                        for j, call in enumerate(step_details.tool_calls):
                            print(f"    Tool Call {j+1}:")
                            print(f"      Type: {type(call)}")
                            print(f"      ID: {getattr(call, 'id', 'N/A')}")
                            
                            if hasattr(call, 'bing_grounding'):
                                bing_data = call.bing_grounding
                                print(f"      Bing grounding data type: {type(bing_data)}")
                                
                                if bing_data:
                                    print(f"      Bing grounding content: {str(bing_data)[:300]}...")
                                    
                                    # Try to extract URLs from whatever structure this is
                                    found_urls = []
                                    
                                    if isinstance(bing_data, dict):
                                        for key, value in bing_data.items():
                                            if isinstance(value, str) and value.startswith('http'):
                                                found_urls.append(value)
                                    elif isinstance(bing_data, list):
                                        for item in bing_data:
                                            if isinstance(item, str) and item.startswith('http'):
                                                found_urls.append(item)
                                            elif isinstance(item, dict):
                                                for key, value in item.items():
                                                    if isinstance(value, str) and value.startswith('http'):
                                                        found_urls.append(value)
                                    
                                    print(f"      URLs found in bing_grounding: {len(found_urls)}")
                                    for url in found_urls[:3]:
                                        if url.startswith('https://api.bing.microsoft.com'):
                                            print(f"        ❌ {url} (Bing API URL)")
                                        else:
                                            print(f"        ✓ {url}")
        
        except Exception as e:
            print(f"❌ Error examining run steps: {e}")
        
        # Clean up
        try:
            project_client.agents.delete_agent(question_answerer.id)
            print(f"\n✓ Cleaned up agent: {question_answerer.id}")
        except Exception as e:
            print(f"⚠ Failed to clean up agent: {e}")
        
        print("\n" + "="*80)
        print("TEST COMPLETED")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    success = test_question_answerer_raw_output()
    if success:
        print("✓ Test completed successfully")
    else:
        print("❌ Test failed")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)