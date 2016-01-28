"""add name fkey for font

Revision ID: 91a1b031f026
Revises: 
Create Date: 2016-03-20 15:33:46.241441

"""

# revision identifiers, used by Alembic.
revision = '91a1b031f026'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ## add name fkey, drop id fkey 
    ## I recreated the whole db instead
    pass


def downgrade():
    ## the whole db was recreated, this revision should do nothing
    pass
