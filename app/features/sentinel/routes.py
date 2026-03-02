"""Sentinel Feature - API Routes for receiving Coolify Sentinel metrics"""
import logging
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional

from app.core.config import settings
from app.features.sentinel.models import SentinelPushPayload

logger = logging.getLogger("resume_flow")

# Create router — matches Sentinel's expected PUSH_ENDPOINT path
router = APIRouter(prefix="/api/v1/sentinel", tags=["Sentinel"])


@router.post(
    "/push",
    summary="Receive Sentinel metrics",
    description="Endpoint for Coolify Sentinel to push container and filesystem metrics"
)
async def receive_metrics(
    request: Request,
    payload: SentinelPushPayload,
    authorization: Optional[str] = Header(None)
):
    """
    Receive metrics pushed by Coolify Sentinel.

    Sentinel sends container states and filesystem usage on a fixed interval.
    """
    # Validate bearer token if SENTINEL_TOKEN is configured
    if settings.sentinel_token:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization")
        token = authorization.removeprefix("Bearer ")
        if token != settings.sentinel_token:
            raise HTTPException(status_code=403, detail="Invalid sentinel token")

    # Log metrics
    container_count = len(payload.containers)
    disk_usage = payload.filesystem_usage_root.used_percentage

    logger.info(
        f"Sentinel push: {container_count} containers, "
        f"disk usage: {disk_usage}%"
    )

    for container in payload.containers:
        logger.debug(
            f"  Container '{container.name}' ({container.id[:12]}): "
            f"state={container.state}, health={container.health_status}"
        )

    return {"status": "ok", "received": container_count}
