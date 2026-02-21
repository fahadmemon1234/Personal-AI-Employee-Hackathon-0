"""
Quick Twitter Post Generator - Auto Mode
Generates 5 Twitter posts automatically
"""

import os
import sys
import codecs
import random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

MAX_TWEET_LENGTH = 280

# Post templates with hashtags
TEMPLATES = [
    "🚀 {content}\n\n#AI #Automation #Tech",
    "💡 {content}\n\n#Innovation #Business #DigitalTransformation",
    "✨ {content}\n\n#MachineLearning #Productivity #Future",
    "📊 {content}\n\n#Data #Analytics #Growth",
    "🎯 {content}\n\n#Goals #Success #Entrepreneur",
    "{content}\n\nRead more 👇\n\n#Tech #AI",
    "🔥 Breaking: {content}\n\n#News #Update #Tech",
    "📈 Update: {content}\n\n#Business #Growth #Success",
]

# Content variations
CONTENTS = [
    "Our AI automation system just processed 1000+ tasks this week. The future of work is here!",
    "Automating repetitive tasks saves 20+ hours per week. What would you do with extra time?",
    "AI-powered automation is not replacing jobs, it's enhancing human potential.",
    "Just integrated LinkedIn + Email + WhatsApp automation. One system, endless possibilities!",
    "Small businesses using automation see 3x growth in first year. Are you automating yet?",
    "Customer satisfaction up 40% after implementing automated responses. Speed matters!",
    "The ROI of automation: 5 hours saved daily = 125 days per year. Do the math! 📊",
    "2026 Trend: 80% of businesses will use AI automation. Where does your company stand?",
    "Remote work + Automation = The perfect combination for productivity.",
    "Pro tip: Schedule your social posts in advance. Consistency is key! 🔑",
    "New feature alert! Real-time notifications now available for all workflows.",
    "System update: 99.9% uptime achieved this month. Reliability is our priority.",
    "Integration complete: Now supporting LinkedIn, Twitter, Email & WhatsApp in one dashboard.",
    "Performance boost: API response times reduced by 60% after latest optimization.",
    "The companies winning today are those that embraced automation early.",
]

def generate_tweet():
    """Generate a single tweet"""
    template = random.choice(TEMPLATES)
    content = random.choice(CONTENTS)
    
    tweet = template.format(content=content)
    
    # Ensure within limit
    if len(tweet) > MAX_TWEET_LENGTH:
        tweet = tweet[:MAX_TWEET_LENGTH-3] + "..."
    
    return tweet

def save_tweet(content):
    """Save tweet to Pending_Approval"""
    pending_dir = Path("Pending_Approval")
    pending_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"twitter_post_{timestamp}.txt"
    filepath = pending_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

print("="*60)
print("  TWITTER POST GENERATOR (Auto)")
print("  Generating 5 Twitter-optimized posts")
print("="*60)

print("\n📝 Generating posts...\n")

for i in range(5):
    tweet = generate_tweet()
    filename = save_tweet(tweet)
    print(f"{i+1}. ✅ {filename}")
    print(f"   {tweet[:80]}...")
    print(f"   Length: {len(tweet)} chars\n")

print("="*60)
print("✅ Generated 5 Twitter posts!")
print("   Location: Pending_Approval/")
print("\nNext step: Run 'python approve_twitter_simple.py' to post")
print("="*60)
