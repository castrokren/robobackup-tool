# RoboBackup Tool

A Python-based backup tool that provides automated file backup functionality with logging and configuration management.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows OS (primary target)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/robobackup-tool.git
   cd robobackup-tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
Backup_APP_1/
├── .github/          # GitHub workflows and CI/CD
├── assets/           # Icons, images, and static resources
├── config/           # Configuration files and settings
├── installers/       # Installer scripts and NSIS files
├── logs/             # Application logs (with archive subfolder)
├── scripts/          # Build scripts and utilities
├── backupapp.py      # Main application GUI
├── backup_core.py    # Core backup functionality
├── backup_service.py # Windows service functionality
├── main.py          # Application entry point
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## 🔧 Development

### Building the Application
```bash
# Run build script
python scripts/build_exe.py

# Or use PyInstaller directly
pyinstaller --onefile --windowed main.py
```

### Running Tests
```bash
python -m pytest test_backup_core.py
```

## 📋 Features

- Automated file backup with configurable schedules
- Comprehensive logging system
- Windows service integration
- GUI interface for easy configuration
- Security audit logging
- Configurable backup destinations

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔄 CI/CD

This project uses GitHub Actions for continuous integration:
- Automated testing on multiple Python versions
- Code linting with flake8
- Automated builds with PyInstaller
- Artifact uploads for releases

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.
