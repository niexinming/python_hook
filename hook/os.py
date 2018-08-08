import sys
import io

##########
# Consts #
##########

_HOOK_TEMPLATES_DICT = \
{
"_hook_%(name)s":
"""
def _hook_%(name)s(self, *args, **kwargs):
    #print "\\nCLS HOOK: %%s.%(name)s(args=%%s, kwargs=%%s) = ..." %% (__name__, args, kwargs)
    _hook_args = args
    _hook_kwargs = kwargs
    (_hook_args, _hook_kwargs) = self._pre_%(name)s_hook(*args, **kwargs)
    #print "\\tCalling _pre_%(name)s_hook(%%s, %%s) = (%%s, %%s)" %% (args, kwargs, _hook_args, _hook_kwargs)
    retval = object.__getattribute__(self, '%(name)s')(*_hook_args, **_hook_kwargs)
    #print "\\tCalling _post_%(name)s(args=%%s, kwargs=%%s) = %%s" %% (_hook_args, _hook_kwargs, str(retval))
    retval = self._post_%(name)s_hook(retval, *_hook_args, **_hook_kwargs)
    #print "= %%s" %% (str(retval))
    return retval
"""
,
"_pre_%(name)s_hook":
"""
def _pre_%(name)s_hook(self, *args, **kwargs):
    return (args, kwargs)
"""
,
"_post_%(name)s_hook":
"""
def _post_%(name)s_hook(self, retval, *args, **kwargs):
    return retval
"""
}

###########
# Classes #
###########

class _CustomGetAttribute:
    def __getattribute__(self, name):
        retval = object.__getattribute__(self, name)

        # "Magic" Objects / Weak "Internal Use" Indicator? AS IS!
        if name.startswith('_'):
            return retval

        # Callable? Hook!
        if callable(retval):
            try:
                return object.__getattribute__(self, '_hook_' + name)
            except AttributeError:
                import types

                # i.e. ("_hook_%(name)s", "def _hook_%(name)s(self, *args, **kwargs): ..."
                for fcn_template_name, fcn_template_code in _HOOK_TEMPLATES_DICT.iteritems():
                    fcn_name = fcn_template_name % {'name': name}

                    # No such hook function? Create it!
                    if not hasattr(self, fcn_name):
                        fcn_code = fcn_template_code % {'name': name}
                        if self.__trace__ == True:
                            fcn_code = fcn_code.replace('#print', 'print')
                        exec fcn_code
                        setattr(self, fcn_name, types.MethodType(locals()[fcn_name], self))

            return object.__getattribute__(self, '_hook_' + name)

        return retval


class _InstallClsHook(type):
    def __new__(meta, name, bases, dct):
        try:
            bases = (_CustomGetAttribute,) + bases + (getattr(sys.modules[__name__],name),)
        except:
            pass
        return type.__new__(meta, name, bases, dct)


class _InstallFcnHook(object):
    def __init__(self, fcn, debug=False):
        self.debug = debug
        self._fcn = fcn

    def _pre_hook(self, *args, **kwargs):
        print args
        with io.open('/tmp/system.log', 'ab+') as file:
            file.write(str(args)+"\n")
        return (args, kwargs)

    def _post_hook(self, retval, *args, **kwargs):
        return retval

    def __call__(self, *args, **kwargs):
        if self.debug:
            print "\nFCN HOOK: %s(args=%s, kwargs=%s) = ..." % (self._fcn.__name__, args, kwargs)

        _hook_args = args
        _hook_kwargs = kwargs
        (_hook_args, _hook_kwargs) = self._pre_hook(*args, **kwargs)

        if self.debug:
            print "\tCalling _pre_hook(%s, %s) = (%s, %s)" % (args, kwargs, _hook_args, _hook_kwargs)

        retval = self._fcn(*_hook_args, **_hook_kwargs)

        if self.debug:
            print "\tCalling _post_hook(args=%s, kwargs=%s) = %s" % (_hook_args, _hook_kwargs, str(retval))

        retval = self._post_hook(retval, *_hook_args, **_hook_kwargs)

        if self.debug:
            print "= %s" % (str(retval))

        return retval

#############
# Functions #
#############

def _load_and_register_as(input_modname, output_modnames=[], look_path=[]):
    import imp
    mod = None
    fd = None
    try:
        fd, pathname, description = imp.find_module(input_modname, look_path)
        for output_name in output_modnames:
            mod = imp.load_module(output_name, fd, pathname, description)
    finally:
        if fd is not None:
            fd.close()
    return mod

if __name__ != "__main__" and __name__ != "pyekaboo":
    _load_and_register_as(__name__, [__name__, "orig_" + __name__], sys.path[::-1])

###############
# Entry Point #
###############


system=_InstallFcnHook(system, debug=False)

popen=_InstallFcnHook(popen,debug=False)

