# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a desktop application for converting various document formats (docx, xlsx, PDF, pptx) to Markdown using Python, tkinter, and the markitdown library. The application includes OpenAI API integration for enhanced conversion capabilities.

## Architecture

The application follows a layered architecture:
- **GUI Layer**: tkinter-based UI with main window and settings dialog
- **Service Layer**: File conversion (markitdown), API integration (OpenAI), configuration management
- **Data Layer**: Clean dataclass models and file system operations

## Development Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

## Key Dependencies

- markitdown>=0.1.2 (core conversion library)
- openai>=1.0.0 (API enhancement)
- python-dotenv>=1.0.0 (environment variables)
- PyInstaller>=5.0.0 (executable packaging)
- pytest>=7.0.0 (testing framework)

## Common Commands

```bash
# Run the application
python src/main.py

# Build executable
pyinstaller FileConverter.spec

# Run tests (when implemented)
pytest

# Run specific test file
pytest tests/unit/test_conversion_service.py
```

## Core Components

### ConversionService
- Handles file conversion using markitdown library
- Supports batch conversion with progress callbacks
- Error handling for unsupported formats

### APIService
- OpenAI API integration for markdown enhancement
- API key validation and secure storage
- Fallback behavior when API unavailable

### ConfigManager
- Persistent settings in ~/.file_converter/config.json
- Secure API token storage in ~/.file_converter/.env
- Default configuration creation

## Building Executable

The application is packaged using PyInstaller:
- One-file executable with all dependencies bundled
- Hidden imports for markitdown, openai, and tkinter libraries
- Resources bundled from resources/ directory
- Windowed mode (no console)

## Threading Model

The application uses threading to prevent UI freezing:
- Main thread handles GUI events
- Worker threads for file conversion operations
- Progress callbacks update UI via thread-safe mechanisms