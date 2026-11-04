"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Created: ${create_date}

Plain PostgreSQL only, so it runs unchanged on Supabase and Amazon RDS. Every new
tenant table needs an org_id column and: SELECT platform.enable_tenant_rls('schema.table');
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
${imports if imports else ""}
revision: str = ${repr(up_revision)}
down_revision: str | None = ${repr(down_revision)}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels)}
depends_on: str | Sequence[str] | None = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    # Forward-only: to undo something, write a new migration.
    raise NotImplementedError("Migrations are forward-only")
