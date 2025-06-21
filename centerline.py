import vtk
import csv
from vmtk import vmtkscripts
import sys

# Read VTP surface
reader = vmtkscripts.vmtkSurfaceReader()
reader.InputFileName = r"C:\Users\asus\miniconda3\envs\cleaned_smoothed_surface.vtp"
reader.Execute()
surface = reader.Surface

print("✅ Surface loaded")

print("🔄 Reading CSV seeds...")

# Read Slicer point list (skip header)
source_coords = []
target_coords = []

with open(r"C:\Users\asus\OneDrive\Documents\seeds.fcsv", newline='') as csvfile:
    reader = csv.reader(csvfile)
    lines = [row for row in reader if not row[0].startswith('#')]

print(f"Found {len(lines)} seed points in CSV")

# First half = sources, second half = targets
mid = len(lines) // 2
for i, row in enumerate(lines):
    # Skip empty rows or rows with insufficient data
    if len(row) < 4:
        continue
    try:
        coord = [float(row[1]), float(row[2]), float(row[3])]
        if i < mid:
            source_coords.extend(coord)
            print(f"Source seed {i}: {coord}")
        else:
            target_coords.extend(coord)
            print(f"Target seed {i-mid}: {coord}")
    except (ValueError, IndexError) as e:
        print(f"Skipping invalid row {i}: {row} - Error: {e}")

print(f"✅ Using {len(source_coords)//3} source points and {len(target_coords)//3} target points")

# Alternative approach using direct VTK centerline filter
print("🔄 Using direct VTK approach...")

try:
    # Create point arrays for sources and targets
    source_points = vtk.vtkPoints()
    target_points = vtk.vtkPoints()
    
    # Add source points
    for i in range(0, len(source_coords), 3):
        source_points.InsertNextPoint(source_coords[i], source_coords[i+1], source_coords[i+2])
    
    # Add target points  
    for i in range(0, len(target_coords), 3):
        target_points.InsertNextPoint(target_coords[i], target_coords[i+1], target_coords[i+2])
    
    # Find closest points on surface
    locator = vtk.vtkPointLocator()
    locator.SetDataSet(surface)
    locator.BuildLocator()
    
    source_ids = vtk.vtkIdList()
    target_ids = vtk.vtkIdList()
    
    print("Finding closest points on surface...")
    for i in range(source_points.GetNumberOfPoints()):
        point = source_points.GetPoint(i)
        closest_id = locator.FindClosestPoint(point)
        source_ids.InsertNextId(closest_id)
        print(f"Source point {i}: {point} -> Surface point ID {closest_id}")
    
    for i in range(target_points.GetNumberOfPoints()):
        point = target_points.GetPoint(i)
        closest_id = locator.FindClosestPoint(point)
        target_ids.InsertNextId(closest_id)
        print(f"Target point {i}: {point} -> Surface point ID {closest_id}")
    
    # Use VTK centerline filter directly
    centerlineFilter = vtk.vtkPolyDataConnectivityFilter()
    centerlineFilter.SetInputData(surface)
    centerlineFilter.SetExtractionModeToAllRegions()
    centerlineFilter.Update()
    
    # Alternative: Try VMTK with manual patching
    print("Trying VMTK with coordinate approach...")
    
    centerline = vmtkscripts.vmtkCenterlines()
    centerline.Surface = surface
    
    # Try different selector approaches
    centerline.SeedSelectorName = 'pickpoint'
    
    # Execute interactively - this will open a window for point selection
    # But we'll try to set it programmatically first
    centerline.SourceSeedIds = source_ids
    centerline.TargetSeedIds = target_ids
    
    centerline.Execute()
    
    print("✅ Centerline extraction successful!")
    
    # Write output
    writer = vmtkscripts.vmtkSurfaceWriter()
    writer.Surface = centerline.Centerlines
    writer.OutputFileName = "centerline_output.vtp"
    writer.Execute()
    
    print("✅ Centerline written to 'centerline_output.vtp'")
    
except Exception as e:
    print(f"❌ Direct approach failed: {e}")
    print("\n🔄 Trying alternative file-based approach...")
    
    # Write points to temporary files for VMTK
    try:
        # Write source points to temporary file
        with open('temp_sources.txt', 'w') as f:
            for i in range(0, len(source_coords), 3):
                f.write(f"{source_coords[i]} {source_coords[i+1]} {source_coords[i+2]}\n")
        
        # Write target points to temporary file  
        with open('temp_targets.txt', 'w') as f:
            for i in range(0, len(target_coords), 3):
                f.write(f"{target_coords[i]} {target_coords[i+1]} {target_coords[i+2]}\n")
        
        print("✅ Temporary point files created")
        print("Manual approach: Use vmtkcenterlines with file input")
        print("Command: vmtkcenterlines -ifile cleaned_smoothed_surface.vtp -ofile centerline_output.vtp")
        
    except Exception as e2:
        print(f"❌ Alternative approach also failed: {e2}")
        
        # Final suggestion
        print("\n💡 Suggestions:")
        print("1. Try converting .fcsv to simple .txt with just coordinates")
        print("2. Use fewer seed points (try with just 1 source and 1 target)")
        print("3. Check if coordinates are in the right coordinate system")
        print("4. Try using vmtkcenterlines command line tool directly")