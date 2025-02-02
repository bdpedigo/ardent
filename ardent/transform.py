# Transform is the primary class in ARDENT.

# import statements.
import numpy as np
import torch
from .presets import get_registration_preset
from .lddmm.transformer import Transformer
from .lddmm.transformer import torch_register
from .lddmm.transformer import torch_apply_transform
# TODO: rename io as fileio to avoid conflict with standard library package io?
# from .io import save as io_save
from . import io
from pathlib import Path
import pickle

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
    
    @staticmethod
    def _handle_registration_parameters(preset:str, params:dict) -> dict:
        """
        Provide default parameters based on <preset>, superseded by the provided parameters <params>.
        
        Arguments:
            preset {str} -- A string keyed to a particular set of registration parameters.
            params {dict} -- A dictionary of registration parameters expressly provided by the user.
        
        Returns:
            dict -- A dictionary of the registration parameters resulting from <preset> updated by <params>.
        """

        # Get default registration parameters based on <preset>.
        preset_parameters = get_registration_preset(preset) # Type: dict.

        # Supplement and supplant with <params> from the caller.
        preset_parameters.update(params)

        return preset_parameters


    # TODO: argument validation and resolution scalar to triple correction.
    def register(self, template:np.ndarray, target:np.ndarray, template_resolution=[1,1,1], target_resolution=[1,1,1], 
        preset=None, sigmaR=None, eV=None, eL=None, eT=None, 
        A=None, v=None, **kwargs) -> None:
        """
        Perform a registration using transformer between template and target.
        Populates attributes for future calls to the apply_transform method.
        
        Arguments:
            template {np.ndarray} -- Image to target.
            target {np.ndarray} -- Image to be registered to.
        
        Keyword Arguments:
            template_resolution {scalar, list} -- Per-axis resolution of template. (default: {[1,1,1]})
            target_resolution {scalar, list} -- Per-axis resolution of target. (default: {[1,1,1]})
            preset {string, NoneType} -- Preset of registration parameters. 
                If any of those values are provided anyway, the provided values supersede the corresponding preset values.
                Supported options:
                    'identity'
                    'clarity, mouse'
                    'nissl, mouse'
                    'mri, human'
                (default: {None})
            sigmaR {float} -- Deformation allowance. (default: {None})
            eV {float} -- Deformation step size. (default: {None})
            eL {float} -- Linear transformation step size. (default: {None})
            eT {float} -- Translation step size. (default: {None})
            A {np.ndarray, NoneType} -- Initial affine transformation. (default: {None})
            v {np.ndarray} -- Initial velocity field. (default: {None})
        
        Returns:
            None -- Sets internal attributes and returns None.
        """

        # Collect registration parameters from chosen caller.
        registration_parameters = dict(sigmaR=sigmaR, eV=eV, eL=eL, eT=eT, **kwargs)
        registration_parameters = {key : value for key, value in registration_parameters.items() if value is not None}
        # Fill unspecified parameters with presets if applicable.
        if preset is not None:
            registration_parameters = Transform._handle_registration_parameters(preset, registration_parameters)

        # Instantiate transformer as a new Transformer object.
        # self.affine and self.v will not be None if this Transform object was read with its load method or if its register method was already called.
        transformer = Transformer(I=template, J=target, Ires=template_resolution, Jres=target_resolution, 
                                    transformer=self.transformer, sigmaR=registration_parameters['sigmaR'], A=A, v=v)

        outdict = torch_register(template, target, transformer, **registration_parameters)
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
        """
        Apply the transformation--computed by the last call to self.register--to subject, 
        deforming it into the space of <deform_to>.
        
        Arguments:
            subject {np.ndarray} -- The image to deform.
        
        Keyword Arguments:
            deform_to {str} -- Either 'template' or 'target' indicating which to deform <subject> to match. (default: {"template"})
            save_path {str, Path} -- The full path to save the output to. (default: {None})
        
        Returns:
            np.ndarray -- The result of deforming <subject> to match <deform_to>.
        """

        deformed_subject = torch_apply_transform(image=subject, deform_to=deform_to, transformer=self.transformer)
        
        if save_path is not None:
            io.save(deformed_subject, save_path)

        return deformed_subject

    
    def save(self, file_path):
        """
        Save the entire instance of this Transform object (self) to file.
        
        Arguments:
            file_path {str, Path} -- The full path to save self to.
        """

        io.save_pickled(self, file_path)


        """Loads an entire object instance from memory and transplants all of its writeable attributes into self."""
    def load(self, file_path):
        """
        Load an entire instance of a Transform object from memory, as from a file created with the save method, 
        and transplants all of its writeable attributes into self.
        
        Arguments:
            file_path {str, Path} -- The full path that a Transform object was saved to.
        """

        transform = io.load_pickled(file_path)

        self.__dict__.update(transform.__dict__)