---

name: Bug report
about: Create a report to help us improve Guard Core MCP
title: '[BUG] '
labels: bug
assignees: ''
---

Bug Description
===============

A clear and concise description of what the bug is.

___

Steps To Reproduce
------------------

Steps to reproduce the behavior:

1. Configure your MCP client with '...'
2. Call the '....' tool with these arguments
3. See error

___

Expected Behavior
-----------------

A clear and concise description of what you expected to happen.

___

Actual Behavior
---------------

What actually happened, including error messages, stack traces, or logs.

___

Environment
-----------

- Guard Core MCP version: [e.g. 0.0.1]
- Python version: [e.g. 3.11.10]
- MCP client: [e.g. Claude Code, Claude Desktop]
- Installed Guard library versions: [e.g. guard-core 3.5.0, fastapi-guard 7.3.0]
- OS: [e.g. Ubuntu 22.04, Windows 11, MacOS 15.4]
- Other relevant dependencies:

___

Configuration
-------------

```python
# Include the tool call that triggers the bug here
result = validate_config(
    config={
        # Your configuration here
    },
    package="fastapi-guard",
)
```

___

Additional Context
------------------

Add any other context about the problem here. For example:

- Is the Guard library you're asking about installed in the same environment as Guard Core MCP?
- Does it happen consistently or intermittently?
- Have you tried any workarounds?
