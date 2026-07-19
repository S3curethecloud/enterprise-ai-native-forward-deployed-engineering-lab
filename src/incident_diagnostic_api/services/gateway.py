"""Local gateway service entry point."""

from incident_diagnostic_api.api.app import create_app
from incident_diagnostic_api.core.config import Settings

settings = Settings(
    service_name="gateway",
    host="127.0.0.1",
    port=8000,
)

app = create_app(settings)
