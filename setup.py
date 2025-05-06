# setup.py

from setuptools import setup, find_packages

setup(
    name='fake_metrics',
    version='0.1',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    description='A tool for analyzing fake metrics like views and likes with anomaly detection.',
    long_description=open('README.md').read(),
    author='GeeksterLab',
    author_email='GeeksterLab@outlook.com',
    url='https://github.com/GeeksterLab/Fake_Metrics_Analyzer',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'scikit-learn',
        'fpdf',
        'plotly',
        'streamlit'
    ],
    python_requires='>=3.10',
)


