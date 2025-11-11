from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any

# Define generic types for Commands and Queries
C = TypeVar('C', bound='Command')
Q = TypeVar('Q', bound='Query')
R = TypeVar('R') # Return type for queries

class Command(ABC):
    """Base class for all commands."""
    pass

class Query(ABC, Generic[R]):
    """Base class for all queries."""
    pass

class CommandHandler(ABC, Generic[C]):
    """Base class for command handlers."""
    @abstractmethod
    async def handle(self, command: C) -> Any:
        """Handles a command and optionally returns a result."""
        raise NotImplementedError

class QueryHandler(ABC, Generic[Q, R]):
    """Base class for query handlers."""
    @abstractmethod
    async def handle(self, query: Q) -> R:
        """Handles a query and returns a result."""
        pass

class CommandBus:
    """Dispatches commands to their respective handlers."""
    def __init__(self):
        self._handlers: Dict[type[Command], CommandHandler] = {}

    def register_handler(self, command_type: type[C], handler: CommandHandler[C]):
        """Registers a command handler for a specific command type."""
        if command_type in self._handlers:
            raise ValueError(f"Handler already registered for command type {command_type.__name__}")
        self._handlers[command_type] = handler

    async def dispatch(self, command: Command) -> Any:
        """Dispatches a command to its registered handler and returns the handler result, if any."""
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for command type {type(command).__name__}")
        return await handler.handle(command)

class QueryBus:
    """Dispatches queries to their respective handlers."""
    def __init__(self):
        self._handlers: Dict[type[Query], QueryHandler] = {}

    def register_handler(self, query_type: type[Q], handler: QueryHandler[Q, R]):
        """Registers a query handler for a specific query type."""
        if query_type in self._handlers:
            raise ValueError(f"Handler already registered for query type {query_type.__name__}")
        self._handlers[query_type] = handler

    async def dispatch(self, query: Query[R]) -> R:
        """Dispatches a query to its registered handler and returns the result."""
        handler = self._handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for query type {type(query).__name__}")
        return await handler.handle(query)
