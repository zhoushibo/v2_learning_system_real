"""
Plugin Metadata Definition
==========================

Defines metadata schema for plugins using Pydantic.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class Permission(str, Enum):
    """Plugin permissions"""
    READ = "read"       # Read files
    WRITE = "write"     # Write files
    EXEC = "exec"       # Execute commands
    NETWORK = "network" # Network access
    ALL = "all"         # All permissions


class ParameterSchema(BaseModel):
    """Parameter schema for a plugin tool"""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (string, int, float, bool, list, dict)")
    required: bool = Field(default=True, description="Whether parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value")
    description: Optional[str] = Field(default=None, description="Parameter description")


class ToolMetadata(BaseModel):
    """Metadata for a single tool in a plugin"""
    name: str = Field(..., description="Tool name (unique)")
    description: str = Field(..., description="Tool description")
    entry_point: str = Field(..., description="Entry point (module:Class)")
    parameters: List[ParameterSchema] = Field(default_factory=list, description="Parameter schemas")
    permissions: List[Permission] = Field(default_factory=list, description="Required permissions")
    category: Optional[str] = Field(default=None, description="Tool category")


class PluginMetadata(BaseModel):
    """Complete plugin metadata"""
    name: str = Field(..., description="Plugin name (unique)")
    version: str = Field(..., description="Plugin version (semver)")
    description: str = Field(..., description="Plugin description")
    author: Optional[str] = Field(default=None, description="Plugin author")
    entry_point: str = Field(..., description="Main entry point (module:PluginClass)")
    tools: List[ToolMetadata] = Field(default_factory=list, description="Tools provided by plugin")
    permissions: List[Permission] = Field(default_factory=list, description="Plugin-wide permissions")
    dependencies: Optional[List[str]] = Field(default_factory=list, description="Python dependencies")

    @validator('version')
    def validate_version(cls, v):
        """Validate semver version"""
        parts = v.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid semver version: {v}")
        return v

    @validator('entry_point')
    def validate_entry_point(cls, v):
        """Validate entry point format"""
        if ':' not in v:
            raise ValueError(f"Invalid entry point format: {v} (expected 'module:Class')")
        return v


# Example metadata
EXAMPLE_PLUGIN_METADATA = {
    "name": "example_plugin",
    "version": "1.0.0",
    "description": "Example plugin for demonstration",
    "author": "Claw",
    "entry_point": "example_plugin:ExamplePlugin",
    "tools": [
        {
            "name": "hello_world",
            "description": "Say hello to the world",
            "entry_point": "example_plugin:HelloWorldTool",
            "parameters": [
                {
                    "name": "name",
                    "type": "string",
                    "required": False,
                    "default": "World",
                    "description": "Name to greet"
                }
            ],
            "permissions": [],
            "category": "example"
        }
    ],
    "permissions": ["read"],
    "dependencies": []
}
