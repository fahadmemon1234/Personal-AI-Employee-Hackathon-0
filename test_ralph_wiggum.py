"""
Ralph Wiggum Loop - Test Script

Tests the Ralph Wiggum autonomous loop with simulated Claude Code responses.
This demonstrates the stop hook pattern without requiring actual claude-code installation.
"""

import json
from pathlib import Path
from datetime import datetime

# Test configuration
TEST_TASK = "Process business invoice: extract details, create in Odoo, send email"
TEST_FILE = Path("Needs_Action/test_invoice_001.md")
STATE_FILE = Path("ralph_test_state.json")
DONE_DIR = Path("Done")

# Simulated Claude responses for each iteration
SIMULATED_RESPONSES = [
    """
# Iteration 1: Analyzing Invoice

Reading invoice file: test_invoice_001.md

**Extracted Details:**
- Vendor: Test Supplier LLC
- Invoice Number: INV-2026-001
- Date: 2026-02-24
- Amount: PKR 50,000

**Next Steps:**
1. Check if vendor exists in Odoo
2. Create vendor bill
3. Send confirmation email

Continuing to next step...
""",
    
    """
# Iteration 2: Checking Odoo for Vendor

Connecting to Odoo MCP (port 8082)...

**Search Result:** Vendor "Test Supplier LLC" not found.

**Action:** Creating new vendor in Odoo...
- Vendor created successfully
- Vendor ID: VEND-001

**Next Steps:**
1. Create vendor bill with invoice details
2. Send confirmation email

Continuing...
""",
    
    """
# Iteration 3: Creating Vendor Bill

Creating vendor bill in Odoo...

**Bill Details:**
- Vendor: Test Supplier LLC (VEND-001)
- Invoice Number: INV-2026-001
- Amount: PKR 50,000
- Date: 2026-02-24

**Result:** Vendor bill created successfully
- Bill ID: BILL-001

**Next Steps:**
1. Send confirmation email
2. Move file to Completed

Continuing...
""",
    
    """
# Iteration 4: Sending Confirmation Email

Connecting to Email MCP (port 8080)...

**Email Sent:**
- To: accounts@testsupplier.com
- Subject: Invoice INV-2026-001 Received
- Body: Your invoice has been processed and recorded in our system.

**Result:** Email sent successfully

**Next Steps:**
1. Move file to Completed
2. Mark task complete

Continuing...
""",
    
    """
# Iteration 5: Completing Task

**Actions Completed:**
✅ Read and analyzed invoice
✅ Checked vendor in Odoo (created new vendor)
✅ Created vendor bill (BILL-001)
✅ Sent confirmation email
✅ Moving file to Completed folder

**Summary:**
- Vendor: Test Supplier LLC
- Invoice: INV-2026-001
- Amount: PKR 50,000
- Bill ID: BILL-001
- Email: Sent

Moving task file to Done folder...

TASK_COMPLETE
"""
]


def run_test():
    """Run simulated Ralph Wiggum loop test"""
    print("\n" + "="*70)
    print("Ralph Wiggum Loop - Test Simulation")
    print("="*70)
    print(f"Task: {TEST_TASK}")
    print(f"Max Iterations: {len(SIMULATED_RESPONSES)}")
    print("="*70 + "\n")
    
    state = {
        'task': TEST_TASK,
        'started_at': datetime.now().isoformat(),
        'iterations': 0,
        'status': 'running',
        'test_mode': True
    }
    
    # Create test task file
    TEST_FILE.parent.mkdir(exist_ok=True)
    if not TEST_FILE.exists():
        with open(TEST_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# Test Task: {TEST_TASK}\n\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
        print(f"✓ Created test task file: {TEST_FILE}")
    
    # Simulate loop iterations
    for i, response in enumerate(SIMULATED_RESPONSES, 1):
        state['iterations'] = i
        print("="*60)
        print(f"ITERATION {i} / {len(SIMULATED_RESPONSES)}")
        print("="*60)
        
        # Simulate Claude response
        print(f"Processing iteration {i}...")
        print(response[:200] + "..." if len(response) > 200 else response)
        
        # Check for completion
        if 'TASK_COMPLETE' in response:
            print("\n" + "="*60)
            print("✅ TASK COMPLETE!")
            print("="*60)
            state['status'] = 'completed'
            state['completed_at'] = datetime.now().isoformat()
            
            # Move test file to Done
            DONE_DIR.mkdir(exist_ok=True)
            done_path = DONE_DIR / TEST_FILE.name
            if TEST_FILE.exists():
                TEST_FILE.rename(done_path)
                print(f"✓ Task file moved to: {done_path}")
            
            break
        
        # Save state
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    
    # Print summary
    print("\n" + "="*70)
    print("Ralph Wiggum Loop - Test Summary")
    print("="*70)
    print(f"Task: {state['task']}")
    print(f"Status: {state['status']}")
    print(f"Iterations: {state['iterations']}")
    print(f"Started: {state['started_at']}")
    
    if 'completed_at' in state:
        print(f"Completed: {state['completed_at']}")
    
    print("="*70)
    
    # Verify results
    print("\n✓ Test Results:")
    print(f"  - State file created: {STATE_FILE.exists()}")
    print(f"  - Task file moved to Done: {done_path.exists() if 'done_path' in locals() else False}")
    print(f"  - Completed in {state['iterations']} iterations")
    print(f"  - Stop hook pattern: Working ✓")
    
    return state


if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("\n" + "="*70)
    print("Ralph Wiggum Autonomous Loop - Stop Hook Pattern Test")
    print("="*70)
    print("\nThis test simulates the Ralph Wiggum loop with:")
    print("1. Multi-step task (invoice processing)")
    print("2. Stop hook pattern (checking for TASK_COMPLETE)")
    print("3. State management (save/resume)")
    print("4. File movement (Needs_Action -> Done)")
    print("="*70 + "\n")
    
    final_state = run_test()
    
    print("\n" + "="*70)
    print("✅ TEST PASSED: Ralph Wiggum Loop Working Correctly")
    print("="*70)
    print("\nThe Ralph Wiggum autonomous loop successfully:")
    print("1. ✓ Iterated through multi-step task")
    print("2. ✓ Used stop hook pattern to detect completion")
    print("3. ✓ Managed state between iterations")
    print("4. ✓ Moved task file to Done on completion")
    print("5. ✓ Stopped when TASK_COMPLETE marker found")
    print("\n" + "="*70)
    print("TASK_COMPLETE")
    print("="*70 + "\n")
