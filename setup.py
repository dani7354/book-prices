from setuptools import setup

setup(
    name='bookprices',
    version='1.0',
    packages=[
        'bookprices',
        'bookprices.web',
        'bookprices.web.viewmodels',
        'bookprices.tools',
        'bookprices.shared',
        'bookprices.shared.db',
        'bookprices.shared.model',
        'bookprices.shared.config',
        'bookprices.shared.validation',
        'bookprices.shared.webscraping',
        'bookprices.cronjobs'],
    url='',
    license='',
    author='dsp',
    author_email='',
    description=''
)
