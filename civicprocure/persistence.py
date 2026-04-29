from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import Engine, create_engine

from civicprocure.award_packet import build_award_packet_checklist
from civicprocure.rfp_draft import draft_rfp_outline


metadata = sa.MetaData()

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


class ProcureWorkpaperRepository:
    def __init__(self, *, db_url: str | None = None, engine: Engine | None = None) -> None:
        base_engine = engine or create_engine(db_url or "sqlite+pysqlite:///:memory:", future=True)
        if base_engine.dialect.name == "sqlite":
            self.engine = base_engine.execution_options(schema_translate_map={"civicprocure": None})
        else:
            self.engine = base_engine
            with self.engine.begin() as connection:
                connection.execute(sa.text("CREATE SCHEMA IF NOT EXISTS civicprocure"))
        metadata.create_all(self.engine)

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
