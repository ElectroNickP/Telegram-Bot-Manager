#!/usr/bin/env python3
"""
Live Context Validator

Проверяет актуальность AI-контекста в реальном времени.
Гарантирует, что вся информация в .ai/ соответствует реальному коду.

Usage:
    python3 .ai/tools/validate-context.py
    python3 .ai/tools/validate-context.py --fix  # Auto-fix issues
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONTEXT_FILE = PROJECT_ROOT / '.ai' / 'LIVE_CONTEXT.json'


@dataclass
class ValidationIssue:
    """Проблема с актуальностью контекста"""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'missing_file', 'wrong_location', 'outdated_info', etc.
    message: str
    file_path: Optional[str] = None
    fix_available: bool = False
    fix_action: Optional[str] = None


class LiveContextValidator:
    """
    Validates that AI context is up-to-date with actual code.
    
    Checks:
    - Files mentioned in context actually exist
    - Function/class locations are correct
    - Import paths are valid
    - Feature states match reality
    - No "zombie" references to deleted code
    """
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
        self.project_root = PROJECT_ROOT
    
    def validate_all(self) -> Tuple[bool, List[ValidationIssue]]:
        """
        Run all validation checks.
        
        Returns:
            (is_valid, issues)
        """
        logger.info("🔍 Starting live context validation...")
        
        # Check 1: Critical files exist
        self._check_critical_files()
        
        # Check 2: Features are correctly described
        self._check_feature_reality()
        
        # Check 3: Import paths work
        self._check_import_paths()
        
        # Check 4: Function/class locations
        self._check_code_locations()
        
        # Check 5: No zombie references
        self._check_zombie_references()
        
        # Check 6: Context freshness
        self._check_context_freshness()
        
        # Summary
        errors = [i for i in self.issues if i.severity == 'error']
        warnings = [i for i in self.issues if i.severity == 'warning']
        
        is_valid = len(errors) == 0
        
        logger.info(f"\n📊 Validation complete:")
        logger.info(f"   Errors:   {len(errors)}")
        logger.info(f"   Warnings: {len(warnings)}")
        logger.info(f"   Status:   {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        return is_valid, self.issues
    
    def _check_critical_files(self):
        """Check that all critical files mentioned in context exist"""
        logger.info("Checking critical files...")
        
        critical_files = [
            # Core features
            "core/features/base.py",
            "core/features/registry.py",
            "core/features/__init__.py",
            
            # Features
            "src/features/user_sessions/feature.py",
            "src/features/voice_messages/feature.py",
            "src/features/link_transformation/feature.py",
            
            # Main app files
            "src/app.py",
            "src/telegram_bot.py",
            "start.py",
            
            # Config
            ".env.example",
            "requirements.txt",
            "pyproject.toml",
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='missing_file',
                    message=f"Critical file missing: {file_path}",
                    file_path=file_path
                ))
    
    def _check_feature_reality(self):
        """Check that features exist and match descriptions"""
        logger.info("Checking feature reality...")
        
        # Expected features from context
        expected_features = {
            'user_sessions': {
                'path': 'src/features/user_sessions/feature.py',
                'class': 'UserSessionsFeature',
                'commands': ['/connect', '/exit'],
                'has_api': True,
            },
            'voice_messages': {
                'path': 'src/features/voice_messages/feature.py',
                'class': 'VoiceMessagesFeature',
                'has_whisper': True,
                'has_api': True,
            },
            'link_transformation': {
                'path': 'src/features/link_transformation/feature.py',
                'class': 'LinkTransformationFeature',
                'has_api': True,
            }
        }
        
        for feature_name, expected in expected_features.items():
            feature_path = self.project_root / expected['path']
            
            if not feature_path.exists():
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='missing_feature',
                    message=f"Feature file missing: {expected['path']}",
                    file_path=expected['path']
                ))
                continue
            
            # Parse file and check class exists
            try:
                with open(feature_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                class_found = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if node.name == expected['class']:
                            class_found = True
                            
                            # Check if inherits from Feature
                            inherits_feature = False
                            for base in node.bases:
                                if isinstance(base, ast.Name) and base.id == 'Feature':
                                    inherits_feature = True
                            
                            if not inherits_feature:
                                self.issues.append(ValidationIssue(
                                    severity='warning',
                                    category='wrong_inheritance',
                                    message=f"{expected['class']} doesn't inherit from Feature",
                                    file_path=expected['path']
                                ))
                
                if not class_found:
                    self.issues.append(ValidationIssue(
                        severity='error',
                        category='missing_class',
                        message=f"Class {expected['class']} not found in {expected['path']}",
                        file_path=expected['path']
                    ))
                
            except Exception as e:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='parse_error',
                    message=f"Failed to parse {expected['path']}: {e}",
                    file_path=expected['path']
                ))
    
    def _check_import_paths(self):
        """Check that import paths in context are valid"""
        logger.info("Checking import paths...")
        
        # Key imports that should work
        test_imports = [
            "from core.features.base import Feature, FeatureMetadata",
            "from core.features.registry import feature_registry",
            "from src.features import UserSessionsFeature, VoiceMessagesFeature, LinkTransformationFeature",
        ]
        
        # We'll do a syntax-only check (actual import would require dependencies)
        for import_line in test_imports:
            # Extract module path
            match = re.search(r'from ([^\s]+)', import_line)
            if match:
                module_path = match.group(1).replace('.', '/')
                
                # Check if file exists
                possible_paths = [
                    self.project_root / f"{module_path}.py",
                    self.project_root / module_path / "__init__.py",
                ]
                
                exists = any(p.exists() for p in possible_paths)
                
                if not exists:
                    self.issues.append(ValidationIssue(
                        severity='error',
                        category='invalid_import',
                        message=f"Import path doesn't exist: {import_line}",
                        file_path=module_path
                    ))
    
    def _check_code_locations(self):
        """Check that functions/classes are where context says they are"""
        logger.info("Checking code locations...")
        
        # Key locations from context
        locations = {
            'feature_registry': 'core/features/registry.py',
            'Feature': 'core/features/base.py',
            'UserSessionsFeature': 'src/features/user_sessions/feature.py',
            'VoiceMessagesFeature': 'src/features/voice_messages/feature.py',
            'LinkTransformationFeature': 'src/features/link_transformation/feature.py',
        }
        
        for name, expected_path in locations.items():
            file_path = self.project_root / expected_path
            
            if not file_path.exists():
                continue  # Already reported in critical files
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if name appears (class or variable)
                if name.endswith('Feature'):
                    pattern = rf'class\s+{name}\s*\('
                else:
                    pattern = rf'\b{name}\b'
                
                if not re.search(pattern, content):
                    self.issues.append(ValidationIssue(
                        severity='warning',
                        category='wrong_location',
                        message=f"{name} not found in {expected_path}",
                        file_path=expected_path
                    ))
            
            except Exception as e:
                logger.debug(f"Error checking {expected_path}: {e}")
    
    def _check_zombie_references(self):
        """Check for references to deleted/moved code"""
        logger.info("Checking for zombie references...")
        
        # Old code that should NOT exist anymore
        zombie_patterns = [
            # Old session handling (now in features)
            (r'def\s+get_user_session_service\s*\(\s*\):', 'src/telegram_bot.py', 
             "Old get_user_session_service should use features now"),
            
            # Direct service initialization (should use registry)
            (r'link_transformation_service\s*=\s*LinkTransformationService\(\)', 'src/telegram_bot.py',
             "Should use feature registry, not direct service init"),
        ]
        
        for pattern, file_path, warning in zombie_patterns:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if re.search(pattern, content):
                    self.issues.append(ValidationIssue(
                        severity='warning',
                        category='zombie_code',
                        message=f"Zombie code detected: {warning}",
                        file_path=file_path
                    ))
            
            except Exception as e:
                logger.debug(f"Error checking zombies in {file_path}: {e}")
    
    def _check_context_freshness(self):
        """Check when context was last updated"""
        logger.info("Checking context freshness...")
        
        if not CONTEXT_FILE.exists():
            self.issues.append(ValidationIssue(
                severity='info',
                category='no_timestamp',
                message="LIVE_CONTEXT.json not found - will be created",
                fix_available=True,
                fix_action="create_context_file"
            ))
            return
        
        try:
            with open(CONTEXT_FILE, 'r') as f:
                context = json.load(f)
            
            last_updated = context.get('last_validated')
            if not last_updated:
                self.issues.append(ValidationIssue(
                    severity='info',
                    category='no_timestamp',
                    message="Context has no validation timestamp",
                    fix_available=True,
                    fix_action="update_timestamp"
                ))
        
        except Exception as e:
            self.issues.append(ValidationIssue(
                severity='warning',
                category='parse_error',
                message=f"Failed to parse LIVE_CONTEXT.json: {e}"
            ))
    
    def generate_live_context(self) -> Dict:
        """Generate fresh live context from actual code"""
        logger.info("🔄 Generating live context from actual code...")
        
        context = {
            'last_validated': self._get_timestamp(),
            'project_structure': self._scan_project_structure(),
            'features': self._scan_features(),
            'critical_files': self._list_critical_files(),
            'quick_reference': self._generate_quick_reference(),
        }
        
        return context
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _scan_project_structure(self) -> Dict:
        """Scan actual project structure"""
        structure = {
            'features': [],
            'core_modules': [],
            'api_modules': [],
        }
        
        # Scan features
        features_dir = self.project_root / 'src' / 'features'
        if features_dir.exists():
            for item in features_dir.iterdir():
                if item.is_dir() and not item.name.startswith('_'):
                    structure['features'].append(item.name)
        
        # Scan core
        core_dir = self.project_root / 'core'
        if core_dir.exists():
            for item in core_dir.iterdir():
                if item.is_dir() and not item.name.startswith('_'):
                    structure['core_modules'].append(item.name)
        
        # Scan API
        api_dir = self.project_root / 'src' / 'api'
        if api_dir.exists():
            for item in api_dir.iterdir():
                if item.is_dir() and item.name.startswith('v'):
                    structure['api_modules'].append(item.name)
        
        return structure
    
    def _scan_features(self) -> Dict:
        """Scan all features and their metadata"""
        features = {}
        
        features_dir = self.project_root / 'src' / 'features'
        if not features_dir.exists():
            return features
        
        for feature_dir in features_dir.iterdir():
            if not feature_dir.is_dir() or feature_dir.name.startswith('_'):
                continue
            
            feature_file = feature_dir / 'feature.py'
            if not feature_file.exists():
                continue
            
            try:
                with open(feature_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # Find feature class
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if inherits Feature
                        inherits_feature = any(
                            isinstance(base, ast.Name) and base.id == 'Feature'
                            for base in node.bases
                        )
                        
                        if inherits_feature:
                            features[feature_dir.name] = {
                                'class': node.name,
                                'file': f'src/features/{feature_dir.name}/feature.py',
                                'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                                'has_handlers': 'register_telegram_handlers' in [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                                'has_api': 'register_api_routes' in [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                            }
            
            except Exception as e:
                logger.warning(f"Failed to parse {feature_file}: {e}")
        
        return features
    
    def _list_critical_files(self) -> List[str]:
        """List all critical files that must exist"""
        return [
            "core/features/base.py",
            "core/features/registry.py",
            "src/app.py",
            "src/telegram_bot.py",
            "start.py",
            ".env.example",
        ]
    
    def _generate_quick_reference(self) -> Dict:
        """Generate quick reference guide"""
        return {
            'add_feature': [
                "1. Create src/features/my_feature/feature.py",
                "2. Inherit from Feature",
                "3. Implement metadata(), initialize(), shutdown()",
                "4. Register in telegram_bot.py: feature_registry.register(MyFeature())",
            ],
            'find_feature': [
                "feature = get_feature('feature_name')",
                "if feature: ...",
            ],
            'feature_health': [
                "await feature_registry.health_check_all()",
            ],
        }
    
    def save_live_context(self, context: Dict):
        """Save live context to file"""
        CONTEXT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Live context saved to {CONTEXT_FILE}")


def main():
    """Run validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate AI context')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues')
    parser.add_argument('--generate', action='store_true', help='Generate fresh context')
    args = parser.parse_args()
    
    validator = LiveContextValidator()
    
    if args.generate:
        # Generate fresh context
        context = validator.generate_live_context()
        validator.save_live_context(context)
        logger.info("✅ Fresh context generated")
        return 0
    
    # Validate
    is_valid, issues = validator.validate_all()
    
    # Print issues
    if issues:
        print("\n" + "=" * 70)
        print("VALIDATION ISSUES")
        print("=" * 70)
        
        for issue in issues:
            icon = {'error': '❌', 'warning': '⚠️ ', 'info': 'ℹ️ '}[issue.severity]
            print(f"\n{icon} [{issue.severity.upper()}] {issue.category}")
            print(f"   {issue.message}")
            if issue.file_path:
                print(f"   File: {issue.file_path}")
    
    # Generate fresh context if valid or --fix
    if is_valid or args.fix:
        context = validator.generate_live_context()
        validator.save_live_context(context)
    
    return 0 if is_valid else 1


if __name__ == '__main__':
    sys.exit(main())

