from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='MyProject',
    packages=['MyProject'],
    version='0.0.0',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Victor M Santiago',
    author_email='vsantiago113sec@gmail.com',
    url='https://github.com/vsantiago113/Base-Template',
    download_url='',
    python_requires='>=3.4.0',
    keywords=[
        'Template'
    ],
    install_requires=[

    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
