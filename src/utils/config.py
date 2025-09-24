"""
Configuration classes for the watermark application
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class WatermarkConfig:
    """Configuration for watermark processing"""

    font_size: int = 36
    color: str = "white"
    position: str = "bottom-right"  # top-left, top-right, bottom-left, bottom-right, center
    output_quality: int = 95

    def __post_init__(self):
        """Validate configuration values"""
        if self.font_size <= 0:
            raise ValueError("Font size must be positive")

        if self.output_quality < 1 or self.output_quality > 100:
            raise ValueError("Output quality must be between 1 and 100")

        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        if self.position not in valid_positions:
            raise ValueError(f"Position must be one of: {valid_positions}")

    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            "font_size": self.font_size,
            "color": self.color,
            "position": self.position,
            "output_quality": self.output_quality
        }

    @classmethod
    def from_dict(cls, config_dict: dict) -> "WatermarkConfig":
        """Create configuration from dictionary"""
        return cls(**config_dict)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "WatermarkConfig":
        """
        Create configuration from YAML file

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            WatermarkConfig instance
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
                return cls.from_dict(config_dict)
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {yaml_path}: {e}")

    def save_to_yaml(self, yaml_path: Path) -> None:
        """
        Save configuration to YAML file

        Args:
            yaml_path: Path to save YAML configuration file
        """
        try:
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
        except Exception as e:
            raise ValueError(f"Failed to save configuration to {yaml_path}: {e}")