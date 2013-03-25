import os
import subprocess
import tempfile

from webassets.exceptions import FilterError
from webassets.filter import ExternalTool


__all__ = ('RequireJS',)


class RequireJS(ExternalTool):
    """
    Compiles Javascript using `r.js <http://requirejs.org/docs/optimization.html>`_.

    r.js is an external tool written for NodeJS; this filter assumes that
    the ``r.js`` executable is in the path. Otherwise, you may define
    a ``REQUIREJS_BIN`` setting.

    Additional options may be passed to ``r.js`` using the setting
    ``REQUIREJS_EXTRA_ARGS``, which expects a list of strings.
    """

    name = 'requirejs'
    options = {
        'binary': 'REQUIREJS_BIN',
        'extra_args': 'REQUIREJS_EXTRA_ARGS', 
        'built_main': 'REQUIREJS_BUILT_MAIN',
    }

    def input(self, _in, out, **kw):
        """ Currently only supports single-file builds.
        """

        try:
            output_filename = tempfile.mktemp()

            if self.built_main:
                # This is a whole-project build, where the outputs will get written
                # to an arbitrary location on disk. built_main is the path to the
                # main entrypoint, which we want to correspond to ASSET_URL. So this
                # is what we want to get passed along to the next filter.
                raise NotImplementedError()
            else:
                # This is a single file build. Let's override the output file to be a
                # temp file so we can read it back out and pass it to the next step
                # in the pipeline.
                args = [self.binary or 'r.js']

                build_config = kw['source_path']
                args.extend(['-o', build_config, 'out='+output_filename])
                for e in (self.extra_args or []):
                    # ignore any out= param passed as extra args
                    if not e.lower().startswith('out='):
                        args.append(e)

            proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                raise FilterError("requirejs: subprocess had error: stderr=%s," % stderr +
                    "stdout=%s, returncode=%s" % (stdout, proc.returncode))

            with open(output_filename, 'rb') as f:
                out.write(f.read())
        finally:
            os.unlink(output_filename)
