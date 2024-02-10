from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Win11',
    'Programming Language :: Python'
]

setup(
    name='fyp.ai_pkg',
    version='1.0.0',
    description='Pkg del progetto FIA',
    url='https://github.com/Pietro1377/FindYourPlace_FIA',
    author='<Lorenzo Castellano>',
    license='MIT',
    classifiers=classifiers,
    packages=find_packages(),
    package_data={'fyp_pkg': ['Database/*', 'Trained_Models/*.pkl']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'test=fyp_pkg.main:main',
        ], },
    install_requires=[
        'joblib',
        'pandas',
        'folium',
        'numpy',
        'scikit-learn',
        'requests',
        'overpass',
        'geopy',
        'setuptools',
        'xmltodict',
    ]
)
