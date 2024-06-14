def extract_conda_packages(conda_file):
    packages = []
    with open(conda_file, 'r') as file:
        for line in file:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 2:
                package = f"{parts[0]}=={parts[1]}"
                packages.append(package)
    return packages

def combine_requirements(conda_file, pip_file, output_file):
    conda_packages = extract_conda_packages(conda_file)
    with open(pip_file, 'r') as file:
        pip_packages = file.readlines()
    
    combined_packages = pip_packages + conda_packages

    with open(output_file, 'w') as file:
        for package in combined_packages:
            file.write(package.strip() + '\n')

# Usage
combine_requirements('conda_requirements.txt', 'requirements.txt', 'combined_requirements.txt')
