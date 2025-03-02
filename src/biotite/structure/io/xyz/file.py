# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

__name__ = "biotite.structure.io.xyz"
__author__ = "Benjamin E. Mayer"
__all__ = ["XYZFile"]

import numpy as np
from ...atoms import AtomArray, AtomArrayStack, Atom
import biotite.structure as struc
from ....file import TextFile


# Number of header lines
N_HEADER = 2


class XYZFile(TextFile):
    """
    This class represents a file in XYZ format, which is a very simple
    file format where only a molecule_name in form of a string and the
    number of atoms is contained in the header.
    Followed by as many lines containing atom element and 3D coordinates.

    References
    ----------

    .. footbibliography::

    Examples
    --------

    >>> from os.path import join
    >>> mol_file = XYZFile.read(
    ...     join(path_to_structures, "molecules", "BENZ.xyz")
    ... )
    >>> atom_array = xyz_file.get_structure()
    >>> print(atom_array)
            0             C         0.000    1.403    0.000
            0             H         0.000    2.490    0.000
            0             C        -1.215    0.701    0.000
            0             H        -2.157    1.245    0.000
            0             C        -1.215   -0.701    0.000
            0             H        -2.157   -1.245    0.000
            0             C         0.000   -1.403    0.000
            0             H         0.000   -2.490    0.000
            0             C         1.215   -0.701    0.000
            0             H         2.157   -1.245    0.000
            0             C         1.215    0.701    0.000
            0             H         2.157    1.245    0.000

    """
    def __init__(self):
        super().__init__()
        # empty header lines
        self.lines = [""] * N_HEADER
        # internal variables for storing and writing the header
        self._mol_names = None
        self._atom_numbers = None
        self._model_start_inds = None
        self._structures = None
        self._model_start_inds = None

    def __update_start_lines(self):
        """
        Internal function that is used to update the _model_start_inds
        private member variable where the indices of where a new
        model within the xyz file read starts is stored.
        """
        # Line indices where a new model starts -> where number of atoms
        # is written down as number
        self._model_start_inds = np.array(
            [
                i for i in range(len(self.lines))
                if self.lines[i].strip().isdigit()
            ],
            dtype=int
         )

        if self._model_start_inds.shape[0] > 1:
            # if the mol name line only contains an integer
            # these lines will appear in model_start_inds
            # if calculated as above, therfore we purge all
            # indices that have a distance of 1 to their previous index
            # (this will not work with a file containing multiple models
            #  with solely one coordinate / atom per model )
            self._model_start_inds = self._model_start_inds[
                np.concatenate(
                    (
                        np.array([0], dtype=int),
                        np.where(
                            self._model_start_inds[:-1]
                            -
                            self._model_start_inds[1:]
                            !=
                            -1
                        )[0]+1
                    )
                )
            ]
        elif self._model_start_inds.shape[0] == 2:
            self._model_start_inds = self._model_start_inds[:1]

    def __get_number_of_atoms(self):
        """
        This calculates the number of atoms from the previously read
        file.
        """
        lines_parsed = [x.split() for x in self.lines]
        # All lines containing less then 4 elements after split() have
        # to be header lines based upon the structure of an xyz file.
        inds = np.array(
            [
                i for i in range(
                    len(lines_parsed)
                ) if len(lines_parsed[i]) != 4
            ]
        )
        print(inds.astype(int))
        print(np.array(self.lines)[inds.astype(int)])
        print(inds.shape[0]/2)
        # If there is only one model contained we can simply count
        # and return the number of lines after the header.
        if inds.shape[0] <= 2:
            return [int(len(self.lines[2:]))]
        # otherwise if there are multiple models we can get atom
        # count lines by only considering the first of the two lines
        # per model
        else:
            num_atoms = int(inds.shape[0]/2)
            inds = np.array([inds[2*i] for i in range(num_atoms)])
            line_lengths = np.array(self.lines)[inds.astype(int)]
            return line_lengths

    def get_model_count(self):
        """
        Get the number of models contained in the xyz file.

        Returns
        -------
        model_count : int
            The number of models.
        """
        return len(self.__get_number_of_atoms())

    def get_header(self, model=None):
        """
        Get the header from the XYZ file.

        Parameters
        ----------
        model: int, optional
            Specifies for which of the models contained in this XYZFile
            the according header should be returned.

        Returns
        -------
        atom_number: int
            The number of atoms per model
        mol_name : str
            The name of the molecule or the names of the multiple models
        """
        # Line indices where a new model starts -> where number of atoms
        # is written down as number
        self.__update_start_lines()
        # parse all atom_numbers into integers
        if self._atom_numbers is None:
            self._atom_numbers = [
                int(
                    self.lines[i].strip().strip(" ")
                ) for i in self._model_start_inds
            ]
        # parse all lines containing names
        if self._mol_names is None:
            self._mol_names = [
                self.lines[i+1].strip() for i in self._model_start_inds
            ]

        if model is not None:
            if model > len(self._atom_numbers):
                msg = "Tried to get header of model ["+str(model) + "]."
                msg += " But has only " + str(len(self._atom_numbers))
                msg += " many models."
                raise ValueError(msg)
            else:
                return self._atom_numbers[model], self._mol_names[model]
        elif len(self._atom_numbers) == 1:
            return self._atom_numbers[0], self._mol_names[0]
        else:
            return self._atom_numbers, self._mol_names

    def set_header(self, mol_name, model=None):
        """
        Set the header for the XYZ file.
        As the header consist only out of the mol_name and the number
        of atoms in the structure / structures this can only be
        used after setting a structure. Since the second line
        is calculated by counting the

        Parameters
        ----------
        mol_name : str
            The name of the molecule.
        model: int, optional
            If this parameter is set only the molecule name of the
            specified models header will be modified.
        """

        # call get_header first if member variables are still None
        # meaning if header hasn't been read yet
        if self._mol_names is None:
            self.get_header()

        if model is not None:
            if len(self._mol_names) > model:
                self._mol_names[model] = mol_name
            else:
                msg = "Specified model value [" + str(model) + "] is not"
                msg += "compatible with number of models ["
                msg += str(self.get_model_count()) + "]"
                raise ValueError(
                    msg
                )
        elif (len(self.lines) > 2):
            self.lines[1] = str(mol_name)
            self.lines[0] = str(self.__get_number_of_atoms()[0])
            self._mol_names = [mol_name]
            self._atom_numbers = [int(self.lines[0])]
            self.__update_start_lines()
        else:
            raise ValueError(
                    "Can not set header of an empty XYZFile"
                    "Use set_structure first, so that number of atoms"
                    "can be derived from set structure"
                )

    def get_structure(self, model=None):
        """
        Get an :class:`AtomArray` or :class:`AtomArrayStack` from the XYZ file.

        Parameters
        ----------
        model : int, optional
            If this parameter is given, the function will return an
            :class:`AtomArray` from the atoms corresponding to the given
            model number (starting at 1).
            Negative values are used to index models starting from the
            last model insted of the first model.
            If this parameter is omitted, an :class:`AtomArrayStack`
            containing all models will be returned, even if the
            structure contains only one model.

        Returns
        -------
        array : AtomArray or AtomArrayStack
            The return type depends on the `model` parameter.
        """

        if len(self.lines) <= 2:
            raise ValueError(
                        "Trying to get_structure from empty XYZFile"
            )
        atom_number, names = self.get_header()
        # set a default head if non present since
        # the number of lines will be calculated from the number
        # of atoms field in the file (counts how many lines with numbers
        # there are within the file which are not name lines)
        if names is None or atom_number is None:
            self.set_header("[MOLNAME]")
        self.__update_start_lines()
        # parse all atom_numbers into integers
        if self._atom_numbers is None:
            self._atom_numbers = [
                int(
                    self.lines[i].strip().strip(" ")
                ) for i in self._model_start_inds
            ]
        # parse all lines containing names
        if self._mol_names is None:
            self._mol_names = [
                self.lines[i+1].strip() for i in self._model_start_inds
            ]
        # parse all coordinates
        if self._structures is None:
            array_stack = []
            for i, ind in enumerate(self._model_start_inds):
                ind_end = ind+2 + self._atom_numbers[i]
                lines_cut = self.lines[ind:ind_end]
                array = AtomArray(self._atom_numbers[i])
                if self._atom_numbers[i]+2 != len(lines_cut):
                    raise ValueError(
                        "Number of Atoms not matching with coordinate lines"
                        + ""
                        + " atom_number :: " + str(self._atom_numbers[i])
                        + ""
                        + ""
                        + " |lines_cut| :: " + str(len(lines_cut))
                        + " lines_cut   :: " + str(lines_cut)
                    )

                for j, line in enumerate(lines_cut[2:]):
                    line_parsed = [
                        x for x in line.strip().split(" ") if x != ''
                    ]
                    x = float(line_parsed[1])
                    y = float(line_parsed[2])
                    z = float(line_parsed[3])

                    if np.isnan(x) or np.isnan(y) or np.isnan(z):
                        raise ValueError(
                            "At least one of the coordinates is NaN"
                            ""
                            "(" + str(x) + "," + str(y) + "," + str(z) + ")"
                            ""
                        )
                    atom = Atom([x, y, z])
                    atom.element = line_parsed[0]
                    array[j] = atom

                array_stack.append(array)
            self._structures = struc.stack(array_stack)

        if model is None:
            if self._structures.shape[0] == 1:
                return self._structures[0]
            else:
                return self._structures
        else:
            return self._structures[model]

    def set_structure(self, atoms):
        """
        Set the :class:`AtomArray` :class:`AtomArrayStack` or for the file.
        Based upon the given type of the atoms parameter either a single
        model or multiple model XYZFile will be contained within the
        lines member variable of this XYZFile instance.

        Parameters
        ----------
        atoms : AtomArray, AtomArrayStack
            The array to be saved into this file.
        """

        if isinstance(atoms, AtomArray):
            n_atoms = atoms.shape[0]
            self.lines[0] = str(n_atoms)
            if len(self.lines[1]) == 0:
                self.lines[1] = str("[MOLNAME]")

            self.lines += [""] * n_atoms
            for i, atom in enumerate(atoms):
                line = "  " + str(atom.element)
                line += " {:<11.{}f}".format(atom.coord[0], 6)
                line += "    {:<11.{}f}".format(atom.coord[1], 6)
                line += "    {:<11.{}f}".format(atom.coord[2], 6)
                line += " "
                self.lines[i+2] = line
        elif isinstance(atoms, AtomArrayStack):
            n_lines_per_model = atoms[0].shape[0]+2
            self.lines += [""] * n_lines_per_model*atoms.shape[0]
            for i, atoms_i in enumerate(atoms):
                self.lines[i*n_lines_per_model] = str(atoms[0].shape[0])
                self.lines[i*n_lines_per_model+1] = " " + str(i)
                for j, atom in enumerate(atoms_i):
                    line = "  " + str(atom.element)
                    print(atom.coord)
                    line += " {:>11.{}f}".format(atom.coord[0], 6)
                    line += "    {:>11.{}f}".format(atom.coord[1], 6)
                    line += "    {:>11.{}f}".format(atom.coord[2], 6)
                    line += " "
                    self.lines[i*n_lines_per_model+j+2] = line
