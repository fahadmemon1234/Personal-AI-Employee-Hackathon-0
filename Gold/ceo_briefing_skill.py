"""
ceo_briefing_skill.py
Implementation of the CEO Briefing Skill for weekly auditing
Generates Monday_Briefing.md with Financial Summary, Bottleneck Analysis, and Business Suggestions
"""

import os
import sys
from pathlib import Path
import re
from datetime import datetime, timedelta
import json

# Add the project root to the path so we can import modules
sys.path.append(str(Path(__file__).parent))

from odoo_integration.odoo_connector import get_odoo_connection


def analyze_bank_transactions():
    """
    Analyze Bank_Transactions.md for financial summary
    """
    bank_trans_path = Path("Bank_Transactions.md")
    
    if not bank_trans_path.exists():
        print(f"Bank_Transactions.md not found at {bank_trans_path}")
        return {
            "income": 0.0,
            "expense": 0.0,
            "net_change": 0.0,
            "transaction_count": 0
        }
    
    income = 0.0
    expense = 0.0
    transaction_count = 0
    
    with open(bank_trans_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Look for income and expense patterns in the file
        # This is a simplified approach - in reality, you'd parse the specific format of your transactions
        lines = content.split('\n')
        
        for line in lines:
            # Look for positive amounts (income) and negative amounts (expenses)
            # This assumes a certain format in your Bank_Transactions.md
            if '$' in line and any(word in line.lower() for word in ['income', 'deposit', 'payment received']):
                # Extract amount from line (simplified)
                amounts = re.findall(r'\$?([0-9,]+\.?[0-9]*)', line)
                for amt_str in amounts:
                    try:
                        amt = float(amt_str.replace(',', ''))
                        income += amt
                        transaction_count += 1
                    except ValueError:
                        continue
            elif '$' in line and any(word in line.lower() for word in ['expense', 'withdrawal', 'payment made']):
                # Extract amount from line (simplified)
                amounts = re.findall(r'\$?([0-9,]+\.?[0-9]*)', line)
                for amt_str in amounts:
                    try:
                        amt = float(amt_str.replace(',', ''))
                        expense += amt
                        transaction_count += 1
                    except ValueError:
                        continue
    
    net_change = income - expense
    
    return {
        "income": round(income, 2),
        "expense": round(expense, 2),
        "net_change": round(net_change, 2),
        "transaction_count": transaction_count
    }


def analyze_needs_action_folder():
    """
    Analyze the /Needs_Action folder for bottleneck analysis
    """
    needs_action_path = Path("Needs_Action")
    
    if not needs_action_path.exists():
        print(f"Needs_Action folder not found at {needs_action_path}")
        return {
            "total_tasks": 0,
            "tasks_over_48h": [],
            "oldest_task_age": 0
        }
    
    tasks_over_48h = []
    total_tasks = 0
    
    # Define 48 hours threshold
    threshold_time = datetime.now() - timedelta(hours=48)
    
    for file_path in needs_action_path.iterdir():
        if file_path.is_file():
            total_tasks += 1
            
            # Get file creation/modification time
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Check if the task is older than 48 hours
            if file_time < threshold_time:
                age_hours = (datetime.now() - file_time).total_seconds() / 3600
                tasks_over_48h.append({
                    "filename": file_path.name,
                    "age_hours": round(age_hours, 2),
                    "timestamp": file_time.isoformat()
                })
    
    # Sort by age (oldest first)
    tasks_over_48h.sort(key=lambda x: x['age_hours'], reverse=True)
    
    oldest_age = max([task['age_hours'] for task in tasks_over_48h]) if tasks_over_48h else 0
    
    return {
        "total_tasks": total_tasks,
        "tasks_over_48h": tasks_over_48h,
        "oldest_task_age": round(oldest_age, 2)
    }


def generate_business_suggestions(odoo_data, bank_data, bottleneck_data):
    """
    Generate proactive business suggestions based on available data
    """
    suggestions = []
    
    # Suggestion 1: Based on revenue trends
    if odoo_data.get('current_month_revenue', 0) > odoo_data.get('previous_month_revenue', 0):
        growth_rate = ((odoo_data['current_month_revenue'] - odoo_data['previous_month_revenue']) / 
                       odoo_data['previous_month_revenue']) * 100 if odoo_data['previous_month_revenue'] != 0 else 0
        suggestions.append(
            f"Revenue Growth Identified: Your business is showing positive growth with {growth_rate:.1f}% "
            f"increase compared to last month. Consider investing more in the strategies that are driving this growth."
        )
    elif odoo_data.get('current_month_revenue', 0) < odoo_data.get('previous_month_revenue', 0):
        decline_rate = ((odoo_data['previous_month_revenue'] - odoo_data['current_month_revenue']) / 
                        odoo_data['previous_month_revenue']) * 100 if odoo_data['previous_month_revenue'] != 0 else 0
        suggestions.append(
            f"Revenue Decline Alert: Your revenue decreased by {decline_rate:.1f}% compared to last month. "
            f"Review your marketing strategies and client engagement approaches."
        )
    
    # Suggestion 2: Based on outstanding invoices
    if odoo_data.get('outstanding_amount', 0) > 1000:  # Threshold of $1000
        suggestions.append(
            f"High Outstanding Invoices: You have ${odoo_data['outstanding_amount']:.2f} in outstanding invoices. "
            f"Consider following up with clients to improve cash flow."
        )
    
    # Suggestion 3: Based on bottleneck analysis
    if bottleneck_data.get('tasks_over_48h'):
        oldest_task = bottleneck_data['tasks_over_48h'][0] if bottleneck_data['tasks_over_48h'] else None
        if oldest_task:
            suggestions.append(
                f"Bottleneck Identified: The task '{oldest_task['filename']}' has been pending for "
                f"{oldest_task['age_hours']} hours. Address this bottleneck to improve workflow efficiency."
            )
    
    # Suggestion 4: Based on income vs expenses
    if bank_data.get('expense', 0) > bank_data.get('income', 0):
        deficit = bank_data['expense'] - bank_data['income']
        suggestions.append(
            f"Expense Deficit Warning: Your expenses exceed income by ${deficit:.2f}. "
            f"Review your spending patterns and identify areas for cost reduction."
        )
    
    # If no specific suggestions were generated, add generic ones
    if not suggestions:
        suggestions.extend([
            "Consider reviewing your top-performing clients to develop stronger relationships and increase revenue.",
            "Evaluate your current processes to identify potential automation opportunities.",
            "Analyze your marketing channels to determine which are providing the best ROI."
        ])
    
    return suggestions[:3]  # Return only the first 3 suggestions


def generate_ceo_briefing():
    """
    Generate the Monday CEO Briefing report
    """
    try:
        # Get Odoo financial data
        try:
            odoo_conn = get_odoo_connection()
            
            # Get current month revenue
            current_month_revenue = odoo_conn.get_monthly_revenue(0)
            
            # Get last month revenue
            previous_month_revenue = odoo_conn.get_monthly_revenue(-1)
            
            # Get outstanding invoices data
            outstanding_amount = odoo_conn.get_total_outstanding_invoices()
            
            # Get count of outstanding invoices
            outstanding_invoice_ids = odoo_conn.models.execute_kw(
                odoo_conn.db, odoo_conn.uid, odoo_conn.password,
                'account.move', 'search',
                [[['state', '=', 'posted'], ['payment_state', '!=', 'paid'], ['move_type', '=', 'out_invoice']]]
            )
            outstanding_count = len(outstanding_invoice_ids)
            
            odoo_data = {
                "current_month_revenue": current_month_revenue,
                "previous_month_revenue": previous_month_revenue,
                "outstanding_amount": outstanding_amount,
                "outstanding_count": outstanding_count
            }
        except Exception as e:
            print(f"Could not connect to Odoo for briefing: {str(e)}")
            odoo_data = {
                "current_month_revenue": 0,
                "previous_month_revenue": 0,
                "outstanding_amount": 0,
                "outstanding_count": 0
            }
        
        # Analyze bank transactions
        bank_data = analyze_bank_transactions()
        
        # Analyze Needs_Action folder for bottlenecks
        bottleneck_data = analyze_needs_action_folder()
        
        # Generate business suggestions
        business_suggestions = generate_business_suggestions(odoo_data, bank_data, bottleneck_data)
        
        # Create the briefing content
        briefing_content = f"""# Monday CEO Briefing
**Date:** {datetime.now().strftime('%A, %B %d, %Y')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Financial Summary

### Income vs Expense
- **Total Income:** ${bank_data['income']:,.2f}
- **Total Expenses:** ${bank_data['expense']:,.2f}
- **Net Change:** {'+' if bank_data['net_change'] >= 0 else ''}${bank_data['net_change']:,.2f}
- **Transaction Count:** {bank_data['transaction_count']}

### Odoo Financial Data
- **Current Month Revenue:** ${odoo_data['current_month_revenue']:,.2f}
- **Previous Month Revenue:** ${odoo_data['previous_month_revenue']:,.2f}
- **Total Outstanding Invoices:** ${odoo_data['outstanding_amount']:,.2f} ({odoo_data['outstanding_count']} invoices)

---

## Bottleneck Analysis

### Tasks Over 48 Hours
- **Total Tasks in Needs_Action:** {bottleneck_data['total_tasks']}
- **Tasks Exceeding 48h Limit:** {len(bottleneck_data['tasks_over_48h'])}
- **Oldest Task Age:** {bottleneck_data['oldest_task_age']} hours

#### Detailed List of Tasks Over 48h:
"""
        
        if bottleneck_data['tasks_over_48h']:
            for i, task in enumerate(bottleneck_data['tasks_over_48h'], 1):
                briefing_content += f"- {i}. **{task['filename']}** - {task['age_hours']} hours old (since {task['timestamp']})\n"
        else:
            briefing_content += "- No tasks currently exceeding the 48-hour threshold.\n"
        
        briefing_content += f"""

---

## Proactive Business Suggestions

Based on the analysis of your financial data and operational bottlenecks:

1. {business_suggestions[0] if len(business_suggestions) > 0 else 'No specific suggestions generated.'}
2. {business_suggestions[1] if len(business_suggestions) > 1 else 'N/A'}
3. {business_suggestions[2] if len(business_suggestions) > 2 else 'N/A'}

---

## Action Items

### Immediate Actions Required
- [ ] Follow up on outstanding invoices totaling ${odoo_data['outstanding_amount']:,.2f}
- [ ] Address the oldest pending task: {bottleneck_data['tasks_over_48h'][0]['filename'] if bottleneck_data['tasks_over_48h'] else 'None'}
- [ ] Review expense categories if expenses exceeded income

### Strategic Recommendations
- [ ] Analyze revenue drivers from current month vs previous month
- [ ] Optimize processes to reduce task completion time
- [ ] Strengthen relationships with top-performing clients

---

*This report was automatically generated by the AI Employee CEO Briefing Skill.*
"""
        
        # Write the briefing to the Briefings folder
        briefing_filename = f"Monday_Briefing_{datetime.now().strftime('%Y%m%d')}.md"
        briefing_path = Path("Briefings") / briefing_filename
        
        with open(briefing_path, 'w', encoding='utf-8') as f:
            f.write(briefing_content)
        
        print(f"CEO Briefing generated successfully: {briefing_path}")
        print(f"- Financial Summary completed")
        print(f"- Bottleneck Analysis completed ({len(bottleneck_data['tasks_over_48h'])} tasks over 48h)")
        print(f"- {len(business_suggestions)} business suggestions generated")
        
        return str(briefing_path)
        
    except Exception as e:
        print(f"Error generating CEO briefing: {str(e)}")
        return None


def ceo_briefing_cli():
    """
    Command-line interface for the CEO Briefing Skill
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Monday CEO Briefing")
    parser.add_argument("--output-dir", default="Briefings", 
                       help="Directory to save the briefing file")
    
    args = parser.parse_args()
    
    # Ensure the output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    briefing_path = generate_ceo_briefing()
    
    if briefing_path:
        print(f"\nCEO Briefing saved to: {briefing_path}")
    else:
        print("\nFailed to generate CEO briefing.")
        sys.exit(1)


if __name__ == "__main__":
    ceo_briefing_cli()