"""Initial database schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-12-17 11:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create chat_sessions table
    op.create_table('chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('context_used', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('message_type', sa.String(), nullable=False, default='query'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create content_chunks table
    op.create_table('content_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_file', sa.String(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding_id', sa.String(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('hash', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('embedding_id')
    )

    # Create user_feedback table
    op.create_table('user_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('feedback_type', sa.String(), nullable=False),  # 'like', 'dislike', 'report'
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ),
        sa.ForeignKeyConstraint(['message_id'], ['chat_messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'])
    op.create_index('ix_chat_messages_timestamp', 'chat_messages', ['timestamp'])
    op.create_index('ix_content_chunks_source_file', 'content_chunks', ['source_file'])
    op.create_index('ix_content_chunks_chunk_index', 'content_chunks', ['chunk_index'])
    op.create_index('ix_user_feedback_session_id', 'user_feedback', ['session_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_user_feedback_session_id', table_name='user_feedback')
    op.drop_index('ix_content_chunks_chunk_index', table_name='content_chunks')
    op.drop_index('ix_content_chunks_source_file', table_name='content_chunks')
    op.drop_index('ix_chat_messages_timestamp', table_name='chat_messages')
    op.drop_index('ix_chat_messages_session_id', table_name='chat_messages')

    # Drop tables
    op.drop_table('user_feedback')
    op.drop_table('content_chunks')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')