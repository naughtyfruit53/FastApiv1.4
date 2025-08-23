"""Add Service CRM RBAC models

Revision ID: rbac_service_crm_001
Revises: 022f8e890f40
Create Date: 2025-08-23 08:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'rbac_service_crm_001'
down_revision = '022f8e890f40'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create service_permissions table
    op.create_table('service_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('module', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_permissions_id'), 'service_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_service_permissions_name'), 'service_permissions', ['name'], unique=True)
    op.create_index(op.f('ix_service_permissions_module'), 'service_permissions', ['module'], unique=False)
    op.create_index(op.f('ix_service_permissions_action'), 'service_permissions', ['action'], unique=False)
    op.create_index('idx_service_permission_module_action', 'service_permissions', ['module', 'action'], unique=False)

    # Create service_roles table
    op.create_table('service_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name', name='uq_service_role_org_name')
    )
    op.create_index(op.f('ix_service_roles_id'), 'service_roles', ['id'], unique=False)
    op.create_index(op.f('ix_service_roles_organization_id'), 'service_roles', ['organization_id'], unique=False)
    op.create_index('idx_service_role_org_active', 'service_roles', ['organization_id', 'is_active'], unique=False)

    # Create service_role_permissions table (many-to-many)
    op.create_table('service_role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['service_permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['service_roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uq_service_role_permission')
    )
    op.create_index(op.f('ix_service_role_permissions_id'), 'service_role_permissions', ['id'], unique=False)
    op.create_index('idx_service_role_permission_role', 'service_role_permissions', ['role_id'], unique=False)
    op.create_index('idx_service_role_permission_permission', 'service_role_permissions', ['permission_id'], unique=False)

    # Create user_service_roles table (many-to-many)
    op.create_table('user_service_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('assigned_by_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['service_roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', name='uq_user_service_role')
    )
    op.create_index(op.f('ix_user_service_roles_id'), 'user_service_roles', ['id'], unique=False)
    op.create_index('idx_user_service_role_user', 'user_service_roles', ['user_id'], unique=False)
    op.create_index('idx_user_service_role_role', 'user_service_roles', ['role_id'], unique=False)
    op.create_index('idx_user_service_role_active', 'user_service_roles', ['is_active'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order to handle foreign key constraints
    op.drop_table('user_service_roles')
    op.drop_table('service_role_permissions')
    op.drop_table('service_roles')
    op.drop_table('service_permissions')