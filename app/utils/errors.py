"""Custom error classes for the flexible query builder."""


class QueryBuildError(Exception):
    """Error raised when there is a problem building a query."""
    pass


class DatabaseError(Exception):
    """Error raised when there is a database-related issue."""
    pass


class ValidationError(Exception):
    """Error raised when input validation fails."""
    pass


class ParseError(QueryBuildError):
    """Error raised when parsing query parameters fails."""
    pass


class FieldError(QueryBuildError):
    """Error raised when a field reference is invalid."""
    pass


class JoinError(QueryBuildError):
    """Error raised when there is an issue with joining tables."""
    pass


class SecurityError(QueryBuildError):
    """Error raised when a security check fails."""
    pass


class QueryLimitError(QueryBuildError):
    """Error raised when a query exceeds limits."""

    def __init__(self, message: str, limit_type: str, limit_value: int):
        """Initialize with limit details.

        Args:
            message: Error message
            limit_type: Type of limit exceeded
            limit_value: Maximum allowed value
        """
        self.limit_type = limit_type
        self.limit_value = limit_value
        super().__init__(message)


# Schema Management Error Classes

class SchemaCompatibilityError(QueryBuildError):
    """Error raised when schema compatibility check fails."""

    def __init__(self, message: str, current_hash: str = None, expected_hash: str = None):
        """Initialize with schema hash details.

        Args:
            message: Error message
            current_hash: Current schema hash
            expected_hash: Expected schema hash
        """
        self.current_hash = current_hash
        self.expected_hash = expected_hash
        super().__init__(message)


class SchemaDiscoveryError(QueryBuildError):
    """Error raised when schema discovery encounters an issue."""

    def __init__(self, message: str, table: str = None, column: str = None):
        """Initialize with schema element details.

        Args:
            message: Error message
            table: Table name if applicable
            column: Column name if applicable
        """
        self.table = table
        self.column = column
        if table and column:
            full_message = f"{message} (Table: {table}, Column: {column})"
        elif table:
            full_message = f"{message} (Table: {table})"
        else:
            full_message = message

        super().__init__(full_message)


class SchemaGenerationError(QueryBuildError):
    """Error raised when schema generation fails."""

    def __init__(self, message: str, target_file: str = None):
        """Initialize with generation details.

        Args:
            message: Error message
            target_file: Target file path if applicable
        """
        self.target_file = target_file
        if target_file:
            full_message = f"{message} (File: {target_file})"
        else:
            full_message = message

        super().__init__(full_message)


class SchemaVersionError(SchemaCompatibilityError):
    """Error raised when schema versions are incompatible."""

    def __init__(self, message: str, current_version: str = None, expected_version: str = None):
        """Initialize with version details.

        Args:
            message: Error message
            current_version: Current schema version
            expected_version: Expected schema version
        """
        self.current_version = current_version
        self.expected_version = expected_version
        super().__init__(message)


class SchemaAdapterError(QueryBuildError):
    """Error raised when schema adapter encounters an issue."""

    def __init__(self, message: str, adapter_mode: str = None):
        """Initialize with adapter details.

        Args:
            message: Error message
            adapter_mode: Adapter mode (dynamic/static)
        """
        self.adapter_mode = adapter_mode
        if adapter_mode:
            full_message = f"{message} (Mode: {adapter_mode})"
        else:
            full_message = message

        super().__init__(full_message)


class SchemaMappingError(QueryBuildError):
    """Error raised when field mapping fails."""

    def __init__(self, message: str, field: str = None):
        """Initialize with field details.

        Args:
            message: Error message
            field: Field name if applicable
        """
        self.field = field
        if field:
            full_message = f"{message} (Field: {field})"
        else:
            full_message = message

        super().__init__(full_message)