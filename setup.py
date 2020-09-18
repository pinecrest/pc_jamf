from setuptools import setup

setup(name='pc_jamf',
      version='0.2',
      description='Wrapper library to connect to the PC JAMF server',
      url='https://github.com/pinecrest/pc_jamf',
      author='Sean Tibor',
      author_email='sean.tibor@pinecrest.edu',
      license='MIT',
      packages=['pc_jamf'],
      install_requires=[
            'requests'
      ],
      zip_safe=False)
