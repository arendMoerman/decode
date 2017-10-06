# coding: utf-8

# public items
__all__ = []

# standard library
from collections import OrderedDict

# dependent packages
import decode as dc
import numpy as np
import xarray as xr
from astropy.io import fits
from ..classes import BaseAccessor

# local constants
XCOORDS = lambda array: OrderedDict([
    ('ra', ('x', np.zeros(array.shape[0], dtype=float))),
])

YCOORDS = lambda array: OrderedDict([
    ('dec', ('y', np.zeros(array.shape[1], dtype=float))),
])

CHCOORDS = lambda array: OrderedDict([
    ('kidid', ('ch', np.zeros(array.shape[2], dtype=float))),
    ('kidfq', ('ch', np.zeros(array.shape[2], dtype=float))),
])

SCALARCOORDS = OrderedDict([
    ('coordsys', 'RADEC'),
    ('xref', 0.0),
    ('yref', 0.0),
])


# classes
@xr.register_dataarray_accessor('dcc')
class DecodeCubeAccessor(BaseAccessor):
    def __init__(self, array):
        """Initialize the Decode accessor of an array.

        Note:
            This method is only for the internal use.
            Users can create an array with Decode accessor using dc.array.

        Args:
            array (xarray.DataArray): An array to which Decode accessor is added.

        """
        super().__init__(array)

    def _initcoords(self):
        """Initialize coords with default values.

        Warning:
            Do not use this method after an array is created.
            This forcibly replaces all vaules of coords with default ones.

        """
        self.coords.update(XCOORDS(self))
        self.coords.update(YCOORDS(self))
        self.coords.update(CHCOORDS(self))
        self.coords.update(SCALARCOORDS)

    def fromarray(self, x_grid, y_grid):
        array   = self._dataarray.copy()
        nx_grid = len(x_grid)
        ny_grid = len(y_grid)
        nz_grid = len(array.ch)

        if isinstance(x_grid, list):
            x_grid = xr.DataArray(np.array(x_grid), dims='grid')
        elif isinstance(x_grid, np.ndarray):
            x_grid = xr.DataArray(x_grid, dims='grid')

        if isinstance(y_grid, list):
            y_grid = xr.DataArray(np.array(y_grid), dims='grid')
        elif isinstance(y_grid, np.ndarray):
            y_grid = xr.DataArray(y_grid, dims='grid')

        i     = np.abs(self.x - x_grid).argmin('grid')
        j     = np.abs(self.y - y_grid).argmin('grid')
        index = i + j * nx_grid

        array.coords.update({'index': index})
        griddedarray = array.groupby('index').mean('t')
        cubedata     = griddedarray.values.reshape((ny_grid, nx_grid, nz_grid)).swapaxes(0, 1)

        xcoords  = {'ra': x_grid.values}
        ycoords  = {'dec': y_grid.values}

        return dc.cube(cubedata, xcoords=xcoords, ycoords=ycoords)
