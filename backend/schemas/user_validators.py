from pydantic import field_validator
import re

class UserValidatorsMixin:
    # Strip whitespace from fields
    # ( mario  ) -> (mario)
    @field_validator('username', 'full_name', 'country', 'city')
    def strip_strings(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip()
        return v
    
    # Ensure username has at least one letter and only contains letters, numbers, or underscores
    # Valid: "mariooo", "marioo_123"
    # Invalid: "1234", "__123__", "mario!!!"
    @field_validator('username')
    def validate_username(cls, v: str | None) -> str | None:
        if v is not None and not re.fullmatch(r'^(?=.*[A-Za-z])[A-Za-z0-9_]+$', v):
            raise ValueError("Username must contain at least one letter and can only contain letters, numbers, and underscores")
        return v
    
    # Ensure full name has at least one letter and only contains letters, spaces, hyphens, or apostrophes
    # Valid: "Mario Alexandru", "Mario-Alexandru", "O'Connor"
    @field_validator('full_name')
    def validate_fullname(cls, v: str | None) -> str | None:
        if v is not None and not re.fullmatch(r'^(?=.*[A-Za-z])[A-Za-z \'-]+$', v):
            raise ValueError("Full name must contain at least one letter and can only contain letters, spaces, hyphens, and apostrophes")
        return v
    
    # Prevent empty interests if provided, strip whitespace and convert to lowercase
    @field_validator('interests')
    def validate_interests(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            normalized = [interest.strip().lower() for interest in v if interest.strip()]
            if len(normalized) == 0:
                raise ValueError("Interests cannot be empty")
            return normalized
        return v