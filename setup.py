from setuptools import setup, find_packages

setup(
    name='SkillHelper',
    version='0.1a',
    packages=find_packages(),
    install_requires=["kivy>=1.11.1", "pandas>=1.0.5", "yaml>=0.2.5", "numpy>=1.19.0", "python>=3.8.2"],
    package_data={"source": ["*.kv"]},
    scripts=["main.py"],
    author='hauska',
    author_email='zhekauran@gmail.com',
    description='Interactive notes.'
)
