import os
import numpy as np
from vmtk import vmtkscripts
import vtk

def get_bounds_info(surface, name):
    bounds = surface.GetBounds()
    print(f"{name} bounds: x=[{bounds[0]:.2f}, {bounds[1]:.2f}], y=[{bounds[2]:.2f}, {bounds[3]:.2f}], z=[{bounds[4]:.2f}, {bounds[5]:.2f}]")
    return bounds

# === Step 1: Load the cleaned surface ===
surface_reader = vmtkscripts.vmtkSurfaceReader()
surface_reader.InputFileName = "cleaned_smoothed_surface.vtp"
surface_reader.Execute()
surface = surface_reader.Surface
print("✅ Loaded surface")

# === Step 2: Load the centerlines ===
centerline_reader = vmtkscripts.vmtkSurfaceReader()
centerline_reader.InputFileName = "centerline_output.vtp"
centerline_reader.Execute()
centerlines = centerline_reader.Surface
print("✅ Loaded centerlines")

# Check spatial alignment
surface_bounds = get_bounds_info(surface, "Surface")
centerline_bounds = get_bounds_info(centerlines, "Centerlines")

# === Step 3: Compute centerline attributes (includes radius) ===
attrib = vmtkscripts.vmtkCenterlineAttributes()
attrib.Centerlines = centerlines
attrib.Execute()
centerlines_with_radius = attrib.Centerlines
print("✅ Computed centerline attributes with radius")

# Confirm radius array exists
radius_array = centerlines_with_radius.GetPointData().GetArray("MaximumInscribedSphereRadius")
if radius_array:
    print(f"✅ Radius array found with {radius_array.GetNumberOfTuples()} values")
else:
    print("❌ Radius array 'MaximumInscribedSphereRadius' not found. Reconstruction will fail.")

# === Step 4: Skip branch clipping for now ===
print("⚠️ Skipping branch clipping to avoid issues")
clipped_surface = surface

# === Method 1: PolyBall Modeller ===
print("\n=== Method 1: PolyBall Modeller ===")
try:
    modeller = vmtkscripts.vmtkPolyBallModeller()
    modeller.Centerlines = centerlines_with_radius
    modeller.Surface = clipped_surface
    modeller.RadiusArrayName = "MaximumInscribedSphereRadius"

    x_range = surface_bounds[1] - surface_bounds[0]
    y_range = surface_bounds[3] - surface_bounds[2]
    z_range = surface_bounds[5] - surface_bounds[4]
    max_range = max(x_range, y_range, z_range)
    resolution = max(64, min(128, int(max_range / 2)))
    modeller.SampleDimensions = [resolution, resolution, resolution]
    modeller.UsePolyBallImageBounds = 0

    print(f"Using sample dimensions: {resolution}x{resolution}x{resolution}")
    modeller.Execute()

    image = modeller.Image
    print(f"Created image with dimensions: {image.GetDimensions()}")

    if image.GetDimensions()[0] > 0:
        mc = vmtkscripts.vmtkMarchingCubes()
        mc.Image = image
        mc.Level = 0.5
        mc.Execute()

        if mc.Surface.GetNumberOfPoints() > 0:
            writer = vmtkscripts.vmtkSurfaceWriter()
            writer.Surface = mc.Surface
            writer.OutputFileName = "reconstructed_polyball.vtp"
            writer.Execute()
            print("✅ Method 1 success: Saved reconstructed_polyball.vtp")
        else:
            print("❌ Method 1: Marching cubes produced empty surface")
    else:
        print("❌ Method 1: PolyBall modeller produced empty image")

except Exception as e:
    print(f"❌ Method 1 failed: {e}")

# === Method 2: Tube Filter ===
print("\n=== Method 2: Tube Filter ===")
try:
    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(centerlines_with_radius)
    tube_filter.SetNumberOfSides(12)
    tube_filter.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
    tube_filter.SetInputArrayToProcess(0, 0, 0, 0, "MaximumInscribedSphereRadius")
    tube_filter.CappingOn()
    tube_filter.Update()

    tube_surface = tube_filter.GetOutput()
    print(f"✅ Created tube surface with {tube_surface.GetNumberOfPoints()} points")

    writer = vmtkscripts.vmtkSurfaceWriter()
    writer.Surface = tube_surface
    writer.OutputFileName = "reconstructed_tubes.vtp"
    writer.Execute()
    print("✅ Method 2 success: Saved reconstructed_tubes.vtp")

except Exception as e:
    print(f"❌ Method 2 failed: {e}")

# === Method 3: [REMOVED] ===
# Skipped: vmtkTubeModeller does not exist in your installation

# === Method 4: Alternative PolyBall ===
print("\n=== Method 4: Alternative PolyBall Settings ===")
try:
    modeller2 = vmtkscripts.vmtkPolyBallModeller()
    modeller2.Centerlines = centerlines_with_radius
    modeller2.Surface = clipped_surface
    modeller2.RadiusArrayName = "MaximumInscribedSphereRadius"
    modeller2.SampleDimensions = [100, 100, 100]
    modeller2.Execute()

    image2 = modeller2.Image
    print(f"Alternative PolyBall image dimensions: {image2.GetDimensions()}")

    if image2.GetDimensions()[0] > 0:
        for level in [0.0, 0.1, 0.3, 0.5, 0.7]:
            mc2 = vmtkscripts.vmtkMarchingCubes()
            mc2.Image = image2
            mc2.Level = level
            mc2.Execute()

            if mc2.Surface.GetNumberOfPoints() > 0:
                writer = vmtkscripts.vmtkSurfaceWriter()
                writer.Surface = mc2.Surface
                writer.OutputFileName = f"reconstructed_alt_level_{level}.vtp"
                writer.Execute()
                print(f"✅ Method 4 success at level {level}: Saved reconstructed_alt_level_{level}.vtp")
                break
    else:
        print("❌ Method 4: Alternative PolyBall also produced empty image")

except Exception as e:
    print(f"❌ Method 4 failed: {e}")

# === Summary ===
print("\n=== Summary ===")
output_files = [
    "reconstructed_polyball.vtp",
    "reconstructed_tubes.vtp",
    "reconstructed_alt_level_0.0.vtp",
    "reconstructed_alt_level_0.1.vtp",
    "reconstructed_alt_level_0.3.vtp",
    "reconstructed_alt_level_0.5.vtp",
    "reconstructed_alt_level_0.7.vtp"
]

for filename in output_files:
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"✅ {filename}: {size/1024:.1f} KB")
    else:
        print(f"❌ {filename}: Not created")

print("\nRecommendation: Method 2 (Tube Filter) is most stable with centerline data.")
