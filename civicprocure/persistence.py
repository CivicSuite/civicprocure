from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import Engine, create_engine

from civicprocure.award_packet import build_award_packet_checklist
from civicprocure.rfp_draft import draft_rfp_outline


metadata = sa.MetaData()
SCHEMA_VERSION = "2026-06-05-001"

schema_migrations = sa.Table(
    "schema_migrations",
    metadata,
    sa.Column("schema_version", sa.String(80), primary_key=True),
    sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicprocure",
)

rfp_draft_records = sa.Table(
    "rfp_draft_records",
    metadata,
    sa.Column("draft_id", sa.String(36), primary_key=True),
    sa.Column("procurement_title", sa.String(255), nullable=False),
    sa.Column("procurement_type", sa.String(160), nullable=False),
    sa.Column("recommended_owner", sa.String(255), nullable=False),
    sa.Column("sections", sa.JSON(), nullable=False),
    sa.Column("disclaimer", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicprocure",
)

award_packet_records = sa.Table(
    "award_packet_records",
    metadata,
    sa.Column("packet_id", sa.String(36), primary_key=True),
    sa.Column("solicitation_id", sa.String(255), nullable=False),
    sa.Column("title", sa.String(255), nullable=False),
    sa.Column("format", sa.String(80), nullable=False),
    sa.Column("checklist", sa.JSON(), nullable=False),
    sa.Column("retention_note", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicprocure",
)

staff_review_queue_records = sa.Table(
    "staff_review_queue_records",
    metadata,
    sa.Column("review_id", sa.String(36), primary_key=True),
    sa.Column("solicitation_id", sa.String(255), nullable=True),
    sa.Column("procurement_title", sa.String(500), nullable=False),
    sa.Column("status", sa.String(120), nullable=False),
    sa.Column("reason", sa.Text(), nullable=False),
    sa.Column("assigned_to", sa.String(255), nullable=True),
    sa.Column("resolution", sa.Text(), nullable=True),
    sa.Column("created_by", sa.String(120), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("visibility", sa.String(120), nullable=False),
    schema="civicprocure",
)

OPEN_STAFF_REVIEW_STATUSES = {"open", "in_review"}
RESOLVED_STAFF_REVIEW_STATUSES = {"resolved", "closed"}
STAFF_REVIEW_STATUSES = OPEN_STAFF_REVIEW_STATUSES | RESOLVED_STAFF_REVIEW_STATUSES


@dataclass(frozen=True)
class StoredRfpDraft:
    draft_id: str
    procurement_title: str
    procurement_type: str
    recommended_owner: str
    sections: list[str]
    disclaimer: str
    created_at: datetime


@dataclass(frozen=True)
class StoredAwardPacket:
    packet_id: str
    solicitation_id: str
    title: str
    format: str
    checklist: list[str]
    retention_note: str
    created_at: datetime


@dataclass(frozen=True)
class StaffReviewQueueItem:
    review_id: str
    solicitation_id: str | None
    procurement_title: str
    status: str
    reason: str
    assigned_to: str | None
    resolution: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime
    visibility: str = "staff_only"


@dataclass(frozen=True)
class StaffReviewSummary:
    total_items: int
    by_status: dict[str, int]
    open_items: int
    generated_at: datetime
    visibility: str = "staff_only"


@dataclass(frozen=True)
class SchemaStatus:
    schema_version: str | None
    expected_schema_version: str
    ready: bool
    missing_tables: tuple[str, ...]
    dialect: str


class ProcureWorkpaperRepository:
    def __init__(self, *, db_url: str | None = None, engine: Engine | None = None) -> None:
        base_engine = engine or create_engine(db_url or "sqlite+pysqlite:///:memory:", future=True)
        if base_engine.dialect.name == "sqlite":
            self.engine = base_engine.execution_options(schema_translate_map={"civicprocure": None})
        else:
            self.engine = base_engine
            with self.engine.begin() as connection:
                connection.execute(sa.text("CREATE SCHEMA IF NOT EXISTS civicprocure"))
        self.migrate()

    def migrate(self) -> SchemaStatus:
        metadata.create_all(self.engine)
        with self.engine.begin() as connection:
            exists = connection.execute(
                sa.select(schema_migrations.c.schema_version).where(
                    schema_migrations.c.schema_version == SCHEMA_VERSION
                )
            ).first()
            if exists is None:
                connection.execute(
                    schema_migrations.insert().values(
                        schema_version=SCHEMA_VERSION,
                        applied_at=datetime.now(UTC),
                    )
                )
        return self.schema_status()

    def schema_status(self) -> SchemaStatus:
        inspector = sa.inspect(self.engine)
        translated_schema = None if self.engine.dialect.name == "sqlite" else "civicprocure"
        available_tables = set(inspector.get_table_names(schema=translated_schema))
        expected_tables = {
            "rfp_draft_records",
            "award_packet_records",
            "staff_review_queue_records",
            "schema_migrations",
        }
        missing_tables = tuple(sorted(expected_tables - available_tables))
        schema_version = None
        if "schema_migrations" not in missing_tables:
            with self.engine.begin() as connection:
                schema_version = connection.execute(
                    sa.select(schema_migrations.c.schema_version)
                    .order_by(schema_migrations.c.applied_at.desc())
                    .limit(1)
                ).scalar_one_or_none()
        return SchemaStatus(
            schema_version=schema_version,
            expected_schema_version=SCHEMA_VERSION,
            ready=schema_version == SCHEMA_VERSION and not missing_tables,
            missing_tables=missing_tables,
            dialect=self.engine.dialect.name,
        )

    def create_rfp_draft(
        self, *, procurement_title: str, procurement_type: str, city_need: str
    ) -> StoredRfpDraft:
        draft = draft_rfp_outline(
            procurement_title=procurement_title,
            procurement_type=procurement_type,
            city_need=city_need,
        )
        stored = StoredRfpDraft(
            draft_id=str(uuid4()),
            procurement_title=draft.procurement_title,
            procurement_type=draft.procurement_type,
            recommended_owner=draft.recommended_owner,
            sections=list(draft.sections),
            disclaimer=draft.disclaimer,
            created_at=datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(rfp_draft_records.insert().values(**stored.__dict__))
        return stored

    def get_rfp_draft(self, draft_id: str) -> StoredRfpDraft | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                sa.select(rfp_draft_records).where(rfp_draft_records.c.draft_id == draft_id)
            ).mappings().first()
        return None if row is None else StoredRfpDraft(**dict(row))

    def create_award_packet(
        self, *, solicitation_id: str, title: str, format: str
    ) -> StoredAwardPacket:
        packet = build_award_packet_checklist(
            solicitation_id=solicitation_id,
            title=title,
            format=format,
        )
        stored = StoredAwardPacket(
            packet_id=str(uuid4()),
            solicitation_id=packet.solicitation_id,
            title=packet.title,
            format=packet.format,
            checklist=list(packet.checklist),
            retention_note=packet.retention_note,
            created_at=datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(award_packet_records.insert().values(**stored.__dict__))
        return stored

    def get_award_packet(self, packet_id: str) -> StoredAwardPacket | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                sa.select(award_packet_records).where(award_packet_records.c.packet_id == packet_id)
            ).mappings().first()
        return None if row is None else StoredAwardPacket(**dict(row))

    def create_staff_review_queue_item(
        self,
        *,
        procurement_title: str,
        reason: str,
        solicitation_id: str | None = None,
        created_by: str = "staff",
    ) -> StaffReviewQueueItem:
        now = datetime.now(UTC)
        item = StaffReviewQueueItem(
            review_id=str(uuid4()),
            solicitation_id=solicitation_id,
            procurement_title=procurement_title.strip() or "Untitled procurement",
            status="open",
            reason=reason.strip() or "Procurement support output requires staff review.",
            assigned_to=None,
            resolution=None,
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )
        with self.engine.begin() as connection:
            connection.execute(staff_review_queue_records.insert().values(**_staff_queue_values(item)))
        return item

    def list_staff_review_queue_items(self, *, status: str | None = None) -> tuple[StaffReviewQueueItem, ...]:
        with self.engine.begin() as connection:
            statement = sa.select(staff_review_queue_records).order_by(
                staff_review_queue_records.c.created_at
            )
            if status is not None:
                statement = statement.where(staff_review_queue_records.c.status == status)
            rows = connection.execute(statement).mappings().all()
        return tuple(_row_to_staff_queue_item(row) for row in rows)

    def update_staff_review_queue_item(
        self,
        *,
        review_id: str,
        status: str,
        assigned_to: str | None = None,
        resolution: str | None = None,
    ) -> StaffReviewQueueItem | None:
        if status not in STAFF_REVIEW_STATUSES:
            raise ValueError("status must be one of: closed, in_review, open, resolved.")
        if status in RESOLVED_STAFF_REVIEW_STATUSES and not resolution:
            raise ValueError("resolution is required when resolving or closing a staff review item.")
        current = self.get_staff_review_queue_item(review_id)
        if current is None:
            return None
        updated = StaffReviewQueueItem(
            review_id=current.review_id,
            solicitation_id=current.solicitation_id,
            procurement_title=current.procurement_title,
            status=status,
            reason=current.reason,
            assigned_to=assigned_to,
            resolution=resolution,
            created_by=current.created_by,
            created_at=current.created_at,
            updated_at=datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                staff_review_queue_records.update()
                .where(staff_review_queue_records.c.review_id == review_id)
                .values(**_staff_queue_values(updated))
            )
        return updated

    def get_staff_review_queue_item(self, review_id: str) -> StaffReviewQueueItem | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                sa.select(staff_review_queue_records).where(
                    staff_review_queue_records.c.review_id == review_id
                )
            ).mappings().first()
        return None if row is None else _row_to_staff_queue_item(row)

    def staff_review_summary(self) -> StaffReviewSummary:
        items = self.list_staff_review_queue_items()
        by_status = {status: sum(1 for item in items if item.status == status) for status in STAFF_REVIEW_STATUSES}
        return StaffReviewSummary(
            total_items=len(items),
            by_status=by_status,
            open_items=sum(1 for item in items if item.status in OPEN_STAFF_REVIEW_STATUSES),
            generated_at=datetime.now(UTC),
        )


def _staff_queue_values(item: StaffReviewQueueItem) -> dict[str, object]:
    return {
        "review_id": item.review_id,
        "solicitation_id": item.solicitation_id,
        "procurement_title": item.procurement_title,
        "status": item.status,
        "reason": item.reason,
        "assigned_to": item.assigned_to,
        "resolution": item.resolution,
        "created_by": item.created_by,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "visibility": item.visibility,
    }


def _row_to_staff_queue_item(row: object) -> StaffReviewQueueItem:
    data = dict(row)
    return StaffReviewQueueItem(
        review_id=data["review_id"],
        solicitation_id=data["solicitation_id"],
        procurement_title=data["procurement_title"],
        status=data["status"],
        reason=data["reason"],
        assigned_to=data["assigned_to"],
        resolution=data["resolution"],
        created_by=data["created_by"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        visibility=data["visibility"],
    )
