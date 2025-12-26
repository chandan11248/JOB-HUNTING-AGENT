"""Telegram bot handler with async polling."""

import logging
import os
from telegram import Update, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters,
    ContextTypes
)
from langchain_core.messages import HumanMessage

from config import Config
from agent.graph import job_agent
from agent.state import create_initial_state
from tools.resume_parser import parse_resume, save_resume_text, load_resume_text

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# In-memory user state storage (simple approach)
user_states: dict = {}


def get_user_state(user_id: str) -> dict:
    """Get or create user state."""
    if user_id not in user_states:
        user_states[user_id] = create_initial_state(user_id)
        # Try to load existing resume
        resume = load_resume_text(user_id, Config.DATA_DIR)
        if resume:
            user_states[user_id]["base_resume"] = resume
    return user_states[user_id]


def update_user_state(user_id: str, updates: dict) -> None:
    """Update user state with new values."""
    state = get_user_state(user_id)
    state.update(updates)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user_id = str(update.effective_user.id)
    state = get_user_state(user_id)
    
    # Run through agent
    state["messages"] = [HumanMessage(content="/start")]
    result = job_agent.invoke(state)
    
    await update.message.reply_text(
        result.get("response", "Welcome! Use /help to see commands."),
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    user_id = str(update.effective_user.id)
    state = get_user_state(user_id)
    
    state["messages"] = [HumanMessage(content="/help")]
    result = job_agent.invoke(state)
    
    await update.message.reply_text(
        result.get("response", "Use /search, /customize, /export"),
        parse_mode="Markdown"
    )


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /search command."""
    if not update.message:
        return
    
    user_id = str(update.effective_user.id)
    state = get_user_state(user_id)
    
    # Get full command text
    command_text = update.message.text
    
    state["messages"] = [HumanMessage(content=command_text)]
    result = job_agent.invoke(state)
    
    # Update state with results and search params
    update_user_state(user_id, {
        "jobs_found": result.get("jobs_found", []),
        "search_query": result.get("search_query"),
        "location": result.get("location")
    })
    
    await update.message.reply_text(
        result.get("response", "Search completed."),
        disable_web_page_preview=True
    )


async def customize_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /customize command."""
    if not update.message:
        return
    
    user_id = str(update.effective_user.id)
    state = get_user_state(user_id)
    
    command_text = update.message.text
    
    state["messages"] = [HumanMessage(content=command_text)]
    result = job_agent.invoke(state)
    
    # Update state with customized docs
    if result.get("customized_resume"):
        update_user_state(user_id, {
            "customized_resume": result["customized_resume"],
            "cover_letter": result.get("cover_letter"),
            "selected_job": result.get("selected_job")
        })
    
    # Split long response
    response = result.get("response", "Customization completed.")
    if len(response) > 4000:
        # Send in chunks
        chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(response)


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /export command."""
    user_id = str(update.effective_user.id)
    state = get_user_state(user_id)
    
    state["messages"] = [HumanMessage(content="/export")]
    result = job_agent.invoke(state)
    
    if result.get("sheets_exported"):
        update_user_state(user_id, {
            "sheets_exported": True,
            "sheets_url": result.get("sheets_url")
        })
    
    await update.message.reply_text(
        result.get("response", "Export completed."),
        parse_mode="Markdown",
        disable_web_page_preview=False
    )


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /chat command."""
    if not update.message:
        return
        
    user_id = str(update.effective_user.id)
    state = get_user_state(user_id)
    
    command_text = update.message.text
    
    # Store message in history
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(HumanMessage(content=command_text))
    
    # Run through agent
    result = job_agent.invoke(state)
    
    # Update local state messages (LangGraph doesn't always sync back list updates)
    state["messages"].append(result.get("messages", [])[-1] if result.get("messages") else "")
    
    await update.message.reply_text(
        result.get("response", "How can I help you today?"),
        disable_web_page_preview=True
    )


async def more_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /more command."""
    if not update.message:
        return
        
    user_id = str(update.effective_user.id)
    state = get_user_state(user_id)
    
    # Store message in history
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(HumanMessage(content="/more"))
    
    # Run through agent
    result = job_agent.invoke(state)
    
    # Update local state
    update_user_state(user_id, {
        "jobs_found": result.get("jobs_found", []),
        "search_query": result.get("search_query"),
        "location": result.get("location")
    })
    
    await update.message.reply_text(
        result.get("response", "Finding more jobs..."),
        disable_web_page_preview=True
    )


async def compose_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /compose command."""
    if not update.message:
        return
        
    user_id = str(update.effective_user.id)
    state = get_user_state(user_id)
    
    # Store message in history
    if "messages" not in state:
        state["messages"] = []
    state["messages"].append(HumanMessage(content="/compose"))
    
    # Run through agent
    result = job_agent.invoke(state)
    
    # Update local state
    if result.get("composed_pdf_path"):
        update_user_state(user_id, {"composed_pdf_path": result["composed_pdf_path"]})
    
    await update.message.reply_text(result.get("response", "Composing PDF..."))
    
    # Send the PDF file
    pdf_path = result.get("composed_pdf_path")
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename="Job_Application.pdf",
                caption="📄 Here is your professional CV and Cover Letter!"
            )


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /resume command - prompt for resume upload."""
    await update.message.reply_text(
        "📄 Please send your resume file (PDF, DOCX, or TXT) as a reply to this message.\n\n"
        "Just upload the file directly - I'll process it automatically.",
        parse_mode="Markdown"
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document uploads (resume files)."""
    user_id = str(update.effective_user.id)
    document = update.message.document
    
    if not document:
        return
    
    filename = document.file_name
    supported = [".pdf", ".docx", ".doc", ".txt"]
    
    if not any(filename.lower().endswith(ext) for ext in supported):
        await update.message.reply_text(
            f"❌ Unsupported file format. Please upload: {', '.join(supported)}"
        )
        return
    
    await update.message.reply_text("📥 Downloading and processing your resume...")
    
    try:
        # Download file
        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()
        
        # Parse resume
        resume_text = parse_resume(bytes(file_bytes), filename)
        
        if resume_text.startswith("Error"):
            await update.message.reply_text(f"❌ {resume_text}")
            return
        
        # Save to state and file
        Config.ensure_dirs()
        save_resume_text(resume_text, user_id, Config.DATA_DIR)
        update_user_state(user_id, {"base_resume": resume_text})
        
        preview = resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
        
        await update.message.reply_text(
            f"✅ **Resume uploaded successfully!**\n\n"
            f"**Preview:**\n```\n{preview}\n```\n\n"
            f"📝 Now use /search to find jobs!",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error processing resume: {e}")
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plain text messages (job number shortcuts)."""
    if not update.message or not update.message.text:
        return
    
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    # Check if it's a job number
    try:
        job_num = int(text)
        # Redirect to customize
        state = get_user_state(user_id)
        state["messages"] = [HumanMessage(content=f"/customize {job_num}")]
        result = job_agent.invoke(state)
        
        if result.get("customized_resume"):
            update_user_state(user_id, {
                "customized_resume": result["customized_resume"],
                "cover_letter": result.get("cover_letter"),
                "jobs_found": result.get("jobs_found", []),
                "search_query": result.get("search_query"),
                "location": result.get("location")
            })
        
        response = result.get("response", "")
        if len(response) > 4000:
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response)
            
    except ValueError:
        # Not a number - treat as chat message
        state = get_user_state(user_id)
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append(HumanMessage(content=text))
        
        result = job_agent.invoke(state)
        
        # Update session history
        if result.get("messages"):
             state["messages"].append(result["messages"][-1])
             
        await update.message.reply_text(
            result.get("response", "How can I help you?"),
            disable_web_page_preview=True
        )


async def set_bot_commands(application: Application) -> None:
    """Set bot commands for Telegram menu."""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help message"),
        BotCommand("search", "Search for jobs - /search <keywords> <location>"),
        BotCommand("customize", "Customize resume - /customize <job_number>"),
        BotCommand("export", "Export jobs to Google Sheets"),
        BotCommand("resume", "Upload your resume"),
        BotCommand("chat", "Chat about job advice and suggestions"),
        BotCommand("more", "Find more jobs from other platforms"),
        BotCommand("compose", "Generate professional PDF CV & Cover Letter"),
    ]
    await application.bot.set_my_commands(commands)


def create_bot() -> Application:
    """Create and configure the Telegram bot application."""
    # Validate config
    missing = Config.validate()
    if missing:
        raise ValueError(f"Missing required config: {', '.join(missing)}")
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("customize", customize_command))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(CommandHandler("resume", resume_command))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(CommandHandler("more", more_command))
    application.add_handler(CommandHandler("compose", compose_command))
    
    # Document handler for resume uploads
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Text handler for job number shortcuts
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    return application


async def run_bot() -> None:
    """Run the bot with polling."""
    application = create_bot()
    
    # Set commands
    await set_bot_commands(application)
    
    logger.info("🤖 Bot is starting...")
    
    # Run polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    logger.info("🚀 Bot is running! Press Ctrl+C to stop.")
    
    # Keep running
    try:
        while True:
            import asyncio
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    
    await application.updater.stop()
    await application.stop()
    await application.shutdown()
