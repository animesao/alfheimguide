import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey,
    BigInteger, Boolean, Text, Float, JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class GuildConfig(Base):
    __tablename__ = "guild_configs"
    guild_id = Column(BigInteger, primary_key=True)
    target_channel_id = Column(BigInteger, nullable=True)
    language = Column(String(5), default="ru")

    welcome_channel_id = Column(BigInteger, nullable=True)
    welcome_message = Column(Text, default="Welcome {user}!")
    welcome_title = Column(String(100), default="Welcome!")
    welcome_footer = Column(String(100), default="Glad you joined us!")
    welcome_image_url = Column(Text, nullable=True)
    welcome_thumbnail_url = Column(Text, nullable=True)
    welcome_dm_enabled = Column(Boolean, default=False)
    welcome_dm_message = Column(Text, default="Welcome to {server}!")
    welcome_auto_role_id = Column(BigInteger, nullable=True)
    welcome_leave_message = Column(Text, default="Goodbye {user}!")
    welcome_leave_channel_id = Column(BigInteger, nullable=True)
    welcome_leave_enabled = Column(Boolean, default=True)

    embed_color = Column(Integer, default=0x3498DB)
    bot_prefix = Column(String(5), default="!")
    mod_log_channel_id = Column(BigInteger, nullable=True)

    levels_enabled = Column(Boolean, default=True)
    github_enabled = Column(Boolean, default=True)
    welcome_enabled = Column(Boolean, default=True)

    automod_enabled = Column(Boolean, default=False)
    bad_words = Column(Text, default="")
    anti_spam = Column(Boolean, default=False)
    anti_links = Column(Boolean, default=False)
    automod_action = Column(String(20), default="warn")
    mute_duration = Column(Integer, default=10)

    economy_enabled = Column(Boolean, default=True)
    stats_enabled = Column(Boolean, default=True)
    log_channel_id = Column(BigInteger, nullable=True)
    report_channel_id = Column(BigInteger, nullable=True)


class LevelConfig(Base):
    __tablename__ = "level_configs"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"), unique=True)
    enabled = Column(Boolean, default=True)
    xp_min = Column(Integer, default=5)
    xp_max = Column(Integer, default=15)
    xp_cooldown = Column(Integer, default=60)
    xp_per_message = Column(Boolean, default=True)
    xp_per_voice_minute = Column(Integer, default=2)
    level_base_xp = Column(Integer, default=100)
    level_multiplier = Column(Float, default=1.5)
    level_role_rewards = Column(JSON, default=dict)
    announce_levelup = Column(Boolean, default=True)
    announce_channel_id = Column(BigInteger, nullable=True)
    stack_roles = Column(Boolean, default=False)
    max_level = Column(Integer, default=100)
    xp_boost_role_ids = Column(JSON, default=list)
    xp_boost_multiplier = Column(Float, default=1.5)
    ignore_channel_ids = Column(JSON, default=list)
    ignore_role_ids = Column(JSON, default=list)


class Giveaway(Base):
    __tablename__ = "giveaways"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    channel_id = Column(BigInteger)
    message_id = Column(BigInteger, nullable=True)
    prize = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    winners_count = Column(Integer, default=1)
    ends_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    creator_id = Column(BigInteger)
    ended = Column(Boolean, default=False)
    required_role_id = Column(BigInteger, nullable=True)
    required_level = Column(Integer, default=0)
    required_invites = Column(Integer, default=0)
    role_reward_id = Column(BigInteger, nullable=True)
    image_url = Column(Text, nullable=True)
    color = Column(Integer, default=0x9B59B6)
    ping_on_enter = Column(Boolean, default=False)
    requirements_text = Column(Text, nullable=True)


class GiveawayEntry(Base):
    __tablename__ = "giveaway_entries"
    id = Column(Integer, primary_key=True)
    giveaway_id = Column(Integer, ForeignKey("giveaways.id"))
    user_id = Column(BigInteger)
    entered_at = Column(DateTime, default=datetime.now)


class TempBan(Base):
    __tablename__ = "temp_bans"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    user_id = Column(BigInteger)
    unban_time = Column(DateTime)
    reason = Column(String(255), default="")


class TrackedUser(Base):
    __tablename__ = "tracked_users"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    github_username = Column(String(100), nullable=False)
    guild = relationship("GuildConfig")


class RepoSnapshot(Base):
    __tablename__ = "repo_snapshots"
    id = Column(Integer, primary_key=True)
    tracked_user_id = Column(Integer, ForeignKey("tracked_users.id"))
    repo_name = Column(String(100), nullable=False)
    last_pushed_at = Column(DateTime, nullable=False)
    tracked_user = relationship("TrackedUser")


class ReleaseSnapshot(Base):
    __tablename__ = "release_snapshots"
    id = Column(Integer, primary_key=True)
    tracked_user_id = Column(Integer, ForeignKey("tracked_users.id"))
    repo_name = Column(String(100), nullable=False)
    release_tag = Column(String(100), nullable=False)
    release_name = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=False)
    is_prerelease = Column(Boolean, default=False)
    is_draft = Column(Boolean, default=False)
    tracked_user = relationship("TrackedUser")


class UserLevel(Base):
    __tablename__ = "user_levels"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    user_id = Column(BigInteger)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    last_message_xp = Column(DateTime, nullable=True)
    total_messages = Column(Integer, default=0)
    voice_minutes = Column(Integer, default=0)
    last_voice_update = Column(DateTime, nullable=True)


class Warning(Base):
    __tablename__ = "warnings"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    user_id = Column(BigInteger)
    reason = Column(String(255))
    moderator_id = Column(BigInteger)
    timestamp = Column(DateTime)


class VoiceChannelConfig(Base):
    __tablename__ = "voice_channel_configs"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    creator_channel_id = Column(BigInteger, nullable=False)
    category_id = Column(BigInteger, nullable=True)
    default_name = Column(String(100), default="{user} канал")
    default_user_limit = Column(Integer, default=0)
    control_channel_id = Column(BigInteger, nullable=True)
    bitrate = Column(Integer, default=64000)
    region = Column(String(20), nullable=True)
    send_panel_on_create = Column(Boolean, default=True)
    delete_when_empty = Column(Boolean, default=True)
    empty_timeout_seconds = Column(Integer, default=30)


class TempVoiceChannel(Base):
    __tablename__ = "temp_voice_channels"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    channel_id = Column(BigInteger, nullable=False, unique=True)
    owner_id = Column(BigInteger, nullable=False)
    name = Column(String(100))
    user_limit = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    last_empty_check = Column(DateTime, nullable=True)


class TicketCategory(Base):
    __tablename__ = "ticket_categories"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    name = Column(String(100), nullable=False)
    modal_title = Column(String(100), default="Причина открытия тикета")
    modal_label = Column(String(100), default="Опишите вашу проблему")
    modal_placeholder = Column(String(200), default="Например: Жалоба на игрока / Техническая ошибка")


class VerificationConfig(Base):
    __tablename__ = "verification_configs"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, unique=True, nullable=False)
    channel_id = Column(BigInteger, nullable=True)
    welcome_channel_id = Column(BigInteger, nullable=True)
    message_id = Column(BigInteger, nullable=True)
    title = Column(String(200), default="Верификация")
    description = Column(Text, default="Нажмите кнопку ниже для верификации")
    embed_color = Column(Integer, default=0x3498DB)
    banner_url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    footer_text = Column(String(200), nullable=True)
    enabled = Column(Boolean, default=False)
    require_button_click = Column(Boolean, default=True)
    verified_role_id = Column(BigInteger, nullable=True)
    style = Column(String(20), default="buttons")
    code_verification_enabled = Column(Boolean, default=False)
    code_length = Column(Integer, default=6)
    dm_verification_message = Column(Text, default="Ваш код верификации: {code}")


class VerificationButton(Base):
    __tablename__ = "verification_buttons"
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey("verification_configs.id"))
    button_id = Column(String(50), unique=True, nullable=False)
    label = Column(String(100), nullable=False)
    emoji = Column(String(100), nullable=True)
    style = Column(String(20), default="primary")
    action_type = Column(String(30), default="role")
    action_value = Column(String(200), nullable=True)
    message_text = Column(Text, nullable=True)
    channel_id = Column(BigInteger, nullable=True)
    dm_enabled = Column(Boolean, default=False)
    dm_text = Column(Text, nullable=True)
    order = Column(Integer, default=0)


class VerificationCode(Base):
    __tablename__ = "verification_codes"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger)
    user_id = Column(BigInteger)
    code = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)


class UserEconomy(Base):
    __tablename__ = "user_economy"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    user_id = Column(BigInteger)
    balance = Column(Integer, default=0)
    bank = Column(Integer, default=0)
    last_daily = Column(DateTime, nullable=True)
    last_work = Column(DateTime, nullable=True)


class ShopItem(Base):
    __tablename__ = "shop_items"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    item_type = Column(String(20), default="role")
    item_value = Column(String(200), nullable=True)
    stock = Column(Integer, default=-1)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    user_id = Column(BigInteger)
    amount = Column(Integer)
    transaction_type = Column(String(50))
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)


class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=True)
    user_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    remind_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Poll(Base):
    __tablename__ = "polls"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    channel_id = Column(BigInteger)
    message_id = Column(BigInteger, unique=True)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)
    creator_id = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.now)
    ends_at = Column(DateTime, nullable=True)
    multiple_choice = Column(Boolean, default=False)


class PollVote(Base):
    __tablename__ = "poll_votes"
    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey("polls.id"))
    user_id = Column(BigInteger)
    option_index = Column(Integer)


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    reporter_id = Column(BigInteger)
    reported_user_id = Column(BigInteger)
    reason = Column(Text)
    message_link = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    moderator_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    resolved_at = Column(DateTime, nullable=True)


class MessageLog(Base):
    __tablename__ = "message_logs"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    message_id = Column(BigInteger, unique=True)
    channel_id = Column(BigInteger)
    user_id = Column(BigInteger)
    content = Column(Text)
    attachments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    edited_at = Column(DateTime, nullable=True)
    old_content = Column(Text, nullable=True)


class UserActivity(Base):
    __tablename__ = "user_activity"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    user_id = Column(BigInteger)
    date = Column(DateTime, default=datetime.now)
    message_count = Column(Integer, default=0)
    voice_minutes = Column(Integer, default=0)


class RaidProtection(Base):
    __tablename__ = "raid_protection"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"), unique=True)
    enabled = Column(Boolean, default=False)
    join_threshold = Column(Integer, default=5)
    action = Column(String(20), default="kick")
    lockdown_duration = Column(Integer, default=10)


class SuspiciousJoin(Base):
    __tablename__ = "suspicious_joins"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"))
    user_id = Column(BigInteger)
    joined_at = Column(DateTime, default=datetime.now)


class AutoModConfig(Base):
    __tablename__ = "automod_configs"
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guild_configs.guild_id"), unique=True)
    enabled = Column(Boolean, default=False)
    anti_spam_enabled = Column(Boolean, default=False)
    spam_threshold = Column(Integer, default=5)
    spam_window = Column(Integer, default=5)
    spam_action = Column(String(20), default="mute")
    spam_mute_duration = Column(Integer, default=5)
    anti_links_enabled = Column(Boolean, default=False)
    anti_links_action = Column(String(20), default="warn")
    allowed_link_roles = Column(JSON, default=list)
    bad_words_enabled = Column(Boolean, default=False)
    bad_words_list = Column(Text, default="")
    bad_words_action = Column(String(20), default="warn")
    caps_enabled = Column(Boolean, default=False)
    caps_threshold = Column(Integer, default=70)
    caps_min_length = Column(Integer, default=10)
    caps_action = Column(String(20), default="warn")
    auto_mute_reason = Column(String(100), default="Automatic mute for rule violation")


DATABASE_URL = "sqlite:///db/bot-db.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    os.makedirs(os.path.dirname("db/"), exist_ok=True)
    Base.metadata.create_all(bind=engine)
