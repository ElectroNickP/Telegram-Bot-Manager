"""
Link-to-Button transformation domain entities.

This module contains domain objects for converting links in AI responses 
to Telegram inline buttons based on configurable rules.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re
from enum import Enum


class LinkMatchType(Enum):
    """Types of link matching patterns."""
    DOMAIN = "domain"          # Matches by domain (e.g., script.google.com)
    URL_CONTAINS = "url_contains"  # URL contains specific text
    URL_REGEX = "url_regex"    # Regex pattern matching
    FULL_URL = "full_url"      # Exact URL match
    MARKDOWN_LINK = "markdown_link"  # Matches Markdown-formatted links [text](url)


@dataclass
class LinkTransformationRule:
    """Single rule for transforming links to buttons."""
    
    # Rule identification
    id: str
    name: str
    enabled: bool = True
    
    # Matching criteria
    match_type: LinkMatchType = LinkMatchType.DOMAIN
    match_value: str = ""  # Domain, text, or regex pattern
    case_sensitive: bool = False
    
    # Button configuration
    button_text: str = "🔗 Открыть ссылку"
    button_emoji: str = "🔗"
    
    # Advanced options
    remove_original_link: bool = True  # Remove link from text
    add_preview_text: bool = False     # Add preview before button
    preview_text: str = ""
    
    # Priority for multiple matches (higher = first)
    priority: int = 0
    
    def matches_url(self, url: str) -> bool:
        """Check if URL matches this rule."""
        if not self.enabled:
            return False
            
        search_value = self.match_value if self.case_sensitive else self.match_value.lower()
        search_url = url if self.case_sensitive else url.lower()
        
        try:
            if self.match_type == LinkMatchType.DOMAIN:
                # Extract domain from URL and match
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                return search_value in domain or domain.endswith(search_value)
                
            elif self.match_type == LinkMatchType.URL_CONTAINS:
                return search_value in search_url
                
            elif self.match_type == LinkMatchType.URL_REGEX:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                return bool(re.search(self.match_value, url, flags))
                
            elif self.match_type == LinkMatchType.FULL_URL:
                return search_url == search_value
                
        except Exception:
            # If anything fails, don't match
            return False
            
        return False
    
    def validate(self) -> List[str]:
        """Validate rule configuration."""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Rule name is required")
            
        if not self.match_value or not self.match_value.strip():
            errors.append("Match value is required")
            
        if not self.button_text or not self.button_text.strip():
            errors.append("Button text is required")
            
        # Validate regex if used
        if self.match_type == LinkMatchType.URL_REGEX:
            try:
                re.compile(self.match_value)
            except re.error:
                errors.append("Invalid regex pattern")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "match_type": self.match_type.value,
            "match_value": self.match_value,
            "case_sensitive": self.case_sensitive,
            "button_text": self.button_text,
            "button_emoji": self.button_emoji,
            "remove_original_link": self.remove_original_link,
            "add_preview_text": self.add_preview_text,
            "preview_text": self.preview_text,
            "priority": self.priority,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LinkTransformationRule":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            enabled=data.get("enabled", True),
            match_type=LinkMatchType(data.get("match_type", "domain")),
            match_value=data.get("match_value", ""),
            case_sensitive=data.get("case_sensitive", False),
            button_text=data.get("button_text", "🔗 Открыть ссылку"),
            button_emoji=data.get("button_emoji", "🔗"),
            remove_original_link=data.get("remove_original_link", True),
            add_preview_text=data.get("add_preview_text", False),
            preview_text=data.get("preview_text", ""),
            priority=data.get("priority", 0),
        )


@dataclass 
class LinkTransformationConfig:
    """Configuration for link-to-button transformation feature."""
    
    # Feature toggle
    enabled: bool = False
    
    # Global settings
    max_buttons_per_message: int = 5
    button_layout: str = "vertical"  # "vertical", "horizontal", "auto"
    
    # Processing options
    process_ai_responses: bool = True
    process_user_messages: bool = False
    preserve_message_formatting: bool = True
    
    # Rules for transformation
    transformation_rules: List[LinkTransformationRule] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Validate configuration."""
        errors = []
        
        if self.max_buttons_per_message < 1 or self.max_buttons_per_message > 10:
            errors.append("Max buttons per message must be between 1 and 10")
            
        if self.button_layout not in ["vertical", "horizontal", "auto"]:
            errors.append("Invalid button layout")
            
        # Validate all rules
        for rule in self.transformation_rules:
            rule_errors = rule.validate()
            for error in rule_errors:
                errors.append(f"Rule '{rule.name}': {error}")
                
        # Check for duplicate rule IDs
        rule_ids = [rule.id for rule in self.transformation_rules]
        if len(rule_ids) != len(set(rule_ids)):
            errors.append("Duplicate rule IDs found")
            
        return errors
    
    def get_active_rules(self) -> List[LinkTransformationRule]:
        """Get enabled rules sorted by priority."""
        active_rules = [rule for rule in self.transformation_rules if rule.enabled]
        return sorted(active_rules, key=lambda r: r.priority, reverse=True)
    
    def add_rule(self, rule: LinkTransformationRule) -> None:
        """Add new transformation rule."""
        self.transformation_rules.append(rule)
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove rule by ID."""
        original_length = len(self.transformation_rules)
        self.transformation_rules = [r for r in self.transformation_rules if r.id != rule_id]
        return len(self.transformation_rules) < original_length
    
    def update_rule(self, rule_id: str, updated_rule: LinkTransformationRule) -> bool:
        """Update existing rule."""
        for i, rule in enumerate(self.transformation_rules):
            if rule.id == rule_id:
                self.transformation_rules[i] = updated_rule
                return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[LinkTransformationRule]:
        """Get rule by ID."""
        for rule in self.transformation_rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "enabled": self.enabled,
            "max_buttons_per_message": self.max_buttons_per_message,
            "button_layout": self.button_layout,
            "process_ai_responses": self.process_ai_responses,
            "process_user_messages": self.process_user_messages,
            "preserve_message_formatting": self.preserve_message_formatting,
            "transformation_rules": [rule.to_dict() for rule in self.transformation_rules],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LinkTransformationConfig":
        """Create from dictionary."""
        rules = []
        for rule_data in data.get("transformation_rules", []):
            rules.append(LinkTransformationRule.from_dict(rule_data))
            
        return cls(
            enabled=data.get("enabled", False),
            max_buttons_per_message=data.get("max_buttons_per_message", 5),
            button_layout=data.get("button_layout", "vertical"),
            process_ai_responses=data.get("process_ai_responses", True),
            process_user_messages=data.get("process_user_messages", False),
            preserve_message_formatting=data.get("preserve_message_formatting", True),
            transformation_rules=rules,
        )


# Convenience function to create common rule templates
def create_google_script_rule(button_text: str = "📊 Открыть Google Script") -> LinkTransformationRule:
    """Create rule for Google Scripts links."""
    return LinkTransformationRule(
        id="google_script",
        name="Google Apps Script",
        match_type=LinkMatchType.DOMAIN,
        match_value="script.google.com",
        button_text=button_text,
        button_emoji="📊",
        priority=100
    )


def create_google_sheets_rule(button_text: str = "📋 Открыть Google Sheets") -> LinkTransformationRule:
    """Create rule for Google Sheets links.""" 
    return LinkTransformationRule(
        id="google_sheets",
        name="Google Sheets",
        match_type=LinkMatchType.DOMAIN,
        match_value="docs.google.com/spreadsheets",
        button_text=button_text,
        button_emoji="📋",
        priority=90
    )


def create_github_rule(button_text: str = "💻 Открыть GitHub") -> LinkTransformationRule:
    """Create rule for GitHub links."""
    return LinkTransformationRule(
        id="github",
        name="GitHub Repository", 
        match_type=LinkMatchType.DOMAIN,
        match_value="github.com",
        button_text=button_text,
        button_emoji="💻",
        priority=80
    )


def create_markdown_links_rule(button_text: str = "🔗 Открыть ссылку") -> LinkTransformationRule:
    """Create rule for all Markdown formatted links [text](url)."""
    return LinkTransformationRule(
        id="markdown_all",
        name="Все Markdown ссылки",
        match_type=LinkMatchType.MARKDOWN_LINK,
        match_value="",  # Empty means match all Markdown links
        button_text=button_text,  # Fallback text if Markdown text is empty
        button_emoji="🔗",
        remove_original_link=True,
        priority=1  # Lower priority so specific rules can override
    )


