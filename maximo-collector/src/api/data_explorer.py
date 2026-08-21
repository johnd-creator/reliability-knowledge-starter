"""GET-only engineering Data Explorer API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from src.repositories.database import Database, get_database
from src.repositories.store import CollectorStore
from src.services.data_explorer import DataExplorerService

router = APIRouter(prefix="/data-explorer", tags=["data-explorer"])


def _service(db: Database = Depends(get_database)) -> DataExplorerService:
    return DataExplorerService(CollectorStore(db))


def _not_found(error: KeyError) -> HTTPException:
    return HTTPException(status_code=404, detail="unknown or unavailable Data Explorer resource")


@router.get("/resources")
def resources(service: DataExplorerService = Depends(_service)) -> dict:
    try:
        return service.resources()
    except Exception as error:  # database failures must not expose internals
        raise HTTPException(status_code=503, detail="Collector storage is unavailable") from error


@router.get("/resources/{resource}")
def resource_metadata(resource: str, service: DataExplorerService = Depends(_service)) -> dict:
    try:
        return service.resource_metadata(resource)
    except KeyError as error:
        raise _not_found(error) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="Collector storage is unavailable") from error


@router.get("/integrity")
def integrity(service: DataExplorerService = Depends(_service)) -> dict:
    try:
        return service.integrity()
    except Exception as error:
        raise HTTPException(status_code=503, detail="Collector storage is unavailable") from error


@router.get("/resources/{resource}/records")
def source_records(
    resource: str,
    q: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("updated_desc", pattern="^(updated_desc|updated_asc|status|source_number)$"),
    service: DataExplorerService = Depends(_service),
) -> dict:
    try:
        return service.source_records(resource, offset=offset, limit=limit, q=q, sort=sort)
    except KeyError as error:
        raise _not_found(error) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="Collector storage is unavailable") from error


@router.get("/resources/{resource}/records/{canonical_id}")
def source_record_detail(resource: str, canonical_id: str, service: DataExplorerService = Depends(_service)) -> dict:
    try:
        return service.record_detail(resource, canonical_id)
    except KeyError as error:
        raise _not_found(error) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="Collector storage is unavailable") from error


@router.get("/mart/{entity}")
def mart_records(
    entity: str,
    q: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("updated_desc", pattern="^(updated_desc|updated_asc|status|source_number)$"),
    service: DataExplorerService = Depends(_service),
) -> dict:
    try:
        return service.mart_records(entity, offset=offset, limit=limit, q=q, sort=sort)
    except KeyError as error:
        raise _not_found(error) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="Collector storage is unavailable") from error


@router.get("/mart/{entity}/{canonical_id}")
def mart_record_detail(entity: str, canonical_id: str, service: DataExplorerService = Depends(_service)) -> dict:
    try:
        spec = service.resolve_entity(entity)
        return service.record_detail(spec.source_object, canonical_id)
    except KeyError as error:
        raise _not_found(error) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="Collector storage is unavailable") from error


@router.get("/mappings/{resource}")
def mappings(resource: str, service: DataExplorerService = Depends(_service)) -> dict:
    try:
        return service.mapping(resource)
    except KeyError as error:
        raise _not_found(error) from error
