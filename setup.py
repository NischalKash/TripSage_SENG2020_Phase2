from distutils.core import setup

setup(
	name='Code',
	version='1.0',
	description='CSC 510 Software Engineering Project Phase 2',
 	author='Sharath Bangalore Ramesh Kumar',
	author_email='sbangal2@ncsu.edu',
	url='https://github.com/NischalKash/TripSage_SENG2020_Phase2.git',
	packages=['code'],
	classifiers=[
		"MIT License",
		"Programming Languages :: Python",
		"Topic :: Software Engineering Course",
	],
	license="MIT",
	install_requires = [
		'numpy',
		'django',
                'googlemaps'
	]
      )
