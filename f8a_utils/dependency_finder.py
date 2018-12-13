"""Definition of a class to find dependencies from an input manifest file."""

import json


class DependencyFinder():
    """Implementation of methods to find dependencies from manifest file."""

    @staticmethod
    def scan_and_find_dependencies(ecosystem, manifests):
        """Scan the dependencies files to fetch transitive deps."""
        deps = dict()
        if ecosystem == "npm":
            deps = DependencyFinder.get_npm_dependencies(ecosystem, manifests)
        elif ecosystem == "pypi":
            deps = DependencyFinder.get_pypi_dependencies(ecosystem, manifests)
        elif ecosystem == "maven":
            deps = DependencyFinder.get_maven_dependencies(ecosystem, manifests)
        return deps

    @staticmethod
    def get_maven_dependencies(ecosystem, manifests):
        """Scan the maven dependencies files to fetch transitive deps."""
        deps = {}
        result = []
        details = []
        direct = []
        for manifest in manifests:
            dep = {
                "ecosystem": ecosystem,
                "manifest_file_path": manifest['filepath'],
                "manifest_file": manifest['filename']
            }
            resolved = []
            data = manifest['content']

            module = ''
            for line in data.split("\n"):
                if "->" in line:
                    line = line.replace('"', '')
                    line = line.replace(' ;', '')
                    prefix, suffix = line.strip().split(" -> ")
                    parsed_json = DependencyFinder._parse_string(suffix)
                    if prefix == module and suffix not in direct:
                        transitive = []
                        trans = []
                        direct.append(suffix)
                        transitive = DependencyFinder.get_maven_transitives(data,
                                                                            transitive,
                                                                            suffix,
                                                                            trans)
                        tmp_json = {
                            "package": parsed_json['groupId'] + ":" + parsed_json['artifactId'],
                            "version": parsed_json['version'],
                            "deps": transitive
                        }
                        resolved.append(tmp_json)
                else:
                    module = line[line.find('"') + 1:line.rfind('"')]
            dep['_resolved'] = resolved
            details.append(dep)
            details_json = {"details": details}
            result.append(details_json)

        deps['result'] = result
        return deps

    @staticmethod
    def get_maven_transitives(data, transitive, suffix, trans):
        """Scan the maven dependencies files to fetch transitive deps."""
        for line in data.split("\n"):
            if suffix in line:
                line = line.replace('"', '')
                line = line.replace(' ;', '')
                pref, suff = line.strip().split(" -> ")
                if pref == suffix and suff not in trans:
                    trans.append(suff)
                    parsed_json = DependencyFinder._parse_string(suff)
                    tmp_json = {
                        "package": parsed_json['groupId'] + ":" + parsed_json['artifactId'],
                        "version": parsed_json['version']
                    }
                    transitive.append(tmp_json)
                    transitive = DependencyFinder.get_maven_transitives(data,
                                                                        transitive,
                                                                        suff,
                                                                        trans)
        return transitive

    @staticmethod
    def _parse_string(coordinates_str):
        """Parse string representation into a dictionary."""
        a = {'groupId': '',
             'artifactId': '',
             'packaging': '',
             'version': '',
             'classifier': ''}

        ncolons = coordinates_str.count(':')
        if ncolons == 1:
            a['groupId'], a['artifactId'] = coordinates_str.split(':')
        elif ncolons == 2:
            a['groupId'], a['artifactId'], a['version'] = coordinates_str.split(':')
        elif ncolons == 3:
            a['groupId'], a['artifactId'], a['packaging'], a['version'] = coordinates_str.split(':')
        elif ncolons == 4:
            # Usually, it's groupId:artifactId:packaging:classifier:version but here it's
            # groupId:artifactId:packaging:version:classifier
            a['groupId'], a['artifactId'], a['packaging'], a['version'], a['classifier'] = \
                coordinates_str.split(':')
        else:
            raise ValueError('Invalid Maven coordinates %s', coordinates_str)

        return a

    @staticmethod
    def get_npm_dependencies(ecosystem, manifests):
        """Scan the npm dependencies files to fetch transitive deps."""
        deps = {}
        result = []
        details = []
        for manifest in manifests:
            dep = {
                "ecosystem": ecosystem,
                "manifest_file_path": manifest['filepath'],
                "manifest_file": manifest['filename']
            }

            dependencies = json.loads(manifest['content']).get('dependencies')
            resolved = []
            if dependencies:
                for key, val in dependencies.items():
                    version = val.get('version') or val.get('required').get('version')
                    if version:
                        transitive = []
                        tr_deps = val.get('dependencies') or \
                            val.get('required', {}).get('dependencies')
                        if tr_deps:
                            transitive = DependencyFinder.get_npm_transitives(transitive, tr_deps)
                        tmp_json = {
                            "package": key,
                            "version": version,
                            "deps": transitive
                        }
                        resolved.append(tmp_json)
            dep['_resolved'] = resolved
            details.append(dep)
            details_json = {"details": details}
            result.append(details_json)
        deps['result'] = result
        return deps

    @staticmethod
    def get_npm_transitives(transitive, content):
        """Scan the npm dependencies recursively to fetch transitive deps."""
        if content:
            for key, val in content.items():
                version = val.get('version') or val.get('required').get('version')
                if version:
                    tmp_json = {
                        "package": key,
                        "version": version
                    }
                    transitive.append(tmp_json)
                    tr_deps = val.get('dependencies') or val.get('required', {}).get('dependencies')
                    if tr_deps:
                        transitive = DependencyFinder.get_npm_transitives(transitive, tr_deps)
        return transitive

    @staticmethod
    def get_pypi_dependencies(ecosystem, manifests):
        """Scan the pypi dependencies files to fetch transitive deps."""
        result = []
        details = []
        deps = {}
        for manifest in manifests:
            dep = {
                "ecosystem": ecosystem,
                "manifest_file_path": manifest['filepath'],
                "manifest_file": manifest['filename']
            }
            content = json.loads(manifest['content'])
            dep['_resolved'] = content
            details.append(dep)
            details_json = {"details": details}
            result.append(details_json)
        deps['result'] = result
        return deps
