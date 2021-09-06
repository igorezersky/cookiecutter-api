import setuptools

from {{ cookiecutter.project_slug }} import __version__

with open('README.md', 'r', encoding='utf-8') as fp:
    long_description = fp.read()

install_requires = []
for file in ['base', 'prod']:
    with open(f'requirements/{file}.txt', encoding='utf-8') as fp:
        for line in fp:
            if line.startswith('git'):  # handle private repos
                install_requires.append(f'{line.split("/")[-1].split(".git")[0]} @ {line}')
            elif line.startswith('-'):
                continue  # ignore other files including
            else:
                install_requires.append(line)

setuptools.setup(
    name='{{ cookiecutter.project_slug }}',
    version=__version__,
    author='{{ cookiecutter.author_name }}',
    author_email='{{ cookiecutter.author_email }}',
    description='{{ cookiecutter.project_name }} description',
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    packages=setuptools.find_packages(exclude=('tests*',)),
    install_requires=install_requires,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6,<3.10'
)
