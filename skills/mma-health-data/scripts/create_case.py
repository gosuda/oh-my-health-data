#!/usr/bin/env python3
"""Create a private, local draft from the skill's bundled public templates.

This command does not contact a portal, submit a request, or update a receipt.
It uses only the Python standard library and can move with the skill folder.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any


class CaseError(Exception):
    """An expected validation or filesystem error safe to show to the user."""


def _nonempty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CaseError(f"템플릿의 {field} 값은 비어 있지 않은 문자열이어야 합니다.")
    return value


def load_templates(skill_dir: Path) -> dict[str, Any]:
    source = skill_dir / "assets" / "templates.json"
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        raise CaseError("스킬의 assets/templates.json 파일을 읽을 수 없습니다.") from error
    if not isinstance(data, dict) or data.get("version") != 1:
        raise CaseError("지원하는 템플릿 형식은 version 1입니다.")
    _nonempty_text(data.get("source_baseline"), "source_baseline")
    templates = data.get("templates")
    if not isinstance(templates, list) or not templates:
        raise CaseError("템플릿 목록이 비어 있거나 올바르지 않습니다.")
    template_ids = set()
    for template in templates:
        if not isinstance(template, dict):
            raise CaseError("템플릿 항목은 객체여야 합니다.")
        for field in ("id", "label", "portal_url", "recipient", "title", "opening", "closing"):
            _nonempty_text(template.get(field), field)
        if template["id"] in template_ids:
            raise CaseError("중복된 템플릿 ID가 있습니다.")
        template_ids.add(template["id"])
        questions = template.get("questions")
        if not isinstance(questions, list) or not questions:
            raise CaseError("템플릿 질문 목록이 비어 있거나 올바르지 않습니다.")
        question_ids = set()
        for question in questions:
            if not isinstance(question, dict):
                raise CaseError("질문 항목은 객체여야 합니다.")
            _nonempty_text(question.get("id"), "questions.id")
            _nonempty_text(question.get("text"), "questions.text")
            if question["id"] in question_ids:
                raise CaseError("한 템플릿에 중복된 질문 ID가 있습니다.")
            question_ids.add(question["id"])
    return data


def _is_inside(path: Path, directory: Path) -> bool:
    return path == directory or directory in path.parents


def _has_git_metadata(directory: Path) -> bool:
    marker = directory / ".git"
    # Some sandboxes expose empty, protected .git directories at unrelated
    # locations. A real checkout has HEAD metadata or a worktree gitdir file.
    if marker.is_dir():
        return (marker / "HEAD").is_file()
    if marker.is_file():
        try:
            with marker.open("rb") as handle:
                return handle.read(4096).startswith(b"gitdir:")
        except OSError as error:
            raise CaseError("출력 경로의 Git 메타데이터를 확인할 수 없습니다.") from error
    return False


def validate_output_dir(raw_path: str, skill_dir: Path) -> Path:
    requested = Path(raw_path)
    if not requested.is_absolute():
        raise CaseError("--output-dir에는 저장할 새 폴더의 절대 경로를 입력하세요.")
    # lexists also rejects a dangling symlink instead of writing through it.
    if os.path.lexists(requested):
        raise CaseError("출력 경로가 이미 존재합니다. 다른 새 폴더를 지정하세요.")
    try:
        output = requested.resolve()
    except (OSError, RuntimeError) as error:
        raise CaseError("출력 경로의 심볼릭 링크를 확인할 수 없습니다.") from error
    if _is_inside(output, skill_dir):
        raise CaseError("개인 초안은 설치된 스킬 폴더 밖에 저장해야 합니다.")
    # Only Git metadata is inspected; no checkout contents or Git configuration
    # is read. Worktree pointer files are limited to a small prefix.
    for ancestor in (output, *output.parents):
        if _has_git_metadata(ancestor):
            raise CaseError("개인 초안은 Git 저장소 밖의 새 폴더에 저장해야 합니다.")
    return output


def _create_private_dir(path: Path) -> None:
    missing_parents = []
    parent = path.parent
    while not parent.exists():
        missing_parents.append(parent)
        parent = parent.parent
    if not parent.is_dir():
        raise CaseError("출력 경로의 상위 경로가 폴더가 아닙니다.")
    for missing in reversed(missing_parents):
        try:
            missing.mkdir(mode=0o700)
        except FileExistsError:
            if not missing.is_dir():
                raise CaseError("출력 경로의 상위 경로가 폴더가 아닙니다.")
        else:
            if os.name == "posix":
                missing.chmod(0o700)
    # Never reuse an existing case directory, even if it appears empty.
    path.mkdir(mode=0o700)
    if os.name == "posix":
        path.chmod(0o700)


def _write_private_file(path: Path, content: str) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
        if os.name == "posix":
            os.fchmod(handle.fileno(), 0o600)
        handle.write(content)


def render_draft(template: dict[str, Any], recipient: str, scope: str,
                 questions: list[dict[str, str]]) -> str:
    sections = [f"# {template['title']}", f"수신: {recipient}", template["opening"]]
    if scope:
        sections.append(f"대상 범위: {scope}")
    sections.append("\n\n".join(
        f"{number}. [{question['id']}] {question['text']}"
        for number, question in enumerate(questions, 1)
    ))
    sections.append(template["closing"])
    return "\n\n".join(sections) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="병무청 건강정보 요청의 개인용 로컬 초안을 만듭니다.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true", help="템플릿 ID·이름·질문 ID 목록")
    mode.add_argument("--template", metavar="ID", help="사용할 템플릿 ID")
    parser.add_argument("--output-dir", metavar="ABS_PATH", help="Git 저장소 밖에 만들 새 폴더의 절대 경로")
    parser.add_argument("--recipient", metavar="TEXT", help="수신 기관 변경")
    parser.add_argument("--scope", metavar="TEXT", help="요청 대상 범위")
    parser.add_argument("--question", action="append", metavar="ID", help="포함할 질문 ID; 여러 번 지정 가능")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list and any(value is not None for value in (
        args.output_dir, args.recipient, args.scope, args.question
    )):
        parser.error("--list는 다른 옵션과 함께 사용할 수 없습니다.")
    if not args.list and args.output_dir is None:
        parser.error("--template 사용 시 --output-dir가 필요합니다.")
    skill_dir = Path(__file__).resolve().parents[1]
    try:
        data = load_templates(skill_dir)
        if args.list:
            for template in data["templates"]:
                question_ids = ", ".join(question["id"] for question in template["questions"])
                print(f"{template['id']}\t{template['label']}\t{question_ids}")
            return 0
        template = next((item for item in data["templates"] if item["id"] == args.template), None)
        if template is None:
            raise CaseError("알 수 없는 템플릿 ID입니다. --list로 목록을 확인하세요.")
        known_ids = {question["id"] for question in template["questions"]}
        selected_ids = set(args.question) if args.question else known_ids
        if not selected_ids.issubset(known_ids):
            raise CaseError("선택한 템플릿에 없는 질문 ID입니다. --list로 목록을 확인하세요.")
        # Keep source order and collapse repeated IDs for a stable submission.
        questions = [{"id": question["id"], "text": question["text"]}
                     for question in template["questions"] if question["id"] in selected_ids]
        recipient = template["recipient"] if args.recipient is None else args.recipient.strip()
        if not recipient:
            raise CaseError("수신 기관은 비워 둘 수 없습니다.")
        scope = args.scope.strip() if args.scope is not None else ""
        if template["id"] in {"deletion", "stop"} and not scope:
            raise CaseError("삭제·처리정지 요청에는 --scope로 대상 범위를 구체적으로 지정해야 합니다.")
        output = validate_output_dir(args.output_dir, skill_dir)
        case = {
            "version": 1,
            "template_id": template["id"],
            "route": template["label"],
            "portal_url": template["portal_url"],
            "recipient": recipient,
            "status": "draft",
            "questions": questions,
            "scope": scope,
            "title": template["title"],
            "source_baseline": data["source_baseline"],
            "evidence_checked": False,
            "submitted_at": None,
            "receipt": None,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        draft = render_draft(template, recipient, scope, questions)
        serialized = json.dumps(case, ensure_ascii=False, indent=2) + "\n"
        _create_private_dir(output)
        _write_private_file(output / "draft.md", draft)
        _write_private_file(output / "case.json", serialized)
        print(f"로컬 초안을 저장했습니다: {output}")
        print("상태: draft — 접수하지 않았습니다.")
        return 0
    except CaseError as error:
        print(f"오류: {error}", file=sys.stderr)
        return 1
    except OSError:
        # Do not print the draft, scope, or other private field values on error.
        # Preserve any created files for inspection; never remove user data.
        print("오류: 새 초안 폴더 또는 파일을 만들 수 없습니다. 경로와 권한을 확인하세요.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
