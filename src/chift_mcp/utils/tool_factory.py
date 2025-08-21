from abc import ABC, abstractmethod

from fastmcp.tools import Tool


class ToolFactory(ABC):
    """Base factory class for creating and customizing tools.

    This abstract base class defines the interface that all tool factories
    must implement. Tool factories are responsible for taking a base Tool
    and returning a customized version of it.
    """

    @abstractmethod
    def _customize_tool(self, tool: Tool) -> Tool:
        """Create and return a customized version of the tool.

        This method must be implemented by subclasses to define how
        the tool should be customized.

        Returns:
            A new customized Tool instance, or None if no customization is needed
        """
        pass

    @classmethod
    def execute(cls, tool: Tool, *args, **kwargs) -> Tool:
        """Factory method to create an instance and execute customization.

        This is the main entry point for using the factory. It creates
        an instance of the factory and immediately customizes the tool.

        Args:
            tool: The Tool to customize
            *args: Additional positional arguments for the factory constructor
            **kwargs: Additional keyword arguments for the factory constructor

        Returns:
            A customized Tool instance, or None if no customization is needed
        """
        factory = cls(*args, **kwargs)
        return factory._customize_tool(tool)
