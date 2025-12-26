"""
LangGraph Job Agent Bot - Main Entry Point

A Telegram bot that helps you find jobs, customize your resume,
and track applications using LangGraph, Groq LLM, and Google Sheets.

Usage:
    1. Copy .env.example to .env and fill in your API keys
    2. Run: python main.py
    3. Message your bot on Telegram!
"""

import asyncio
import sys
from config import Config
from bot.telegram_handler import run_bot


def main():
    """Main entry point."""
    print("🤖 LangGraph Job Agent Bot")
    print("=" * 40)
    
    # Validate configuration
    missing = Config.validate()
    if missing:
        print("\n Missing required configuration:")
        for key in missing:
            print(f"   - {key}")
        print("\n Please update your .env file with the required values.")
        print("   See .env.example for reference.")
        sys.exit(1)
    
    print(" Configuration validated")
    print(f"📁 Data directory: {Config.DATA_DIR}")
    
    # Ensure directories exist
    Config.ensure_dirs()
    
    print("\n🚀 Starting Telegram bot...")
    print("   Press Ctrl+C to stop\n")
    
    # Run the bot
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped. Goodbye!")
    except Exception as e:
        print(f"\n Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
