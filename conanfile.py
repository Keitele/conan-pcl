#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conan import ConanFile, Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rmdir
from conan.tools.gnu import PkgConfig

class PclConan(ConanFile):
    name         = 'pcl'
    version      = '1.13.1'
    md5_hash     = '4d4cfb6bf87cc1f08703deeeac1eb6e2'
    license      = 'MIT'
    url          = 'https://github.com/kheaactua/conan-pcl'
    description  = 'Point cloud library'
    settings     = 'os', 'compiler', 'build_type', 'arch'

    requires     = (
                        'eigen/[>=3.2.0]',
                        'flann/[>=1.6.8]',
                        'boost/[>=1.66]',
                        'qhull/8.0.1',
                        'opengl/system',
                        'glew/2.2.0',
                        'vtk/[>=5.6.1]',
                    )

    options      = {
                        'shared':  [True, False],
                        'fPIC':    [True, False],
                        'with_qt': [True, False],
                    }

    default_options =  { 
                            "shared": True, 
                            "fPIC": True, 
                            "with_qt": False, 
                            "boost/*:shared": True,
                            "opengl/*:shared": True,
                            "glew/*:shared": True,
                            "eigen/*:shared": True,
                            "vtk/*:shared": True,
                        }

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        apply_conandata_patches(self)
        
    def export_sources(self):
        export_conandata_patches(self)
        
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["WITH_OPENNI"] = False
        tc.variables["WITH_OPENNI2"] = False
        tc.variables["PCL_BUILD_WITH_BOOST_DYNAMIC_LINKING_WIN32"] = self.options['boost/*:shared']
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        tc.variables['ADDITIONAL_DEFINITIONS:STRING'] ='-DBOOST_UUID_RANDOM_GENERATOR_COMPAT'
        tc.variables['BUILD_surface_on_nurbs:BOOL'] = True

        # vtk = self.dependencies["vtk"]
        # tc.variables['VTK_DIR:PATH']    = vtk.cpp_info
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    # def package_info(self):
    #     self.cpp_info.set_property("cmake_find_mode", "both")
    #     self.cpp_info.set_property("cmake_module_file_name", "Pcl")
    #     self.cpp_info.set_property("cmake_file_name", "pcl")
    #     self.cpp_info.set_property("pkg_config_name", "pcl")

    #     self.cpp_info.libs = collect_libs(self)
    #     self.cpp_info.includedirs = ["include", "include/pcl-1.13"]

    def package_info(self):
        components = [
                    "pcl_2d", "pcl_common", "pcl_features", "pcl_filters", "pcl_geometry", "pcl_io", 
                    "pcl_kdtree", "pcl_keypoints", "pcl_ml", "pcl_octree", "pcl_outofcore", 
                    "pcl_people", "pcl_recognition", "pcl_registration", "pcl_sample_consensus", "pcl_search", "pcl_segmentation", 
                    "pcl_stereo", "pcl_surface", "pcl_tracking", "pcl_visualization", "pcl_search", "pcl_segmentation", 
                    "pcl_people", "pcl_recognition", "pcl_registration", "pcl_sample_consensus", "pcl_search", "pcl_segmentation", 
                ]

        for component in components:
            self.cpp_info.components[component].set_property("cmake_target_name", component)
            pkg_config = PkgConfig(self, component, pkg_config_path=os.path.join(self.package_folder, "lib", "pkgconfig"))
            pkg_config.fill_cpp_info(self.cpp_info.components[component], is_system=False, system_libs=['lz4', 'flann', 'flann_cpp'])