"""Shared JSON schema for college data."""
COLLEGE_SCHEMA = {
    "type": "object",
    "required": ["name", "college_type"],
    "properties": {
        "name": {"type": "string"},
        "college_type": {"type": "string", "enum": ["engineering", "polytechnic", "management"]},
        "location": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "state": {"type": "string", "default": "Maharashtra"},
            }
        },
        "fees": {
            "type": "object",
            "properties": {
                "annual_tuition": {"type": "number"},
                "hostel_annual": {"type": "number"},
            }
        },
        "placements": {
            "type": "object",
            "properties": {
                "avg_package_lpa": {"type": "number"},
                "highest_package_lpa": {"type": "number"},
                "placement_percentage": {"type": "number", "minimum": 0, "maximum": 100},
            }
        },
    }
}
