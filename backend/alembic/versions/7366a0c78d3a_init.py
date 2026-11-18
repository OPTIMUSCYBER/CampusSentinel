"""init

Revision ID: 7366a0c78d3a
Revises: 484d5fb0a79e
Create Date: 2026-08-28 13:16:37.051810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7366a0c78d3a'
down_revision: Union[str, Sequence[str], None] = '484d5fb0a79e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
