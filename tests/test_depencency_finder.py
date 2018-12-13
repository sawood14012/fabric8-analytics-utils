"""Tests for classes from depencency_finder module."""

from f8a_utils.dependency_finder import DependencyFinder
from pathlib import Path


def test_scan_and_find_dependencies():
    """Test scan_and_find_dependencies function."""
    manifests = [{
        "filename": "npmlist.json",
        "filepath": "/bin/local",
        "content": open(str(Path(__file__).parent / "data/npmlist.json")).read()
    }]
    res = DependencyFinder().scan_and_find_dependencies("npm", manifests)
    assert "result" in res
    assert res['result'][0]['details'][0]['_resolved'][0]['package'] == "body-parser"
    assert len(res['result'][0]['details'][0]['_resolved'][0]['deps']) == 2


def test_scan_and_find_dependencies_pypi():
    """Test scan_and_find_dependencies function for pypi."""
    manifests = [{
        "filename": "pylist.json",
        "filepath": "/bin/local",
        "content": open(str(Path(__file__).parent / "data/pylist.json")).read()
    }]
    res = DependencyFinder().scan_and_find_dependencies("pypi", manifests)
    assert "result" in res
    assert res['result'][0]['details'][0]['_resolved'][0]['package'] == "django"
    assert len(res['result'][0]['details'][0]['_resolved'][0]['deps']) == 1


def test_scan_and_find_dependencies_maven():
    """Test scan_and_find_dependencies function for maven."""
    manifests = [{
        "filename": "dependencies.txt",
        "filepath": "/bin/local",
        "content": open(str(Path(__file__).parent / "data/dependencies.txt")).read()
    }]
    res = DependencyFinder().scan_and_find_dependencies("maven", manifests)
    assert "result" in res
    resolved = res['result'][0]['details'][0]['_resolved'][0]
    assert resolved['package'] == "io.vertx:vertx-service-discovery"
    assert len(resolved['deps']) == 16


if __name__ == '__main__':
    test_scan_and_find_dependencies()
    test_scan_and_find_dependencies_pypi()
    test_scan_and_find_dependencies_maven()
