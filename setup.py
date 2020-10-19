from setuptools import setup

setup(name='pc_jamf',
      version='0.3.1',
      description='Wrapper library to connect to a JAMF Pro Server using the beta and classic API',
      url='https://github.com/pinecrest/pc_jamf',
      author='Sean Tibor',
      author_email='sean.tibor@pinecrest.edu',
      license='MIT',
      packages=['pc_jamf'],
      install_requires=[
            'requests',
            'python-decouple'
      ],
      zip_safe=False)
