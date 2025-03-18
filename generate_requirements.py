"""Generate requirements.txt from pyproject.toml dependencies"""
import tomli
import os

def generate_requirements():
    with open("pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)
    
    dependencies = pyproject["project"]["dependencies"]
    
    # Convert dependencies to requirements.txt format
    requirements = []
    for dep in dependencies:
        # Remove version specifiers and comments
        dep = dep.split(">=")[0].split("<=")[0].split("#")[0].strip()
        if dep:
            requirements.append(dep)
    
    # Write requirements.txt
    with open("requirements.txt", "w") as f:
        for req in requirements:
            f.write(f"{req}\n")

if __name__ == "__main__":
    generate_requirements()
