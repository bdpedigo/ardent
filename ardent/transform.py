# Transform is the primary class in ARDENT.

# import statements.
import numpy as np
import torch
from .presets import get_registration_presets
from .lddmm.transformer import Transformer
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

        self.transformer = None # To be instantiated in the register method.
        self.v = None # Attribute of self.transformer.
    
    @staticmethod
    def _handle_registration_parameters(preset:str, params:dict) -> dict:
        """Provides default parameters based on <preset>, superseded by the provided parameters params.
        Returns a dictionary with the resultant parameters."""

        # Get default registration parameters based on <preset>.
        preset_parameters = get_registration_presets(preset) # Type: dict.

        # Supplement and supplant with <params> from the caller.
        preset_parameters.update(params)

        return preset_parameters

    # TODO: argument validation and resolution scalar to triple correction.
    def register(self, template:np.ndarray, target:np.ndarray, template_resolution=[1,1,1], target_resolution=[1,1,1],
        preset=None, sigmaR=None, eV=None, eL=None, eT=None, **kwargs) -> None:
        """Perform a registration using transformer between template and target. 
        Populates attributes for future calls to the apply_transform method.
        
        If used, <preset> will provide default values for sigmaR, eV, eL, and eT, 
        superseded by any such values that are provided.

        <preset> options:
        'clarity'
        """


        # Collect registration parameters from chosen caller.
        registration_parameters = dict(sigmaR=sigmaR, eV=eV, eL=eL, eT=eT, **kwargs)
        registration_parameters = {key : value for key, value in registration_parameters.items() if value is not None}
        # Fill unspecified parameters with presets if applicable.
        if preset is not None:
            registration_parameters = Transform._handle_registration_parameters(preset, registration_parameters)

        # Instantiate transformer as a new Transformer object.
        # self.affine and self.v will not be None if this Transform object was read with its load method or if its register method was already called.
        transformer = Transformer(I_shape=template.shape, J_shape=target.shape, Ires=template_resolution, Jres=target_resolution, A=self.affine, v=self.v)
        """See WARNING in Transformer.__init__ for a confession of this heinousness."""
        transformer.I = torch.tensor(template, dtype=transformer.dtype, device=transformer.device)
        transformer.J = torch.tensor(target, dtype=transformer.dtype, device=transformer.device)


        outdict = torch_register(template, target, transformer, **registration_parameters)
        '''outdict contains:
            - phis
            - phiinvs
            - Aphis
            - phiinvAinvs
            - A

            - transformer
            - v
            - I_shape
            - J_shape
            - Ires
            - Jres
        '''

        # Populate attributes.
        self.phis = outdict['phis']
        self.phiinvs = outdict['phiinvs']
        self.Aphis = outdict['Aphis']
        self.phiinvAinvs = outdict['phiinvAinvs']
        self.affine = outdict['A']

        # Populate attributes of shame.
        self.transformer = outdict['transformer']
        self.v = outdict['v']
        self.I_shape = outdict['I_shape']
        self.J_shape = outdict['J_shape']
        self.Ires = outdict['Ires']
        self.Jres = outdict['Jres']


    def apply_transform(self, subject:np.ndarray, deform_to="template", save_path=None) -> np.ndarray:
        """Apply the transformation--computed by the last call to self.register--
        to <subject>, deforming it into the space of <deform_to>."""

        deformed_subject = torch_apply_transform(image=subject, deform_to=deform_to, transformer=self.transformer)
        
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
            'affine':self.affine,

            'v':self.transformer.v.cpu().numpy(),
            'I_shape':self.I_shape,
            'J_shape':self.J_shape,
            'Ires':self.Ires,
            'Jres':self.Jres,
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

            self.v = attribute_dict['v']
            self.I_shape = attribute_dict['I_shape']
            self.J_shape = attribute_dict['J_shape']
            self.Ires = attribute_dict['Ires']
            self.Jres = attribute_dict['Jres']
            self.transformer = Transformer(I_shape=I_shape, J_shape=J_shape, Ires=Ires, Jres=Jres, A=self.affine, v=self.v)