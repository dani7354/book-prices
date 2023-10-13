from setuptools import setup
import os


def get_requirements() -> list[str]:
    project_root = os.path.dirname(os.path.realpath(__file__))
    requirement_list = os.path.join(project_root, "requirements.txt")

    with open(requirement_list, "r") as file:
        yield file.readline().strip()


setup(
    name="bookprices",
    version="1.0",
    packages=[
        "bookprices",
        "bookprices.web",
        "bookprices.web.mapper",
        "bookprices.web.viewmodels",
        "bookprices.web.blueprints",
        "bookprices.web.cache",
        "bookprices.tool",
        "bookprices.shared",
        "bookprices.shared.db",
        "bookprices.shared.model",
        "bookprices.shared.config",
        "bookprices.shared.validation",
        "bookprices.shared.webscraping",
        "bookprices.cronjob"],
    install_requires=get_requirements(),
    url="https://github.com/dani7354/book-prices",
    license="MIT",
    author="dsp",
    author_email="d@stuhrs.dk")
