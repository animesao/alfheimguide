import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import Base, GuildConfig, SessionLocal, engine


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_guild_config_create(db_session):
    gc = GuildConfig(guild_id=12345)
    db_session.add(gc)
    db_session.commit()

    found = db_session.query(GuildConfig).filter_by(guild_id=12345).first()
    assert found is not None
    assert found.guild_id == 12345
    assert found.language == "ru"
    assert found.welcome_enabled is True


def test_guild_config_defaults(db_session):
    gc = GuildConfig(guild_id=67890)
    db_session.add(gc)
    db_session.commit()

    assert gc.welcome_enabled is True
    assert gc.levels_enabled is True
    assert gc.economy_enabled is True
    assert gc.embed_color == 0x3498DB
