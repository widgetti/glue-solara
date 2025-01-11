import numpy as np
from glue.core.roi import Projected3dROI, UndefinedROI
from scipy.spatial import Delaunay


# Needs to be a subclass of Projected3dROI for glue to use the right call (contains3d) in
# https://github.com/glue-viz/glue/blob/d59f708bd6ef1df6fe6e8f081eba91b28a1fa57d/glue/core/subset.py#L606
# TODO: Add ConvexHullROI to glue
class ConvexHullROI(Projected3dROI):
    """
    A convex hull region of interest defined by a set of points in 3D space.
    The points are defined by front-end (threeJS) coordinates, which use a y-up coordinate system,
    and are scaled by the model_scaling_factor from `glue_solara.viewers.xr.layer_state.XRScatterLayerState`.

    Parameters
    ----------
    hull_array : array-like
        An array of shape (N, 3) of points in 3D space that define the convex hull.
    """

    def __init__(self, hull_array=None):
        super().__init__()
        self.hull = Delaunay(hull_array)

    def update_selection(self, hull_array):
        self.hull = Delaunay(hull_array)

    def contains3d(self, x, y, z):
        if not self.defined():
            raise UndefinedROI

        mask = np.zeros(x.shape, dtype=bool)

        # Apparently threeJS uses a y-up coordinate system, as per
        # https://threejs.org/docs/index.html#api/en/math/Matrix4
        # TODO: Make this more explicit
        for i, p in enumerate(zip(y, z, x)):
            s = self.hull.find_simplex(p)
            if s >= 0:
                mask[i] = 1

        return mask

    def defined(self):
        return len(self.hull.points) > 0

    def __gluestate__(self, context):
        return dict(hull_array=self.hull.points)

    @classmethod
    def __setgluestate__(cls, rec, context):
        return cls(hull_array=context.object(rec["hull_array"]))
