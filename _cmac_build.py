"""Build-time customization for the ``cmac.calc_kdp_ray_fir`` Cython extension.

Two parts of the extension build cannot be expressed statically in
``pyproject.toml``: NumPy's C header directory is only discoverable once
NumPy is importable, and ``[tool.setuptools] ext-modules`` cannot express
``define-macros`` two-tuples. Both are applied here and wired up through
``[tool.setuptools.cmdclass]``, so no ``setup.py`` is needed.
"""

from setuptools.command.build_ext import build_ext as _build_ext

# Compile against the stable NumPy C API rather than the deprecated one.
NUMPY_API_MACRO = ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")


class build_ext(_build_ext):
    """``build_ext`` that resolves the NumPy include directory at build time."""

    def finalize_options(self):
        super().finalize_options()
        import numpy

        self.include_dirs.append(numpy.get_include())
        for ext in self.distribution.ext_modules or []:
            ext.define_macros.append(NUMPY_API_MACRO)
