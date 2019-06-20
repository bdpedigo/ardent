# Transform is the primary class in ARDENT.

# import statements.
import numpy as np
from .lddmm.transformer import torch_register
from .lddmm.transformer import torch_apply_transform
from .io import save as io_save
# TODO: rename io as fileio.
from pathlib import Path

class Transform():
    """transform stores the deformation that is output by a registration 
    and provides methods for applying that transformation to various images."""
    
    def __init__(self):
        """Initialize Transform object. If used without arguments, sets attributes 
        to None. 
        TODO: Add option to register on initialization?"""

        # Create attributes.
        self.phis = None
        self.phiinvs = None
        self.Aphis = None
        self.phiinvAinvs = None
        self.affine = None

        self.transformer = None
    

    def register(self, template:np.ndarray, target:np.ndarray, sigmaR, eV, eL=0, eT=0, **kwargs) -> None:
        """Perform a registration using transformer between template and target. 
        Populates attributes for future calls to the apply_transform method."""

        outdict = torch_register(template, target, sigmaR, eV, eL=0, eT=0, **kwargs)
        '''outdict contains:
            - phis
            - phiinvs
            - Aphis
            - phiinvAinvs
            - A

            - transformer
        '''

        # Populate attributes.
        self.phis = outdict['phis']
        self.phiinvs = outdict['phiinvs']
        self.Aphis = outdict['Aphis']
        self.phiinvAinvs = outdict['phiinvAinvs']
        self.affine = outdict['A']

        self.transformer = outdict['transformer']


    def apply_transform(self, subject:np.ndarray, deform_to="template", save_path=None) -> np.ndarray:
        """Apply the transformation--computed by the last call to self.register--
        to <subject>, deforming it into the space of <deform_to>."""

        deformed_subject = torch_apply_transform(image=subject, deform_to=deform_to, Aphis=self.Aphis, phiinvAinvs=self.phiinvAinvs, transformer=self.transformer)
        
        if save_path is not None:
            io_save(deformed_subject, save_path)

        return deformed_subject

    
    def save(self, file_path):
        """Saves the following attributes to file_path: phis, phiinvs, Aphis, phiinvAinvs, & A.
        The file is saved in .npz format."""

        attribute_dict = {
            'phis':self.phis,
            'phiinvs':self.phiinvs,
            'Aphis':self.Aphis,
            'phiinvAinvs':self.phiinvAinvs,
            'affine':self.affine
            }
        
        io_save(attribute_dict, file_path)

    def load(self, file_path):
        """Loads the following attributes from file_path: phis, phiinvs, Aphis, phiinvAinvs, & A.
        Presently they can only be accessed. This is not sufficient to run apply_transform 
        without first running register."""

        # Validate file_path.
        file_path = Path(file_path)
        if not file_path.suffix:
            file_path = file_path.with_suffix('.npz')
        elif file_path.suffix != '.npz':
            raise ValueError(f"file_path may not have an extension other than .npz.\n"
                f"file_path.suffix: {file_path.suffix}.")
        # file_path is appropriate.

        with np.load(file_path) as attribute_dict:
            self.phis = attribute_dict['phis']
            self.phiinvs = attribute_dict['phiinvs']
            self.Aphis = attribute_dict['Aphis']
            self.phiinvAinvs = attribute_dict['phiinvAinvs']
            self.affine = attribute_dict['affine']
        