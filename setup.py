from setuptools import setup

setup(
    name='myjournal',
    packages=['myjournal'],
    include_package_data=True,
    install_requires=[
        'flask',
        'markdown2',
        'flask-bootstrap',
    ],
)
