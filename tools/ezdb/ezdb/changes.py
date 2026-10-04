import re
from dataclasses import dataclass
from .paths import get_changelog_path, get_root_path

REGEX_CHANGE = r"-+\s*Version (?P<major>[0-9]+)\.(?P<minor>[0-9]+), .+?\`\`\`sql\s*(?P<sql>.+?)\s*\`\`\`.*?-{5}"

@dataclass
class Change:
    major_version: int
    minor_version: int
    sql: str

def get_changes() -> list[Change]:
    changelog_path = get_changelog_path()
    if not changelog_path.exists():
        return []

    with open(changelog_path, "r", encoding="utf-8", errors="replace") as file:
        changelog = file.read()
        changes = []

        for change_match in re.finditer(REGEX_CHANGE, changelog, re.MULTILINE | re.DOTALL):
            changes.append(Change(
                int(change_match.group("major")),
                int(change_match.group("minor")),
                change_match.group("sql")
            ))

        changes.sort(key = lambda change: (change.major_version, change.minor_version), reverse = True)

        return changes

def get_current_version():
    defines_path = get_root_path() / "code" / "__DEFINES" / "subsystems.dm"
    text = defines_path.read_text(encoding="utf-8", errors="replace")

    major = re.search(r"#define\s+DB_MAJOR_VERSION\s+(\d+)", text)
    minor = re.search(r"#define\s+DB_MINOR_VERSION\s+(\d+)", text)
    assert major and minor, "Could not find DB_MAJOR_VERSION/DB_MINOR_VERSION in subsystems.dm"

    return (int(major.group(1)), int(minor.group(1)))