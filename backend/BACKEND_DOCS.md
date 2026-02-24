# Mini Coder Backend Documentation

## Overview
The **Mini Coder Backend** provides a secure, sandboxed environment for analyzing and executing Python and C code. It returns a standardized, AI-ready JSON response containing execution output, errors, and metadata.

## API Contract

### Input
The backend accepts code and language as input.

- **code** (string): The source code to analyze.
- **language** (string): The programming language (`python` or `c`).

### Output (JSON Schema)
The response is a JSON object with the following structure:

```json
{
  "status": "success",     // "success" or "error"
  "language": "python",    // "python" or "c"
  "output": "Hello World\n", // Standard output (stdout) from the code
  "errors": [              // List of error objects (empty if no errors)
    {
      "category": "Syntax Error",      // Broad category: Syntax, Runtime, Security, Compilation, System
      "type": "SyntaxError",           // Specific error type (e.g., ZeroDivisionError, CodeLengthExceeded)
      "line": 1,                       // Line number where error occurred (0 if unknown)
      "message": "invalid syntax",     // Raw error message
      "explanation": "Typo or grammar error...", // User-friendly explanation
      "severity": "error"              // "error" or "warning"
    }
  ],
  "metadata": {
    "execution_time": 0.045,           // Total analysis time in seconds
    "code_length": 120                 // Length of the submitted code
  }
}
```

## Security & Execution Controls

To ensure system stability and security, the following controls are enforced:

### 1. Code Length Limit
- **Max Length**: 1000 characters.
- **Action**: Rejects code exceeding this limit with `CodeLengthExceeded` error.

### 2. Forbidden Patterns (Regex)
The following patterns are blocked before execution:
- `import os`, `import subprocess`, `import sys`, `import shutil`
- `exec(`, `eval(`, `open(`, `system(`, `popen(`, `fork(`
- `__import__`

### 3. Execution Timeout
- **Limit**: 2 seconds.
- **Action**: Terminates execution and returns `TimeoutError` if code runs longer.

### 4. Restricted Environment
- **Python**: Runs in a standard subprocess. Imports of dangerous modules are blocked by regex static analysis.
- **C**: Compiled with `gcc`. Executable is run with the same timeout. Segfaults and runtime crashes are captured.

## Error Categories

| Category | Description | Example |
| :--- | :--- | :--- |
| **Syntax Error** | Code violates language grammar rules. | Missing parentheses, indentation errors. |
| **Runtime Error** | Code fails during execution. | Division by zero, index out of bounds, segfault. |
| **Security Error** | Code attempts restricted actions. | Importing `os`, using `eval()`, exceeding length. |
| **Compilation Error** | (C only) Compiler fails to build the code. | Missing semicolons, undefined symbols. |
| **System Error** | Internal backend failure. | GCC not found, unexpected exception. |
