"""
Example Plugin
==============

This is an example plugin demonstrating the plugin system API.
"""
from plugin_system import BaseTool, ParameterSchema


class ExamplePlugin:
    """Example plugin class"""

    def __init__(self):
        self.name = "example_plugin"
        self.version = "1.0.0"
        print(f"[{self.name}] Plugin initialized")

    def on_load(self):
        """Called when plugin is loaded"""
        print(f"[{self.name}] Plugin loaded")

    def on_unload(self):
        """Called when plugin is unloaded"""
        print(f"[{self.name}] Plugin unloaded")


class HelloWorldTool(BaseTool):
    """Hello World tool - greets a user"""

    def __init__(self):
        super().__init__(
            name="hello_world",
            description="Say hello to someone"
        )

    def execute(self, name: str = "World") -> str:
        """
        Say hello.

        Args:
            name: Name to greet

        Returns:
            Greeting message
        """
        return f"Hello, {name}!"

    def get_schema(self):
        """Get parameter schema"""
        return [
            ParameterSchema(
                name="name",
                type="string",
                required=False,
                default="World",
                description="Name to greet"
            )
        ]


class CalculatorTool(BaseTool):
    """Simple calculator tool"""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform basic arithmetic operations"
        )

    def execute(self, a: int, b: int, operation: str = "add") -> dict:
        """
        Perform arithmetic operation.

        Args:
            a: First operand
            b: Second operand
            operation: Operation (add, subtract, multiply, divide)

        Returns:
            Result dict with operation details
        """
        result = None

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            result = a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return {
            "operation": operation,
            "operands": [a, b],
            "result": result
        }

    def get_schema(self):
        """Get parameter schema"""
        return [
            ParameterSchema(
                name="a",
                type="int",
                required=True,
                description="First operand"
            ),
            ParameterSchema(
                name="b",
                type="int",
                required=True,
                description="Second operand"
            ),
            ParameterSchema(
                name="operation",
                type="string",
                required=False,
                default="add",
                description="Operation (add, subtract, multiply, divide)"
            )
        ]


class ReverseStringTool(BaseTool):
    """Reverse a string"""

    def __init__(self):
        super().__init__(
            name="reverse_string",
            description="Reverse a given string"
        )

    def execute(self, text: str) -> str:
        """
        Reverse string.

        Args:
            text: Text to reverse

        Returns:
            Reversed string
        """
        return text[::-1]

    def get_schema(self):
        """Get parameter schema"""
        return [
            ParameterSchema(
                name="text",
                type="string",
                required=True,
                description="Text to reverse"
            )
        ]
