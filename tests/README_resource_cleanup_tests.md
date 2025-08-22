# Resource Cleanup Tests for FoundryAgentSession

## Overview

This document describes the comprehensive unit tests implemented for the `FoundryAgentSession` context manager to guarantee proper resource cleanup under all conditions.

## Test File Location

- **File**: `tests/test_resource_cleanup.py`
- **Class**: `TestFoundryAgentSessionCleanup`
- **Test Count**: 15 comprehensive test cases

## Test Coverage

### Core Cleanup Guarantees

The tests verify that `delete_agent()` and `threads.delete()` are called **exactly once** in all scenarios:

1. **Successful Execution**: Normal context manager flow with proper cleanup
2. **Exception During Context**: Exceptions thrown inside the `with` block
3. **Partial Creation Failures**: Exceptions during agent/thread creation
4. **Cleanup Method Failures**: Robust error handling during cleanup itself

### Specific Test Cases

#### 1. **test_successful_context_manager_cleanup**
- Verifies normal operation with proper resource cleanup
- Asserts creation and deletion methods called exactly once

#### 2. **test_exception_during_context_guarantees_cleanup**
- Simulates exception during context execution
- Ensures cleanup still occurs despite the exception

#### 3. **test_exception_during_agent_creation_partial_cleanup**
- Tests failure during agent creation
- Verifies no cleanup is attempted since no resources were created

#### 4. **test_exception_during_thread_creation_agent_cleanup**
- Tests failure during thread creation after successful agent creation
- Ensures agent cleanup occurs but thread cleanup doesn't (since thread wasn't created)

#### 5-7. **Cleanup Robustness Tests**
- `test_cleanup_exception_handling_agent_delete_fails`
- `test_cleanup_exception_handling_thread_delete_fails`
- `test_cleanup_exception_handling_both_deletes_fail`
- Verify that cleanup failures don't crash the application

#### 8. **test_context_exception_not_suppressed_by_cleanup_failure**
- Ensures original exceptions aren't masked by cleanup failures
- Critical for proper error reporting

#### 9-11. **Response Format Handling**
- Tests handling of different agent/thread response formats:
  - Objects with `.id` attribute
  - Dictionaries with `'id'` key
  - Direct ID strings

#### 12-13. **Configuration Tests**
- Verifies proper parameter passing to creation methods
- Tests filtering of `None` values from configuration

#### 14-15. **Edge Cases**
- Partial failure sequences
- ID getter method behavior

## Mock Strategy

### AIProjectClient Mocking

The tests use `unittest.mock.Mock` to create comprehensive mocks of the `AIProjectClient`:

```python
# Mock the client and its nested agent/thread operations
self.mock_client = Mock()
self.mock_client.agents.create_agent.return_value = mock_agent
self.mock_client.agents.threads.create.return_value = mock_thread
self.mock_client.agents.delete_agent = Mock()
self.mock_client.agents.threads.delete = Mock()
```

### Exception Simulation

Tests simulate various failure conditions:

```python
# Simulate agent creation failure
self.mock_client.agents.create_agent.side_effect = RuntimeError("Agent creation failed")

# Simulate cleanup failures
self.mock_client.agents.delete_agent.side_effect = Exception("Agent deletion failed")
```

## Key Assertions

### Cleanup Call Verification

All tests verify that cleanup methods are called exactly once:

```python
# Verify cleanup methods called exactly once
self.mock_client.agents.delete_agent.assert_called_once_with("test-agent-123")
self.mock_client.agents.threads.delete.assert_called_once_with("test-thread-456")

# Or verify they're NOT called when appropriate
self.mock_client.agents.delete_agent.assert_not_called()
```

### Exception Handling

Tests use `pytest.raises` to verify proper exception propagation:

```python
with pytest.raises(ValueError, match="Test exception in context"):
    with session as (agent, thread):
        raise ValueError("Test exception in context")
```

## Running the Tests

### Using pytest (recommended)
```bash
python -m pytest tests/test_resource_cleanup.py -v
```

### Using unittest
```bash
python -m unittest tests/test_resource_cleanup.py -v
```

### Direct execution
```bash
python tests/test_resource_cleanup.py
```

## Test Results

All 15 tests pass successfully, confirming that:
- ✅ Resources are always cleaned up exactly once
- ✅ Exceptions don't prevent cleanup
- ✅ Partial failures are handled correctly
- ✅ Cleanup failures don't crash the application
- ✅ Original exceptions aren't suppressed
- ✅ All response formats are handled properly

## Dependencies

- `unittest.mock` (built-in)
- `pytest` (for enhanced test runner)
- The `FoundryAgentSession` class from `utils.resource_manager`

## Integration

These tests complement the existing test suite and follow the same patterns established in `test_questionnaire_agent.py`, using mocks to isolate the units under test and verify behavior without requiring actual Azure AI services.
