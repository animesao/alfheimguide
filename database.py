import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, BigInteger, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class GuildConfig(Base):
    __tablename__ = 'guild_configs'
    guild_id = Column(BigInteger, primary_key=True)
    target_channel_id = Column(BigInteger, nullable=True)
    language = Column(String(5), default='ru')
    
    # Auto-mod settings
    automod_enabled = Column(Boolean, default=False)
    bad_words = Column(Text, default='') # Comma separated
    
    # Greeting settings
    welcome_channel_id = Column(BigInteger, nullable=True)
    welcome_message = Column(Text, default='Welcome {user}!')
    welcome_title = Column(String(100), default='Welcome!')
    welcome_footer = Column(String(100), default='Glad you joined us!')
    welcome_image_url = Column(Text, nullable=True)
    
    # Customization
    embed_color = Column(Integer, default=0x3498db) # Default blue
    bot_prefix = Column(String(5), default='!')

    # Log settings
    mod_log_channel_id = Column(BigInteger, nullable=True)
    
    # Module toggles
    levels_enabled = Column(Boolean, default=True)
    github_enabled = Column(Boolean, default=True)
    welcome_enabled = Column(Boolean, default=True)
    
    # Automod settings
    automod_enabled = Column(Boolean, default=False)
    bad_words = Column(Text, default='') # Comma separated
    anti_spam = Column(Boolean, default=False)
    anti_links = Column(Boolean, default=False)

class TrackedUser(Base):
    __tablename__ = 'tracked_users'
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guild_configs.guild_id'))
    github_username = Column(String(100), nullable=False)
    
    guild = relationship("GuildConfig")

class RepoSnapshot(Base):
    __tablename__ = 'repo_snapshots'
    id = Column(Integer, primary_key=True)
    tracked_user_id = Column(Integer, ForeignKey('tracked_users.id'))
    repo_name = Column(String(100), nullable=False)
    last_pushed_at = Column(DateTime, nullable=False)
    
    tracked_user = relationship("TrackedUser")

class UserLevel(Base):
    __tablename__ = 'user_levels'
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guild_configs.guild_id'))
    user_id = Column(BigInteger)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)

class Warning(Base):
    __tablename__ = 'warnings'
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guild_configs.guild_id'))
    user_id = Column(BigInteger)
    reason = Column(String(255))
    moderator_id = Column(BigInteger)
    timestamp = Column(DateTime)

class VoiceChannelConfig(Base):
    __tablename__ = 'voice_channel_configs'
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guild_configs.guild_id'))
    creator_channel_id = Column(BigInteger, nullable=False)
    category_id = Column(BigInteger, nullable=True)
    default_name = Column(String(100), default='{user} канал')
    default_user_limit = Column(Integer, default=0)
    control_channel_id = Column(BigInteger, nullable=True)

class TempVoiceChannel(Base):
    __tablename__ = 'temp_voice_channels'
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey('guild_configs.guild_id'))
    channel_id = Column(BigInteger, nullable=False, unique=True)
    owner_id = Column(BigInteger, nullable=False)
    name = Column(String(100))
    user_limit = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)

class TicketCategory(Base):
    __tablename__ = 'ticket_categories'
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    name = Column(String(100), nullable=False)
    modal_title = Column(String(100), default='Причина открытия тикета')
    modal_label = Column(String(100), default='Опишите вашу проблему')
    modal_placeholder = Column(String(200), default='Например: Жалоба на игрока / Техническая ошибка')

# Use local SQLite database
DATABASE_URL = 'sqlite:///db/bot-db.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
