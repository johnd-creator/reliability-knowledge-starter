"""Single measurement contract shared by inspection and frozen reviewed evidence."""
from datetime import datetime
import math
from typing import Annotated, Literal
from pydantic import Field, StrictStr, StrictInt, StrictFloat, StrictBool, field_validator
from src.domain.condition_evidence import EvidenceModel
from src.domain.text import NONBLANK_TEXT_PATTERN

ExtensionScalar = Annotated[StrictStr, Field(max_length=2000)] | StrictInt | StrictFloat | StrictBool | None
class ManualMeasurement(EvidenceModel):
    quantity: StrictStr = Field(min_length=1,max_length=120,pattern=NONBLANK_TEXT_PATTERN)
    value: ExtensionScalar = None
    unit: StrictStr | None = Field(default=None,max_length=40)
    measured_at: datetime | None = None
    point_ref: StrictStr | None = Field(default=None,max_length=200)
    quality: Literal["UNKNOWN","INSPECTOR_REPORTED"] = "UNKNOWN"
    provenance: Literal["HUMAN_ENTERED_MEASUREMENT"] = "HUMAN_ENTERED_MEASUREMENT"
    @field_validator('value')
    @classmethod
    def finite(cls,value):
        if isinstance(value,float) and not math.isfinite(value):
            raise ValueError('nonfinite measurement')
        return value
