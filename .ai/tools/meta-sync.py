#!/usr/bin/env python3
"""
Auto-generate and sync .meta files

Автоматически генерирует и синхронизирует мета-информацию:
- Парсит Python файлы (AST)
- Находит where используется (grep)
- Генерирует .meta/*.md файлы
- Проверяет актуальность

Usage:
    # Сгенерировать meta для файла
    python3 .ai/tools/meta-sync.py generate core/domain/user_session.py
    
    # Проверить актуальность всех meta
    python3 .ai/tools/meta-sync.py check
    
    # Обновить устаревшие meta
    python3 .ai/tools/meta-sync.py sync
    
    # Авто-генерация для всех критичных файлов
    python3 .ai/tools/meta-sync.py auto
"""

import ast
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Optional
from dataclasses import dataclass

# Критичные файлы для авто-генерации
CRITICAL_FILES = [
    "core/domain/bot.py",
    "core/domain/user_session.py",
    "core/domain/conversation.py",
    "core/services/user_session_service.py",
    "core/usecases/user_session_management.py",
    "core/usecases/bot_management.py",
    "adapters/storage/json_adapter.py",
    "src/app.py",
    "src/config_manager.py",
    "src/telegram_bot.py",
    "start.py",
]

@dataclass
class FileInfo:
    """Информация о файле"""
    path: Path
    type: str  # module, class, function
    layer: str  # domain, usecase, adapter, etc
    classes: List[str]
    functions: List[str]
    imports: List[str]
    used_by: List[str]
    criticality: str  # low, medium, high, critical

class MetaGenerator:
    """Генератор мета-информации"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def parse_file(self, file_path: Path) -> FileInfo:
        """Парсит Python файл и извлекает информацию"""
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):  # Skip private
                    functions.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif node.module:
                    imports.append(node.module)
        
        # Определяем слой архитектуры
        path_str = str(file_path)
        if 'core/domain' in path_str:
            layer = 'domain'
        elif 'core/usecases' in path_str:
            layer = 'usecase'
        elif 'core/services' in path_str:
            layer = 'service'
        elif 'adapters' in path_str:
            layer = 'adapter'
        elif 'src/api' in path_str:
            layer = 'api'
        else:
            layer = 'application'
        
        # Находим где файл используется
        used_by = self.find_usage(file_path)
        
        # Определяем критичность
        criticality = self.determine_criticality(file_path, used_by)
        
        return FileInfo(
            path=file_path,
            type='module',
            layer=layer,
            classes=classes,
            functions=functions,
            imports=imports,
            used_by=used_by,
            criticality=criticality
        )
    
    def find_usage(self, file_path: Path) -> List[str]:
        """Находит где файл используется через grep"""
        # Получаем имя модуля для поиска
        rel_path = file_path.relative_to(self.project_root)
        module_name = str(rel_path).replace('/', '.').replace('.py', '')
        
        used_by = []
        try:
            # Ищем импорты этого модуля
            result = subprocess.run(
                ['grep', '-r', f'from {module_name}', '.', 
                 '--include=*.py', '--exclude-dir=venv', '--exclude-dir=.git'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            
            for line in result.stdout.splitlines():
                if ':' in line:
                    file = line.split(':')[0].strip('./')
                    if file != str(rel_path) and file not in used_by:
                        used_by.append(file)
        except subprocess.TimeoutExpired:
            pass
        
        return used_by[:10]  # Ограничиваем топ-10
    
    def determine_criticality(self, file_path: Path, used_by: List[str]) -> str:
        """Определяет критичность файла"""
        path_str = str(file_path)
        
        # Критичные по умолчанию
        if any(p in path_str for p in ['app.py', 'config_manager.py', 'start.py']):
            return 'critical'
        
        # По слоям
        if 'core/domain' in path_str:
            return 'high' if len(used_by) > 3 else 'medium'
        elif 'core/usecases' in path_str:
            return 'high'
        elif 'adapters/storage' in path_str:
            return 'high'
        
        # По количеству использований
        if len(used_by) > 5:
            return 'high'
        elif len(used_by) > 2:
            return 'medium'
        
        return 'low'
    
    def generate_meta(self, file_info: FileInfo) -> str:
        """Генерирует содержимое .meta файла"""
        rel_path = file_info.path.relative_to(self.project_root)
        
        meta = f"""# Meta-файл для {rel_path.name}

**Auto-generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**File:** {rel_path}  
**Layer:** {file_info.layer}  
**Criticality:** {file_info.criticality.upper()}

---

## 📋 Обзор

"""
        
        # Добавляем классы
        if file_info.classes:
            meta += "### Классы\n\n"
            for cls in file_info.classes:
                meta += f"- **`{cls}`**\n"
            meta += "\n"
        
        # Добавляем функции
        if file_info.functions:
            meta += "### Публичные функции\n\n"
            for func in file_info.functions[:10]:  # Топ-10
                meta += f"- `{func}()`\n"
            meta += "\n"
        
        # Зависимости
        if file_info.imports:
            meta += "## 🔗 Зависимости\n\n"
            meta += "### Импорты\n"
            for imp in file_info.imports[:15]:  # Топ-15
                meta += f"- `{imp}`\n"
            meta += "\n"
        
        # Где используется
        if file_info.used_by:
            meta += "### Используется в\n\n"
            for usage in file_info.used_by:
                meta += f"- `{usage}`\n"
            meta += "\n"
        
        # Warnings по критичности
        if file_info.criticality in ['high', 'critical']:
            meta += "## ⚠️ Warnings\n\n"
            if file_info.criticality == 'critical':
                meta += "- **CRITICAL FILE** - изменения влияют на весь проект!\n"
                meta += "- Тщательно тестируй перед коммитом\n"
            else:
                meta += f"- **HIGH criticality** - используется в {len(file_info.used_by)} местах\n"
            meta += "\n"
        
        # Hints
        meta += "## 💡 Hints\n\n"
        if file_info.layer == 'domain':
            meta += "- Domain layer - NO external dependencies!\n"
            meta += "- Pure business logic only\n"
        elif file_info.layer == 'usecase':
            meta += "- Use case layer - orchestrates domain logic\n"
            meta += "- Uses ports for external communication\n"
        elif file_info.layer == 'adapter':
            meta += "- Adapter layer - implements ports\n"
            meta += "- Handles external systems\n"
        
        meta += f"- См. тесты: `tests/unit/test_{rel_path.stem}.py`\n"
        meta += f"- Architecture: `docs/ARCHITECTURE_BRIEF.md`\n"
        
        meta += "\n---\n"
        meta += "\n*Этот файл автоматически сгенерирован. Не редактируй вручную!*\n"
        meta += "*Обнови: `python3 .ai/tools/meta-sync.py generate {rel_path}`*\n"
        
        return meta
    
    def save_meta(self, file_path: Path, content: str) -> Path:
        """Сохраняет meta-файл"""
        # Определяем путь к meta-файлу
        rel_path = file_path.relative_to(self.project_root)
        meta_dir = self.project_root / '.meta' / rel_path.parent
        meta_file = meta_dir / f"{rel_path.stem}.md"
        
        # Создаем директорию если нужно
        meta_dir.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем
        with open(meta_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return meta_file
    
    def check_outdated(self) -> List[tuple]:
        """Проверяет устаревшие meta-файлы"""
        outdated = []
        
        meta_root = self.project_root / '.meta'
        if not meta_root.exists():
            return outdated
        
        for meta_file in meta_root.rglob('*.md'):
            if meta_file.name == 'INDEX.md':
                continue
            
            # Находим соответствующий Python файл
            rel_meta = meta_file.relative_to(meta_root)
            py_file = self.project_root / rel_meta.parent / f"{meta_file.stem}.py"
            
            if not py_file.exists():
                continue
            
            # Сравниваем даты изменения
            meta_mtime = meta_file.stat().st_mtime
            py_mtime = py_file.stat().st_mtime
            
            if py_mtime > meta_mtime:
                age = (py_mtime - meta_mtime) / 3600  # в часах
                outdated.append((py_file, meta_file, age))
        
        return outdated
    
    def update_index(self):
        """Обновляет .meta/INDEX.md"""
        index_path = self.project_root / '.meta' / 'INDEX.md'
        
        # Собираем все meta-файлы
        meta_files = []
        for meta_file in (self.project_root / '.meta').rglob('*.md'):
            if meta_file.name != 'INDEX.md':
                rel_path = meta_file.relative_to(self.project_root / '.meta')
                meta_files.append(str(rel_path))
        
        meta_files.sort()
        
        # Генерируем index
        content = f"""# Meta Index - Auto-generated

**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Total files:** {len(meta_files)}

---

## 📁 All Meta Files

"""
        
        # Группируем по директориям
        by_dir = {}
        for meta_file in meta_files:
            dir_name = str(Path(meta_file).parent)
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append(meta_file)
        
        for dir_name in sorted(by_dir.keys()):
            content += f"\n### {dir_name}/\n\n"
            for meta_file in by_dir[dir_name]:
                py_file = meta_file.replace('.md', '.py')
                content += f"- [`{Path(meta_file).name}`](./{meta_file}) → `{py_file}`\n"
        
        content += "\n---\n\n"
        content += "*Auto-generated by meta-sync.py*\n"
        content += f"*Update: `python3 .ai/tools/meta-sync.py sync`*\n"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Index updated: {len(meta_files)} files")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-sync .meta files")
    parser.add_argument('command', choices=['generate', 'check', 'sync', 'auto'],
                       help="Command to run")
    parser.add_argument('file', nargs='?', help="File to generate meta for")
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent.parent
    generator = MetaGenerator(project_root)
    
    if args.command == 'generate':
        if not args.file:
            print("❌ Error: file argument required for 'generate'")
            return 1
        
        file_path = project_root / args.file
        if not file_path.exists():
            print(f"❌ Error: file not found: {args.file}")
            return 1
        
        print(f"📝 Generating meta for {args.file}...")
        file_info = generator.parse_file(file_path)
        meta_content = generator.generate_meta(file_info)
        meta_path = generator.save_meta(file_path, meta_content)
        print(f"✅ Generated: {meta_path}")
        
        generator.update_index()
        
    elif args.command == 'check':
        print("🔍 Checking for outdated meta files...")
        outdated = generator.check_outdated()
        
        if not outdated:
            print("✅ All meta files are up-to-date!")
        else:
            print(f"\n⚠️  Found {len(outdated)} outdated meta files:\n")
            for py_file, meta_file, age in outdated:
                print(f"  - {py_file.name} (outdated by {age:.1f}h)")
            print(f"\nRun: python3 .ai/tools/meta-sync.py sync")
        
    elif args.command == 'sync':
        print("🔄 Syncing all meta files...")
        outdated = generator.check_outdated()
        
        for py_file, meta_file, age in outdated:
            print(f"  Updating {py_file.name}...")
            file_info = generator.parse_file(py_file)
            meta_content = generator.generate_meta(file_info)
            generator.save_meta(py_file, meta_content)
        
        generator.update_index()
        print(f"✅ Synced {len(outdated)} files")
        
    elif args.command == 'auto':
        print("🤖 Auto-generating meta for critical files...")
        generated = 0
        
        for file_path in CRITICAL_FILES:
            full_path = project_root / file_path
            if full_path.exists():
                print(f"  Processing {file_path}...")
                file_info = generator.parse_file(full_path)
                meta_content = generator.generate_meta(file_info)
                generator.save_meta(full_path, meta_content)
                generated += 1
        
        generator.update_index()
        print(f"✅ Generated {generated} meta files")
    
    return 0

if __name__ == "__main__":
    exit(main())

