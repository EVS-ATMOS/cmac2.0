"""Build-time customization for the ``cmac.calc_kdp_ray_fir`` Cython extension.

Three parts of the extension build cannot be expressed statically in
``pyproject.toml``: NumPy's C header directory is only discoverable once
NumPy is importable, ``[tool.setuptools] ext-modules`` cannot express
``define-macros`` two-tuples, and the interpreter's own ``CFLAGS`` may name
options the available compiler does not accept. All three are applied here
and wired up through ``[tool.setuptools.cmdclass]``, so no ``setup.py`` is
needed.
"""

import os
import re
import subprocess
import tempfile

from setuptools.command.build_ext import build_ext as _build_ext

# Compile against the stable NumPy C API rather than the deprecated one.
NUMPY_API_MACRO = ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")

# gcc: "unrecognized command-line option '-partition=none'"
# clang: "unknown argument: '-partition=none'"
# GCC quotes with U+2018/U+2019 under a UTF-8 locale, so the quoting around
# the flag is matched loosely rather than assumed to be ASCII.
QUOTES = "\"'`\u2018\u2019\u201c\u201d"
UNSUPPORTED_FLAG = re.compile(
    r"(?:unrecognized\s+(?:command[-\s]line\s+)?option"
    r"|unknown\s+argument:?)"
    r"\s*[" + QUOTES + r"]*\s*"
    r"(-[^\s,;()" + QUOTES + r"]+)",
    re.IGNORECASE,
)

# Ask the compiler for ASCII diagnostics so the pattern above has the easiest
# possible job; the loose quoting stays as a backstop if this is ignored.
C_LOCALE_ENV = dict(os.environ, LC_ALL="C", LANG="C")

# Every compiler/linker command line distutils may hand us. Which of these
# exist varies with the setuptools version, so they are probed by name.
FLAG_ATTRS = (
    "compiler",
    "compiler_so",
    "compiler_so_cxx",
    "compiler_cxx",
    "linker_so",
    "linker_so_cxx",
    "linker_exe",
)


def _rejected_flags(command, source):
    """Return the flags in ``command`` that the compiler refuses outright.

    Returns an empty set when the trial compile succeeds, and also when it
    fails for any other reason -- this is a best-effort cleanup, so a real
    build error is left for the real build to report.
    """
    probe = subprocess.run(
        list(command) + ["-c", source, "-o", os.devnull],
        capture_output=True,
        text=True,
        env=C_LOCALE_ENV,
    )
    if probe.returncode == 0:
        return set()
    return set(UNSUPPORTED_FLAG.findall(probe.stderr))


def drop_unsupported_flags(compiler):
    """Strip options the compiler rejects from ``compiler``'s command lines.

    A conda-forge interpreter records the flags of whichever GCC built it in
    ``sysconfig``'s ``CFLAGS``, and ``customize_compiler`` copies those into
    every command line verbatim. When the compiler doing the building is not
    that same GCC -- an older system gcc, or a conda toolchain pinned a
    release behind -- the build dies on an option it has never heard of, e.g.
    ``-partition=none`` from GCC 16. Dropping those flags costs nothing: they
    are optimization and LTO tuning, not semantics.
    """
    if not getattr(compiler, "compiler_so", None):
        return set()

    dropped = set()
    with tempfile.TemporaryDirectory() as tmpdir:
        source = os.path.join(tmpdir, "flag_probe.c")
        with open(source, "w") as handle:
            handle.write("int main(void) { return 0; }\n")

        # Each pass can only surface the flags the compiler reaches before
        # giving up, so re-probe until it stops complaining. The bound just
        # guarantees termination if a flag somehow survives removal.
        for _ in range(8):
            rejected = _rejected_flags(compiler.compiler_so, source) - dropped
            if not rejected:
                break
            dropped |= rejected
            for attr in FLAG_ATTRS:
                command = getattr(compiler, attr, None)
                if command:
                    setattr(
                        compiler,
                        attr,
                        [arg for arg in command if arg not in rejected],
                    )
    return dropped


class build_ext(_build_ext):
    """``build_ext`` that resolves NumPy's headers and sanitizes CFLAGS."""

    def finalize_options(self):
        super().finalize_options()
        import numpy

        self.include_dirs.append(numpy.get_include())
        for ext in self.distribution.ext_modules or []:
            ext.define_macros.append(NUMPY_API_MACRO)

    def build_extensions(self):
        # Runs after distutils has built self.compiler from sysconfig.
        dropped = drop_unsupported_flags(self.compiler)
        if dropped:
            self.announce(
                "dropping compiler flags not supported by this compiler: "
                + " ".join(sorted(dropped)),
                level=2,
            )
        super().build_extensions()
