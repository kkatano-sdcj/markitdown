# Design Document

## Overview

The File Converter Application is a desktop application built with Python that converts various document formats (docx, xlsx, PDF, pptx) to Markdown format using the markitdown library. The application features a user-friendly GUI, OpenAI API integration for enhanced conversion capabilities, and packages as a standalone executable for easy distribution.

## Architecture

The application follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────┐
│            GUI Layer                │
├─────────────────────────────────────┤
│         Application Layer           │
├─────────────────────────────────────┤
│          Service Layer              │
├─────────────────────────────────────┤
│         Data Access Layer           │
└─────────────────────────────────────┘
```

### Core Components:
- **GUI Layer**: Desktop user interface with main window, settings dialog, and progress indicators
- **Application Layer**: Business logic coordination and workflow management
- **Service Layer**: File conversion, API integration, and configuration management
- **Data Access Layer**: File system operations and configuration persistence

## GUI Framework Selection

### Recommended Options:
1. **PyQt6/PySide6**: Professional, feature-rich framework with excellent styling capabilities
2. **CustomTkinter**: Modern, customizable tkinter wrapper with contemporary design
3. **Flet**: Modern framework with Flutter-like development experience

### Framework Decision Factors:
- **Ease of Development**: CustomTkinter offers simplicity with modern aesthetics
- **Professional Appearance**: PyQt6/PySide6 provides the most polished look
- **Cross-platform**: All options support Windows, macOS, and Linux
- **Packaging**: All frameworks work well with PyInstaller

## User Interface Design

### Main Window Layout:
```
┌─────────────────────────────────────────────────────────┐
│ File Converter                                    [_][□][×]│
├─────────────────────────────────────────────────────────┤
│ File  Settings  Help                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Selected Files:                    [Browse Files]   │ │
│ │ ┌─────────────────────────────────────────────────┐ │ │
│ │ │ document1.docx                            [×]   │ │ │
│ │ │ spreadsheet.xlsx                          [×]   │ │ │
│ │ │ presentation.pptx                         [×]   │ │ │
│ │ └─────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Output Directory:              [Browse Directory]   │ │
│ │ C:\Users\User\Documents\Converted                   │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│                    [Convert Files]                      │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Progress: Converting document1.docx... [████████  ] │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Ready                                                   │
└─────────────────────────────────────────────────────────┘
```

### Design Principles:
- **Simplicity**: Clean, uncluttered interface focusing on core functionality
- **Clarity**: Clear visual hierarchy and intuitive workflow
- **Feedback**: Immediate visual feedback for all user actions
- **Accessibility**: Keyboard navigation and screen reader support

## Components and Interfaces

### 1. Main Application Window (MainWindow)
- **Purpose**: Primary user interface for file selection and conversion
- **Key Features**:
  - File selection with drag-and-drop support
  - Output directory selection
  - Conversion progress display
  - Menu bar with settings access
- **UI Elements**:
  - File list display with remove functionality
  - Browse buttons for file and directory selection
  - Convert button with progress indication
  - Status bar for current operation display

### 2. Settings Dialog (SettingsDialog)
- **Purpose**: API configuration and application preferences
- **Key Features**:
  - OpenAI API token input with masking
  - Configuration validation
  - Settings persistence
- **UI Elements**:
  - Secure text input for API token
  - Test connection button
  - Save/Cancel buttons
  - Default directory preferences

### 3. File Conversion Service (ConversionService)
- **Purpose**: Core conversion logic using markitdown
- **Key Methods**:
  ```python
  def convert_file(self, input_path: str, output_path: str) -> ConversionResult
  def batch_convert(self, file_list: List[str], output_dir: str) -> List[ConversionResult]
  def get_supported_formats(self) -> List[str]
  ```

### 4. API Integration Service (APIService)
- **Purpose**: OpenAI API communication for enhanced conversion
- **Key Methods**:
  ```python
  def enhance_markdown(self, content: str) -> str
  def validate_api_key(self, api_key: str) -> bool
  def get_api_status(self) -> APIStatus
  ```

### 5. Configuration Manager (ConfigManager)
- **Purpose**: Application settings and API token management
- **Key Methods**:
  ```python
  def load_config(self) -> Config
  def save_config(self, config: Config) -> None
  def get_api_token(self) -> Optional[str]
  def set_api_token(self, token: str) -> None
  ```

### 6. Progress Manager (ProgressManager)
- **Purpose**: Conversion progress tracking and UI updates
- **Key Methods**:
  ```python
  def start_progress(self, total_files: int) -> None
  def update_progress(self, current_file: str, completed: int) -> None
  def complete_progress(self, results: List[ConversionResult]) -> None
  ```

## Data Models

### ConversionResult
```python
@dataclass
class ConversionResult:
    input_file: str
    output_file: str
    success: bool
    error_message: Optional[str] = None
    processing_time: float = 0.0
```

### Config
```python
@dataclass
class Config:
    api_token: Optional[str] = None
    default_output_dir: Optional[str] = None
    use_api_enhancement: bool = False
    last_input_dir: Optional[str] = None
```

### APIStatus
```python
@dataclass
class APIStatus:
    is_valid: bool
    error_message: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
```

## Error Handling

### Error Categories:
1. **File Access Errors**: Permission denied, file not found, corrupted files
2. **Conversion Errors**: Unsupported format, markitdown library errors
3. **API Errors**: Invalid token, rate limits, network issues
4. **Configuration Errors**: Invalid settings, missing configuration

### Error Handling Strategy:
- **Graceful Degradation**: Continue processing other files if one fails
- **User Feedback**: Clear error messages with actionable suggestions
- **Logging**: Comprehensive logging for debugging and support
- **Recovery**: Automatic retry for transient errors

### Error Display:
```python
class ErrorDialog:
    def show_conversion_errors(self, failed_files: List[ConversionResult]) -> None
    def show_api_error(self, error: APIError) -> None
    def show_configuration_error(self, error: ConfigError) -> None
```

## Testing Strategy

### Unit Testing:
- **ConversionService**: Test file conversion with various formats
- **ConfigManager**: Test configuration persistence and validation
- **APIService**: Test API integration with mocked responses

### Integration Testing:
- **End-to-End Conversion**: Test complete conversion workflow
- **GUI Integration**: Test UI interactions and state management
- **File System Operations**: Test file handling and directory operations

### Test Structure:
```
tests/
├── unit/
│   ├── test_conversion_service.py
│   ├── test_config_manager.py
│   └── test_api_service.py
├── integration/
│   ├── test_conversion_workflow.py
│   └── test_gui_integration.py
└── fixtures/
    ├── sample_documents/
    └── test_configs/
```

### Testing Tools:
- **pytest**: Primary testing framework
- **unittest.mock**: API and file system mocking
- **GUI testing framework**: Appropriate testing utilities for chosen UI framework

## Development Environment Setup

### Virtual Environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Dependencies:
```
markitdown>=0.11.0
openai>=1.0.0
python-dotenv>=1.0.0
PyInstaller>=5.0.0
pytest>=7.0.0
# GUI Framework (choose one):
# PyQt6>=6.4.0 OR PySide6>=6.4.0 OR customtkinter>=5.0.0 OR flet>=0.10.0
```

### Project Structure:
```
file-converter-app/
├── src/
│   ├── gui/
│   │   ├── main_window.py
│   │   ├── settings_dialog.py
│   │   └── progress_dialog.py
│   ├── services/
│   │   ├── conversion_service.py
│   │   ├── api_service.py
│   │   └── config_manager.py
│   ├── models/
│   │   └── data_models.py
│   └── main.py
├── tests/
├── resources/
├── requirements.txt
└── build_exe.py
```

## Packaging and Distribution

### PyInstaller Configuration:
```python
# build_exe.py
import PyInstaller.__main__

PyInstaller.__main__.run([
    'src/main.py',
    '--onefile',
    '--windowed',
    '--name=FileConverter',
    '--add-data=resources;resources',
    '--hidden-import=markitdown',
    '--hidden-import=openai',
    # Add GUI framework specific imports as needed
    # '--hidden-import=PyQt6' or '--hidden-import=customtkinter' etc.
])
```

### Build Process:
1. **Environment Preparation**: Activate virtual environment
2. **Dependency Installation**: Install all required packages
3. **Testing**: Run complete test suite
4. **Packaging**: Generate executable with PyInstaller
5. **Validation**: Test executable on clean system

### Distribution Considerations:
- **File Size**: Optimize executable size by excluding unnecessary modules
- **Dependencies**: Bundle all required libraries and resources
- **Compatibility**: Test on different Windows versions
- **Security**: Code signing for trusted distribution