"""create fda tables

Revision ID: create_fda_tables
Revises: previous_revision
Create Date: 2024-03-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_fda_tables'
down_revision = 'previous_revision'  # Update this to your previous migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create enum types
    op.execute("""
        CREATE TYPE application_type AS ENUM (
            'IND', 'NDA', 'BLA', 'ANDA'
        )
    """)
    
    op.execute("""
        CREATE TYPE trial_phase AS ENUM (
            'PHASE1', 'PHASE2', 'PHASE3', 'PHASE4'
        )
    """)
    
    op.execute("""
        CREATE TYPE application_status AS ENUM (
            'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'WITHDRAWN', 'ON_HOLD'
        )
    """)
    
    op.execute("""
        CREATE TYPE designation_type AS ENUM (
            'FAST_TRACK', 'BREAKTHROUGH', 'ACCELERATED', 'PRIORITY_REVIEW', 'ORPHAN'
        )
    """)

    # Create FDA applications table
    op.create_table(
        'fda_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('application_number', sa.String(), nullable=False),
        sa.Column('application_type', postgresql.ENUM('IND', 'NDA', 'BLA', 'ANDA', name='application_type'), nullable=True),
        sa.Column('therapeutic_area', sa.String(), nullable=True),
        sa.Column('drug_name', sa.String(), nullable=True),
        sa.Column('indication', sa.Text(), nullable=True),
        sa.Column('current_status', postgresql.ENUM('SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'WITHDRAWN', 'ON_HOLD', name='application_status'), nullable=True),
        sa.Column('submission_date', sa.Date(), nullable=True),
        sa.Column('pdufa_date', sa.Date(), nullable=True),
        sa.Column('approval_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.symbol'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fda_applications_application_number'), 'fda_applications', ['application_number'], unique=True)
    op.create_index(op.f('ix_fda_applications_id'), 'fda_applications', ['id'], unique=False)

    # Create clinical trials table
    op.create_table(
        'clinical_trials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=True),
        sa.Column('nct_number', sa.String(), nullable=False),
        sa.Column('phase', postgresql.ENUM('PHASE1', 'PHASE2', 'PHASE3', 'PHASE4', name='trial_phase'), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('estimated_completion_date', sa.Date(), nullable=True),
        sa.Column('actual_completion_date', sa.Date(), nullable=True),
        sa.Column('enrollment_target', sa.Integer(), nullable=True),
        sa.Column('enrollment_actual', sa.Integer(), nullable=True),
        sa.Column('primary_endpoint', sa.Text(), nullable=True),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['fda_applications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clinical_trials_id'), 'clinical_trials', ['id'], unique=False)
    op.create_index(op.f('ix_clinical_trials_nct_number'), 'clinical_trials', ['nct_number'], unique=True)

    # Create regulatory designations table
    op.create_table(
        'regulatory_designations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=True),
        sa.Column('designation_type', postgresql.ENUM('FAST_TRACK', 'BREAKTHROUGH', 'ACCELERATED', 'PRIORITY_REVIEW', 'ORPHAN', name='designation_type'), nullable=True),
        sa.Column('granted_date', sa.Date(), nullable=True),
        sa.Column('expiration_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['fda_applications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_regulatory_designations_id'), 'regulatory_designations', ['id'], unique=False)

    # Create advisory committee meetings table
    op.create_table(
        'advisory_committee_meetings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=True),
        sa.Column('meeting_date', sa.Date(), nullable=True),
        sa.Column('committee_name', sa.String(), nullable=True),
        sa.Column('outcome', sa.String(), nullable=True),
        sa.Column('vote_result', sa.String(), nullable=True),
        sa.Column('key_findings', sa.Text(), nullable=True),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['fda_applications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_advisory_committee_meetings_id'), 'advisory_committee_meetings', ['id'], unique=False)

def downgrade() -> None:
    # Drop tables
    op.drop_table('advisory_committee_meetings')
    op.drop_table('regulatory_designations')
    op.drop_table('clinical_trials')
    op.drop_table('fda_applications')
    
    # Drop enum types
    op.execute('DROP TYPE application_type')
    op.execute('DROP TYPE trial_phase')
    op.execute('DROP TYPE application_status')
    op.execute('DROP TYPE designation_type') 