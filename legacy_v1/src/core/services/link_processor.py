"""
Link processing service for converting URLs to Telegram buttons.

This service handles the detection, parsing, and transformation of links
in AI responses according to bot configuration rules.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional, NamedTuple
from urllib.parse import urlparse
from dataclasses import dataclass

from ..domain.link_transformation import LinkTransformationConfig, LinkTransformationRule

logger = logging.getLogger(__name__)


class DetectedLink(NamedTuple):
    """Detected link with metadata."""
    url: str
    start_pos: int
    end_pos: int
    original_text: str


@dataclass
class ProcessedMessage:
    """Result of message processing."""
    text: str  # Modified text with links removed/replaced
    buttons: List[Dict[str, str]]  # List of button data
    has_transformations: bool  # Whether any links were transformed
    original_text: str  # Original message text
    detected_links: List[DetectedLink]  # All detected links


class LinkProcessor:
    """Service for processing links in messages."""
    
    # Enhanced URL regex pattern
    URL_PATTERN = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    def __init__(self):
        """Initialize the link processor."""
        pass
    
    def process_message(
        self, 
        message_text: str, 
        config: LinkTransformationConfig
    ) -> ProcessedMessage:
        """
        Process message text and transform matching links to buttons.
        
        Args:
            message_text: Original message text
            config: Link transformation configuration
            
        Returns:
            ProcessedMessage with transformed text and button data
        """
        logger.debug(f"Processing message with {len(message_text)} characters")
        
        if not config.enabled or not message_text.strip():
            return ProcessedMessage(
                text=message_text,
                buttons=[],
                has_transformations=False,
                original_text=message_text,
                detected_links=[]
            )
        
        # Detect all links in the message
        detected_links = self._detect_links(message_text)
        logger.debug(f"Detected {len(detected_links)} links")
        
        if not detected_links:
            return ProcessedMessage(
                text=message_text,
                buttons=[],
                has_transformations=False,
                original_text=message_text,
                detected_links=[]
            )
        
        # Get active transformation rules
        active_rules = config.get_active_rules()
        if not active_rules:
            logger.debug("No active transformation rules")
            return ProcessedMessage(
                text=message_text,
                buttons=[],
                has_transformations=False,
                original_text=message_text,
                detected_links=detected_links
            )
        
        # Process each link and create transformations
        transformations = []
        buttons = []
        
        for link in detected_links:
            transformation = self._find_matching_rule(link.url, active_rules)
            if transformation:
                transformations.append((link, transformation))
                
                # Create button data
                button_data = self._create_button_data(link.url, transformation)
                buttons.append(button_data)
                
                # Respect max buttons limit
                if len(buttons) >= config.max_buttons_per_message:
                    logger.debug(f"Reached max buttons limit: {config.max_buttons_per_message}")
                    break
        
        # Transform the message text
        transformed_text = self._transform_message_text(
            message_text, 
            transformations, 
            config.preserve_message_formatting
        )
        
        logger.info(f"Transformed {len(transformations)} links into buttons")
        
        return ProcessedMessage(
            text=transformed_text,
            buttons=buttons,
            has_transformations=len(transformations) > 0,
            original_text=message_text,
            detected_links=detected_links
        )
    
    def _detect_links(self, text: str) -> List[DetectedLink]:
        """Detect all URLs in the text."""
        links = []
        
        for match in self.URL_PATTERN.finditer(text):
            url = match.group()
            start_pos = match.start()
            end_pos = match.end()
            
            # Validate URL
            if self._is_valid_url(url):
                links.append(DetectedLink(
                    url=url,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    original_text=text[start_pos:end_pos]
                ))
        
        return links
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate if the URL is properly formatted."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _find_matching_rule(
        self, 
        url: str, 
        rules: List[LinkTransformationRule]
    ) -> Optional[LinkTransformationRule]:
        """Find the first matching rule for the URL."""
        for rule in rules:
            try:
                if rule.matches_url(url):
                    logger.debug(f"URL '{url}' matched rule '{rule.name}'")
                    return rule
            except Exception as e:
                logger.warning(f"Error checking rule '{rule.name}' against URL '{url}': {e}")
                continue
        
        return None
    
    def _create_button_data(
        self, 
        url: str, 
        rule: LinkTransformationRule
    ) -> Dict[str, str]:
        """Create button data for Telegram inline keyboard."""
        button_text = rule.button_text
        
        # Add emoji if specified and not already in text
        if rule.button_emoji and rule.button_emoji not in button_text:
            button_text = f"{rule.button_emoji} {button_text.strip()}"
        
        return {
            "text": button_text,
            "url": url,
            "rule_id": rule.id,
            "rule_name": rule.name
        }
    
    def _transform_message_text(
        self,
        original_text: str,
        transformations: List[Tuple[DetectedLink, LinkTransformationRule]],
        preserve_formatting: bool
    ) -> str:
        """Transform message text by removing/replacing links."""
        if not transformations:
            return original_text
        
        # Sort transformations by position (reverse order to preserve indices)
        transformations.sort(key=lambda x: x[0].start_pos, reverse=True)
        
        transformed_text = original_text
        
        for link, rule in transformations:
            if rule.remove_original_link:
                # Remove the link from text
                before = transformed_text[:link.start_pos]
                after = transformed_text[link.end_pos:]
                
                # Add preview text if configured
                replacement = ""
                if rule.add_preview_text and rule.preview_text:
                    replacement = rule.preview_text
                
                transformed_text = before + replacement + after
            
            elif rule.add_preview_text and rule.preview_text:
                # Replace link with preview text but keep the link
                before = transformed_text[:link.start_pos]
                after = transformed_text[link.end_pos:]
                
                replacement = f"{rule.preview_text} {link.url}"
                transformed_text = before + replacement + after
        
        # Clean up extra whitespace if formatting should be preserved
        if preserve_formatting:
            # Remove multiple consecutive spaces but preserve line breaks
            transformed_text = re.sub(r' {2,}', ' ', transformed_text)
            # Remove trailing spaces on lines
            transformed_text = '\n'.join(line.rstrip() for line in transformed_text.split('\n'))
        
        return transformed_text.strip()
    
    def create_telegram_keyboard(
        self, 
        buttons: List[Dict[str, str]], 
        layout: str = "vertical"
    ) -> List[List[Dict[str, str]]]:
        """
        Create Telegram inline keyboard markup from button data.
        
        Args:
            buttons: List of button data dictionaries
            layout: Layout style - "vertical", "horizontal", or "auto"
            
        Returns:
            Telegram inline keyboard markup structure
        """
        if not buttons:
            return []
        
        if layout == "horizontal":
            # All buttons in one row (if they fit)
            return [buttons] if len(buttons) <= 3 else [buttons[i:i+3] for i in range(0, len(buttons), 3)]
        
        elif layout == "vertical":
            # One button per row
            return [[button] for button in buttons]
        
        else:  # auto layout
            # Smart layout based on button count and text length
            if len(buttons) == 1:
                return [[buttons[0]]]
            elif len(buttons) == 2:
                # Check if texts are short enough for horizontal layout
                if all(len(btn["text"]) <= 20 for btn in buttons):
                    return [buttons]
                else:
                    return [[btn] for btn in buttons]
            else:
                # For 3+ buttons, use vertical or 2-column layout
                if len(buttons) <= 4:
                    return [[btn] for btn in buttons]
                else:
                    # 2-column layout for many buttons
                    keyboard = []
                    for i in range(0, len(buttons), 2):
                        row = buttons[i:i+2]
                        keyboard.append(row)
                    return keyboard
    
    def validate_transformation_rules(
        self, 
        rules: List[LinkTransformationRule]
    ) -> List[str]:
        """Validate a list of transformation rules."""
        errors = []
        
        # Validate individual rules
        for i, rule in enumerate(rules):
            rule_errors = rule.validate()
            for error in rule_errors:
                errors.append(f"Rule {i+1} ({rule.name}): {error}")
        
        # Check for duplicate IDs
        rule_ids = [rule.id for rule in rules if rule.id]
        duplicate_ids = set([rid for rid in rule_ids if rule_ids.count(rid) > 1])
        for dup_id in duplicate_ids:
            errors.append(f"Duplicate rule ID found: {dup_id}")
        
        # Check for conflicting rules (same match criteria)
        for i, rule1 in enumerate(rules):
            for j, rule2 in enumerate(rules[i+1:], i+1):
                if (rule1.match_type == rule2.match_type and 
                    rule1.match_value.lower() == rule2.match_value.lower()):
                    errors.append(f"Conflicting rules found: '{rule1.name}' and '{rule2.name}' have same match criteria")
        
        return errors
