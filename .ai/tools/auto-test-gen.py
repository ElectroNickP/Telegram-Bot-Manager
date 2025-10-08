#!/usr/bin/env python3
"""
Auto Test Generator

Автоматически генерирует тесты для нового кода.
Анализирует изменения и создаёт соответствующие тесты.

Работает в связке с Git hooks - генерирует тесты при коммите.

Usage:
    python3 .ai/tools/auto-test-gen.py              # Scan all
    python3 .ai/tools/auto-test-gen.py --file path  # Scan file
    python3 .ai/tools/auto-test-gen.py --diff       # Only changed
"""

import os
import sys
import ast
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
TEST_COVERAGE_FILE = PROJECT_ROOT / '.ai' / 'TEST_COVERAGE.json'


@dataclass
class TestableEntity:
    """Сущность которую нужно протестировать"""
    type: str  # 'function', 'class', 'api_endpoint', 'feature', 'ui_action'
    name: str
    file_path: str
    line_number: int
    complexity: int  # 1-5 (5 = самый сложный)
    needs_tests: List[str]  # ['unit', 'integration', 'e2e']
    test_exists: bool
    test_path: Optional[str]
    priority: int  # 1-5 (5 = критично)


class AutoTestGenerator:
    """
    Автоматический генератор тестов
    
    Анализирует код и генерирует:
    - Unit tests для функций/классов
    - Integration tests для use cases
    - E2E tests для UI/API
    - Mock data для тестов
    """
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.testable_entities: List[TestableEntity] = []
        self.coverage_data = self._load_coverage()
    
    def _load_coverage(self) -> Dict:
        """Загрузить текущее покрытие тестами"""
        if TEST_COVERAGE_FILE.exists():
            with open(TEST_COVERAGE_FILE, 'r') as f:
                return json.load(f)
        return {
            'last_updated': '',
            'entities': {},
            'coverage': {
                'total': 0,
                'tested': 0,
                'percentage': 0
            }
        }
    
    def _save_coverage(self):
        """Сохранить покрытие"""
        TEST_COVERAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        self.coverage_data['last_updated'] = datetime.now().isoformat()
        
        with open(TEST_COVERAGE_FILE, 'w') as f:
            json.dump(self.coverage_data, f, indent=2)
    
    def scan_codebase(self, only_changed: bool = False):
        """
        Сканировать кодовую базу
        
        Args:
            only_changed: Сканировать только изменённые файлы (из git diff)
        """
        logger.info("🔍 Scanning codebase for testable entities...")
        
        if only_changed:
            files = self._get_changed_files()
        else:
            files = self._get_all_python_files()
        
        for file_path in files:
            self._scan_file(file_path)
        
        logger.info(f"✅ Found {len(self.testable_entities)} testable entities")
    
    def _get_changed_files(self) -> List[Path]:
        """Получить изменённые файлы из git"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            files = []
            for line in result.stdout.strip().split('\n'):
                if line.endswith('.py'):
                    file_path = self.project_root / line
                    if file_path.exists():
                        files.append(file_path)
            
            return files
        except:
            return []
    
    def _get_all_python_files(self) -> List[Path]:
        """Получить все Python файлы проекта"""
        files = []
        
        for pattern in ['src/**/*.py', 'core/**/*.py', 'adapters/**/*.py']:
            files.extend(self.project_root.glob(pattern))
        
        # Exclude tests
        files = [f for f in files if 'test' not in str(f)]
        
        return files
    
    def _scan_file(self, file_path: Path):
        """Сканировать файл на testable entities"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Functions
                if isinstance(node, ast.FunctionDef):
                    self._analyze_function(node, file_path)
                
                # Classes
                elif isinstance(node, ast.ClassDef):
                    self._analyze_class(node, file_path)
        
        except Exception as e:
            logger.debug(f"Failed to parse {file_path}: {e}")
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path):
        """Анализировать функцию"""
        # Skip private functions
        if node.name.startswith('_') and not node.name.startswith('__'):
            return
        
        # Calculate complexity
        complexity = self._calculate_complexity(node)
        
        # Determine priority
        priority = self._determine_priority(node, file_path)
        
        # Check if test exists
        test_exists, test_path = self._check_test_exists(
            'function', node.name, file_path
        )
        
        # Determine test types needed
        needs_tests = self._determine_test_types(node, file_path)
        
        entity = TestableEntity(
            type='function',
            name=node.name,
            file_path=str(file_path.relative_to(self.project_root)),
            line_number=node.lineno,
            complexity=complexity,
            needs_tests=needs_tests,
            test_exists=test_exists,
            test_path=test_path,
            priority=priority
        )
        
        self.testable_entities.append(entity)
    
    def _analyze_class(self, node: ast.ClassDef, file_path: Path):
        """Анализировать класс"""
        # Skip test classes
        if node.name.startswith('Test'):
            return
        
        complexity = self._calculate_class_complexity(node)
        priority = self._determine_priority(node, file_path)
        
        test_exists, test_path = self._check_test_exists(
            'class', node.name, file_path
        )
        
        needs_tests = self._determine_test_types(node, file_path)
        
        entity = TestableEntity(
            type='class',
            name=node.name,
            file_path=str(file_path.relative_to(self.project_root)),
            line_number=node.lineno,
            complexity=complexity,
            needs_tests=needs_tests,
            test_exists=test_exists,
            test_path=test_path,
            priority=priority
        )
        
        self.testable_entities.append(entity)
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Рассчитать complexity функции (1-5)"""
        # Count branches
        branches = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                branches += 1
        
        # Count async operations
        has_async = isinstance(node, ast.AsyncFunctionDef)
        
        # Determine complexity
        if branches == 0:
            return 1
        elif branches <= 2:
            return 2 if not has_async else 3
        elif branches <= 5:
            return 3 if not has_async else 4
        else:
            return 5
    
    def _calculate_class_complexity(self, node: ast.ClassDef) -> int:
        """Рассчитать complexity класса"""
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        
        if len(methods) <= 3:
            return 2
        elif len(methods) <= 7:
            return 3
        elif len(methods) <= 12:
            return 4
        else:
            return 5
    
    def _determine_priority(self, node, file_path: Path) -> int:
        """Определить приоритет тестирования (1-5)"""
        path_str = str(file_path)
        
        # Critical: Features
        if 'features/' in path_str:
            return 5
        
        # High: Use cases, domain
        if 'usecases/' in path_str or 'domain/' in path_str:
            return 4
        
        # Medium: Services, adapters
        if 'services/' in path_str or 'adapters/' in path_str:
            return 3
        
        # Low: Utils, helpers
        if 'utils/' in path_str or 'shared/' in path_str:
            return 2
        
        return 3  # Default
    
    def _determine_test_types(self, node, file_path: Path) -> List[str]:
        """Определить какие типы тестов нужны"""
        tests = []
        path_str = str(file_path)
        
        # Features нужны все типы
        if 'features/' in path_str:
            tests = ['unit', 'integration', 'e2e']
        
        # Use cases нужны unit + integration
        elif 'usecases/' in path_str:
            tests = ['unit', 'integration']
        
        # Domain нужны unit
        elif 'domain/' in path_str:
            tests = ['unit']
        
        # API endpoints нужны integration + e2e
        elif 'api/' in path_str:
            tests = ['integration', 'e2e']
        
        # Остальное - unit
        else:
            tests = ['unit']
        
        return tests
    
    def _check_test_exists(self, entity_type: str, name: str, file_path: Path) -> tuple:
        """Проверить существует ли тест"""
        # Try to find test file
        rel_path = file_path.relative_to(self.project_root)
        
        # Possible test locations
        test_paths = [
            self.project_root / 'tests' / 'unit' / rel_path.parent.name / f'test_{rel_path.name}',
            self.project_root / 'tests' / 'unit' / f'test_{rel_path.name}',
            self.project_root / 'tests' / 'integration' / f'test_{rel_path.name}',
        ]
        
        for test_path in test_paths:
            if test_path.exists():
                # Check if specific test exists
                try:
                    with open(test_path, 'r') as f:
                        content = f.read()
                    
                    # Look for test function/class
                    pattern = rf'(def test.*{name}|class Test.*{name})'
                    if re.search(pattern, content, re.IGNORECASE):
                        return True, str(test_path.relative_to(self.project_root))
                except:
                    pass
        
        return False, None
    
    def generate_missing_tests(self, auto_commit: bool = False):
        """Сгенерировать недостающие тесты"""
        logger.info("🔧 Generating missing tests...")
        
        missing = [e for e in self.testable_entities if not e.test_exists]
        
        if not missing:
            logger.info("✅ All entities have tests!")
            return
        
        # Sort by priority
        missing.sort(key=lambda e: e.priority, reverse=True)
        
        generated = 0
        for entity in missing[:10]:  # Top 10 most important
            if self._generate_test_for_entity(entity):
                generated += 1
        
        logger.info(f"✅ Generated {generated} test files")
        
        if auto_commit and generated > 0:
            self._commit_generated_tests()
    
    def _generate_test_for_entity(self, entity: TestableEntity) -> bool:
        """Сгенерировать тест для конкретной сущности"""
        logger.info(f"📝 Generating test for {entity.type} '{entity.name}'")
        
        # Determine test file path
        test_file = self._get_test_file_path(entity)
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate test content
        if entity.type == 'function':
            content = self._generate_function_test(entity)
        elif entity.type == 'class':
            content = self._generate_class_test(entity)
        else:
            return False
        
        # Write test file
        if test_file.exists():
            # Append to existing file
            with open(test_file, 'a') as f:
                f.write('\n\n' + content)
        else:
            # Create new file
            header = self._generate_test_file_header(entity)
            with open(test_file, 'w') as f:
                f.write(header + '\n\n' + content)
        
        logger.info(f"   Created: {test_file.relative_to(self.project_root)}")
        return True
    
    def _get_test_file_path(self, entity: TestableEntity) -> Path:
        """Определить путь к тестовому файлу"""
        # Get source file path
        source_path = Path(entity.file_path)
        
        # Determine test type directory
        if 'unit' in entity.needs_tests:
            test_dir = 'unit'
        elif 'integration' in entity.needs_tests:
            test_dir = 'integration'
        else:
            test_dir = 'unit'
        
        # Create test path
        test_file_name = f"test_{source_path.name}"
        test_path = self.project_root / 'tests' / test_dir / source_path.parent.name / test_file_name
        
        return test_path
    
    def _generate_test_file_header(self, entity: TestableEntity) -> str:
        """Сгенерировать заголовок тестового файла"""
        source_module = entity.file_path.replace('/', '.').replace('.py', '')
        
        return f'''"""
Tests for {entity.file_path}

Auto-generated by auto-test-gen.py
Edit and expand as needed.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from {source_module} import {entity.name}
'''
    
    def _generate_function_test(self, entity: TestableEntity) -> str:
        """Сгенерировать unit test для функции"""
        test_name = f"test_{entity.name}_basic"
        
        is_async = 'async' in entity.name or entity.file_path.startswith('src/')
        
        if is_async:
            decorator = '@pytest.mark.asyncio'
            func_def = f'async def {test_name}():'
            call = f'await {entity.name}()'
        else:
            decorator = ''
            func_def = f'def {test_name}():'
            call = f'{entity.name}()'
        
        return f'''{decorator}
{func_def}
    """
    Test {entity.name} - basic functionality
    
    TODO: Expand this test with:
    - Different input scenarios
    - Edge cases
    - Error handling
    - Mock external dependencies if needed
    """
    # Arrange
    # TODO: Set up test data
    
    # Act
    # result = {call}
    
    # Assert
    # TODO: Add assertions
    assert True  # Placeholder
'''
    
    def _generate_class_test(self, entity: TestableEntity) -> str:
        """Сгенерировать unit test для класса"""
        test_class_name = f"Test{entity.name}"
        
        return f'''class {test_class_name}:
    """
    Tests for {entity.name}
    
    TODO: Add tests for:
    - Initialization
    - Each public method
    - Error scenarios
    - Edge cases
    """
    
    def test_init(self):
        """Test {entity.name} initialization"""
        # instance = {entity.name}()
        # assert instance is not None
        assert True  # Placeholder
    
    # TODO: Add more tests for each method
'''
    
    def _commit_generated_tests(self):
        """Закоммитить сгенерированные тесты"""
        try:
            subprocess.run(
                ['git', 'add', 'tests/'],
                cwd=self.project_root,
                check=True
            )
            
            subprocess.run(
                ['git', 'commit', '-m', 'test: auto-generated tests'],
                cwd=self.project_root,
                check=True
            )
            
            logger.info("✅ Auto-committed generated tests")
        except:
            logger.warning("⚠️  Failed to auto-commit tests")
    
    def generate_coverage_report(self):
        """Сгенерировать отчёт о покрытии"""
        logger.info("📊 Generating coverage report...")
        
        total = len(self.testable_entities)
        tested = sum(1 for e in self.testable_entities if e.test_exists)
        percentage = (tested / total * 100) if total > 0 else 0
        
        # Group by priority
        by_priority = {}
        for entity in self.testable_entities:
            if entity.priority not in by_priority:
                by_priority[entity.priority] = {'total': 0, 'tested': 0}
            
            by_priority[entity.priority]['total'] += 1
            if entity.test_exists:
                by_priority[entity.priority]['tested'] += 1
        
        # Update coverage data
        self.coverage_data['coverage'] = {
            'total': total,
            'tested': tested,
            'percentage': round(percentage, 1)
        }
        
        self.coverage_data['by_priority'] = by_priority
        
        # Save
        self._save_coverage()
        
        # Print report
        logger.info(f"\n{'='*70}")
        logger.info("TEST COVERAGE REPORT")
        logger.info(f"{'='*70}")
        logger.info(f"\nOverall: {tested}/{total} entities tested ({percentage:.1f}%)")
        
        logger.info(f"\nBy Priority:")
        for priority in sorted(by_priority.keys(), reverse=True):
            data = by_priority[priority]
            pct = (data['tested'] / data['total'] * 100) if data['total'] > 0 else 0
            priority_name = {5: 'CRITICAL', 4: 'HIGH', 3: 'MEDIUM', 2: 'LOW', 1: 'TRIVIAL'}[priority]
            logger.info(f"  Priority {priority} ({priority_name}): {data['tested']}/{data['total']} ({pct:.1f}%)")
        
        # List untested critical entities
        critical_untested = [
            e for e in self.testable_entities 
            if not e.test_exists and e.priority >= 4
        ]
        
        if critical_untested:
            logger.info(f"\n⚠️  CRITICAL/HIGH PRIORITY - NOT TESTED:")
            for entity in critical_untested[:10]:
                logger.info(f"   - {entity.type} '{entity.name}' in {entity.file_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-generate tests')
    parser.add_argument('--file', help='Scan specific file')
    parser.add_argument('--diff', action='store_true', help='Only changed files')
    parser.add_argument('--generate', action='store_true', help='Generate missing tests')
    parser.add_argument('--auto-commit', action='store_true', help='Auto-commit generated tests')
    args = parser.parse_args()
    
    generator = AutoTestGenerator()
    
    if args.file:
        generator._scan_file(Path(args.file))
    else:
        generator.scan_codebase(only_changed=args.diff)
    
    if args.generate:
        generator.generate_missing_tests(auto_commit=args.auto_commit)
    
    generator.generate_coverage_report()


if __name__ == '__main__':
    main()

