from setuptools import setup, find_packages
import re

def get_version_from_file(file_path: str, version_var: str = "VERSION"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = rf"^{version_var}\s*=\s*['\"](.*?)['\"]|{version_var}\s*=\s*([\d.]+)"
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return match.group(1) or match.group(2)
    return None

def read_requirements(file_path: str = "requirements.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            requirements = []
            for line in f:
                line = line.strip()
                # Пропускаем пустые строки и комментарии
                if line and not line.startswith("#"):
                    requirements.append(line)
            return requirements
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. No dependencies will be installed.")
        return []

version = get_version_from_file("FlaskAPIServer/server.py")
install_requires = read_requirements()

setup(
    name='FlaskAPIServer',
    version=version,
    packages=find_packages(where="."),
    include_package_data=True,
    package_data={
        "developer_application": ["*"],
    },
    install_requires=install_requires,
    description='Готовый сервер flask для быстрого использования API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='falbue',
    author_email='cyansair05@gmail.com',
    url='https://github.com/falbue/FlaskAPIServer',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)