from vmtk import vmtkscripts
import numpy as np

reader = vmtkscripts.vmtkImageReader()
reader.InputFileName = r"C:\Users\asus\OneDrive\Documents\Research\findings\vessel_volume.nii.gz"
reader.Execute()

obj_enhancer = vmtkscripts.vmtkImageObjectEnhancement()
obj_enhancer.Image = reader.Image
obj_enhancer.Execute()

vesselEnhancer = vmtkscripts.vmtkImageVesselEnhancement()
vesselEnhancer.Image = reader.Image
vesselEnhancer.Execute()

vessel_np = vmtkscripts.vmtkImageToNumpy()
vessel_np.Image = vesselEnhancer.Image
vessel_np.Execute()
vessel_array = vessel_np.ArrayDict['pointdata']['Imagescalars']

object_np = vmtkscripts.vmtkImageToNumpy()
object_np.Image = obj_enhancer.Image
object_np.Execute()
object_array = object_np.ArrayDict['pointdata']['Imagescalars']

combined_array = 0.8 * vessel_array + 0.2 * object_array


numpy_to_image = vmtkscripts.vmtkNumpyToImage()
numpy_to_image.Array = combined_array.astype(np.float32)  # Ensure float32
numpy_to_image.Execute()

# Now write to disk (e.g., NIfTI format)
image_writer = vmtkscripts.vmtkImageWriter()
image_writer.Image = numpy_to_image.Image
image_writer.OutputFileName = "fused_enhanced_image.nii.gz"
image_writer.Execute()

imageWriter = vmtkscripts.vmtkImageWriter()
imageWriter.Image = obj_enhancer.Image
imageWriter.OutputFileName = '02.5_obj_enhanced.nii.gz'
imageWriter.Execute()
