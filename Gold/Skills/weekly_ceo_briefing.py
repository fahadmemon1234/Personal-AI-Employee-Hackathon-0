"""
Weekly CEO Briefing Skill
Generates comprehensive weekly business briefing for CEO review

Trigger: Sunday night (scheduled) or manual
Data Sources: Business_Goals.md, Completed tasks, Odoo financials, Bank CSVs
Output: /Briefings/YYYY-MM-DD_Monday_Briefing.md
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
BRIEFINGS_DIR = Path("Briefings")
COMPLETED_DIR = Path("Completed")
PLANS_DIR = Path("Plans")
NEEDS_ACTION_DIR = Path("Needs_Action")
PENDING_APPROVAL_DIR = Path("Pending_Approval")

# MCP Server URLs
ODOO_MCP_URL = "http://localhost:8082"
SOCIAL_MCP_URL = "http://localhost:8083"
X_MCP_URL = "http://localhost:8084"

# Create directories
BRIEFINGS_DIR.mkdir(exist_ok=True)


class WeeklyCEOBriefing:
    """Generate weekly CEO briefing using Ralph Wiggum reasoning loop"""
    
    def __init__(self):
        self.briefing_data = {
            'period': '',
            'generated_at': datetime.now().isoformat(),
            'business_goals': [],
            'completed_tasks': [],
            'financial_summary': {},
            'social_media_summary': {},
            'bottlenecks': [],
            'suggestions': [],
            'key_metrics': {}
        }
    
    def ralph_wiggum_loop(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ralph Wiggum Reasoning Loop for multi-step briefing generation
        
        Each step has:
        - name: Step identifier
        - action: Function to execute
        - depends_on: Previous steps this depends on
        - data: Input data for the step
        
        The loop processes steps sequentially, passing results between dependent steps.
        """
        results = {}
        
        print("\n" + "="*70)
        print("🔄 Ralph Wiggum Reasoning Loop - CEO Briefing Generation")
        print("="*70)
        
        for step in steps:
            step_name = step['name']
            step_action = step['action']
            step_depends = step.get('depends_on', [])
            step_data = step.get('data', {})
            
            # Gather dependencies
            dep_results = {}
            for dep in step_depends:
                if dep in results:
                    dep_results[dep] = results[dep]
                else:
                    print(f"⚠️  Warning: Dependency '{dep}' not found for step '{step_name}'")
            
            print(f"\n📌 Step: {step_name}")
            print("-" * 50)
            
            try:
                # Execute step action
                result = step_action(**dep_results, **step_data)
                results[step_name] = result
                print(f"✅ Completed: {step_name}")
            except Exception as e:
                print(f"❌ Error in {step_name}: {str(e)}")
                results[step_name] = {'error': str(e)}
        
        print("\n" + "="*70)
        print("📋 Ralph Wiggum Loop Complete")
        print("="*70 + "\n")
        
        return results
    
    def read_business_goals(self, **kwargs) -> Dict[str, Any]:
        """Read and parse Business_Goals.md"""
        goals_file = Path("Business_Goals.md")
        goals = {
            'strategic_goals': [],
            'quarterly_targets': [],
            'current_focus': []
        }
        
        if goals_file.exists():
            with open(goals_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Parse strategic goals (look for bullet points after ## Strategic Goals)
                if '## Strategic Goals' in content or '## 🎯 Strategic Goals' in content:
                    section_marker = '## Strategic Goals' if '## Strategic Goals' in content else '## 🎯 Strategic Goals'
                    section = content.split(section_marker)[1]
                    if '##' in section:
                        section = section.split('##')[0]
                    # Extract bullet points
                    for line in section.strip().split('\n'):
                        line = line.strip()
                        if line.startswith('-') or line.startswith('*'):
                            goal = line.lstrip('-').lstrip('*').strip()
                            if goal and not goal.startswith('['):  # Skip checkboxes
                                goals['strategic_goals'].append(goal)
                
                # Parse quarterly targets
                if '## Quarterly Targets' in content or '## 📈 Quarterly Targets' in content:
                    section_marker = '## Quarterly Targets' if '## Quarterly Targets' in content else '## 📈 Quarterly Targets'
                    section = content.split(section_marker)[1]
                    if '##' in section:
                        section = section.split('##')[0]
                    goals['quarterly_targets'] = [
                        line.strip().lstrip('- ').lstrip('* ').lstrip('- [ ] ').lstrip('- [x] ')
                        for line in section.strip().split('\n')
                        if line.strip() and not line.startswith('#')
                    ]
                
                # Parse current focus
                if '## Current Focus' in content or '## 🔥 Current Focus' in content:
                    section_marker = '## Current Focus' if '## Current Focus' in content else '## 🔥 Current Focus'
                    section = content.split(section_marker)[1]
                    if '##' in section:
                        section = section.split('##')[0]
                    goals['current_focus'] = [
                        line.strip().lstrip('- ').lstrip('* ').lstrip('- [ ] ').lstrip('- [x] ')
                        for line in section.strip().split('\n')
                        if line.strip() and not line.startswith('#')
                    ]
            
            print(f"   Found {len(goals['strategic_goals'])} strategic goals")
        else:
            print("   ⚠️  Business_Goals.md not found - using defaults")
            goals['strategic_goals'] = [
                "Grow AI-driven automation services",
                "Expand client base",
                "Improve operational efficiency"
            ]
        
        self.briefing_data['business_goals'] = goals
        return goals
    
    def read_completed_tasks(self, **kwargs) -> Dict[str, Any]:
        """Read completed tasks from last week"""
        completed = {
            'tasks': [],
            'total_count': 0,
            'by_category': {}
        }
        
        # Calculate date range (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        
        # Read from Completed directory
        if COMPLETED_DIR.exists():
            for file in COMPLETED_DIR.iterdir():
                if file.suffix == '.md':
                    try:
                        mtime = datetime.fromtimestamp(file.stat().st_mtime)
                        if mtime > week_ago:
                            with open(file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                # Extract task info
                                task = {
                                    'file': file.name,
                                    'completed_at': mtime.isoformat(),
                                    'title': file.stem
                                }
                                
                                # Try to extract category from content
                                if 'Category:' in content:
                                    match = re.search(r'Category:\s*(.+)', content)
                                    if match:
                                        task['category'] = match.group(1).strip()
                                
                                completed['tasks'].append(task)
                    except Exception as e:
                        print(f"   Warning: Could not read {file.name}: {e}")
        
        # Also check recent Plans that might be completed
        if PLANS_DIR.exists():
            for file in PLANS_DIR.iterdir():
                if file.suffix == '.md':
                    try:
                        mtime = datetime.fromtimestamp(file.stat().st_mtime)
                        if mtime > week_ago:
                            # Count as potential activity
                            pass
                    except:
                        pass
        
        completed['total_count'] = len(completed['tasks'])
        
        # Group by category
        categories = {}
        for task in completed['tasks']:
            cat = task.get('category', 'Uncategorized')
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        completed['by_category'] = categories
        
        print(f"   Found {completed['total_count']} completed tasks")
        print(f"   Categories: {list(categories.keys())}")
        
        self.briefing_data['completed_tasks'] = completed
        return completed
    
    def get_odoo_financials(self, **kwargs) -> Dict[str, Any]:
        """Fetch financial data from Odoo via MCP"""
        financials = {
            'revenue': 0,
            'expenses': 0,
            'receivables': 0,
            'payables': 0,
            'recent_invoices': [],
            'odoo_status': 'unknown'
        }
        
        try:
            # Check Odoo MCP health
            health_resp = requests.get(f"{ODOO_MCP_URL}/health", timeout=5)
            if health_resp.status_code == 200:
                financials['odoo_status'] = 'connected'
                
                # Get account balances
                try:
                    balance_resp = requests.post(
                        f"{ODOO_MCP_URL}/tools/get_account_balances",
                        json={},
                        timeout=10
                    )
                    if balance_resp.status_code == 200:
                        balances = balance_resp.json()
                        if balances.get('success'):
                            financials['receivables'] = balances.get('receivables', 0)
                            financials['payables'] = balances.get('payables', 0)
                            print(f"   Receivables: PKR {financials['receivables']:,.2f}")
                            print(f"   Payables: PKR {financials['payables']:,.2f}")
                except Exception as e:
                    print(f"   Warning: Could not fetch balances: {e}")
                
                # Get recent invoices
                try:
                    invoices_resp = requests.post(
                        f"{ODOO_MCP_URL}/tools/get_invoices",
                        json={'limit': 10},
                        timeout=10
                    )
                    if invoices_resp.status_code == 200:
                        invoices = invoices_resp.json()
                        if invoices.get('success'):
                            financials['recent_invoices'] = invoices.get('invoices', [])
                            # Calculate revenue from paid invoices
                            for inv in financials['recent_invoices']:
                                if inv.get('state') == 'posted':
                                    financials['revenue'] += inv.get('amount_total', 0)
                except Exception as e:
                    print(f"   Warning: Could not fetch invoices: {e}")
            else:
                financials['odoo_status'] = 'disconnected'
                print("   ⚠️  Odoo MCP not responding")
        
        except requests.RequestException as e:
            financials['odoo_status'] = 'error'
            print(f"   ⚠️  Odoo MCP connection error: {e}")
        
        self.briefing_data['financial_summary'] = financials
        return financials
    
    def get_social_media_summary(self, **kwargs) -> Dict[str, Any]:
        """Fetch social media activity from MCP servers"""
        social = {
            'facebook_posts': 0,
            'instagram_posts': 0,
            'twitter_posts': 0,
            'total_engagement': 0,
            'recent_posts': []
        }
        
        # Get Meta (Facebook/Instagram) summary
        try:
            meta_resp = requests.get(f"{SOCIAL_MCP_URL}/tools/generate_meta_summary")
            if meta_resp.status_code == 200:
                meta_data = meta_resp.json()
                if meta_data.get('success'):
                    summary = meta_data.get('summary', {})
                    social['facebook_posts'] = summary.get('facebook_posts', 0)
                    social['instagram_posts'] = summary.get('instagram_posts', 0)
        except Exception as e:
            print(f"   Warning: Could not fetch Meta summary: {e}")
        
        # Get X (Twitter) summary
        try:
            x_resp = requests.get(f"{X_MCP_URL}/tools/generate_x_summary")
            if x_resp.status_code == 200:
                x_data = x_resp.json()
                if x_data.get('success'):
                    summary = x_data.get('summary', {})
                    social['twitter_posts'] = summary.get('total_posts', 0)
        except Exception as e:
            print(f"   Warning: Could not fetch X summary: {e}")
        
        social['total_posts'] = (
            social['facebook_posts'] + 
            social['instagram_posts'] + 
            social['twitter_posts']
        )
        
        print(f"   Facebook Posts: {social['facebook_posts']}")
        print(f"   Instagram Posts: {social['instagram_posts']}")
        print(f"   Twitter Posts: {social['twitter_posts']}")
        
        self.briefing_data['social_media_summary'] = social
        return social
    
    def identify_bottlenecks(self, **kwargs) -> Dict[str, Any]:
        """Identify bottlenecks and delayed tasks"""
        bottlenecks = []
        
        # Get data from previous steps
        completed = kwargs.get('read_completed_tasks', {})
        financials = kwargs.get('get_odoo_financials', {})
        
        # Check for low completion rate
        if completed.get('total_count', 0) < 5:
            bottlenecks.append({
                'type': 'low_productivity',
                'severity': 'medium',
                'description': 'Low task completion rate this week',
                'suggestion': 'Review pending tasks and prioritize high-impact activities'
            })
        
        # Check for unpaid invoices (receivables)
        if financials.get('receivables', 0) > 100000:
            bottlenecks.append({
                'type': 'cash_flow',
                'severity': 'high',
                'description': f'High receivables: PKR {financials["receivables"]:,.2f}',
                'suggestion': 'Follow up on outstanding invoices'
            })
        
        # Check pending approvals
        if PENDING_APPROVAL_DIR.exists():
            pending_count = len(list(PENDING_APPROVAL_DIR.iterdir()))
            if pending_count > 5:
                bottlenecks.append({
                    'type': 'approval_bottleneck',
                    'severity': 'medium',
                    'description': f'{pending_count} items pending approval',
                    'suggestion': 'Review and approve pending items to unblock workflows'
                })
        
        # Check needs_action directory
        if NEEDS_ACTION_DIR.exists():
            needs_action_count = len(list(NEEDS_ACTION_DIR.iterdir()))
            if needs_action_count > 50:
                bottlenecks.append({
                    'type': 'backlog',
                    'severity': 'low',
                    'description': f'{needs_action_count} items in Needs_Action',
                    'suggestion': 'Process backlog to prevent accumulation'
                })
        
        print(f"   Identified {len(bottlenecks)} bottlenecks")
        
        self.briefing_data['bottlenecks'] = bottlenecks
        return {'bottlenecks': bottlenecks}
    
    def generate_suggestions(self, **kwargs) -> List[Dict[str, str]]:
        """Generate proactive suggestions based on analysis"""
        suggestions = []
        
        # Get data from previous steps
        bottlenecks_data = kwargs.get('identify_bottlenecks', {})
        financials = kwargs.get('get_odoo_financials', {})
        
        bottlenecks = bottlenecks_data.get('bottlenecks', [])
        
        # Financial suggestions
        if financials.get('payables', 0) > 50000:
            suggestions.append({
                'category': 'finance',
                'priority': 'high',
                'action': 'Review outstanding payables',
                'details': f'PKR {financials["payables"]:,.2f} in payables - consider payment scheduling'
            })
        
        # Productivity suggestions
        if len(bottlenecks) > 0:
            for bottleneck in bottlenecks:
                suggestions.append({
                    'category': 'operations',
                    'priority': bottleneck.get('severity', 'medium'),
                    'action': f'Address {bottleneck["type"]}',
                    'details': bottleneck.get('suggestion', '')
                })
        
        # Growth suggestions (default)
        suggestions.append({
            'category': 'growth',
            'priority': 'medium',
            'action': 'Review strategic goals progress',
            'details': 'Schedule quarterly review meeting'
        })
        
        print(f"   Generated {len(suggestions)} suggestions")
        
        self.briefing_data['suggestions'] = suggestions
        return suggestions
    
    def calculate_key_metrics(self, **kwargs) -> Dict[str, Any]:
        """Calculate key business metrics"""
        # Get data from previous steps
        completed = kwargs.get('read_completed_tasks', {})
        social = kwargs.get('get_social_media_summary', {})
        financials = kwargs.get('get_odoo_financials', {})
        
        metrics = {
            'tasks_completed': completed.get('total_count', 0),
            'tasks_per_day': round(completed.get('total_count', 0) / 7, 1),
            'social_posts': social.get('total_posts', 0),
            'revenue': financials.get('revenue', 0),
            'receivables': financials.get('receivables', 0),
            'system_health': 'healthy'
        }
        
        # Calculate efficiency score
        efficiency_score = 0
        if metrics['tasks_completed'] >= 10:
            efficiency_score += 30
        elif metrics['tasks_completed'] >= 5:
            efficiency_score += 20
        else:
            efficiency_score += 10
        
        if metrics['social_posts'] >= 5:
            efficiency_score += 20
        elif metrics['social_posts'] >= 2:
            efficiency_score += 10
        
        if financials.get('odoo_status') == 'connected':
            efficiency_score += 30
        else:
            efficiency_score += 15
        
        metrics['efficiency_score'] = efficiency_score
        metrics['efficiency_rating'] = (
            'Excellent' if efficiency_score >= 80 else
            'Good' if efficiency_score >= 60 else
            'Needs Improvement'
        )
        
        print(f"   Efficiency Score: {efficiency_score}/100 ({metrics['efficiency_rating']})")
        
        self.briefing_data['key_metrics'] = metrics
        return metrics
    
    def generate_briefing_document(self, **kwargs) -> str:
        """Generate the final briefing markdown document"""
        now = datetime.now()
        period_start = now - timedelta(days=7)
        
        self.briefing_data['period'] = f"{period_start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}"
        
        # Generate filename
        filename = f"{now.strftime('%Y-%m-%d')}_Monday_Briefing.md"
        filepath = BRIEFINGS_DIR / filename
        
        # Build document content
        content = f"""# Weekly CEO Briefing

**Period:** {self.briefing_data['period']}  
**Generated:** {now.strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** Ready for Review

---

## 📊 Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| Tasks Completed | {self.briefing_data['key_metrics'].get('tasks_completed', 0)} | {'✅' if self.briefing_data['key_metrics'].get('tasks_completed', 0) >= 5 else '⚠️'} |
| Social Posts | {self.briefing_data['key_metrics'].get('social_posts', 0)} | {'✅' if self.briefing_data['key_metrics'].get('social_posts', 0) >= 2 else '⚠️'} |
| Revenue (Week) | PKR {self.briefing_data['key_metrics'].get('revenue', 0):,.2f} | 📊 |
| Receivables | PKR {self.briefing_data['key_metrics'].get('receivables', 0):,.2f} | {'⚠️' if self.briefing_data['key_metrics'].get('receivables', 0) > 100000 else '✅'} |
| Efficiency Score | {self.briefing_data['key_metrics'].get('efficiency_score', 0)}/100 | {self.briefing_data['key_metrics'].get('efficiency_rating', 'N/A')} |

---

## 🎯 Business Goals Progress

"""
        
        # Add business goals
        goals = self.briefing_data.get('business_goals', {})
        for goal in goals.get('strategic_goals', [])[:5]:
            content += f"- [ ] {goal}\n"
        
        content += "\n---\n\n"
        
        # Add completed tasks
        content += "## ✅ Completed Tasks (Last 7 Days)\n\n"
        completed = self.briefing_data.get('completed_tasks', {})
        if completed.get('tasks'):
            content += f"**Total:** {completed['total_count']} tasks\n\n"
            content += "| Date | Task | Category |\n|------|------|----------|\n"
            for task in completed['tasks'][-10:]:  # Last 10
                date = task.get('completed_at', 'N/A')[:10]
                title = task.get('title', 'Unknown')[:50]
                category = task.get('category', 'General')
                content += f"| {date} | {title} | {category} |\n"
        else:
            content += "*No tasks marked as completed this week.*\n"
        
        content += "\n---\n\n"
        
        # Add financial summary
        content += "## 💰 Financial Summary\n\n"
        financials = self.briefing_data.get('financial_summary', {})
        content += f"| Account | Amount (PKR) |\n|---------|---------------|\n"
        content += f"| Revenue (Week) | {financials.get('revenue', 0):,.2f} |\n"
        content += f"| Receivables | {financials.get('receivables', 0):,.2f} |\n"
        content += f"| Payables | {financials.get('payables', 0):,.2f} |\n"
        content += f"\n**Odoo Status:** {'🟢 Connected' if financials.get('odoo_status') == 'connected' else '🔴 Disconnected'}\n"
        
        content += "\n---\n\n"
        
        # Add social media summary
        content += "## 📱 Social Media Activity\n\n"
        social = self.briefing_data.get('social_media_summary', {})
        content += f"| Platform | Posts |\n|----------|-------|\n"
        content += f"| Facebook | {social.get('facebook_posts', 0)} |\n"
        content += f"| Instagram | {social.get('instagram_posts', 0)} |\n"
        content += f"| Twitter/X | {social.get('twitter_posts', 0)} |\n"
        content += f"| **Total** | **{social.get('total_posts', 0)}** |\n"
        
        content += "\n---\n\n"
        
        # Add bottlenecks
        content += "## ⚠️ Bottlenecks & Issues\n\n"
        bottlenecks = self.briefing_data.get('bottlenecks', [])
        if bottlenecks:
            for i, b in enumerate(bottlenecks, 1):
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(b.get('severity', 'medium'), '🟡')
                content += f"{i}. {severity_icon} **{b.get('type', 'Issue')}**: {b.get('description', 'N/A')}\n"
                content += f"   - 💡 {b.get('suggestion', 'No suggestion')}\n\n"
        else:
            content += "*No significant bottlenecks identified.*\n"
        
        content += "\n---\n\n"
        
        # Add suggestions
        content += "## 💡 Proactive Suggestions\n\n"
        suggestions = self.briefing_data.get('suggestions', [])
        if suggestions:
            for i, s in enumerate(suggestions, 1):
                priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(s.get('priority', 'medium'), '🟡')
                content += f"{i}. {priority_icon} **{s.get('action', 'N/A')}** ({s.get('category', 'general')})\n"
                content += f"   - {s.get('details', 'No details')}\n\n"
        else:
            content += "*No specific suggestions at this time.*\n"
        
        content += "\n---\n\n"
        
        # Add action items for CEO
        content += "## 📋 Action Items for CEO\n\n"
        content += "- [ ] Review completed tasks and provide feedback\n"
        content += "- [ ] Approve pending items in Pending_Approval folder\n"
        content += "- [ ] Address high-priority bottlenecks\n"
        content += "- [ ] Schedule weekly review meeting\n"
        
        content += "\n---\n\n"
        
        # Footer
        content += f"""---

*Generated by AI Digital FTE Employee*  
*Next Briefing: {(now + timedelta(days=7)).strftime('%Y-%m-%d')}*  
*Questions? Check `/Skills/mcp_management.md` for documentation*
"""
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n📄 Briefing saved to: {filepath}")
        
        return str(filepath)
    
    def update_dashboard(self, **kwargs) -> Dict[str, str]:
        """Update Dashboard.md with last briefing info"""
        dashboard_file = Path("Dashboard.md")
        
        # Get briefing path from previous step
        briefing_result = kwargs.get('generate_briefing_document', '')
        briefing_path = briefing_result if isinstance(briefing_result, str) else briefing_result.get('path', '')
        
        if not dashboard_file.exists():
            print("   ⚠️  Dashboard.md not found")
            return {'status': 'dashboard_not_found'}
        
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if "Last Briefing" section exists
        last_briefing_section = f"""
---

## 📋 Last Briefing

**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**File:** [{Path(briefing_path).name}]({briefing_path})  
**Status:** Ready for Review

"""
        
        if "## 📋 Last Briefing" in content:
            # Replace existing section
            lines = content.split('\n')
            new_lines = []
            skip = False
            for line in lines:
                if line.startswith('## 📋 Last Briefing'):
                    skip = True
                    new_lines.append(last_briefing_section.strip())
                elif skip and line.startswith('## '):
                    skip = False
                    new_lines.append(line)
                elif not skip:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        else:
            # Add new section before the last "---"
            if "---" in content:
                parts = content.rsplit('---', 1)
                content = parts[0] + last_briefing_section + '---' + parts[1]
            else:
                content += last_briefing_section
        
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Dashboard updated with last briefing info")
        
        return {'status': 'success', 'path': str(dashboard_file)}
    
    def generate(self) -> str:
        """Main entry point - generate complete CEO briefing"""
        print("\n" + "="*70)
        print("📊 Weekly CEO Briefing Generation")
        print("="*70)
        print(f"Period: {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
        
        # Define Ralph Wiggum Loop steps
        steps = [
            {
                'name': 'read_business_goals',
                'action': self.read_business_goals,
                'depends_on': [],
                'data': {}
            },
            {
                'name': 'read_completed_tasks',
                'action': self.read_completed_tasks,
                'depends_on': [],
                'data': {}
            },
            {
                'name': 'get_odoo_financials',
                'action': self.get_odoo_financials,
                'depends_on': [],
                'data': {}
            },
            {
                'name': 'get_social_media_summary',
                'action': self.get_social_media_summary,
                'depends_on': [],
                'data': {}
            },
            {
                'name': 'identify_bottlenecks',
                'action': self.identify_bottlenecks,
                'depends_on': ['read_completed_tasks', 'get_odoo_financials'],
                'data': {}
            },
            {
                'name': 'generate_suggestions',
                'action': self.generate_suggestions,
                'depends_on': ['identify_bottlenecks', 'get_odoo_financials'],
                'data': {}
            },
            {
                'name': 'calculate_key_metrics',
                'action': self.calculate_key_metrics,
                'depends_on': ['read_completed_tasks', 'get_social_media_summary', 'get_odoo_financials'],
                'data': {}
            },
            {
                'name': 'generate_briefing_document',
                'action': self.generate_briefing_document,
                'depends_on': [
                    'read_business_goals',
                    'read_completed_tasks',
                    'get_odoo_financials',
                    'get_social_media_summary',
                    'identify_bottlenecks',
                    'generate_suggestions',
                    'calculate_key_metrics'
                ],
                'data': {}
            },
            {
                'name': 'update_dashboard',
                'action': self.update_dashboard,
                'depends_on': ['generate_briefing_document'],
                'data': {}
            }
        ]
        
        # Execute Ralph Wiggum Loop
        results = self.ralph_wiggum_loop(steps)
        
        # Return briefing path
        briefing_path = results.get('generate_briefing_document', '')
        
        print("\n" + "="*70)
        print("✅ CEO Briefing Generation Complete!")
        print("="*70)
        print(f"Briefing: {briefing_path}")
        print(f"Period: {self.briefing_data['period']}")
        print(f"Tasks Completed: {self.briefing_data['key_metrics'].get('tasks_completed', 0)}")
        print(f"Social Posts: {self.briefing_data['key_metrics'].get('social_posts', 0)}")
        print(f"Efficiency: {self.briefing_data['key_metrics'].get('efficiency_score', 0)}/100")
        
        return briefing_path


# ============================================================================
# CLI Entry Point
# ============================================================================

if __name__ == "__main__":
    briefing = WeeklyCEOBriefing()
    briefing_path = briefing.generate()
    print(f"\n📄 Briefing generated: {briefing_path}")
