"""
Plugin Runtime (Sandbox)
========================

Sandbox runtime for executing plugin tools with safety restrictions.
"""
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import traceback

from .plugin_metadata import Permission, ParameterSchema
from .plugin_registry import get_registry


class PermissionDeniedError(Exception):
    """Raised when a tool tries to perform a forbidden operation"""
    pass


class ToolExecutionContext:
    """Context for tool execution"""

    def __init__(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        self.tool_name = tool_name
        self.parameters = parameters
        self.user_id = user_id
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.error: Optional[str] = None
        self.result: Optional[Any] = None

    @property
    def duration_ms(self) -> float:
        """Get execution duration in milliseconds"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds() * 1000


class SandboxedRuntime:
    """
    Sandboxed runtime for executing plugin tools.

    Implements "soft sandbox" - not absolute isolation, but restricted environment.
    """

    # Safe functions to expose to plugins
    SAFE_BUILTINS = {
        'abs': abs,
        'all': all,
        'any': any,
        'bool': bool,
        'dict': dict,
        'enumerate': enumerate,
        'filter': filter,
        'float': float,
        'int': int,
        'len': len,
        'list': list,
        'map': map,
        'max': max,
        'min': min,
        'range': range,
        'round': round,
        'set': set,
        'sorted': sorted,
        'str': str,
        'sum': sum,
        'tuple': tuple,
        'zip': zip,
        'isinstance': isinstance,
        'issubclass': issubclass,
        'type': type,
        'print': print,  # Safe (no I/O restrictions)
    }

    # Dangerous functions to blacklist
    DANGEROUS_FUNCTIONS = [
        'open', 'exec', 'eval', 'compile', '__import__',
        'globals', 'locals', 'vars', 'dir',
        'getattr', 'setattr', 'delattr',
        'exit', 'quit'
    ]

    def __init__(self, allow_list: Optional[List[Permission]] = None):
        """
        Initialize sandboxed runtime.

        Args:
            allow_list: List of allowed permissions (None = all permissions allowed)
        """
        self.allow_list = allow_list or []

    def _create_sandbox_globals(self) -> Dict[str, Any]:
        """
        Create restricted globals dict for sandbox execution.

        Returns:
            Globals dict with safe builtins only
        """
        # Start with safe builtins
        sandbox_globals = {
            '__builtins__': self.SAFE_BUILTINS.copy(),
        }

        # Remove dangerous functions
        for func_name in self.DANGEROUS_FUNCTIONS:
            if func_name in sandbox_globals['__builtins__']:
                del sandbox_globals['__builtins__'][func_name]

        return sandbox_globals

    def _check_permission(
        self,
        tool_name: str,
        required_permission: Permission
    ) -> bool:
        """
        Check if tool has required permission.

        Args:
            tool_name: Tool name
            required_permission: Required permission

        Returns:
            True if permission granted, False otherwise
        """
        # If allow_list is empty, all permissions are allowed
        if not self.allow_list:
            return True

        # Check if permission is in allow_list
        # If runtime allows this permission, grant it regardless of tool metadata
        if required_permission in self.allow_list:
            return True

        # If not in allow_list, check tool metadata for additional restrictions
        registry = get_registry()
        if registry.check_tool_permission(tool_name, required_permission):
            return True

        return False

    def _validate_parameters(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Validate parameters against tool schema.

        Args:
            tool_name: Tool name
            parameters: Parameters dict

        Returns:
            True if valid, False otherwise
        """
        registry = get_registry()
        tool = registry.get_tool(tool_name)

        if not tool:
            return False

        # Check required parameters
        for param in tool.parameters:
            if param.required and param.name not in parameters:
                print(f"[Sandbox] Missing required parameter: {param.name}")
                return False

            # Type validation (basic)
            if param.name in parameters:
                value = parameters[param.name]
                type_map = {
                    'string': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                }
                expected_type = type_map.get(param.type)
                if expected_type and not isinstance(value, expected_type):
                    print(f"[Sandbox] Invalid type for {param.name}: expected {param.type}, got {type(value)}")
                    return False

        return True

    def execute_tool(
        self,
        tool_instance,
        tool_name: str,
        parameters: Dict[str, Any],
        requested_permission: Optional[Permission] = None,
        skip_validation: bool = False
    ) -> ToolExecutionContext:
        """
        Execute a plugin tool in the sandbox.

        Args:
            tool_instance: Tool instance to execute
            tool_name: Tool name
            parameters: Tool parameters
            requested_permission: Permission required for this execution
            skip_validation: Skip parameter validation (for unit tests)

        Returns:
            Execution context with result or error
        """
        ctx = ToolExecutionContext(tool_name, parameters)

        try:
            # Check permission
            if requested_permission and not self._check_permission(tool_name, requested_permission):
                raise PermissionDeniedError(f"Permission denied: {requested_permission}")

            # Validate parameters (skip if requested)
            if not skip_validation and not self._validate_parameters(tool_name, parameters):
                raise ValueError("Invalid parameters")

            # Execute tool
            result = tool_instance.execute(**parameters)

            ctx.result = result
            ctx.end_time = datetime.now()

            # Audit log
            self._audit_log(ctx, success=True)

            return ctx

        except Exception as e:
            ctx.error = str(e)
            ctx.end_time = datetime.now()

            # Audit log
            self._audit_log(ctx, success=False)

            return ctx

    def _audit_log(self, ctx: ToolExecutionContext, success: bool):
        """Audit log for tool execution"""
        status = "SUCCESS" if success else "FAILED"
        print(f"[Audit] Tool {ctx.tool_name} {status} | Duration: {ctx.duration_ms:.1f}ms | User: {ctx.user_id}")

        if not success and ctx.error:
            print(f"[Audit]   Error: {ctx.error}")

    def execute_code(
        self,
        code: str,
        sandbox_globals: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute Python code in the sandbox (advanced use only).

        Args:
            code: Python code to execute
            sandbox_globals: Optional custom globals dict

        Returns:
            Result of code execution

        Raises:
            PermissionDeniedError: If dangerous functions detected
        """
        # Check for dangerous functions
        for func_name in self.DANGEROUS_FUNCTIONS:
            if func_name in code:
                raise PermissionDeniedError(f"Dangerous function detected: {func_name}")

        # Use provided globals or create sandbox
        if sandbox_globals is None:
            sandbox_globals = self._create_sandbox_globals()

        # Execute
        try:
            result = eval(code, sandbox_globals)
            return result
        except Exception as e:
            print(f"[Sandbox] Code execution failed: {e}")
            raise


# Example: Base class for plugin tools
class BaseTool:
    """Base class for plugin tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, **kwargs) -> Any:
        """
        Execute the tool. Must be overridden by subclasses.

        Args:
            **kwargs: Tool parameters

        Returns:
            Tool result
        """
        raise NotImplementedError("Tool.execute() must be implemented")

    def get_schema(self) -> List[ParameterSchema]:
        """
        Get tool parameter schema. Must be overridden by subclasses.

        Returns:
            List of parameter schemas
        """
        raise NotImplementedError("Tool.get_schema() must be implemented")
