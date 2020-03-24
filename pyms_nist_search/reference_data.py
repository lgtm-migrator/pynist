#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#  reference_data.py
#
#  This file is part of PyMassSpec NIST Search
#  Python interface to the NIST MS Search DLL
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  PyMassSpec NIST Search is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation; either version 3 of
#  the License, or (at your option) any later version.
#
#  PyMassSpec NIST Search is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  PyMassSpec NIST Search includes the redistributable binaries for NIST MS Search in
#  the x86 and x64 directories. Available from
#  ftp://chemdata.nist.gov/mass-spc/v1_7/NISTDLL3.zip .
#  ctnt66.dll and ctnt66_64.dll copyright 1984-1996 FairCom Corporation.
#  "FairCom" and "c-tree Plus" are trademarks of FairCom Corporation
#  and are registered in the United States and other countries.
#  All Rights Reserved.


# stdlib
import copy

# 3rd party
from pyms.Spectrum import MassSpectrum
from chemistry_tools.cas import cas_int_to_string

# this package
from .utils import parse_name_chars
from .base import NISTBase


class ReferenceData(NISTBase):
	def __init__(self, name='', cas='', nist_no=0, id=0, mw=0.0, formula='', contributor='', mass_spec=None, synonyms=None):
		"""
		
		:param name: The name of the compound
		:type name: str
		:param cas: The CAS number of the compound
		:type cas: str
		:param nist_no:
		:type nist_no:
		:param id:
		:type id:
		:param mw:
		:type mw:
		:param formula:
		:type formula:
		:param contributor:
		:type contributor:
		:param mass_spec:
		:type mass_spec:
		:param synonyms:
		:type synonyms:
		"""
		
		NISTBase.__init__(self, name, cas)
		
		self._formula = formula
		self._contributor = contributor
		
		self._nist_no = int(nist_no)
		self._id = int(id)
		
		self._mw = float(mw)
		
		if mass_spec is None:
			self._mass_spec = None
		elif isinstance(mass_spec, dict):
			self._mass_spec = MassSpectrum(**mass_spec)
		else:
			self._mass_spec = copy.copy(mass_spec)
		
		if synonyms is None:
			self._synonyms = []
		else:
			self._synonyms = synonyms[:]

	@property
	def formula(self):
		return self._formula
	
	@property
	def contributor(self):
		return self._contributor
	
	@property
	def nist_no(self):
		return int(self._nist_no)
	
	@property
	def id(self):
		return int(self._id)
	
	@property
	def mw(self):
		return int(self._mw)
	
	@property
	def mass_spec(self):
		return copy.copy(self._mass_spec)
	
	@property
	def synonyms(self):
		return self._synonyms[:]
	
	@classmethod
	def from_pynist(cls, pynist_dict):
		return cls(
				name=parse_name_chars(pynist_dict["name_chars"]),
				cas=cas_int_to_string(pynist_dict["cas"]),
				formula=pynist_dict["formula"],
				contributor=pynist_dict["contributor"],
				nist_no=pynist_dict["nist_no"],
				id=pynist_dict["id"],
				mw=pynist_dict["mw"],
				mass_spec=MassSpectrum(pynist_dict["mass_list"], pynist_dict["intensity_list"]),
				synonyms=[parse_name_chars(synonym) for synonym in pynist_dict["synonyms_chars"]],
				)
	
	def __repr__(self):
		return f"Reference Data: {self.name} \t({self.cas})"
	
	def __dict__(self):
		return dict(
				name=self._name,
				cas=self.cas,
				formula=self.formula,
				contributor=self.contributor,
				nist_no=self.nist_no,
				id=self.id,
				mw=self.mw,
				mass_spec=copy.copy(self.mass_spec),
				synonyms=self.synonyms[:],
				)
