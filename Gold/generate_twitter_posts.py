"""
Twitter Post Generator
======================
Generates Twitter-optimized posts from content/topics
Creates posts in Pending_Approval folder
"""

import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import random

load_dotenv()

# Twitter settings
MAX_TWEET_LENGTH = 280
HASHTAGS = [
    "#AI", "#Automation", "#Tech", "#Innovation", "#DigitalTransformation",
    "#MachineLearning", "#Business", "#Startup", "#Productivity", "#Future"
]

# Post templates
TEMPLATES = [
    "🚀 {content}\n\n{hashtags}",
    "💡 {content}\n\n{hashtags}",
    "✨ {content}\n\n{hashtags}",
    "📊 {content}\n\n{hashtags}",
    "🎯 {content}\n\n{hashtags}",
    "{content}\n\nRead more 👇\n\n{hashtags}",
    "🔥 Breaking: {content}\n\n{hashtags}",
    "📈 Update: {content}\n\n{hashtags}",
]

# Topics for generating posts
TOPICS = [
    {
        "title": "AI Automation",
        "contents": [
            "Our AI automation system just processed 1000+ tasks this week. The future of work is here!",
            "Automating repetitive tasks saves 20+ hours per week. What would you do with extra time?",
            "AI-powered automation is not replacing jobs, it's enhancing human potential.",
            "Just integrated LinkedIn + Email + WhatsApp automation. One system, endless possibilities!",
        ]
    },
    {
        "title": "Business Growth",
        "contents": [
            "Small businesses using automation see 3x growth in first year. Are you automating yet?",
            "Customer satisfaction up 40% after implementing automated responses. Speed matters!",
            "The ROI of automation: 5 hours saved daily = 125 days per year. Do the math! 📊",
            "From manual to automated: Our journey of digital transformation.",
        ]
    },
    {
        "title": "Tech Updates",
        "contents": [
            "New feature alert! 🚨 Real-time notifications now available for all workflows.",
            "System update: 99.9% uptime achieved this month. Reliability is our priority.",
            "Integration complete: Now supporting LinkedIn, Twitter, Email & WhatsApp in one dashboard.",
            "Performance boost: API response times reduced by 60% after latest optimization.",
        ]
    },
    {
        "title": "Industry Insights",
        "contents": [
            "2026 Trend: 80% of businesses will use AI automation. Where does your company stand?",
            "Remote work + Automation = The perfect combination for productivity.",
            "Customer expectations are changing. Automated systems help you keep up 24/7.",
            "The companies winning today are those that embraced automation early.",
        ]
    },
    {
        "title": "Tips & Tricks",
        "contents": [
            "Pro tip: Schedule your social posts in advance. Consistency is key! 🔑",
            "Automation hack: Use templates for repetitive responses. Save time, stay consistent.",
            "Best practice: Always review automated posts before publishing. Quality matters!",
            "Time-saving tip: Batch create content weekly, schedule automatically. Work smarter!",
        ]
    },
]


def generate_hashtags(count=3):
    """Generate random hashtags"""
    return " ".join(random.sample(HASHTAGS, min(count, len(HASHTAGS))))


def create_tweet(content, hashtags_count=3):
    """Create a tweet with hashtags"""
    template = random.choice(TEMPLATES)
    hashtags = generate_hashtags(hashtags_count)
    
    tweet = template.format(
        content=content,
        hashtags=hashtags
    )
    
    # Ensure within limit
    if len(tweet) > MAX_TWEET_LENGTH:
        # Reduce hashtags
        tweet = template.format(
            content=content,
            hashtags=generate_hashtags(1)
        )
    
    # Final check - truncate if needed
    if len(tweet) > MAX_TWEET_LENGTH:
        remaining = MAX_TWEET_LENGTH - 3 - len(hashtags)
        tweet = template.format(
            content=content[:remaining],
            hashtags=hashtags
        )
    
    return tweet[:MAX_TWEET_LENGTH]


def save_tweet(content, topic="general"):
    """Save tweet to Pending_Approval folder"""
    pending_dir = Path("Pending_Approval")
    pending_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"twitter_post_{timestamp}.txt"
    filepath = pending_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created: {filename}")
    return filepath


def generate_posts(count=5):
    """Generate multiple Twitter posts"""
    print(f"\n📝 Generating {count} Twitter posts...\n")
    
    created = 0
    for i in range(count):
        # Pick random topic
        topic = random.choice(TOPICS)
        content = random.choice(topic["contents"])
        
        # Create tweet
        tweet = create_tweet(content)
        
        # Save
        save_tweet(tweet, topic["title"])
        created += 1
        
        print(f"   Content: {content[:50]}...")
        print(f"   Length: {len(tweet)} chars\n")
    
    print(f"✅ Generated {created} Twitter posts!")
    print(f"   Location: Pending_Approval/")


def generate_from_topic(topic_index=None):
    """Generate posts from specific topic"""
    if topic_index is not None and 0 <= topic_index < len(TOPICS):
        topics = [TOPICS[topic_index]]
    else:
        topics = TOPICS
    
    print("\n📋 Available Topics:")
    for i, topic in enumerate(topics, 1):
        print(f"   {i}. {topic['title']} ({len(topic['contents'])} variations)")
    
    print("\nGenerating posts from all topics...\n")
    
    for topic in topics:
        print(f"\n📌 Topic: {topic['title']}")
        for content in topic["contents"]:
            tweet = create_tweet(content)
            save_tweet(tweet, topic["title"])
            print(f"   ✅ {content[:40]}...")


def custom_tweet():
    """Create custom tweet from user input"""
    print("\n✏️  Create Custom Tweet\n")
    print(f"   Max length: {MAX_TWEET_LENGTH} characters\n")
    
    content = input("Enter your tweet: ").strip()
    
    if not content:
        print("❌ Empty content")
        return
    
    # Add hashtags
    add_hashtags = input("Add hashtags? (y/n): ").strip().lower()
    if add_hashtags == 'y':
        content = create_tweet(content)
    
    # Check length
    if len(content) > MAX_TWEET_LENGTH:
        print(f"\n⚠️  Too long: {len(content)} chars (max: {MAX_TWEET_LENGTH})")
        truncate = input("Truncate? (y/n): ").strip().lower()
        if truncate == 'y':
            content = content[:MAX_TWEET_LENGTH-3] + "..."
        else:
            print("❌ Not saved")
            return
    
    # Save
    save_tweet(content, "custom")
    print(f"\n✅ Tweet saved! ({len(content)} chars)")
    print(f"   Content: {content}")


def main():
    print("="*60)
    print("  TWITTER POST GENERATOR")
    print("  Create Twitter-optimized posts")
    print("="*60)
    
    print("\nOptions:")
    print("  1. Generate random posts (5)")
    print("  2. Generate from all topics")
    print("  3. Generate from specific topic")
    print("  4. Create custom tweet")
    print("  5. View pending tweets")
    print("  0. Exit")
    print("-"*60)
    
    choice = input("\nYour choice (0-5): ").strip()
    
    if choice == "0":
        print("\n👋 Goodbye!")
        return
    
    elif choice == "1":
        count = input("How many posts? (default 5): ").strip()
        count = int(count) if count.isdigit() else 5
        generate_posts(count)
    
    elif choice == "2":
        generate_from_topic()
    
    elif choice == "3":
        print("\nSelect topic:")
        for i, topic in enumerate(TOPICS, 1):
            print(f"   {i}. {topic['title']}")
        
        idx = input("\nTopic number: ").strip()
        if idx.isdigit():
            idx = int(idx) - 1
            if 0 <= idx < len(TOPICS):
                generate_from_topic(idx)
    
    elif choice == "4":
        custom_tweet()
    
    elif choice == "5":
        pending_dir = Path("Pending_Approval")
        if pending_dir.exists():
            tweets = list(pending_dir.glob("twitter_post_*.txt"))
            print(f"\n📁 Found {len(tweets)} Twitter posts:\n")
            for i, tweet in enumerate(tweets[-10:], 1):
                with open(tweet, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   {i}. {tweet.name}")
                print(f"      {content[:60]}...")
                print(f"      Length: {len(content)} chars\n")
        else:
            print("\n✅ No pending tweets found!")
    
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
