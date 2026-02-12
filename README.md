# Ransomware Simulator

## Project Overview

This is a final-year project focused on developing a safe, educational ransomware simulator. The application allows users to simulate ransomware attacks in a controlled environment to understand detection, mitigation, and recovery strategies. It includes AI-powered risk assessment, real-time monitoring with canary tokens, and comprehensive reporting features.

## Specific Objectives

1. **Educational Tool Development**: Create a comprehensive simulator for learning about ransomware behavior, detection techniques, and mitigation strategies.
2. **Safe Simulation Environment**: Implement a sandboxed system that prevents any real data loss while accurately mimicking ransomware characteristics.
3. **Multi-Algorithm Encryption Support**: Support various encryption algorithms (AES, RSA, ChaCha20) to demonstrate different attack vectors.
4. **AI-Powered Risk Assessment**: Develop an AI model that analyzes simulation metrics and generates detailed risk summaries with severity levels and mitigation recommendations.
5. **Real-Time Monitoring**: Implement canary file monitoring system for early detection of suspicious file system activity.
6. **Comprehensive Reporting**: Provide detailed simulation reports with metrics, risk assessments, and recovery options.
7. **User-Friendly Interface**: Develop an intuitive GUI that guides users through simulations, monitoring, and analysis.

## Functional Requirements

1. **Simulation Engine**
   - Encrypt files using AES-256-GCM, RSA, or ChaCha20 algorithms
   - Support selective file type targeting (.txt, .pdf, .docx, .png, .jpg, etc.)
   - Generate ransom notes with customizable content
   - Provide real-time progress tracking and metrics collection
   - Support simulation abortion and cleanup

2. **Risk Assessment System**
   - Analyze encryption speed, file types, and system impact
   - Generate severity classifications (LOW, MEDIUM, HIGH, CRITICAL)
   - Provide threat descriptions, impact assessments, and mitigation steps
   - Use AI model for natural language risk summaries

3. **Monitoring and Detection**
   - Deploy canary files for early threat detection
   - Real-time file system monitoring using watchdog
   - Alert system for triggered canary files
   - Status tracking for active monitoring points

4. **Recovery System**
   - Decrypt files using stored encryption keys
   - Support multiple algorithm recovery
   - Batch recovery operations
   - Verification of successful recovery

5. **Reporting and Analytics**
   - Generate detailed simulation reports
   - Export reports in multiple formats
   - Historical report storage and retrieval
   - Performance metrics visualization

6. **User Interface**
   - Multi-page GUI with navigation sidebar
   - Dashboard for simulation control and monitoring
   - Settings configuration panels
   - Real-time status updates and progress bars

## Non-Functional Requirements

1. **Safety and Security**
   - Mandatory test mode preventing real file damage
   - Safe zone verification before any file operations
   - Secure key generation and storage
   - No network connectivity for malicious purposes

2. **Performance**
   - Efficient encryption/decryption operations
   - Minimal system resource overhead during monitoring
   - Responsive GUI with smooth animations
   - Scalable to handle large file sets

3. **Usability**
   - Intuitive navigation and clear visual hierarchy
   - Comprehensive help guides and tooltips
   - Error handling with user-friendly messages
   - Consistent design language throughout

4. **Reliability**
   - Robust error handling and recovery
   - Data integrity during simulations
   - Stable monitoring without false positives
   - Consistent AI model performance

5. **Maintainability**
   - Modular code architecture
   - Clear documentation and comments
   - Separation of concerns (frontend/backend/AI)
   - Easy configuration management

## Development Steps Carried Out

1. **Research and Planning (2 weeks)**
   - Studied ransomware attack patterns and mitigation techniques
   - Analyzed existing security tools and educational simulators
   - Defined project scope and requirements
   - Created system architecture diagrams

2. **Backend Development (4 weeks)**
   - Implemented encryption/decryption modules using cryptography library
   - Developed file scanning and safety verification systems
   - Created simulation engine with metrics collection
   - Built key management and storage system

3. **AI Model Development (3 weeks)**
   - Generated synthetic training data for risk assessment
   - Fine-tuned GPT-2 model for natural language generation
   - Implemented risk summary generator with template fallbacks
   - Integrated AI model with backend processing

4. **Frontend Development (4 weeks)**
   - Designed GUI layout with CustomTkinter
   - Implemented multi-page navigation system
   - Created dashboard with real-time monitoring
   - Developed simulation control panels and settings

5. **Integration and Testing (3 weeks)**
   - Integrated all components into cohesive application
   - Implemented inter-module communication
   - Conducted comprehensive testing in safe zone
   - Validated AI model accuracy and performance

6. **Documentation and Finalization (2 weeks)**
   - Created user guides and technical documentation
   - Added safety disclaimers and liability notices
   - Performed final validation and bug fixes
   - Prepared project presentation materials

## System Design and Considerations

### Architecture

The application follows a modular three-tier architecture:

- **Frontend Layer**: CustomTkinter-based GUI with multiple pages
- **Backend Layer**: Core business logic including encryption, scanning, and monitoring
- **AI Layer**: Machine learning models for risk assessment and report generation

### Safety Considerations

- **Safe Zone Enforcement**: All operations are restricted to a designated "Ransomware_Test" directory
- **Test Mode Default**: Simulations create encrypted copies while preserving originals
- **Path Verification**: Every file operation includes safety checks
- **No Network Features**: Prevents any potential for real-world malicious use

### Technical Considerations

- **Cross-Platform Compatibility**: Designed for Windows with Python ecosystem
- **Library Selection**: Used well-maintained libraries (cryptography, transformers, customtkinter)
- **Performance Optimization**: Efficient algorithms and resource monitoring
- **Error Resilience**: Comprehensive exception handling and graceful degradation

### Ethical Considerations

- **Educational Purpose Only**: Clearly marked as a learning tool
- **Liability Disclaimers**: Explicit warnings about misuse
- **No Malicious Intent**: Designed without features that could enable attacks
- **Responsible Disclosure**: Encourages ethical use and security awareness

### Scalability Considerations

- **Modular Design**: Easy to extend with new algorithms or features
- **Configurable Parameters**: Adjustable settings for different use cases
- **Resource Management**: Efficient memory and CPU usage
- **Data Handling**: Support for various file types and sizes

## Installation and Usage

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python frontend/app.py`
3. Follow the GUI prompts to set up simulations
4. Always operate within the safe zone directory

## Dependencies

- cryptography: For secure encryption operations
- customtkinter: Modern GUI framework
- transformers/torch: AI model implementation
- watchdog: File system monitoring
- psutil/scipy/numpy: Performance monitoring and analysis

## Disclaimer

This tool is for educational purposes only. The creators are not responsible for any misuse or damage caused by modifying the code. Always use in a controlled, disposable environment.

## Packaging and Deployment Guide

Based on the project structure (a Python-based ransomware simulator with GUI, AI components, and dependencies), here's a step-by-step guide to packaging and deploying the application for others to use. This focuses on creating a standalone executable for Windows users.

### 1. Prepare Your Application for Packaging

- Verify that the app runs correctly in your development environment, testing all features (simulations, AI reports, monitoring, recovery).
- Clean up the codebase by removing unnecessary files (e.g., old virtual environments, temporary files).
- Ensure `requirements.txt` accurately lists all dependencies.
- Update file paths in code to use relative paths for data files (e.g., AI model in `risk_summary_model/`).
- Enhance the README with clear user instructions, including safety warnings.

### 2. Choose a Packaging Tool

- Use **PyInstaller** (free and popular for creating Windows executables). Install it via `pip install pyinstaller`.
- Alternatives include cx_Freeze or py2exe, but PyInstaller is recommended for simplicity.

### 3. Create a Standalone Executable

- Navigate to the project root in a terminal.
- Run `pyinstaller --onefile --windowed frontend/app.py` to create a single .exe file.
  - `--onefile`: Bundles everything into one executable.
  - `--windowed`: Hides the console window for GUI apps.
- If data files (like the AI model) are missed, edit the generated `app.spec` file to include them (e.g., `datas=[('risk_summary_model', 'risk_summary_model')]`), then re-run with `pyinstaller app.spec`.
- Test the .exe from the `dist/` folder to ensure all features work.

### 4. Bundle Additional Resources

- Create a distribution folder (e.g., `RansomwareSimulator_v1.0/`) and include:
  - The .exe file.
  - Updated README.md as user guide.
  - Template files like the "Ransomware_Test" folder structure.

### 5. Create an Installer (Optional but Recommended)

- Use **Inno Setup** (free for Windows):
  - Download and install Inno Setup.
  - Create a script defining app details, source files, and installation options.
  - Compile to generate a .exe installer (e.g., `RansomwareSimulatorSetup.exe`).
- Alternative: Use NSIS for scripting-based installers.

### 6. Test the Package on a Clean Environment

- Install and run on a system without Python or dependencies.
- Verify key features and safe zone functionality.
- Gather feedback from test users.

### 7. Distribute the Package

- Upload to GitHub Releases, file-sharing sites, or academic platforms.
- Tag the code version in Git for tracking.
- Include disclaimers about educational use and liability.

### Additional Tips

- The executable may be large due to AI models; compress if needed.
- Test for cross-platform support if required (repeat process on other OSes).
- Address any PyInstaller issues by checking library compatibility.
- Estimated time: 1-2 days for testing and refinement.
