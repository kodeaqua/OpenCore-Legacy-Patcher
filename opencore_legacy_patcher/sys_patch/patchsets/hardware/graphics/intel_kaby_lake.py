"""
intel_kaby_lake.py: Intel Kaby Lake detection

Kaby Lake (Gen 9.5) iGPUs retained native support through macOS 15, Sequoia.
Support was dropped with macOS 26, Tahoe, alongside every Kaby Lake Mac.

Also covers Amber Lake-Y (UHD Graphics 617, MacBookAir8,x), which shares the
AppleIntelKBLGraphics driver family.

NOTE: The binaries referenced below (AppleIntelKBLGraphics*, sourced from the
last Sequoia release that shipped them) must be added to PatcherSupportPkg
under the version directories resolved in `_resolve_kaby_lake_binaries()` /
`_resolve_kaby_lake_framebuffers()` before this patch set can be applied.
"""

from ..base import BaseHardware, HardwareVariant, HardwareVariantGraphicsSubclass

from ...base import PatchType

from ...shared_patches.monterey_opencl import MontereyOpenCL

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class IntelKabyLake(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Intel Kaby Lake"


    def present(self) -> bool:
        """
        Targeting Intel Kaby Lake GPUs
        """
        return self._is_gpu_architecture_present(
            gpu_architectures=[
                device_probe.Intel.Archs.Kaby_Lake
            ]
        )


    def native_os(self) -> bool:
        """
        Dropped support with macOS 26, Tahoe
        """
        return self._xnu_major < os_data.tahoe.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.GRAPHICS


    def hardware_variant_graphics_subclass(self) -> HardwareVariantGraphicsSubclass:
        """
        Type of hardware variant subclass

        Kaby Lake (Gen 9.5) shares the Skylake (Gen 9) Metal driver family
        """
        return HardwareVariantGraphicsSubclass.METAL_31001_GRAPHICS


    def _resolve_kaby_lake_binaries(self) -> str:
        """
        Resolve PatcherSupportPkg directory for Kaby Lake driver bundles
        last shipped in macOS 15, Sequoia
        """
        # TODO: create matching PatcherSupportPkg directories
        return "15.6" if self._xnu_major < os_data.tahoe else "15.6-26"


    def _resolve_kaby_lake_framebuffers(self) -> str:
        """
        Resolve PatcherSupportPkg directory for Kaby Lake framebuffers:
        - AppleIntelKBLGraphics.kext
        - AppleIntelKBLGraphicsFramebuffer.kext
        """
        # TODO: create matching PatcherSupportPkg directories
        return "15.6" if self._xnu_major < os_data.tahoe else "15.6-26"


    def _model_specific_patches(self) -> dict:
        """
        Model specific patches
        """
        return {
            "Intel Kaby Lake": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleIntelKBLGraphics.kext":            self._resolve_kaby_lake_framebuffers(),
                        "AppleIntelKBLGraphicsFramebuffer.kext": self._resolve_kaby_lake_framebuffers(),
                        "AppleIntelKBLGraphicsGLDriver.bundle":  self._resolve_kaby_lake_binaries(),
                        "AppleIntelKBLGraphicsMTLDriver.bundle": self._resolve_kaby_lake_binaries(),
                        "AppleIntelKBLGraphicsVADriver.bundle":  self._resolve_kaby_lake_binaries(),
                        "AppleIntelKBLGraphicsVAME.bundle":      self._resolve_kaby_lake_binaries(),
                        "AppleIntelGraphicsShared.bundle":       self._resolve_kaby_lake_binaries(),
                    },
                },
            },
        }


    def patches(self) -> dict:
        """
        Patches for Intel Kaby Lake iGPUs
        """
        if self.native_os() is True:
            return {}

        return {
            **MontereyOpenCL(self._xnu_major, self._xnu_minor, self._constants.detected_os_version).patches(),
            **self._model_specific_patches(),
        }
