"""Add ticket management models for Service CRM

Revision ID: ticket_mgmt_001
Revises: rbac_service_crm_001
Create Date: 2025-01-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ticket_mgmt_001'
down_revision = 'rbac_service_crm_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tickets table
    op.create_table('tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('ticket_number', sa.String(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('ticket_type', sa.String(), nullable=False),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('actual_hours', sa.Float(), nullable=True),
        sa.Column('customer_rating', sa.Integer(), nullable=True),
        sa.Column('customer_feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ticket_created_at', 'tickets', ['created_at'], unique=False)
    op.create_index('idx_ticket_due_date', 'tickets', ['due_date'], unique=False)
    op.create_index('idx_ticket_org_assigned', 'tickets', ['organization_id', 'assigned_to_id'], unique=False)
    op.create_index('idx_ticket_org_customer', 'tickets', ['organization_id', 'customer_id'], unique=False)
    op.create_index('idx_ticket_org_priority', 'tickets', ['organization_id', 'priority'], unique=False)
    op.create_index('idx_ticket_org_status', 'tickets', ['organization_id', 'status'], unique=False)
    op.create_index('idx_ticket_org_type', 'tickets', ['organization_id', 'ticket_type'], unique=False)
    op.create_index(op.f('ix_tickets_id'), 'tickets', ['id'], unique=False)
    op.create_index(op.f('ix_tickets_organization_id'), 'tickets', ['organization_id'], unique=False)
    op.create_index(op.f('ix_tickets_ticket_number'), 'tickets', ['ticket_number'], unique=False)
    
    # Create unique constraint for ticket number per organization
    op.create_unique_constraint('uq_ticket_org_number', 'tickets', ['organization_id', 'ticket_number'])

    # Create ticket_history table
    op.create_table('ticket_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('field_changed', sa.String(), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('changed_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ticket_history_action', 'ticket_history', ['action'], unique=False)
    op.create_index('idx_ticket_history_created_at', 'ticket_history', ['created_at'], unique=False)
    op.create_index('idx_ticket_history_org_ticket', 'ticket_history', ['organization_id', 'ticket_id'], unique=False)
    op.create_index('idx_ticket_history_user', 'ticket_history', ['changed_by_id'], unique=False)
    op.create_index(op.f('ix_ticket_history_id'), 'ticket_history', ['id'], unique=False)
    op.create_index(op.f('ix_ticket_history_organization_id'), 'ticket_history', ['organization_id'], unique=False)

    # Create ticket_attachments table
    op.create_table('ticket_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ticket_attachment_org_ticket', 'ticket_attachments', ['organization_id', 'ticket_id'], unique=False)
    op.create_index('idx_ticket_attachment_type', 'ticket_attachments', ['file_type'], unique=False)
    op.create_index('idx_ticket_attachment_uploaded_by', 'ticket_attachments', ['uploaded_by_id'], unique=False)
    op.create_index(op.f('ix_ticket_attachments_id'), 'ticket_attachments', ['id'], unique=False)
    op.create_index(op.f('ix_ticket_attachments_organization_id'), 'ticket_attachments', ['organization_id'], unique=False)


def downgrade() -> None:
    # Drop ticket_attachments table
    op.drop_index(op.f('ix_ticket_attachments_organization_id'), table_name='ticket_attachments')
    op.drop_index(op.f('ix_ticket_attachments_id'), table_name='ticket_attachments')
    op.drop_index('idx_ticket_attachment_uploaded_by', table_name='ticket_attachments')
    op.drop_index('idx_ticket_attachment_type', table_name='ticket_attachments')
    op.drop_index('idx_ticket_attachment_org_ticket', table_name='ticket_attachments')
    op.drop_table('ticket_attachments')
    
    # Drop ticket_history table
    op.drop_index(op.f('ix_ticket_history_organization_id'), table_name='ticket_history')
    op.drop_index(op.f('ix_ticket_history_id'), table_name='ticket_history')
    op.drop_index('idx_ticket_history_user', table_name='ticket_history')
    op.drop_index('idx_ticket_history_org_ticket', table_name='ticket_history')
    op.drop_index('idx_ticket_history_created_at', table_name='ticket_history')
    op.drop_index('idx_ticket_history_action', table_name='ticket_history')
    op.drop_table('ticket_history')
    
    # Drop tickets table
    op.drop_constraint('uq_ticket_org_number', 'tickets', type_='unique')
    op.drop_index(op.f('ix_tickets_ticket_number'), table_name='tickets')
    op.drop_index(op.f('ix_tickets_organization_id'), table_name='tickets')
    op.drop_index(op.f('ix_tickets_id'), table_name='tickets')
    op.drop_index('idx_ticket_org_type', table_name='tickets')
    op.drop_index('idx_ticket_org_status', table_name='tickets')
    op.drop_index('idx_ticket_org_priority', table_name='tickets')
    op.drop_index('idx_ticket_org_customer', table_name='tickets')
    op.drop_index('idx_ticket_org_assigned', table_name='tickets')
    op.drop_index('idx_ticket_due_date', table_name='tickets')
    op.drop_index('idx_ticket_created_at', table_name='tickets')
    op.drop_table('tickets')