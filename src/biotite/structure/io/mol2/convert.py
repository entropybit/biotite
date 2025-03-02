# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

__name__ = "biotite.structure.io.mol2"
__author__ = "Benjamin E. Mayer"
__all__ = [
    "get_structure", "set_structure",
    "get_charges", "set_charges",
    "get_model_count"
]


def get_structure(mol2_file, model=None):
    """
    Get an :class:`AtomArray` from the MOL2 File.

    Ths function is a thin wrapper around
    :meth:`MOL2File.get_structure()`.

    Parameters
    ----------
    mol2_file : MOL2File
        The MOL2File.

    Returns
    -------
    array : AtomArray, AtomArrayStack
        Return an AtomArray or AtomArrayStack containing the structure or
        structures depending on if file contains single or multiple models.
        If something other then `NO_CHARGE` is set in the charge_type field
        of the according mol2 file, the AtomArray or AtomArrayStack will
        contain the charge field.
    """
    return mol2_file.get_structure(model)


def set_structure(mol2_file, atoms):
    """
    Set the :class:`AtomArray` for the MOL2 File.

    Ths function is a thin wrapper around
    :meth:`MOL2File.set_structure(atoms)`.

    Parameters
    ----------
    mol2_file : MOL2File
        The XYZ File.
    array : AtomArray
        The array to be saved into this file.
        Must have an associated :class:`BondList`.
        If charge field set this is used for storage within the according
        MOL2 charge column.
    """
    mol2_file.set_structure(atoms)


def get_charges(mol2_file):
    """
    Get an ndarray containing the partial charges from the MOL2File

    This function is a thin wrapper around
    :meth:`MOL2File.get_charges()`.

    Parameters
    ----------
    xyz_file : XYZFile
        The XYZ File.

    Returns
    -------
    array : AtomArray
        This :class:`AtomArray` contains the optional ``charge``
        annotation and has an associated :class:`BondList`.
        All other annotation categories, except ``element`` are
        empty.
    """
    return mol2_file.get_charges()


def set_charges(mol2_file, charges):
    """
    Set the partial charges in the MOL2File to an ndarray
    specified as parameter here.

    Ths function is a thin wrapper around
    :meth:`MOL2File.set_charges(charges)`.

    Parameters
    ----------
    mol2_file: MOL2File
        The MOL2File
    charges: ndarray
        A ndarray containing data with `float` type to be written as
        partial charges.

    """
    return mol2_file.set_charges(charges)


def get_model_count(mol2_file):
    """
    Get the number of models contained in the xyz file.

    This function is a thin wrapper around
    :meth:`MOL2File.get_model_count()`.

    Returns
    -------
    model_count : int
        The number of models.
    """
    return mol2_file.get_model_count()
