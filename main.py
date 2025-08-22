#!/usr/bin/env python3
"""
Web-Based Questionnaire Answering Agent (CLI Prototype)

A command-line tool that accepts a natural-language question and orchestrates 
three agents in sequence to provide a well-researched, fact-checked answer.
"""

import sys
import argparse
import logging
from typing import Tuple
from agents.question_answerer import QuestionAnswerer
from agents.answer_checker import AnswerChecker
from agents.link_checker import LinkChecker
from utils.logger import setup_logger


class QuestionnaireAgent:
    """Main orchestrator for the three-agent question answering system."""
    
    MAX_ATTEMPTS = 10
    
    def __init__(self):
        self.question_answerer = QuestionAnswerer()
        self.answer_checker = AnswerChecker()
        self.link_checker = LinkChecker()
        self.logger = logging.getLogger(__name__)
    
    def answer_question(self, question: str) -> Tuple[bool, str]:
        """
        Orchestrate the three agents to answer a question.
        
        Args:
            question: The natural language question to answer
            
        Returns:
            Tuple of (success: bool, result: str)
        """
        attempt = 1
        
        while attempt <= self.MAX_ATTEMPTS:
            self.logger.info(f"Attempt {attempt}/{self.MAX_ATTEMPTS}")
            
            # Step 1: Generate answer
            print("Question Answerer: Generating answer...")
            try:
                candidate_answer = self.question_answerer.generate_answer(question)
                if not candidate_answer:
                    error_msg = "Question Answerer failed to generate an answer"
                    self.logger.error(error_msg)
                    return False, error_msg
                    
                print(f"Generated candidate answer: {candidate_answer[:200]}...")
            except Exception as e:
                error_msg = f"Question Answerer error: {e}"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Step 2: Check answer quality
            print("Answer Checker: Validating answer...")
            try:
                answer_valid, answer_feedback = self.answer_checker.validate_answer(
                    question, candidate_answer
                )
                if not answer_valid:
                    print(f"Answer Checker rejected: {answer_feedback}")
                    attempt += 1
                    continue
                    
                print("Answer Checker approved the answer")
            except Exception as e:
                error_msg = f"Answer Checker error: {e}"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Step 3: Check links
            print("Link Checker: Verifying URLs...")
            try:
                links_valid, link_feedback = self.link_checker.validate_links(
                    candidate_answer
                )
                if not links_valid:
                    print(f"Link Checker rejected: {link_feedback}")
                    attempt += 1
                    continue
                    
                print("Link Checker approved all URLs")
            except Exception as e:
                error_msg = f"Link Checker error: {e}"
                self.logger.error(error_msg)
                return False, error_msg
            
            # All checks passed
            print("All agents approved the answer!")
            return True, candidate_answer
        
        # Max attempts reached
        error_msg = f"Failed to generate acceptable answer after {self.MAX_ATTEMPTS} attempts"
        self.logger.error(error_msg)
        return False, error_msg


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Web-Based Questionnaire Answering Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  questionnaire-agent "Why is the sky blue?"
  questionnaire-agent "What are the benefits of renewable energy?"
        """
    )
    
    parser.add_argument(
        "question",
        help="The natural language question to answer"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with REST call logging"
    )
    
    parser.add_argument(
        "--log-file",
        help="Path to log file (default: logs to console)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.debug:
        # Enable debug mode with REST call logging
        log_level = logging.DEBUG
        setup_logger(log_level, args.log_file)
        # Enable Azure SDK logging for REST calls
        logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.DEBUG)
        logging.getLogger('azure.identity').setLevel(logging.DEBUG)
    elif args.verbose:
        log_level = logging.INFO
        setup_logger(log_level, args.log_file)
    else:
        # Minimal logging - only errors
        log_level = logging.ERROR
        setup_logger(log_level, args.log_file)
        # Suppress Azure SDK noise
        logging.getLogger('azure').setLevel(logging.ERROR)
    
    logger = logging.getLogger(__name__)
    if args.debug or args.verbose:
        logger.info(f"Starting questionnaire agent for question: '{args.question}'")
    
    # Initialize and run the agent
    try:
        agent = QuestionnaireAgent()
        success, result = agent.answer_question(args.question)
        
        if success:
            print("\n" + "="*80)
            print("FINAL ANSWER:")
            print("="*80)
            print(result)
            print("="*80)
            sys.exit(0)
        else:
            print(f"\nERROR: {result}", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
