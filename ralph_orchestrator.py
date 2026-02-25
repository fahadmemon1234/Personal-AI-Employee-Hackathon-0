"""
Ralph Wiggum Autonomous Loop Orchestrator

Implements autonomous task execution with stop hook pattern.
Continues iterating until task is complete or max iterations reached.

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

Usage:
    python ralph_orchestrator.py --task "Process complex invoice"
    python ralph_orchestrator.py --task-file "Needs_Action/invoice_001.md"
"""

import os
import sys
import json
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Configuration
MAX_ITERATIONS = 20
STATE_FILE = Path("ralph_state.json")
TASK_FILE = Path("ralph_task.md")
DONE_DIR = Path("Done")
LOG_FILE = Path("ralph_loop.log")
CONTEXT_DIR = Path("Ralph_Context")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ralph_orchestrator')


class RalphWiggumLoop:
    """
    Ralph Wiggum Autonomous Loop with Stop Hook Pattern
    
    This orchestrator runs Claude Code in a loop, checking for completion
    signals after each iteration. It continues until:
    - Task is marked complete (TASK_COMPLETE in output)
    - Task file is moved to /Done directory
    - Max iterations reached
    - Error occurs
    """
    
    def __init__(self, task: str = None, task_file: str = None, max_iterations: int = 20):
        self.task = task
        self.task_file = Path(task_file) if task_file else None
        self.max_iterations = max_iterations
        self.state = {
            'task': task or f"Process {task_file}" if task_file else "Unknown task",
            'started_at': datetime.now().isoformat(),
            'iterations': 0,
            'status': 'running',
            'last_output': '',
            'errors': [],
            'state_files': [],
            'max_iterations': max_iterations
        }
        self.output_history: List[str] = []
        
        # Create directories
        DONE_DIR.mkdir(exist_ok=True)
        CONTEXT_DIR.mkdir(exist_ok=True)
        
        logger.info("="*70)
        logger.info("Ralph Wiggum Autonomous Loop Started")
        logger.info("="*70)
        logger.info(f"Task: {self.state['task']}")
        logger.info(f"Max Iterations: {MAX_ITERATIONS}")
        logger.info(f"State File: {STATE_FILE}")
        logger.info("="*70)
    
    def save_state(self):
        """Save current state to file"""
        self.state['last_saved'] = datetime.now().isoformat()
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
        logger.debug(f"State saved to {STATE_FILE}")
    
    def load_state(self) -> bool:
        """Load existing state if available"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
                logger.info(f"Loaded existing state from {STATE_FILE}")
                return True
            except Exception as e:
                logger.warning(f"Could not load state: {e}")
        return False
    
    def create_task_file(self):
        """Create task file if not exists"""
        if self.task_file and not self.task_file.exists():
            with open(self.task_file, 'w', encoding='utf-8') as f:
                f.write(f"# Task: {self.state['task']}\n\n")
                f.write(f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("## Instructions\n\n")
                f.write(f"Execute the following task autonomously:\n\n")
                f.write(f"{self.state['task']}\n\n")
                f.write("## Progress\n\n")
                f.write("- [ ] Task started\n")
                f.write("\n## Notes\n\n")
                f.write("*Add notes here*\n")
            logger.info(f"Created task file: {self.task_file}")
    
    def check_task_complete(self, output: str) -> bool:
        """
        Check if task is complete using stop hook pattern
        
        Looks for:
        1. TASK_COMPLETE marker in output
        2. Task file moved to /Done directory
        3. Explicit completion signal
        """
        # Check for TASK_COMPLETE marker
        if 'TASK_COMPLETE' in output:
            logger.info("✓ Found TASK_COMPLETE marker in output")
            return True
        
        # Check if task file moved to Done
        if self.task_file and self.task_file.exists():
            done_path = DONE_DIR / self.task_file.name
            if done_path.exists():
                logger.info(f"✓ Task file moved to {DONE_DIR}")
                return True
        
        # Check for completion phrases
        completion_phrases = [
            'task is complete',
            'task completed',
            'finished successfully',
            'all steps completed',
            '✅ complete'
        ]
        
        output_lower = output.lower()
        for phrase in completion_phrases:
            if phrase in output_lower:
                logger.info(f"✓ Found completion phrase: '{phrase}'")
                return True
        
        return False
    
    def get_continuation_prompt(self) -> str:
        """Generate prompt for next iteration"""
        iteration = self.state['iterations']
        
        if iteration == 0:
            # First iteration - initial task
            prompt = f"""
# Ralph Wiggum Autonomous Loop - Task Execution

**Task:** {self.state['task']}

**Instructions:**
1. Execute this task autonomously using available tools and MCP servers
2. Break down complex tasks into steps
3. Use stop hook pattern: when you need to pause for external action, indicate clearly
4. Continue until task is fully complete
5. When done, output: TASK_COMPLETE

**Available MCP Servers:**
- Email MCP (8080): Send/receive emails
- Browser MCP (8081): Web automation
- Odoo MCP (8082): ERP/Accounting
- Social MCP (8083): Facebook/Instagram
- X MCP (8084): Twitter

**Example Workflow:**
1. Analyze task requirements
2. Create plan if needed
3. Execute step-by-step
4. Handle errors gracefully
5. Mark TASK_COMPLETE when done

**Current State:** Starting task

Begin execution now. Output TASK_COMPLETE when finished.
"""
        else:
            # Continuation - resume from last state
            last_output = self.output_history[-1][-500:] if self.output_history else ""
            
            prompt = f"""
# Ralph Wiggum Autonomous Loop - Continue Task

**Task:** {self.state['task']}
**Iteration:** {iteration} of {MAX_ITERATIONS}

**Instructions:**
1. Continue from where you left off
2. Review last output below
3. Execute next steps
4. If blocked, note what's needed
5. When fully complete, output: TASK_COMPLETE

**Last Output (last 500 chars):**
{last_output}

**State:** Continuing task execution

Continue now. Output TASK_COMPLETE when finished.
"""
        
        return prompt
    
    def run_claude(self, prompt: str) -> str:
        """
        Run Claude Code with the given prompt
        
        Returns the output from Claude
        """
        logger.info(f"Running Claude Code (iteration {self.state['iterations']})...")
        
        try:
            # Save prompt to context file
            context_file = CONTEXT_DIR / f"prompt_{self.state['iterations']:03d}.md"
            with open(context_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Run claude-code command
            # Note: Adjust command based on how claude-code is installed
            cmd = [
                'claude',
                '--prompt', prompt,
                '--output-format', 'text'
            ]
            
            logger.debug(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per iteration
            )
            
            output = result.stdout
            if result.stderr:
                logger.warning(f"Stderr: {result.stderr}")
            
            # Save output to context file
            output_file = CONTEXT_DIR / f"output_{self.state['iterations']:03d}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            
            logger.info(f"Claude output: {len(output)} chars")
            return output
            
        except subprocess.TimeoutExpired:
            error_msg = f"Iteration {self.state['iterations']} timed out after 300s"
            logger.error(error_msg)
            self.state['errors'].append(error_msg)
            return f"ERROR: {error_msg}"
            
        except FileNotFoundError:
            error_msg = "claude command not found. Make sure claude-code is installed."
            logger.error(error_msg)
            self.state['errors'].append(error_msg)
            return f"ERROR: {error_msg}"
            
        except Exception as e:
            error_msg = f"Iteration {self.state['iterations']} error: {str(e)}"
            logger.error(error_msg)
            self.state['errors'].append(error_msg)
            return f"ERROR: {error_msg}"
    
    def run(self) -> Dict[str, Any]:
        """
        Main loop - run until complete or max iterations
        
        Returns final state dictionary
        """
        logger.info("Starting Ralph Wiggum autonomous loop...")
        
        # Load existing state or start fresh
        if not self.load_state():
            self.create_task_file()
        
        self.save_state()
        
        # Main loop
        while self.state['iterations'] < self.max_iterations:
            self.state['iterations'] += 1
            iteration = self.state['iterations']
            
            logger.info("="*60)
            logger.info(f"ITERATION {iteration} / {self.max_iterations}")
            logger.info("="*60)
            
            # Generate prompt
            prompt = self.get_continuation_prompt()
            
            # Run Claude
            output = self.run_claude(prompt)
            
            # Store output
            self.output_history.append(output)
            self.state['last_output'] = output[-1000:]  # Last 1000 chars
            
            # Check for completion
            if self.check_task_complete(output):
                logger.info("="*60)
                logger.info("✅ TASK COMPLETE!")
                logger.info("="*60)
                self.state['status'] = 'completed'
                self.state['completed_at'] = datetime.now().isoformat()
                self.save_state()
                
                # Move task file to Done if exists
                if self.task_file and self.task_file.exists():
                    done_path = DONE_DIR / self.task_file.name
                    try:
                        self.task_file.rename(done_path)
                        logger.info(f"Task file moved to: {done_path}")
                    except Exception as e:
                        logger.warning(f"Could not move task file: {e}")
                
                return self.state
            
            # Check for errors
            if output.startswith('ERROR:'):
                logger.warning(f"Error in iteration {iteration}: {output}")
            
            # Save state
            self.save_state()
            
            # Small delay between iterations
            import time
            time.sleep(2)
        
        # Max iterations reached
        logger.warning("="*60)
        logger.warning(f"⚠️ MAX ITERATIONS ({MAX_ITERATIONS}) REACHED")
        logger.warning("="*60)
        self.state['status'] = 'max_iterations'
        self.state['ended_at'] = datetime.now().isoformat()
        self.save_state()
        
        return self.state
    
    def print_summary(self):
        """Print execution summary"""
        print("\n" + "="*70)
        print("Ralph Wiggum Loop - Execution Summary")
        print("="*70)
        print(f"Task: {self.state['task']}")
        print(f"Status: {self.state['status']}")
        print(f"Iterations: {self.state['iterations']}")
        print(f"Started: {self.state['started_at']}")
        
        if 'completed_at' in self.state:
            print(f"Completed: {self.state['completed_at']}")
        
        if self.state['errors']:
            print(f"\nErrors ({len(self.state['errors'])}):")
            for error in self.state['errors'][-5:]:  # Last 5 errors
                print(f"  - {error}")
        
        print("="*70)


def main():
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Autonomous Loop Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ralph_orchestrator.py --task "Process complex invoice from email"
  python ralph_orchestrator.py --task-file "Needs_Action/invoice_001.md"
  python ralph_orchestrator.py --task "Setup new customer in Odoo and send welcome email"
        """
    )
    
    parser.add_argument(
        '--task', '-t',
        help='Task description to execute'
    )
    
    parser.add_argument(
        '--task-file', '-f',
        help='Path to task file'
    )
    
    parser.add_argument(
        '--max-iterations', '-m',
        type=int,
        default=20,
        help='Maximum iterations (default: 20)'
    )
    
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Resume from existing state file'
    )
    
    args = parser.parse_args()
    
    if not args.task and not args.task_file:
        parser.print_help()
        print("\nError: Either --task or --task-file is required")
        sys.exit(1)
    
    # Create and run loop with custom max iterations
    loop = RalphWiggumLoop(task=args.task, task_file=args.task_file, max_iterations=args.max_iterations)
    
    try:
        final_state = loop.run()
        loop.print_summary()
        
        # Exit code based on completion
        if final_state['status'] == 'completed':
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Loop interrupted by user")
        loop.state['status'] = 'interrupted'
        loop.save_state()
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        loop.state['status'] = 'error'
        loop.state['errors'].append(str(e))
        loop.save_state()
        sys.exit(1)


if __name__ == "__main__":
    main()
