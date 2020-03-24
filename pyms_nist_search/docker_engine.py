#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  docker_engine.py
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
import time

# 3rd party
import docker
import docker.errors
# from docker.types import Mount
import requests

# this package
from .hit_list import hit_list_from_json, hit_list_with_ref_data_from_json
from .json import PyNISTEncoder
from .reference_data import ReferenceData


client = docker.from_env()

class Engine:
	def __init__(self, lib_path, lib_type, work_dir=None):
		"""

		Values of arguments don't matter on non-Win32

		:param lib_path:
		:type lib_path:
		:param lib_type:
		:type lib_type:
		:param work_dir:
		:type work_dir:
		"""
		
		# TODO: Start the Server and setup hook to stop it
		
		print(client.containers.list(all=True, filters={"status": "running"}))
		
		# Check if the server is already running
		for container in client.containers.list(all=True, filters={"status": "running"}):
			print(container)
			if container.name == "pyms-nist-server":
				self.docker = container
				break
		else:
			
			# TODO: Allow library to be on local file system, not in docker image
			# library_mount = Mount("/mainlib", lib_path, read_only=True)
			
			self.docker = client.containers.run(
					"pywine-pyms-nist",
					ports={5001: 5001},
					detach=True,
					name="pyms-nist-server",
					remove=True,
					# stdout=False,
					# stderr=False,
					stdin_open=False,
					# mounts=[library_mount]
					)
		
		atexit.register(self.uninit)
		
		# Allow time for docker container to fully start
		time.sleep(5)
	
	def uninit(self):
		"""
		Uninitialize the Search Engine
		"""
		
		print("Shutting down docker server")
		self.docker.stop()
	
	def spectrum_search(self):
		# TODO
		pass
	
	def full_spectrum_search(self, mass_spec):
		# TODO: type check
		
		res = requests.post(
				f"http://localhost:5001/search/spectrum/",
				json=json.dumps(mass_spec, cls=PyNISTEncoder)
				)
		
		return hit_list_from_json(res.text)
	
	def full_search_with_ref_data(self, mass_spec):
		# TODO: type check
		
		res = requests.post(
				f"http://localhost:5001/search/spectrum_with_ref_data/",
				json=json.dumps(mass_spec, cls=PyNISTEncoder)
				)
		
		return hit_list_with_ref_data_from_json(res.text)
	
	def get_reference_data(self, spec_loc):
		res = requests.post(f"http://localhost:5001/search/loc/{spec_loc}")
		
		return ReferenceData(**json.loads(res.text))

