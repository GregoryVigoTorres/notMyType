"""Copyright should be Text field

Revision ID: a362621378f0
Revises: 4d10356cc6d8
Create Date: 2016-10-17 17:06:25.864369

"""

# revision identifiers, used by Alembic.
revision = 'a362621378f0'
down_revision = '4d10356cc6d8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
    this was run after switching to postgres
    """
    op.alter_column('fonts', 'copyright', type_=sa.Text())

def downgrade():
    op.alter_column('fonts', 'copyright', type_=sa.String(255))
