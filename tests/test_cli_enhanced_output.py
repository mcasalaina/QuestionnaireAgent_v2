#!/usr/bin/env python3
"""
Test for CLI enhanced output functionality.
Verifies that CLI mode shows answer preview and link count after processing each question.
"""

import os
import sys
import subprocess
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_cli_enhanced_output():
    """Test that CLI Excel processing shows answer preview and link count."""
    
    # Get the path to the sample file
    sample_file = os.path.join("tests", "sample_questionnaire_1_sheet.xlsx")
    
    # Verify the sample file exists
    assert os.path.exists(sample_file), f"Sample file not found: {sample_file}"
    
    # Create output file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/tmp/test_cli_enhanced_output_{timestamp}.xlsx"
    
    try:
        # Run the CLI command and capture output
        cmd = [
            "python3", "question_answerer.py",
            "--import-excel", sample_file,
            "--output-excel", output_file,
            "--verbose",
            "--mock",
            "--context", "Test Context",
            "--char-limit", "150"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        
        # Check that the command succeeded
        assert result.returncode == 0, f"CLI command failed: {result.stderr}"
        
        output = result.stdout
        
        # Check for enhanced output patterns
        # Should see "Processing question X:" lines
        processing_lines = re.findall(r"Processing question \d+:", output)
        assert len(processing_lines) > 0, "No 'Processing question' lines found"
        
        # Should see "Answer:" lines
        answer_lines = re.findall(r"Answer: .*", output)
        assert len(answer_lines) > 0, "No 'Answer:' lines found in output"
        
        # Should see "Found X documentation links" lines
        link_lines = re.findall(r"Found \d+ documentation links", output)
        assert len(link_lines) > 0, "No 'Found X documentation links' lines found"
        
        # Should see "Successfully processed" lines
        success_lines = re.findall(r"Successfully processed question \d+", output)
        assert len(success_lines) > 0, "No 'Successfully processed' lines found"
        
        # For each processed question, we should have:
        # 1. Processing question X:
        # 2. Answer: [preview]
        # 3. Found X documentation links  
        # 4. Successfully processed question X
        
        # Count should be the same for answer lines and link lines
        assert len(answer_lines) == len(link_lines), \
            f"Mismatch: {len(answer_lines)} answer lines vs {len(link_lines)} link lines"
        
        # Verify the pattern appears for each question
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if "Processing question" in line and "..." in line:
                # Look for the answer line right after
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    assert next_line.startswith("Answer: "), \
                        f"Expected 'Answer:' after processing line, but got: {next_line}"
                
                # Look for the link count line after the answer
                if i + 2 < len(lines):
                    link_line = lines[i + 2]
                    assert "Found" in link_line and "documentation links" in link_line, \
                        f"Expected link count after answer, but got: {link_line}"
        
        # Verify output file was created
        assert os.path.exists(output_file), "Output file was not created"
        
        print("✓ CLI enhanced output test passed")
        print(f"  - Found {len(processing_lines)} processing lines")
        print(f"  - Found {len(answer_lines)} answer preview lines")  
        print(f"  - Found {len(link_lines)} link count lines")
        print(f"  - Found {len(success_lines)} success lines")
        
        # Show a sample of the enhanced output
        print("\nSample enhanced output:")
        sample_lines = []
        for i, line in enumerate(lines):
            if "Processing question" in line and "..." in line:
                sample_lines.append(line)
                if i + 1 < len(lines):
                    sample_lines.append(lines[i + 1])
                if i + 2 < len(lines): 
                    sample_lines.append(lines[i + 2])
                if i + 3 < len(lines):
                    sample_lines.append(lines[i + 3])
                break
        
        for line in sample_lines:
            print(f"  {line}")
                
    except Exception as e:
        print(f"Test failed: {e}")
        raise
    finally:
        # Clean up output file
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == "__main__":
    test_cli_enhanced_output()
    print("Enhanced CLI output test completed successfully!")