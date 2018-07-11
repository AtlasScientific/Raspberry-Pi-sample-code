import setuptools

setuptools.setup(
    name='Atlas_Sensors',
    version='0.1dev',
    packages=['Atlas_Sensors'],
    license='MIT',
    author='Sam Korn',
    author_email='korn94sam@gmail.com',
    install_requires=[
		'smbus2',
    ],
#    long_description=open('README.txt').read(),
	url='https://github.com/sako0938/Raspberry-Pi-sample-code'
)