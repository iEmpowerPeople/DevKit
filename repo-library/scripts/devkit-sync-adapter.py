#!/usr/bin/env python3
"""Profile-driven sync adapter for Claude Code + OpenCode.

Design rules (enforced):
- Sync only profile-enabled tools.
- Never overwrite/delete anything the adapter does not own.
- Prune (delete) only when: profile says enabled:false AND adapter owns the destination path.
- Skills are directories: copy entire folder.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Optional, Tuple, cast
import platform
import re
import os

Category = Literal["agents", "commands", "skills", "skills-user-only"]
Target = Literal["claude", "opencode"]


@dataclass(frozen=True)
class Entry:
    category: Category
    id: str
    author: str
    enabled: bool


def abort(msg: str, exit_code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(exit_code)


def prompt_and_abort(title: str, body: str, exit_code: int = 1) -> None:
    print(title, file=sys.stderr)
    print(body.rstrip() + "\n", file=sys.stderr)
    try:
        input("Press Enter to abort...")
    except (EOFError, KeyboardInterrupt):
        pass
    raise SystemExit(exit_code)


def repo_root() -> Path:
    # Script is at repo-library/scripts/, so go up 3 levels to reach repo root
    return Path(__file__).resolve().parent.parent.parent


def default_state_file(profile: str) -> Path:
    # Keep it in repo (gitignored) so it travels with the repo clone.
    # Uses profile name so each profile has its own state.
    return repo_root() / f".sync-state-{profile}.json"


def load_yaml(path: Path) -> Dict[str, Any]:
    try:
        import yaml as pyyaml  # type: ignore
    except Exception:
        pyyaml = None
    if pyyaml is None:
        prompt_and_abort(
            "Missing dependency: PyYAML",
            "This script requires PyYAML. Install it (example):\n"
            "  python3 -m pip install pyyaml\n",
        )
    assert pyyaml is not None
    data: Any = None
    try:
        data = pyyaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        prompt_and_abort("Failed to read profile", f"Profile: {path}\nError: {e}")
    if not isinstance(data, dict):
        prompt_and_abort("Invalid profile format", f"Expected YAML mapping at top-level: {path}")
    return cast(Dict[str, Any], data)


def load_state(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "version": 1,
            "owned": {
                "claude": {"agents": {}, "commands": {}, "skills": {}, "skills-user-only": {}},
                "opencode": {"agents": {}, "commands": {}, "skills": {}, "skills-user-only": {}},
            },
        }
    data: Any = None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        prompt_and_abort("Failed to read state file", f"State: {path}\nError: {e}")
    if not isinstance(data, dict):
        prompt_and_abort("Invalid state file", f"Expected JSON object: {path}")
    data_dict = cast(Dict[str, Any], data)
    data_dict.setdefault("version", 1)
    data_dict.setdefault("owned", {})
    for t in ("claude", "opencode"):
        data_dict["owned"].setdefault(t, {})
        for c in ("agents", "commands", "skills", "skills-user-only"):
            data_dict["owned"][t].setdefault(c, {})
    return data_dict


def save_state(path: Path, state: Dict[str, Any]) -> None:
    state["updatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_entries(profile: Dict[str, Any]) -> list[Entry]:
    out: list[Entry] = []
    for category in ("agents", "commands", "skills", "skills-user-only"):
        items = profile.get(category, [])
        if items is None:
            items = []
        if not isinstance(items, list):
            prompt_and_abort("Invalid profile", f"Expected list for '{category}'")
        for item in items:
            if not isinstance(item, dict):
                prompt_and_abort("Invalid profile", f"Expected mapping items under '{category}'")
            tool_id = item.get("id")
            author = item.get("author")
            enabled = item.get("enabled")
            if not isinstance(tool_id, str) or not tool_id:
                prompt_and_abort("Invalid profile", f"Missing/invalid id under '{category}'")
            if not isinstance(author, str) or not author:
                prompt_and_abort("Invalid profile", f"Missing/invalid author for {category}:{tool_id}")
            if not isinstance(enabled, bool):
                prompt_and_abort("Invalid profile", f"Missing/invalid enabled for {category}:{tool_id}")
            tool_id_str = cast(str, tool_id)
            author_str = cast(str, author)
            enabled_bool = cast(bool, enabled)
            out.append(Entry(category=cast(Category, category), id=tool_id_str, author=author_str, enabled=enabled_bool))
    return out


def parse_extras(profile: Dict[str, Any]) -> list[Dict[str, Any]]:
    items = profile.get("extras", [])
    if items is None:
        items = []
    if not isinstance(items, list):
        prompt_and_abort("Invalid profile", "Expected list for 'extras'")
    out: list[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            prompt_and_abort("Invalid profile", "Expected mapping items under 'extras'")
        tool_id = item.get("id")
        enabled = item.get("enabled")
        if not isinstance(tool_id, str) or not tool_id:
            prompt_and_abort("Invalid profile", "Missing/invalid id under 'extras'")
        if not isinstance(enabled, bool):
            prompt_and_abort("Invalid profile", f"Missing/invalid enabled for extras:{tool_id}")
        out.append({"id": tool_id, "enabled": enabled})
    return out


def _which(cmd: str) -> Optional[str]:
    import shutil as _shutil

    return _shutil.which(cmd)


def _parse_semver(text: str) -> Optional[Tuple[int, int, int]]:
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def _semver_ge(have: Tuple[int, int, int], want: Tuple[int, int, int]) -> bool:
    return have >= want


def _cmd_output(argv: list[str]) -> str:
    import subprocess

    p = subprocess.run(argv, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return (p.stdout or "").strip()


def _cmd_exit_code(argv: list[str]) -> int:
    import subprocess

    p = subprocess.run(argv, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p.returncode


def _brew_has_cask(name: str) -> bool:
    if _which("brew") is None:
        return False
    return _cmd_exit_code(["brew", "list", "--cask", name]) == 0


def _macos_app_exists(app_name: str) -> bool:
    candidates = [
        Path("/Applications") / f"{app_name}.app",
        Path.home() / "Applications" / f"{app_name}.app",
    ]
    return any(path.exists() for path in candidates)


def extras_install_hints(extra_ids: list[str]) -> list[str]:
    # Prints actions; does not install.
    sysname = platform.system()
    have_brew = _which("brew") is not None
    out: list[str] = []

    def add_block(title: str, lines: list[str]) -> None:
        out.append(f"extras: {title}")
        out.extend([f"  {ln}" for ln in lines])

    want_git = (2, 30, 0)

    if sysname == "Darwin" and not have_brew:
        add_block(
            "(xapids suggestion) homebrew",
            [
                "Install Homebrew first, install everything through homebrew. simplifies management and update processes",
                "https://brew.sh/",
            ],
        )

    for tool_id in extra_ids:
        if tool_id == "git-cli":
            path = _which("git")
            if not path:
                if sysname == "Darwin":
                    if have_brew:
                        add_block("git-cli", ["missing", "1) brew install git", "2) if blocked: xcode-select --install", "3) https://git-scm.com/downloads"])
                    else:
                        add_block(
                            "git-cli",
                            [
                                "missing",
                                "1) (xapids suggestion) install Homebrew: https://brew.sh/",
                                "2) brew install git",
                                "3) if blocked: xcode-select --install",
                                "4) https://git-scm.com/downloads",
                            ],
                        )
                elif sysname == "Linux":
                    add_block("git-cli", ["missing"])
                else:
                    add_block("git-cli", ["missing"])
                continue

            have = _parse_semver(_cmd_output(["git", "--version"]))
            if have and not _semver_ge(have, want_git):
                if sysname == "Darwin":
                    if have_brew:
                        add_block("git-cli", [f"outdated ({have[0]}.{have[1]}.{have[2]})", "1) brew upgrade git", "2) https://git-scm.com/downloads"])
                    else:
                        add_block(
                            "git-cli",
                            [
                                f"outdated ({have[0]}.{have[1]}.{have[2]})",
                                "1) (xapids suggestion) install Homebrew: https://brew.sh/",
                                "2) brew upgrade git",
                                "3) https://git-scm.com/downloads",
                            ],
                        )
                else:
                    add_block("git-cli", [f"outdated ({have[0]}.{have[1]}.{have[2]})"])
            else:
                add_block("git-cli", ["ok"])

        elif tool_id == "github-cli":
            if not _which("gh"):
                if sysname == "Darwin":
                    if have_brew:
                        add_block("github-cli", ["missing", "1) brew install gh", "2) https://cli.github.com/"])
                    else:
                        add_block(
                            "github-cli",
                            [
                                "missing",
                                "1) (xapids suggestion) install Homebrew: https://brew.sh/",
                                "2) brew install gh",
                                "3) https://cli.github.com/",
                            ],
                        )
                elif sysname == "Linux":
                    add_block("github-cli", ["missing"])
                else:
                    add_block("github-cli", ["missing"])
            else:
                add_block("github-cli", ["ok"])

        elif tool_id == "claude-code-cli":
            if not _which("claude"):
                if sysname == "Darwin":
                    if have_brew:
                        add_block("claude-code-cli", ["missing", "1) brew install --cask <claude> (if published)", "2) https://code.claude.com/"])
                    else:
                        add_block("claude-code-cli", ["missing", "1) https://code.claude.com/"])
                elif sysname == "Linux":
                    add_block("claude-code-cli", ["missing"])
                else:
                    add_block("claude-code-cli", ["missing", "https://code.claude.com/"])
            else:
                add_block("claude-code-cli", ["ok"])

        elif tool_id == "opencode-cli":
            if not _which("opencode"):
                if sysname == "Darwin":
                    if have_brew:
                        add_block("opencode-cli", ["missing", "1) brew install opencode (if published)", "2) https://opencode.ai/"])
                    else:
                        add_block("opencode-cli", ["missing", "1) https://opencode.ai/"])
                elif sysname == "Linux":
                    add_block("opencode-cli", ["missing"])
                else:
                    add_block("opencode-cli", ["missing", "https://opencode.ai/"])
            else:
                add_block("opencode-cli", ["ok"])

        elif tool_id == "opencode-gui":
            installed = False
            if sysname == "Darwin":
                installed = _macos_app_exists("OpenCode") or (have_brew and _brew_has_cask("opencode"))
            if installed:
                add_block("opencode-gui", ["ok"])
            elif sysname == "Darwin" and have_brew:
                add_block("opencode-gui", ["missing", "1) brew install --cask opencode (if published)", "2) https://opencode.ai/"])
            elif sysname == "Linux":
                add_block("opencode-gui", ["missing", "1) https://opencode.ai/"])
            else:
                add_block("opencode-gui", ["missing", "1) https://opencode.ai/"])

        elif tool_id == "codelayer-gui":
            installed = False
            if sysname == "Darwin":
                installed = _macos_app_exists("CodeLayer") or (have_brew and _brew_has_cask("codelayer"))
            if installed:
                add_block("codelayer-gui", ["ok"])
            elif sysname == "Darwin" and have_brew:
                add_block("codelayer-gui", ["missing", "1) brew install --cask codelayer (if published)", "2) provider instructions"])
            elif sysname == "Linux":
                add_block("codelayer-gui", ["missing", "1) provider instructions"])
            else:
                add_block("codelayer-gui", ["missing", "1) provider instructions"])

        elif tool_id == "vscode-gui":
            installed = False
            if _which("code"):
                installed = True
            elif sysname == "Darwin":
                installed = _macos_app_exists("Visual Studio Code") or (have_brew and _brew_has_cask("visual-studio-code"))
            if installed:
                add_block("vscode-gui", ["ok"])
            elif sysname == "Darwin" and have_brew:
                add_block("vscode-gui", ["missing", "1) brew install --cask visual-studio-code", "2) https://code.visualstudio.com/"])
            elif sysname == "Linux":
                add_block("vscode-gui", ["missing", "1) https://code.visualstudio.com/"])
            else:
                add_block("vscode-gui", ["missing", "1) https://code.visualstudio.com/"])

        else:
            add_block(tool_id, ["unknown", "1) see library/shared/extras/"])

    return out


def detect_duplicates(entries: Iterable[Entry]) -> Optional[Tuple[Category, str, list[Entry]]]:
    by_key: Dict[Tuple[Category, str], list[Entry]] = {}
    for e in entries:
        by_key.setdefault((e.category, e.id), []).append(e)
    for (category, tool_id), group in by_key.items():
        if len(group) > 1:
            return category, tool_id, group
    return None


def src_path(e: Entry, root: Path) -> Path:
    category_dir = ".commands" if e.category == "commands" else e.category
    base = root / "library" / e.author / category_dir
    if e.category in ("skills", "skills-user-only"):
        return base / e.id
    return base / f"{e.id}.md"


def claude_dest(e: Entry, claude_root: Path) -> Path:
    if e.category in ("skills", "skills-user-only"):
        return claude_root / e.category / e.id
    return claude_root / e.category / f"{e.id}.md"


def opencode_dest(e: Entry, opencode_root: Path) -> Path:
    if e.category in ("skills", "skills-user-only"):
        return opencode_root / e.category / e.id
    return opencode_root / e.category / f"{e.id}.md"


def is_owned(state: Dict[str, Any], target: Target, e: Entry, dest: Path) -> bool:
    owned_map = state.get("owned", {}).get(target, {}).get(e.category, {})
    if not isinstance(owned_map, dict):
        return False
    recorded = owned_map.get(e.id)
    if not isinstance(recorded, str):
        return False
    return Path(recorded) == dest


def set_owned(state: Dict[str, Any], target: Target, e: Entry, dest: Path) -> None:
    state["owned"][target][e.category][e.id] = str(dest)


def clear_owned(state: Dict[str, Any], target: Target, e: Entry) -> None:
    state["owned"][target][e.category].pop(e.id, None)


def ensure_parent(dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dest: Path) -> None:
    ensure_parent(dest)
    shutil.copy2(src, dest)


def copy_skill_dir(src_dir: Path, dest_dir: Path) -> None:
    ensure_parent(dest_dir)
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    shutil.copytree(src_dir, dest_dir)


def delete_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sync DevKit profile to Claude Code and OpenCode")
    parser.add_argument("profile", help="Profile name (e.g. xapids)")
    parser.add_argument(
        "--target",
        choices=["both", "claude", "opencode"],
        default="both",
        help="Where to sync (default: both)",
    )
    parser.add_argument(
        "--no-prune",
        action="store_true",
        help="Disable pruning of adapter-owned disabled entries",
    )
    parser.add_argument(
        "--state-file",
        default=None,
        help="Override state file path (default: .sync-state-<profile>.json in repo root)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without changing filesystem",
    )
    parser.add_argument(
        "--claude-root",
        default=str(Path.home() / ".claude"),
        help="Claude config root (default: ~/.claude)",
    )
    parser.add_argument(
        "--opencode-root",
        default=str(Path.home() / ".config" / "opencode"),
        help="OpenCode config root (default: ~/.config/opencode)",
    )
    args = parser.parse_args(argv)

    profile_path = repo_root() / "profiles" / f"{args.profile}.yml"
    if not profile_path.exists():
        prompt_and_abort("Profile not found", f"Expected: {profile_path}")

    state_path = Path(args.state_file).expanduser() if args.state_file else default_state_file(args.profile)
    state = load_state(state_path)

    profile = load_yaml(profile_path)
    entries = parse_entries(profile)
    extras = parse_extras(profile)
    enabled_extras = [e["id"] for e in extras if e.get("enabled") is True]

    dup = detect_duplicates(entries)
    if dup is not None:
        category, tool_id, group = dup
        authors = ", ".join(sorted({e.author for e in group}))
        prompt_and_abort(
            "Duplicate id in profile",
            f"Category: {category}\nId: {tool_id}\nAuthors: {authors}\n\n"
            "Fix: change ids in the repo/profile to be unique, then re-run.",
        )

    root = repo_root()
    claude_root = Path(args.claude_root).expanduser()
    opencode_root = Path(args.opencode_root).expanduser()
    targets: list[Target]
    if args.target == "both":
        targets = ["claude", "opencode"]
    else:
        targets = [args.target]  # type: ignore[assignment]

    enabled = [e for e in entries if e.enabled]
    disabled = [e for e in entries if not e.enabled]

    # Preflight: sources exist; writes do not conflict with non-owned destinations.
    planned_writes: list[Tuple[Target, Entry, Path, Path]] = []
    planned_deletes: list[Tuple[Target, Entry, Path]] = []

    for e in enabled:
        src = src_path(e, root)
        if e.category in ("skills", "skills-user-only"):
            if not src.exists() or not src.is_dir():
                prompt_and_abort(
                    "Missing skill source directory",
                    f"Expected directory: {src}\nFrom: {e.category}:{e.id} (author {e.author})",
                )
        else:
            if not src.exists() or not src.is_file():
                prompt_and_abort(
                    "Missing source file",
                    f"Expected file: {src}\nFrom: {e.category}:{e.id} (author {e.author})",
                )

        for t in targets:
            dest = claude_dest(e, claude_root) if t == "claude" else opencode_dest(e, opencode_root)
            if dest.exists() and not is_owned(state, t, e, dest):
                prompt_and_abort(
                    "Destination conflict (not adapter-owned)",
                    f"Tool: {e.category}:{e.id} (author {e.author})\n"
                    f"Source: {src}\nDestination: {dest}\n\n"
                    "The destination exists but was not created by this adapter, so it will not be overwritten.\n"
                    "Resolution: rename/move/delete the existing destination path OR change this tool's id to avoid collision.\n"
                    "Then re-run sync.",
                )
            planned_writes.append((t, e, src, dest))

    if not args.no_prune:
        for e in disabled:
            for t in targets:
                dest = claude_dest(e, claude_root) if t == "claude" else opencode_dest(e, opencode_root)
                if is_owned(state, t, e, dest):
                    planned_deletes.append((t, e, dest))

    # Execute
    def say(line: str) -> None:
        print(line)

    if args.dry_run:
        say("DRY RUN: no filesystem changes")

    for t, e, src, dest in planned_writes:
        owned = is_owned(state, t, e, dest)
        action = "update" if owned and dest.exists() else "install"
        say(f"{t}: {action} {e.category}:{e.id} -> {dest}")
        if args.dry_run:
            continue
        if e.category in ("skills", "skills-user-only"):
            copy_skill_dir(src, dest)
        else:
            copy_file(src, dest)
        set_owned(state, t, e, dest)

    for t, e, dest in planned_deletes:
        say(f"{t}: prune {e.category}:{e.id} -> {dest}")
        if args.dry_run:
            continue
        delete_path(dest)
        clear_owned(state, t, e)

    if not args.dry_run:
        save_state(state_path, state)
        say(f"State updated: {state_path}")

    if enabled_extras:
        say("")
        say("Enabled extras")
        say("----------------------------------------")
        for line in extras_install_hints(enabled_extras):
            say(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
