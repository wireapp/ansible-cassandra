from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    # Python 2
    from itertools import izip
except ImportError:
    # Python 3
    izip = zip

from itertools import cycle

import ansible.errors as errors
try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

try:
    # ansible 2.0 - 2.3
    from ansible.plugins.lookup import LookupBase
    from ansible.utils.listify import listify_lookup_plugin_terms
    from jinja2.exceptions import UndefinedError

    class LookupModule(LookupBase):
        """
        Zip two arrays, thereby cycling through the second array:
        [1, 2, 3], [4, 5] -> [1, 4], [2, 5], [3, 4]
        """
        def _lookup_variables(self, terms):
            results = []
            for x in terms:
                try:
                    intermediate = listify_lookup_plugin_terms(x, templar=self._templar, loader=self._loader)
                except UndefinedError as e:
                    raise errors.AnsibleUndefinedVariable(
                        "One of the nested variables was undefined. The error was: %s" % e)
                results.append(intermediate)
            return results

        def run(self, terms, variables, **kwargs):
            terms = self._lookup_variables(terms)
            my_list = terms[:]
            if len(my_list) != 2:
                raise errors.AnsibleError("with_zip_cycle requires exactly two lists")
            return [self._flatten(x) for x in izip(my_list[0], cycle(my_list[1]))]

except ImportError:
    # ansible-1.9.x
    from ansible.utils import listify_lookup_plugin_terms

    def flatten(terms):
        ret = []
        for term in terms:
            if isinstance(term, list):
                ret.extend(term)
            elif isinstance(term, tuple):
                ret.extend(term)
            else:
                ret.append(term)
        return ret

    class LookupModule(object):
        """
        Zip two arrays, thereby cycling through the second array:
        [1, 2, 3], [4, 5] -> [1, 4], [2, 5], [3, 4]
        """
        def __init__(self, basedir=None, **kwargs):
            self.basedir = basedir

        def __lookup_injects(self, terms, inject):
            results = []
            for x in terms:
                intermediate = listify_lookup_plugin_terms(x, self.basedir, inject)
                results.append(intermediate)
            return results

        def run(self, terms, inject=None, **kwargs):
            terms = listify_lookup_plugin_terms(terms, self.basedir, inject)
            terms = self.__lookup_injects(terms, inject)
            my_list = terms[:]
            if len(my_list) != 2:
                raise errors.AnsibleError("with_zip_cycle requires exactly two lists")
            res = [flatten(x) for x in izip(my_list[0], cycle(my_list[1]))]
            print("res: {}".format(res))
            return res
