"""
Link Transformation Use Cases.

This module contains business logic for processing and transforming links 
in messages according to configured rules.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import urlparse
from dataclasses import dataclass

try:
    from src.core.domain.link_transformation import (
        LinkTransformationConfig,
        LinkTransformationRule,
        LinkMatchType
    )
except ImportError:
    # Fallback for when running standalone
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.core.domain.link_transformation import (
        LinkTransformationConfig,
        LinkTransformationRule,
        LinkMatchType
    )

logger = logging.getLogger(__name__)


@dataclass
class TransformationResult:
    """Result of link transformation operation."""
    original_text: str
    processed_text: str
    buttons: List[Dict[str, str]]  # [{"text": "button_text", "url": "url"}]
    transformations_count: int
    matched_rules: List[str]  # Rule names that matched
    
    
@dataclass
class LinkMatch:
    """Information about a matched link."""
    url: str
    full_match: str  # The full text that was matched
    rule: LinkTransformationRule
    button_text: str
    start_pos: int
    end_pos: int


class LinkTransformationService:
    """Service for transforming links to buttons in messages."""
    
    def __init__(self):
        """Initialize the service."""
        self.logger = logging.getLogger(__name__)
        
    def process_message(self, text: str, config: LinkTransformationConfig) -> TransformationResult:
        """
        Process a message and transform links according to configuration.
        
        Args:
            text: The message text to process
            config: Transformation configuration
            
        Returns:
            TransformationResult with processed text and buttons
        """
        if not config.enabled or not text:
            return TransformationResult(
                original_text=text,
                processed_text=text,
                buttons=[],
                transformations_count=0,
                matched_rules=[]
            )
            
        try:
            # Get active rules sorted by priority
            active_rules = config.get_active_rules()
            if not active_rules:
                return TransformationResult(
                    original_text=text,
                    processed_text=text,
                    buttons=[],
                    transformations_count=0,
                    matched_rules=[]
                )
            
            # Find all matches
            matches = self._find_matches(text, active_rules)
            
            # Limit matches per message
            matches = matches[:config.max_buttons_per_message]
            
            # Process matches and create result
            processed_text = text
            buttons = []
            matched_rules = []
            
            # Sort matches by position (descending) to process from end to start
            # This prevents position shifts when removing text
            matches.sort(key=lambda m: m.start_pos, reverse=True)
            
            for match in matches:
                # Create button
                button = {
                    "text": match.button_text,
                    "url": match.url
                }
                buttons.append(button)
                matched_rules.append(match.rule.name)
                
                # Remove original link from text if configured
                if match.rule.remove_original_link:
                    # Replace with preview text if configured
                    replacement = ""
                    if match.rule.add_preview_text and match.rule.preview_text:
                        replacement = self._format_preview_text(match.rule.preview_text, match.url)
                    
                    processed_text = (
                        processed_text[:match.start_pos] + 
                        replacement + 
                        processed_text[match.end_pos:]
                    )
            
            # Reverse buttons to maintain original order
            buttons.reverse()
            matched_rules.reverse()
            
            # Clean up text (remove extra spaces)
            processed_text = re.sub(r'\s+', ' ', processed_text).strip()
            
            return TransformationResult(
                original_text=text,
                processed_text=processed_text,
                buttons=buttons,
                transformations_count=len(matches),
                matched_rules=list(set(matched_rules))  # Remove duplicates
            )
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            # Return original text on error
            return TransformationResult(
                original_text=text,
                processed_text=text,
                buttons=[],
                transformations_count=0,
                matched_rules=[]
            )
    
    def _find_matches(self, text: str, rules: List[LinkTransformationRule]) -> List[LinkMatch]:
        """Find all matching links in text."""
        matches = []
        
        for rule in rules:
            try:
                rule_matches = self._find_rule_matches(text, rule)
                matches.extend(rule_matches)
            except Exception as e:
                self.logger.warning(f"Error processing rule '{rule.name}': {e}")
                continue
        
        # Remove overlapping matches (keep higher priority)
        matches = self._remove_overlapping_matches(matches)
        
        return matches
    
    def _find_rule_matches(self, text: str, rule: LinkTransformationRule) -> List[LinkMatch]:
        """Find matches for a specific rule."""
        matches = []
        
        if rule.match_type == LinkMatchType.MARKDOWN_LINK:
            # Handle Markdown links [text](url)
            matches = self._find_markdown_matches(text, rule)
        else:
            # Handle regular URL patterns
            matches = self._find_url_matches(text, rule)
            
        return matches
    
    def _find_markdown_matches(self, text: str, rule: LinkTransformationRule) -> List[LinkMatch]:
        """Find Markdown format links [text](url)."""
        matches = []
        
        # Regex for Markdown links: [text](url)
        markdown_pattern = r'\[([^\[\]]*?)\]\(([^)]+)\)'
        
        for match in re.finditer(markdown_pattern, text):
            link_text = match.group(1).strip()
            url = match.group(2).strip()
            full_match = match.group(0)
            
            # Use link text as button text, fallback to rule button text
            button_text = link_text if link_text else rule.button_text
            
            # Format button text with emoji if configured
            if rule.button_emoji and not button_text.startswith(rule.button_emoji):
                button_text = f"{rule.button_emoji} {button_text}"
            
            matches.append(LinkMatch(
                url=url,
                full_match=full_match,
                rule=rule,
                button_text=button_text,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        return matches
    
    def _find_url_matches(self, text: str, rule: LinkTransformationRule) -> List[LinkMatch]:
        """Find URL matches based on rule criteria."""
        matches = []
        
        # Common URL pattern
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+[^\s<>"{}|\\^`[\].,;:!?)]'
        
        for match in re.finditer(url_pattern, text):
            url = match.group(0)
            
            # Check if URL matches rule criteria
            if rule.matches_url(url):
                # Format button text
                button_text = self._format_button_text(rule.button_text, url)
                if rule.button_emoji and not button_text.startswith(rule.button_emoji):
                    button_text = f"{rule.button_emoji} {button_text}"
                
                matches.append(LinkMatch(
                    url=url,
                    full_match=url,
                    rule=rule,
                    button_text=button_text,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
        
        return matches
    
    def _format_button_text(self, template: str, url: str) -> str:
        """Format button text with URL placeholders."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Replace placeholders
            formatted = template.replace('{url}', url)
            formatted = formatted.replace('{domain}', domain)
            
            return formatted
        except Exception:
            return template
    
    def _format_preview_text(self, template: str, url: str) -> str:
        """Format preview text with URL placeholders."""
        return self._format_button_text(template, url)
    
    def _remove_overlapping_matches(self, matches: List[LinkMatch]) -> List[LinkMatch]:
        """Remove overlapping matches, keeping higher priority ones."""
        if not matches:
            return matches
        
        # Sort by priority (descending) then by position
        matches.sort(key=lambda m: (-m.rule.priority, m.start_pos))
        
        non_overlapping = []
        
        for match in matches:
            # Check if this match overlaps with any accepted match
            overlaps = False
            for accepted in non_overlapping:
                if not (match.end_pos <= accepted.start_pos or match.start_pos >= accepted.end_pos):
                    overlaps = True
                    break
            
            if not overlaps:
                non_overlapping.append(match)
        
        return non_overlapping
    
    def test_rule(self, rule: LinkTransformationRule, url: str) -> bool:
        """Test if a rule matches a specific URL."""
        try:
            return rule.matches_url(url)
        except Exception as e:
            self.logger.error(f"Error testing rule '{rule.name}' against URL '{url}': {e}")
            return False
    
    def preview_transformation(self, text: str, config: LinkTransformationConfig) -> Dict[str, Any]:
        """
        Preview how text would be transformed without actually applying changes.
        
        Args:
            text: Text to preview
            config: Transformation configuration
            
        Returns:
            Dictionary with preview information
        """
        result = self.process_message(text, config)
        
        return {
            "original_text": result.original_text,
            "processed_text": result.processed_text,
            "buttons": result.buttons,
            "stats": {
                "transformations_count": result.transformations_count,
                "matched_rules": result.matched_rules,
                "buttons_created": len(result.buttons)
            }
        }
    
    def validate_configuration(self, config: LinkTransformationConfig) -> List[str]:
        """
        Validate transformation configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        return config.validate()
    
    def create_inline_keyboard(self, buttons: List[Dict[str, str]], layout: str = "vertical") -> List[List[Dict[str, str]]]:
        """
        Create Telegram inline keyboard markup from buttons.
        
        Args:
            buttons: List of button dictionaries with 'text' and 'url'
            layout: Layout style ('vertical', 'horizontal', 'auto')
            
        Returns:
            2D array suitable for Telegram inline keyboard
        """
        if not buttons:
            return []
        
        keyboard = []
        
        if layout == "horizontal":
            # All buttons in one row
            keyboard.append([
                {"text": btn["text"], "url": btn["url"]} 
                for btn in buttons
            ])
        elif layout == "auto":
            # 2 buttons per row
            for i in range(0, len(buttons), 2):
                row = []
                for j in range(i, min(i + 2, len(buttons))):
                    row.append({
                        "text": buttons[j]["text"], 
                        "url": buttons[j]["url"]
                    })
                keyboard.append(row)
        else:  # vertical (default)
            # One button per row
            for btn in buttons:
                keyboard.append([{
                    "text": btn["text"], 
                    "url": btn["url"]
                }])
        
        return keyboard


def create_simple_rule(domain: str, button_text: str, emoji: str = "🔗") -> LinkTransformationRule:
    """
    Convenience function to create a simple domain-based rule.
    
    Args:
        domain: Domain to match (e.g., "script.google.com")
        button_text: Text for the button
        emoji: Emoji for the button
        
    Returns:
        Configured LinkTransformationRule
    """
    import uuid
    
    return LinkTransformationRule(
        id=str(uuid.uuid4()),
        name=f"Rule for {domain}",
        match_type=LinkMatchType.DOMAIN,
        match_value=domain,
        button_text=button_text,
        button_emoji=emoji,
        enabled=True,
        remove_original_link=True,
        priority=50
    )


def create_quick_config_from_domains(domain_configs: List[Dict[str, str]]) -> LinkTransformationConfig:
    """
    Quick way to create configuration from list of domain configurations.
    
    Args:
        domain_configs: List of dicts with keys: domain, button_text, emoji (optional)
        
    Example:
        config = create_quick_config_from_domains([
            {"domain": "script.google.com", "button_text": "📊 Открыть Google Script"},
            {"domain": "github.com", "button_text": "💻 Открыть GitHub"}
        ])
    
    Returns:
        LinkTransformationConfig with rules for specified domains
    """
    config = LinkTransformationConfig(enabled=True)
    
    for domain_config in domain_configs:
        rule = create_simple_rule(
            domain=domain_config["domain"],
            button_text=domain_config["button_text"],
            emoji=domain_config.get("emoji", "🔗")
        )
        config.add_rule(rule)
    
    return config


# Example usage and testing
if __name__ == "__main__":
    # Create service
    service = LinkTransformationService()
    
    # Test with Google Scripts example
    config = create_quick_config_from_domains([
        {
            "domain": "script.google.com", 
            "button_text": "📊 Открыть Google Script",
            "emoji": "📊"
        }
    ])
    
    test_text = """
    Вот полезная ссылка для автоматизации: https://script.google.com/d/abc123/edit
    А также можно посмотреть документацию: https://developers.google.com/apps-script
    """
    
    result = service.process_message(test_text, config)
    
    print("Original:", result.original_text)
    print("Processed:", result.processed_text)
    print("Buttons:", result.buttons)
    print("Stats:", f"{result.transformations_count} transformations by rules: {result.matched_rules}")