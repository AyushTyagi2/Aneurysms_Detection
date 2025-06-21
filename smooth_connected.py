from vmtk import vmtkscripts

# === Load the extracted surface ===
reader = vmtkscripts.vmtkSurfaceReader()
reader.InputFileName = "vessel_surface.vtp"  # your input surface
reader.Execute()

# === Surface Smoothing ===
smoother = vmtkscripts.vmtkSurfaceSmoothing()
smoother.Surface = reader.Surface
smoother.NumberOfIterations = 30  # You can adjust for more or less smoothing
smoother.PassBand = 0.1           # Controls smoothing aggressiveness (0.1–0.3)
smoother.Execute()
print("✅ Surface smoothed.")


connectivity = vmtkscripts.vmtkSurfaceConnectivity()
connectivity.Surface = smoother.Surface
connectivity.Method = 'largest'
connectivity.Execute()

writer = vmtkscripts.vmtkSurfaceWriter()
writer.Surface = connectivity.Surface
writer.OutputFileName = "cleaned_smoothed_surface.vtp"
writer.Execute()
print("✅ Output saved to 'cleaned_smoothed_surface.vtp'")
