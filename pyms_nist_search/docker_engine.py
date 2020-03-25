#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  docker_engine.py
"""
Search engine for Linux and other platforms supporting Docker
"""
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
import atexit
import json
import os
import time

# 3rd party
import docker
import docker.errors
import requests
from pyms.Spectrum import MassSpectrum

# this package
from .json import PyNISTEncoder
from .reference_data import ReferenceData
from .search_result import SearchResult


client = docker.from_env()


class Engine:
	"""
	Search engine for Linux and other platforms supporting Docker
	"""
	
	def __init__(self, lib_path, lib_type, work_dir=None):
		"""
		:param lib_path: The path to the mass spectral library
		:type lib_path: str or pathlib.Path
		:param lib_type: The type of library. One of NISTMS_MAIN_LIB, NISTMS_USER_LIB, NISTMS_REP_LIB
		:type lib_type: int
		:param work_dir: The path to the working directory
		:type work_dir: str or pathlib.Path
		"""
		
		if not os.path.exists(lib_path):
			raise FileNotFoundError(f"Library not found at the given path: {lib_path}")
		
		# # Check if the server is already running
		# for container in client.containers.list(all=True, filters={"status": "running"}):
		# 	if container.name == "pyms-nist-server":
		# 		self.docker = container
		# 		break
		# else:
		#
		
		print("Launching Docker...")
		
		self.docker = client.containers.run(
				"pywine-pyms-nist",
				ports={5001: 5001},
				detach=True,
				name="pyms-nist-server",
				remove=True,
				# stdout=False,
				# stderr=False,
				stdin_open=False,
				volumes={lib_path: {'bind': '/mainlib', 'mode': 'ro'}},
				)
		
		# TODO: Pass library type through to docker.
		#  For now only User Libraries are supported
		
		atexit.register(self.uninit)
		
		retry_count = 0
		
		# Wait for server to come online
		while retry_count < 1000:
			try:
				if requests.get("http://localhost:5001/").text == "ready":
					return
				
			except requests.exceptions.ConnectionError:
				time.sleep(0.5)
				retry_count += 1
		
		raise TimeoutError("Unable to communicate with the search server.")
			
	def uninit(self):
		"""
		Uninitialize the Search Engine
		"""
		
		print("Shutting down docker server")
		
		# print("Server log follows:")
		# print(self.docker.logs(timestamps=True).decode("utf-8"))
		
		try:
			self.docker.stop()
		except docker.errors.NotFound:
			print("Unable to shut down the docker server")
	
	def spectrum_search(self):
		# TODO
		pass
	
	def full_spectrum_search(self, mass_spec):
		"""
		Perform a Full Spectrum Search of the mass spectral library

		:param mass_spec: The mass spectrum to search against the library
		:type mass_spec: pyms.Spectrum.MassSpectrum

		:return: List of possible identities for the mass spectrum
		:rtype: list of SearchResult
		"""

		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")
		
		retry_count = 0
		
		# Keep trying until it works
		while retry_count < 1000:
			try:
				res = requests.post(
						"http://localhost:5001/search/spectrum/",
						json=json.dumps(mass_spec, cls=PyNISTEncoder)
						)
				return hit_list_from_json(res.text)
			
			except requests.exceptions.ConnectionError:
				time.sleep(0.5)
				retry_count += 1
			
		raise TimeoutError("Unable to communicate with the search server.")
	
	def full_search_with_ref_data(self, mass_spec):
		"""
		Perform a Full Spectrum Search of the mass spectral library, including reference data.

		:param mass_spec: The mass spectrum to search against the library
		:type mass_spec: pyms.Spectrum.MassSpectrum

		:return: List of tuples consisting of the possible identities for the mass spectrum and the reference data from the library
		:rtype: list of (SearchResult, ReferenceData) tuples
		"""
		
		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")
		
		retry_count = 0
		
		# Keep trying until it works
		while retry_count < 1000:
			try:
				res = requests.post(
						"http://localhost:5001/search/spectrum_with_ref_data/",
						json=json.dumps(mass_spec, cls=PyNISTEncoder)
						)
				return hit_list_with_ref_data_from_json(res.text)
			except requests.exceptions.ConnectionError:
				time.sleep(0.5)
				retry_count += 1
	
		raise TimeoutError("Unable to communicate with the search server.")
	
	def get_reference_data(self, spec_loc):
		"""
		Get reference data from the library for the compound at the given location.

		:type spec_loc: int

		:rtype: ReferenceData
		"""
		
		retry_count = 0
		
		# Keep trying until it works
		while retry_count < 1000:
			try:
				res = requests.post(f"http://localhost:5001/search/loc/{spec_loc}")
				return ReferenceData(**json.loads(res.text))
			
			except requests.exceptions.ConnectionError:
				time.sleep(0.5)
		
		raise TimeoutError("Unable to communicate with the search server.")


def hit_list_from_json(json_data):
	"""
	Parse json data into a list of SearchResult objects

	:type json_data: str

	:rtype: list of SearchResult
	"""
	
	raw_output = json.loads(json_data)
	
	hit_list = []
	
	for hit in raw_output:
		hit_list.append(SearchResult(**hit))
	
	return hit_list


def hit_list_with_ref_data_from_json(json_data):
	"""
	Parse json data into a list of (SearchResult, ReferenceData) tuples

	:type json_data: str

	:rtype: list of (SearchResult, ReferenceData) tuples
	"""
	
	raw_output = json.loads(json_data)
	
	hit_list = []
	
	for hit, ref_data in raw_output:
		hit_list.append((SearchResult(**hit), ReferenceData(**ref_data)))
	
	return hit_list
