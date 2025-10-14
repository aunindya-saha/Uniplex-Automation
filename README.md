Clone this project and run these commands line in the terminal. 
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# if Activation is blocked, allow for this session:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
pip install -r .\requirements.txt

Give your username and id in the .env file and run the script:
python uniplex.py
