"""
booking_db.py — persistent storage for astrologer consultations.

This is the only part of the backend that stores anything. The horoscope
endpoints remain stateless; only a booking (made with the user's consent)
is kept, and its personal data is wiped RETENTION_DAYS after the appointment
(see purge_personal_data()).

Database: PostgreSQL, reached through the DATABASE_URL environment variable,
e.g. a free Neon or Supabase database:
    DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
The web host's disk is wiped on every deploy, so SQLite is used only by the
tests. Every time is stored in UTC (timestamptz) and turned into IST only for
display.

Double bookings are impossible because of the partial unique index
uq_bookings_confirmed_slot: the database itself refuses a second confirmed
booking for the same astrologer and slot, whatever the number of server
processes or threads. Nothing about a booking is kept in process memory.

The same tables are written out as plain SQL in schema.sql.
"""
import os
from datetime import datetime, timezone

from sqlalchemy import (JSON, Boolean, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer,
                        MetaData, SmallInteger, String, Table, Text, create_engine, text)

metadata = MetaData()

astrologers = Table(
    'astrologers', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(80), nullable=False),
    Column('age', SmallInteger, nullable=False),
    Column('phone_e164', String(20), nullable=False),   # shown publicly on the list page, by design
    Column('email', String(254), nullable=False),
    Column('fee_inr', Integer, nullable=False),
    Column('is_active', Boolean, nullable=False, server_default=text('true')),
    Column('bio', Text),
    Column('languages', String(120)),
    Column('created_at', DateTime(timezone=True), nullable=False),
    Column('updated_at', DateTime(timezone=True), nullable=False),
    CheckConstraint('age BETWEEN 18 AND 120', name='ck_astrologers_age'),
    CheckConstraint('fee_inr >= 0', name='ck_astrologers_fee'),
)

# Weekly working hours in IST, one row per window: weekday 0 = Monday.
# An astrologer with no rows at all is available 09:00-20:00 every day.
availability = Table(
    'availability', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('astrologer_id', Integer, ForeignKey('astrologers.id', ondelete='CASCADE'), nullable=False),
    Column('weekday', SmallInteger, nullable=False),
    Column('start_min', SmallInteger, nullable=False),   # minutes after IST midnight
    Column('end_min', SmallInteger, nullable=False),
    CheckConstraint('weekday BETWEEN 0 AND 6', name='ck_availability_weekday'),
    CheckConstraint('start_min >= 0 AND end_min <= 1440 AND start_min < end_min', name='ck_availability_range'),
)
Index('ix_availability_astrologer', availability.c.astrologer_id)

# One-off unavailable ranges (leave, festival days), in UTC.
availability_blocks = Table(
    'availability_blocks', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('astrologer_id', Integer, ForeignKey('astrologers.id', ondelete='CASCADE'), nullable=False),
    Column('start_utc', DateTime(timezone=True), nullable=False),
    Column('end_utc', DateTime(timezone=True), nullable=False),
    Column('reason', String(120)),
    CheckConstraint('start_utc < end_utc', name='ck_blocks_range'),
)
Index('ix_blocks_astrologer', availability_blocks.c.astrologer_id, availability_blocks.c.start_utc)

bookings = Table(
    'bookings', metadata,
    Column('id', String(36), primary_key=True),          # UUID4
    Column('astrologer_id', Integer, ForeignKey('astrologers.id'), nullable=False),
    Column('slot_start_utc', DateTime(timezone=True), nullable=False),
    Column('slot_end_utc', DateTime(timezone=True), nullable=False),
    Column('status', String(12), nullable=False),         # confirmed | cancelled
    Column('user_name', String(80), nullable=False),
    Column('user_email', String(254), nullable=False),
    Column('user_whatsapp', String(20), nullable=False),
    Column('questions', JSON, nullable=False),            # list of up to 5 strings
    Column('horoscope_input', JSON, nullable=False),      # birth details only, not the computed chart
    Column('lang', String(4), nullable=False),
    Column('cancel_token_hash', String(64), nullable=False),
    Column('idempotency_key', String(64), unique=True),
    Column('consent_share_at', DateTime(timezone=True), nullable=False),
    Column('consent_messages_at', DateTime(timezone=True), nullable=False),
    Column('adult_confirmed_at', DateTime(timezone=True), nullable=False),
    Column('notification_status', JSON, nullable=False),
    Column('created_at', DateTime(timezone=True), nullable=False),
    Column('cancelled_at', DateTime(timezone=True)),
    Column('cancelled_by', String(12)),                   # user | admin
    Column('purged_at', DateTime(timezone=True)),         # personal data wiped
    CheckConstraint("status IN ('confirmed', 'cancelled')", name='ck_bookings_status'),
)
Index('uq_bookings_confirmed_slot', bookings.c.astrologer_id, bookings.c.slot_start_utc, unique=True,
      postgresql_where=text("status = 'confirmed'"), sqlite_where=text("status = 'confirmed'"))
Index('ix_bookings_slot', bookings.c.slot_start_utc)

# Notifications waiting to be sent, one row per message. Written in the same
# transaction as the booking, sent by the background worker in notify.py.
outbox = Table(
    'outbox', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('booking_id', String(36), ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False),
    Column('event', String(20), nullable=False),          # confirmed | cancelled
    Column('channel', String(12), nullable=False),        # email
    Column('recipient', String(12), nullable=False),      # user | astrologer
    Column('status', String(10), nullable=False),         # pending | sent | failed | skipped
    Column('attempts', SmallInteger, nullable=False, server_default=text('0')),
    Column('next_attempt_at', DateTime(timezone=True), nullable=False),
    Column('last_error', String(300)),
    Column('created_at', DateTime(timezone=True), nullable=False),
    Column('sent_at', DateTime(timezone=True)),
)
Index('ix_outbox_due', outbox.c.status, outbox.c.next_attempt_at)

_engine = None


def utcnow():
    return datetime.now(timezone.utc)


def as_utc(dt):
    """A timestamp read back from the database, as an aware UTC datetime (SQLite returns naive ones)."""
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def database_url():
    url = os.environ.get('DATABASE_URL', '').strip()
    # Heroku-style URLs and plain "postgresql://" both go through psycopg 3.
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]
    if url.startswith('postgresql://'):
        url = 'postgresql+psycopg://' + url[len('postgresql://'):]
    return url


def configured():
    return bool(database_url())


def engine():
    """The shared engine, created on first use. Raises RuntimeError when DATABASE_URL is not set."""
    global _engine
    if _engine is None:
        url = database_url()
        if not url:
            raise RuntimeError('DATABASE_URL is not set')
        kwargs = {'pool_pre_ping': True, 'future': True}
        if url.startswith('postgresql'):
            # Free databases close idle connections; recycle before they do.
            kwargs.update(pool_size=3, max_overflow=2, pool_recycle=280)
        _engine = create_engine(url, **kwargs)
    return _engine


def reset_engine():
    """Forget the engine (used by the tests when they switch databases)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None


def init_db():
    """Create any missing table. Safe to run on every start."""
    metadata.create_all(engine())
