"""Default local CLI entry point for the gateway service."""

import uvicorn

from incident_diagnostic_api.services.gateway import app, settings


def run() -> None:
    """Run the local gateway without reload or production workers."""

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=False,
        workers=1,
    )


if __name__ == "__main__":  # pragma: no cover
    run()
