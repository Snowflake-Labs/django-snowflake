from setuptools import find_packages, setup

setup(
    name='django-snowflake',
    version=__import__('django_snowflake').__version__,
    python_requires='>=3.6',
    url='https://github.com/cedar-team/django-snowflake',
    maintainer='Tim Graham',
    maintainer_email='timograham@gmail.com',
    license='MIT License',
    description='Django backend for Snowflake',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    project_urls={
        'Source': 'https://github.com/cedar-team/django-snowflake',
        'Tracker': 'https://github.com/cedar-team/django-snowflake/issues',
    },
    install_requires=['snowflake-connector-python'],
)
