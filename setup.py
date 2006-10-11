from setuptools import setup, find_packages

setup(
    name='TaskTracker',
    version="",
    #description="",
    #author="",
    #author_email="",
    #url="",
    install_requires=["Pylons>=0.9.2", "PasteScript"],
    packages=find_packages(),
    include_package_data=True,
    test_suite = 'nose.collector',
    package_data={'tasktracker': ['i18n/*/LC_MESSAGES/*.mo']},
    dependency_links=["http://svn.webwareforpython.org/Component/trunk#egg=Component"],
    entry_points="""
    [paste.app_factory]
    main=tasktracker:make_app
    [paste.app_install]
    main=paste.script.appinstall:Installer
    """,
)
