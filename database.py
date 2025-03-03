"""Database management for the Streamlit chat application."""
import peewee as pw
from datetime import datetime
import os
from contextlib import contextmanager
from typing import List, Dict, Optional
import logging
import uuid
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_DIR, 'chat_history.db')

# Initialize database with connection pooling
db = pw.SqliteDatabase(None)

class DatabaseManager:
    """Manages database operations with connection pooling and error handling."""
    
    @staticmethod
    def initialize_database() -> None:
        """Initialize database connection and create tables."""
        try:
            # Ensure database directory exists
            os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
            
            # Initialize database with optimized settings
            db.init(DB_FILE, pragmas={
                'journal_mode': 'wal',
                'cache_size': -1024 * 64,
                'foreign_keys': 1,
                'synchronous': 0
            })
            
            # Create tables
            with db:
                db.create_tables([Messages, Chat, Prompts], safe=True)
            logger.info(f"Database initialized successfully at {DB_FILE}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise

    @staticmethod
    @contextmanager
    def get_db():
        """Get database connection from pool."""
        if db.is_closed():
            db.connect()
        try:
            yield db
        finally:
            if not db.is_closed():
                db.close()

class BaseModel(pw.Model):
    """Base model with timestamp fields."""
    created_at = pw.DateTimeField(default=datetime.now)
    updated_at = pw.DateTimeField(default=datetime.now)
    
    class Meta:
        database = db
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class Chat(BaseModel):
    """Chat session model."""
    id = pw.CharField(primary_key=True)
    title = pw.CharField()
    last_message = pw.DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'chats'

class Messages(BaseModel):
    """Message model."""
    id = pw.AutoField()
    chat_id = pw.ForeignKeyField(Chat, backref='messages', on_delete='CASCADE')
    role = pw.CharField()
    content = pw.TextField()
    
    class Meta:
        table_name = 'messages'

class Prompts(BaseModel):
    """Prompt templates model."""
    id = pw.CharField(primary_key=True, default=lambda: str(uuid.uuid4()))
    name = pw.CharField(unique=True)
    content = pw.TextField()
    description = pw.CharField(null=True)
    is_default = pw.BooleanField(default=False)
    
    class Meta:
        table_name = 'prompts'

def get_all_chats() -> List[Dict]:
    """Get all chat sessions ordered by last message."""
    try:
        with DatabaseManager.get_db():
            chats = Chat.select().order_by(Chat.last_message.desc())
            return [{"id": chat.id, "title": chat.title} for chat in chats]
    except Exception as e:
        logger.error(f"Error fetching chats: {str(e)}")
        return []

def save_message(chat_id: Optional[str], role: str, content: str) -> str:
    """Save a message to the database."""
    try:
        with DatabaseManager.get_db():
            # Create new chat if needed
            if not chat_id:
                chat_id = str(uuid.uuid4())
                Chat.create(
                    id=chat_id,
                    title=content[:50] + "..." if len(content) > 50 else content
                )
            
            # Update chat's last message time
            try:
                chat = Chat.get(Chat.id == chat_id)
                chat.last_message = datetime.now()
                chat.save()
            except pw.DoesNotExist:
                # Create the chat if it doesn't exist
                logger.warning(f"Chat {chat_id} not found, creating new chat")
                chat_id = str(uuid.uuid4())
                Chat.create(
                    id=chat_id,
                    title=content[:50] + "..." if len(content) > 50 else content
                )
            
            # Save message
            Messages.create(
                chat_id=chat_id,
                role=role,
                content=content
            )
            
            return chat_id
    except Exception as e:
        logger.error(f"Error saving message: {str(e)}")
        # Return chat_id even if there's an error to maintain conversation flow
        return chat_id if chat_id else str(uuid.uuid4())

def get_chat_history(chat_id: str) -> List[Dict]:
    """Get chat history with proper connection handling."""
    try:
        with DatabaseManager.get_db():
            messages = (Messages
                       .select()
                       .where(Messages.chat_id == chat_id)
                       .order_by(Messages.id))
            return [{"role": msg.role, "content": msg.content} for msg in messages]
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}")
        return []

def delete_chat(chat_id: str) -> bool:
    """Delete a chat and all its messages."""
    try:
        with DatabaseManager.get_db():
            chat = Chat.get_or_none(Chat.id == chat_id)
            if chat:
                # Messages will be deleted automatically due to CASCADE
                chat.delete_instance()
                logger.info(f"Successfully deleted chat {chat_id}")
                return True
            else:
                logger.warning(f"Chat {chat_id} not found")
                return False
    except Exception as e:
        logger.error(f"Failed to delete chat {chat_id}: {str(e)}")
        return False

def save_prompt(name: str, content: str, description: Optional[str] = None, is_default: bool = False) -> bool:
    """Save a prompt template."""
    try:
        with DatabaseManager.get_db():
            Prompts.create(
                name=name,
                content=content,
                description=description,
                is_default=is_default
            )
            logger.info(f"Successfully saved prompt: {name}")
            return True
    except Exception as e:
        logger.error(f"Failed to save prompt {name}: {str(e)}")
        return False

def get_prompt(name: str) -> Optional[Dict]:
    """Get a prompt template by name."""
    try:
        with DatabaseManager.get_db():
            prompt = Prompts.get_or_none(Prompts.name == name)
            if prompt:
                return {
                    "id": prompt.id,
                    "name": prompt.name,
                    "content": prompt.content,
                    "description": prompt.description,
                    "is_default": prompt.is_default
                }
            return None
    except Exception as e:
        logger.error(f"Failed to get prompt {name}: {str(e)}")
        return None

def get_all_prompts() -> List[Dict]:
    """Get all prompt templates."""
    try:
        with DatabaseManager.get_db():
            prompts = Prompts.select()
            return [{
                "id": p.id,
                "name": p.name,
                "content": p.content,
                "description": p.description,
                "is_default": p.is_default
            } for p in prompts]
    except Exception as e:
        logger.error(f"Failed to get prompts: {str(e)}")
        return []

def delete_prompt(name: str) -> bool:
    """Delete a prompt template."""
    try:
        with DatabaseManager.get_db():
            prompt = Prompts.get(Prompts.name == name)
            prompt.delete_instance()
            logger.info(f"Deleted prompt template: {name}")
            return True
    except Exception as e:
        logger.error(f"Failed to delete prompt {name}: {str(e)}")
        return False

def create_chat(title: str) -> str:
    """Create a new chat session."""
    try:
        with DatabaseManager.get_db():
            chat_id = str(uuid.uuid4())
            Chat.create(
                id=chat_id,
                title=title
            )
            logger.info(f"Created new chat: {chat_id}")
            return chat_id
    except Exception as e:
        logger.error(f"Error creating chat: {str(e)}")
        # Generate a UUID even if database operation fails
        return str(uuid.uuid4())

# Initialize database on module import
DatabaseManager.initialize_database()
