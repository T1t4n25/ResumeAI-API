"""Sentinel Feature - Pydantic Models"""
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class ContainerInfo(BaseModel):
    """Container metrics from Coolify Sentinel"""
    time: str
    id: str
    image: str
    labels: Dict[str, Any] = {}
    name: str
    state: str
    health_status: str = "unknown"


class FilesystemUsage(BaseModel):
    """Filesystem usage from Coolify Sentinel"""
    used_percentage: str


class SentinelPushPayload(BaseModel):
    """Payload pushed by Coolify Sentinel"""
    containers: list[ContainerInfo] = []
    filesystem_usage_root: FilesystemUsage
