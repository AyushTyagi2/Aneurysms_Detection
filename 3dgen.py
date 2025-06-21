from vmtk import vmtkscripts

# Step 1: Read binarized image
image_reader = vmtkscripts.vmtkImageReader()
image_reader.InputFileName = r"C:\Users\asus\miniconda3\envs\03_binary_mask.nii.gz"
image_reader.Execute()

# Step 2: Extract surface using marching cubes
mc = vmtkscripts.vmtkMarchingCubes()
mc.Image = image_reader.Image
mc.Level = 1  # binarized: vessel label
mc.Execute()

# Step 3: Write surface to file
surface_writer = vmtkscripts.vmtkSurfaceWriter()
surface_writer.Surface = mc.Surface
surface_writer.OutputFileName = "vessel_surface.vtp"
surface_writer.Execute()

print("✅ Surface extracted and saved.")
