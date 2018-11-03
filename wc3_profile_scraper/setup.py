from setuptools import setup

setup(name='wc3_profile_scraper',
      version='0.1',
      description="Extracts all data from a given player's WC3 Battlenet page.",
      url='https://github.com/chrisdaly/wc3-bnet-scraping',
      author='Chris Daly',
      author_email='chrisdaly1988@gmail.com',
      license='MIT',
      packages=['wc3_profile_scraper'],
      install_requires=['requests', 'bs4', 'lxml'],
      zip_safe=False)
