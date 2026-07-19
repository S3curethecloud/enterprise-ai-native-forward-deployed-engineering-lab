"""Local runtime service entry point with no workflow authority."""

from incident_diagnostic_api.api.app import create_app
from incident_diagnostic_api.core.config import Settings

settings = Settings(
    service_name="runtime",
    host="127.0.0.1",
    port=8001,
)

app = create_app(settings)
