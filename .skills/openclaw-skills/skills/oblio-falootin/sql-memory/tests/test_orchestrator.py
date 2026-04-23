#!/usr/bin/env python3
"""
test_orchestrator.py — Oblio Unit Test Pipeline Orchestrator
=============================================================
MACRO: Ensure every Python file has comprehensive unit tests,
       written to consistent best-practices standards, that
       all pass before code is considered shippable.

PIPELINE:
  Phase 1 (Parallel):
    - Agent A: Scan all .py files, identify which need tests, create stub files
    - Agent B: For each file with a stub, analyze code and write actual tests
  Phase 2 (Sequential):
    - Agent C: Execute all tests, capture failures
    - Agent D (if failures): Pass failures back to Agent B for revision
  Loop Phase 2 until all tests pass.

All tasks queued to SQL TaskQueue for async execution.
"""

import os
import sys
import ast
import json
import logging
from pathlib import Path
from datetime import datetime

# ── Bootstrap path ──────────────────────────────────────────────────────────
WORKSPACE = Path('/home/oblio/.openclaw/workspace')
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / 'infrastructure'))

try:
    from dotenv import load_dotenv
    load_dotenv(WORKSPACE / '.env')
except ImportError:
    env_path = WORKSPACE / '.env'
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

from infrastructure.sql_memory import SQLMemory

# ── Config ───────────────────────────────────────────────────────────────────
TESTS_DIR = WORKSPACE / 'tests'
TESTS_DIR.mkdir(exist_ok=True)

LOG_PATH = WORKSPACE / 'logs' / 'test_orchestrator.log'
LOG_PATH.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [test_orchestrator] %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger('test_orchestrator')

# Files to skip (no meaningful tests needed)
SKIP_FILES = {
    '__init__.py',
    'piper_speak.sh',
    'morning-report.py',  # script-level, no functions
}

# Files that are pure scripts (entry points), test differently
SCRIPT_FILES = {
    'bin/morning-report.py',
    'bin/watchdog.py',
}


def extract_testable_functions(filepath: Path) -> list[dict]:
    """
    Parse a Python file and extract all functions/methods that should be tested.
    Returns list of {name, type, lineno, docstring, args}.
    """
    try:
        source = filepath.read_text(encoding='utf-8')
        tree = ast.parse(source)
    except Exception as e:
        log.warning(f"Could not parse {filepath}: {e}")
        return []

    testable = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip private/dunder unless they're __init__
            name = node.name
            if name.startswith('__') and name != '__init__':
                continue
            if name.startswith('_') and not name.startswith('__'):
                continue  # skip private helpers

            docstring = ast.get_docstring(node) or ''
            args = [a.arg for a in node.args.args if a.arg != 'self']

            testable.append({
                'name': name,
                'type': 'async' if isinstance(node, ast.AsyncFunctionDef) else 'sync',
                'lineno': node.lineno,
                'docstring': docstring[:200],
                'args': args,
            })

    return testable


def get_test_filepath(source_path: Path) -> Path:
    """Map a source file to its corresponding test file."""
    # Flatten to just filename for test naming
    parts = source_path.relative_to(WORKSPACE).parts

    # Remove directory prefix, build test filename
    if parts[0] in ('infrastructure', 'agents', 'bin'):
        name = '_'.join(parts[1:]).replace('.py', '')
    else:
        name = parts[-1].replace('.py', '')

    return TESTS_DIR / f"test_{name}.py"


def create_stub_test_file(source_path: Path, functions: list[dict]) -> Path:
    """Create a stub test file with TODO markers for each function."""
    test_path = get_test_filepath(source_path)
    module_name = source_path.stem
    rel_path = source_path.relative_to(WORKSPACE)

    lines = [
        f'#!/usr/bin/env python3',
        f'"""',
        f'Unit tests for {rel_path}',
        f'Auto-generated stub — {datetime.now().strftime("%Y-%m-%d")}',
        f'',
        f'BEST PRACTICES:',
        f'  - One test per function/behavior',
        f'  - Arrange → Act → Assert pattern',
        f'  - Mock all external dependencies (SQL, Ollama, filesystem)',
        f'  - Test happy path + edge cases + error conditions',
        f'  - Use pytest fixtures for reusable setup',
        f'  - All tests must be independent (no shared state)',
        f'"""',
        f'',
        f'import pytest',
        f'import sys',
        f'from pathlib import Path',
        f'from unittest.mock import MagicMock, patch, call',
        f'',
        f'# ── Path setup ──────────────────────────────────────────────────────────────',
        f'WORKSPACE = Path(__file__).parent.parent',
        f'sys.path.insert(0, str(WORKSPACE))',
        f'sys.path.insert(0, str(WORKSPACE / "infrastructure"))',
        f'',
        f'# ── Fixtures ────────────────────────────────────────────────────────────────',
        f'',
        f'@pytest.fixture',
        f'def mock_sql():',
        f'    """Mock SQLMemory to prevent real DB calls in tests."""',
        f'    with patch("infrastructure.sql_memory.SQLMemory") as mock:',
        f'        instance = mock.return_value',
        f'        instance.queue_task.return_value = True',
        f'        instance.log_event.return_value = True',
        f'        instance.get_pending_tasks.return_value = []',
        f'        yield instance',
        f'',
        f'',
        f'@pytest.fixture',
        f'def mock_ollama():',
        f'    """Mock Ollama API calls."""',
        f'    with patch("urllib.request.urlopen") as mock:',
        f'        import json',
        f'        mock.return_value.__enter__.return_value.read.return_value = \\',
        f'            json.dumps({{"response": "Mock Ollama response"}}).encode()',
        f'        yield mock',
        f'',
        f'',
    ]

    # Generate stub test class
    class_name = ''.join(w.capitalize() for w in module_name.split('_'))
    lines += [
        f'# ── Tests for {rel_path} ──────────────────────────────────────────────────────',
        f'',
        f'class Test{class_name}:',
        f'    """Test suite for {module_name}."""',
        f'',
    ]

    if not functions:
        lines += [
            f'    def test_module_imports(self):',
            f'        """Verify module can be imported without errors."""',
            f'        # TODO: Import the module and assert no exceptions',
            f'        pass  # STUB — implement me',
            f'',
        ]
    else:
        for fn in functions:
            test_name = f"test_{fn['name']}"
            lines += [
                f'    def {test_name}(self, mock_sql, mock_ollama):',
                f'        """',
                f'        Test: {fn["name"]}()',
                f'        Source line: {fn["lineno"]}',
                f'        {"Docstring: " + fn["docstring"][:100] if fn["docstring"] else "TODO: Add test docstring"}',
                f'        """',
                f'        # TODO: Implement test for {fn["name"]}',
                f'        # Arrange',
                f'        # ... set up test data ...',
                f'        # Act',
                f'        # result = {fn["name"]}({", ".join(repr("test") for _ in fn["args"])})',
                f'        # Assert',
                f'        # assert result is not None',
                f'        pytest.skip("STUB — implement me")',
                f'',
            ]

            # Add error case stub
            lines += [
                f'    def {test_name}_handles_errors(self, mock_sql):',
                f'        """Test error handling in {fn["name"]}()."""',
                f'        # TODO: Test error conditions (bad input, network failure, etc.)',
                f'        pytest.skip("STUB — implement me")',
                f'',
            ]

    # Write file only if it doesn't already exist (don't overwrite real tests!)
    if test_path.exists():
        log.info(f"  ⏭ Test file already exists: {test_path.name}")
        return test_path
    else:
        test_path.write_text('\n'.join(lines), encoding='utf-8')
        log.info(f"  ✅ Created stub: {test_path.name} ({len(functions)} functions)")
        return test_path


def queue_test_tasks(mem: SQLMemory, source_path: Path, test_path: Path, functions: list[dict]):
    """Queue SQL tasks for the test-writing and test-running pipeline."""
    rel = str(source_path.relative_to(WORKSPACE))
    test_rel = str(test_path.relative_to(WORKSPACE))

    # Task 1: Agent writes actual tests (can run in parallel with other files)
    mem.queue_task(
        agent='unit_test_writer',
        task_type='write_unit_tests',
        payload=json.dumps({
            'source_file': rel,
            'test_file': test_rel,
            'functions': functions,
            'macro': f'Ensure {rel} has comprehensive unit tests covering all public functions',
            'micro': (
                f'1. Read {rel} carefully\n'
                f'2. For each function in test stubs, write a real test\n'
                f'3. Follow Arrange→Act→Assert pattern\n'
                f'4. Mock all external deps (SQL, Ollama, filesystem, network)\n'
                f'5. Test happy path + at least one error condition per function\n'
                f'6. Remove pytest.skip() when test is implemented\n'
                f'7. All tests must be independent — no shared state'
            ),
            'best_practices': [
                'AAA pattern (Arrange, Act, Assert)',
                'Mock all I/O (SQL, Ollama, file system, network)',
                'One assertion focus per test',
                'Descriptive test names (test_function_does_x_when_y)',
                'No shared mutable state between tests',
                'Fast tests — no real network/DB calls',
            ]
        }),
        priority='high'
    )

    # Task 2: Run tests after writing (depends on write task completing)
    mem.queue_task(
        agent='unit_test_runner',
        task_type='run_and_validate_tests',
        payload=json.dumps({
            'test_file': test_rel,
            'source_file': rel,
            'macro': f'Validate all unit tests in {test_rel} pass successfully',
            'micro': (
                f'1. Run: python3 -m pytest {test_rel} -v --tb=short\n'
                f'2. Capture output\n'
                f'3. If ALL pass: mark done, log success to SQL\n'
                f'4. If ANY fail: queue revision task back to unit_test_writer\n'
                f'5. Include full failure output in revision task payload\n'
                f'6. Max 3 revision cycles before escalating to CRITICAL'
            ),
            'on_failure': 'requeue_to_writer',
            'max_revisions': 3,
        }),
        priority='medium'
    )


def scan_and_queue_all(mem: SQLMemory) -> dict:
    """
    Main entry: scan all Python files, create stubs, queue tasks.
    Returns summary dict.
    """
    summary = {
        'scanned': 0,
        'skipped': 0,
        'stubs_created': 0,
        'stubs_existing': 0,
        'tasks_queued': 0,
        'files': []
    }

    python_files = sorted(WORKSPACE.rglob('*.py'))

    for filepath in python_files:
        # Skip test files, __pycache__, .git
        parts = filepath.parts
        if 'tests' in parts or '__pycache__' in parts or '.git' in parts:
            continue
        if filepath.name in SKIP_FILES:
            summary['skipped'] += 1
            continue

        summary['scanned'] += 1
        rel = filepath.relative_to(WORKSPACE)
        log.info(f"Scanning: {rel}")

        functions = extract_testable_functions(filepath)

        if not functions:
            log.info(f"  ⏭ No testable functions in {rel}")
            summary['skipped'] += 1
            continue

        test_path = get_test_filepath(filepath)

        existed = test_path.exists()
        stub_path = create_stub_test_file(filepath, functions)

        if existed:
            summary['stubs_existing'] += 1
        else:
            summary['stubs_created'] += 1

        # Always queue tasks (even if stub existed — may need re-running)
        queue_test_tasks(mem, filepath, test_path, functions)
        summary['tasks_queued'] += 2  # write + run
        summary['files'].append({
            'source': str(rel),
            'test': str(test_path.relative_to(WORKSPACE)),
            'functions': len(functions),
            'stub_existed': existed,
        })

    return summary


def main():
    log.info("=" * 60)
    log.info("Unit Test Orchestrator starting")
    log.info("=" * 60)

    mem = SQLMemory('cloud')

    summary = scan_and_queue_all(mem)

    log.info("")
    log.info("=" * 60)
    log.info("SCAN COMPLETE")
    log.info(f"  Files scanned:    {summary['scanned']}")
    log.info(f"  Files skipped:    {summary['skipped']}")
    log.info(f"  Stubs created:    {summary['stubs_created']}")
    log.info(f"  Stubs existing:   {summary['stubs_existing']}")
    log.info(f"  Tasks queued:     {summary['tasks_queued']}")
    log.info("=" * 60)

    # Log to SQL
    mem.log_event(
        event_type='test_orchestrator_scan',
        agent='test_orchestrator',
        description=f"Scanned {summary['scanned']} files, created {summary['stubs_created']} stubs, queued {summary['tasks_queued']} tasks",
        metadata=json.dumps(summary)
    )

    # Print file table
    print(f"\n{'Source File':<50} {'Test File':<40} {'Functions':>10} {'Status'}")
    print("-" * 115)
    for f in summary['files']:
        status = '⏭ existed' if f['stub_existed'] else '✅ created'
        print(f"{f['source']:<50} {f['test']:<40} {f['functions']:>10}  {status}")

    return summary


if __name__ == '__main__':
    main()
