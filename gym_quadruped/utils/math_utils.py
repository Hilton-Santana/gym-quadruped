import numpy as np
from scipy.spatial.transform import Rotation


def skew(x):
    """Skew symmetric matrix from a 3D vector."""
    return np.array([[0, -x[2], x[1]],
                     [x[2], 0, -x[0]],
                     [-x[1], x[0], 0]])


def homogenous_transform(vec: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Apply a homogeneous transformation matrix to a 3D vector.

    Args:
    ----
        vec: (3,) vector
        X: (4, 4) homogeneous transformation matrix

    Returns:
    -------
        (3,) vector
    """
    assert vec.flatten().shape == (3,), f"Expected 3D vector, got {vec} of shape {vec.shape}"
    assert X.shape == (4, 4) and X[3, 3] == 1, f"Expected homogeneous transformation matrix, got {X}"
    pos_hom = np.concatenate([vec.flatten(), [1]])
    X_pos_hom = X @ pos_hom
    return X_pos_hom[:3]


def hom2pos_quatwxyz(X: np.ndarray):
    assert X.shape == (4, 4), f"Expected homogeneous transformation matrix, got {X}"
    pos = X[:3, 3]
    quat_xyzw = Rotation.from_matrix(X[:3, :3]).as_quat()