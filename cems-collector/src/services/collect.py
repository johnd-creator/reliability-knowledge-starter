"""CollectService: poll all registry parameters, normalize, persist.

One cycle: read every active parameter (read-only), self-heal implausible
SO2/CO reads via the diagnostic prober, normalize the batch, insert rows.
A parameter that fails to read is logged and skipped — one bad parameter
never aborts a cycle. Learned Modbus overrides live in memory only; the
registry file stays the durable source of truth.
"""

from __future__ import annotations

import dataclasses
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.adapters.modbus.client import ModbusClient, ReadResult
from src.adapters.modbus.diagnostics import (
    probe_parameter,
    should_probe_after_success,
)
from src.config import CemsConfig
from src.domain.models import ModbusReadConfig, ParameterSpec
from src.repositories.store import CollectorStore
from src.services.normalize import Normalizer

LOG = logging.getLogger(__name__)


@dataclass
class CollectStats:
    run_type: str = "collect"
    mode: str = "poll"
    rows_seen: int = 0
    upserted: int = 0
    skipped: int = 0
    errors: int = 0
    watermark: datetime | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None


def _override_from_context(context: dict) -> dict:
    """Extract the learned override keys from a probe context dict."""
    override: dict = {}
    if context.get("address_base") not in (None, "direct"):
        override["address_base"] = int(context["address_base"])
        override["zero_based"] = bool(context.get("zero_based", False))
    return override


class CollectService:
    def __init__(
        self,
        client: ModbusClient,
        store: CollectorStore,
        config: CemsConfig,
        clock=time.monotonic,
    ):
        self._client = client
        self._store = store
        self._config = config
        self._clock = clock
        self._overrides: dict[str, dict] = {}
        self._probe_cooldowns: dict[str, float] = {}

    # -- one cycle ---------------------------------------------------------------
    def collect_once(self) -> CollectStats:
        stats = CollectStats()
        try:
            self._collect_once_inner(stats)
        finally:
            stats.finished_at = datetime.now(timezone.utc)
            self._store.record_run(stats)
        return stats

    def _collect_once_inner(self, stats: CollectStats) -> None:
        parameters = self._store.active_parameters(stack_id=self._config.stack_id)
        if not parameters:
            raise RuntimeError(
                "no active parameters in the local store for stack "
                f"{self._config.stack_id!r} — run `cemscollector load-registry` first"
            )
        stack = self._store.get_stack(self._config.stack_id)
        timestamp = datetime.now(timezone.utc)

        raw: dict[str, float] = {}
        contexts: dict[str, ReadResult] = {}
        for spec in parameters:
            try:
                result = self._read_parameter(spec)
                if should_probe_after_success(spec.code, result.value):
                    result = self._probe_or_keep(spec, result)
                raw[spec.code] = result.value
                contexts[spec.code] = result
            except Exception as error:  # noqa: BLE001 — skip, never abort the cycle
                stats.errors += 1
                LOG.warning(
                    "read %s failed (register=%s): %s",
                    spec.code, spec.modbus.register, error,
                )

        stats.rows_seen = len(raw)
        normalizer = Normalizer(
            {spec.code: spec for spec in parameters}, stack, at=timestamp
        )
        readings = normalizer.transform_batch(raw, timestamp)
        readings = [
            dataclasses.replace(
                reading,
                sources={
                    "cems": {
                        "read": contexts[reading.parameter_code].context,
                        "raw_registers": list(contexts[reading.parameter_code].registers),
                    }
                },
            )
            if reading.parameter_code in contexts
            else reading
            for reading in readings
        ]
        stats.upserted = self._store.insert_readings(readings)
        stats.skipped = sum(
            1 for r in readings if r.transformation_status == "failed"
        )
        stats.watermark = timestamp

    def _read_parameter(self, spec: ParameterSpec) -> ReadResult:
        modbus = spec.modbus
        override = self._overrides.get(spec.code)
        if override:
            modbus = ModbusReadConfig(
                register=modbus.register,
                register_type=override.get("register_type", modbus.register_type),
                data_type=modbus.data_type,
                word_order=override.get("word_order", modbus.word_order),
                byte_order=override.get("byte_order", modbus.byte_order),
                address_base=override.get("address_base", modbus.address_base),
                zero_based=override.get("zero_based", modbus.zero_based),
            )
        return self._client.read_parameter(modbus)

    def _probe_or_keep(self, spec: ParameterSpec, result: ReadResult) -> ReadResult:
        probe = probe_parameter(
            self._client,
            spec.modbus,
            spec.code,
            log_cooldowns=self._probe_cooldowns,
            clock=self._clock,
        )
        if probe is None:
            return result
        self._remember_working_config(spec.code, probe)
        return probe

    def _remember_working_config(self, code: str, probe: ReadResult) -> None:
        context = probe.context or {}
        override: dict = {
            "register_type": context.get("register_type", "holding"),
            "word_order": context.get("word_order", "big"),
            "byte_order": context.get("byte_order", "big"),
        }
        override.update(_override_from_context(context))
        if self._overrides.get(code) == override:
            return
        self._overrides[code] = override
        LOG.info("learned stable %s modbus config from diagnostics: %s", code, override)

    # -- continuous loop -----------------------------------------------------------
    def run_forever(self, stop_flag=None) -> None:
        interval = self._config.poll_interval_seconds
        while not (stop_flag is not None and stop_flag.is_set()):
            started = time.monotonic()
            try:
                stats = self.collect_once()
                LOG.info(
                    "collect cycle: %s read, %s stored, %s failed-read, %s failed-transform",
                    stats.rows_seen, stats.upserted, stats.errors, stats.skipped,
                )
            except Exception as error:  # noqa: BLE001 — the loop must survive
                LOG.error("collect cycle failed: %s", error)
            elapsed = time.monotonic() - started
            delay = max(0.0, interval - elapsed)
            if delay:
                time.sleep(delay)
