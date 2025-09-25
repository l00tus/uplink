from pydantic import field_validator

class ActivityValidatorMixin:
    @field_validator('title', 'description', 'location')
    def strip_string(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip()
        return v
    
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            normalized = [tag.strip().lower() for tag in v if tag.strip()]
            if len(normalized) == 0:
                raise ValueError("Tags cannot be empty")
            return normalized
        return v