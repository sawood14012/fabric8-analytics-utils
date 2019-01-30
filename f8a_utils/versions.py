"""Helper functions related to versions."""

import requests
import logging
from urllib.request import urlopen
from lxml import etree
from f8a_version_comparator.comparable_version import ComparableVersion

_logger = logging.getLogger(__name__)


def get_versions_for_ep(ecosystem, package_name):
    """Get all versions for given (ecosystem, package).

    :param ecosystem: str, ecosystem name
    :param package_name: str, package name
    :return list, list of versions
    """
    if package_name is None:
        raise ValueError('Package name is not provided')

    # check against the supported ecosystems
    if ecosystem == 'npm':
        return get_versions_for_npm_package(package_name)
    if ecosystem == 'pypi':
        return get_versions_for_pypi_package(package_name)
    if ecosystem == 'maven':
        return get_versions_for_maven_package(package_name)
    else:
        raise ValueError('Unsupported ecosystem: {e}'.format(e=ecosystem))


def get_latest_versions_for_ep(ecosystem, package_name):
    """Get all versions for given (ecosystem, package).

    :param ecosystem: str, ecosystem name
    :param package_name: str, package name
    :return version
    """
    if package_name is None:
        raise ValueError('Package name is not provided')

    # check against the supported ecosystems
    if ecosystem == 'npm':
        version = get_versions_for_npm_package(package_name, True)
    elif ecosystem == 'pypi':
        version = get_versions_for_pypi_package(package_name, True)
    elif ecosystem == 'maven':
        version = get_versions_for_maven_package(package_name, True)
    else:
        raise ValueError('Unsupported ecosystem: {e}'.format(e=ecosystem))
    return version


def get_versions_for_npm_package(package_name, latest=False):
    """Get all versions for given NPM package.

    :param package_name: str, package name
    :param latest: boolean value, to return only the latest version
    :return list, list of versions
    """
    url = 'https://registry.npmjs.org/{pkg_name}'.format(
        pkg_name=package_name
    )

    response = requests.get(url)

    if response.status_code != 200:
        _logger.error(
            'Unable to fetch versions for package {pkg_name}'.format(pkg_name=package_name)
        )
        return []

    response_json = {}
    try:
        response_json = response.json()
    except ValueError:
        pass
    finally:
        if not response_json:
            return []
    ver_list = list({x for x in response_json.get('versions', {})})
    if latest:
        version = response_json.get('dist-tags', {})['latest'] if \
            response_json.get('dist-tags', {}) else select_latest_version(ver_list)
        return version
    return ver_list


def get_versions_for_pypi_package(package_name, latest=False):
    """Get all versions for given PyPI package.

    :param package_name: str, package name
    :param latest: boolean value, to return only the latest version
    :return list, list of versions
    """
    pypi_package_url = 'https://pypi.python.org/pypi/{pkg_name}/json'.format(
        pkg_name=package_name
    )

    response = requests.get(pypi_package_url)
    if response.status_code != 200:
        _logger.error(
            'Unable to fetch versions for package {pkg_name}'.format(pkg_name=package_name)
        )
        return []

    ver_list = list({x for x in response.json().get('releases', {})})

    if latest:
        version = response.json().get('info', {})['version'] if \
            'version' in response.json().get('info', {}) else select_latest_version(ver_list)
        return version
    return ver_list


def get_versions_for_maven_package(package_name, latest=False):
    """Get all versions for given package from Maven Central.

    :param package_name: str, package name
    :param latest: boolean value, to return only the latest version
    :return list, list of versions
    """
    try:
        g, a = package_name.split(':')
        g = g.replace('.', '/')

        filenames = {'maven-metadata.xml', 'maven-metadata-local.xml'}

        versions = set()
        ok = False
        for filename in filenames:

            url = 'https://repo.maven.apache.org/maven2/{g}/{a}/{f}'.format(g=g, a=a, f=filename)
            try:
                metadata_xml = etree.parse(urlopen(url))
                ok = True  # We successfully downloaded the file
                version_elements = metadata_xml.findall('.//version')
                version = metadata_xml.find('.//release').text if \
                    metadata_xml.find('.//release') is not None else None
                versions = versions.union({x.text for x in version_elements})
            except (OSError, etree.XMLSyntaxError):
                # Not both XML files have to exist, so don't freak out yet
                pass

        if not ok:
            _logger.error(
                'Unable to fetch versions for package {pkg_name}'.format(pkg_name=package_name)
            )
        if latest:
            version = version if version else select_latest_version(list(versions))
            return version
        return list(versions)
    except ValueError:
        # wrong package specification etc.
        return []


def select_latest_version(versions=[]):
    """Select latest version from list."""
    version_arr = []
    for x in versions:
        version_arr.append(ComparableVersion(x))
    version_arr.sort()
    return version_arr[-1]
