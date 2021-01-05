from setuptools import setup

if __name__ == "__main__":
    setup(
        name='nvim-todo',
        description='User interface for todo.txt files',
        author='Afoucaul',
        url='https://github.com/Afoucaul/nvim-todo',
        license='MIT',
        python_requires='>=3',
        install_requires=[
            'pynvim>=0.3.1',
            'sly>=0.4',
        ],
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Topic :: Text Editors',
        ],
    )
