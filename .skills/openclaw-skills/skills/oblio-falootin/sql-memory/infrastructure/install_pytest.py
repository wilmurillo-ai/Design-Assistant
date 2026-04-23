import subprocess

# Function to install pytest
try:
    subprocess.run(["pip", "install", "pytest"], check=True)
    print("pytest installed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error installing pytest: {e}")