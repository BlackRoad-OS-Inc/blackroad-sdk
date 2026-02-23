from setuptools import setup, find_packages

setup(
    name="blackroad-sdk",
    version="0.1.0",
    description="BlackRoad OS Python SDK — AI agent coordination and memory",
    author="BlackRoad OS, Inc.",
    author_email="dev@blackroad.ai",
    url="https://github.com/BlackRoad-OS-Inc/blackroad-sdk",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["httpx>=0.27"],
    extras_require={"dev": ["pytest", "pytest-asyncio"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
)
