from setuptools import setup, find_packages

setup(
    name="music-analyzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "librosa>=0.10.0",
        "numpy>=1.23.0",
        "scipy>=1.10.0",
        "pydantic>=2.0.0",
        "soundfile>=0.12.0",
        "matplotlib>=3.7.0",
    ],
    extras_require={
        "standard": [
            "essentia>=2.1b6",
            "pyloudnorm>=0.1.0",
        ],
        "full": [
            "essentia>=2.1b6",
            "pyloudnorm>=0.1.0",
            "demucs>=4.0.0",
            "faster-whisper>=0.10.0",
            "laion-clap>=1.1.4",
            "torch>=2.0.0",
            "torchaudio>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "music-analyzer=music_analyzer.cli:main",
        ],
    },
    python_requires=">=3.9",
)
