# Uniplex Project

A streamlined automation tool designed for efficiency. Follow the steps below to set up your local development environment and get started.

---

## 🛠 Prerequisites

Ensure you have **Python 3.x** installed on your system. You can verify this by running `python --version` in your terminal.

## 🚀 Getting Started

### 1. Clone & Environment Setup
First, create a virtual environment to isolate the project dependencies:
```powershell
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```
Note: If the activation script is blocked by Windows, run the following command to allow it for the current session:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
```
### 2. Install Dependencies
Once the environment is active, install the required packages:
```powershell
pip install -r .\requirements.txt
```
### 3. Configuration
The script requires authentication via a .env file.

Open the .env file in the project root.

Update the following fields with your credentials:

USERNAME: <br> 
PASSWORD: 
### 🏃 Execution
To launch the project, simply run the main script:
```powershell
python uniplex.py
```
