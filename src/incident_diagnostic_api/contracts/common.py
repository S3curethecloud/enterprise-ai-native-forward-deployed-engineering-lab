"""Shared types and validation rules for executable interface contracts."""

from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints

ContractVersion = Literal["1.0"]

OpaqueIdentifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$",
    ),
]

ShortText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=500,
    ),
]

BoundedText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=4000,
    ),
]

ReasonCode = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=80,
        pattern=r"^[A-Z][A-Z0-9_]*$",
    ),
]

ContentHash = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=8,
        max_length=128,
        pattern=r"^[a-fA-F0-9]+$",
    ),
]

Timestamp = AwareDatetime

ConfidenceScore = Annotated[float, Field(ge=0.0, le=1.0)]
NonNegativeDuration = Annotated[float, Field(ge=0.0)]


class ContractModel(BaseModel):
    """Fail-closed base configuration shared by all contracts."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        populate_by_name=False,
        str_strip_whitespace=True,
        validate_assignment=True,
        validate_default=True,
    )


class VersionedContract(ContractModel):
    """Base contract carrying the only currently supported version."""

    contract_version: ContractVersion = "1.0"
