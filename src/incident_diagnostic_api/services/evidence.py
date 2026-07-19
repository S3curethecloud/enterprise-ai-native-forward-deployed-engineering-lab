"""Local evidence service entry point with enterprise retrieval disabled."""

from incident_diagnostic_api.api.app import create_app
from incident_diagnostic_api.core.config import Settings

settings = Settings(
    service_name="evidence",
    host="127.0.0.1",
    port=8002,
)

app = create_app(settings)
