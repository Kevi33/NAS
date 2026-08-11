"""Optional headless VTK preview rendering for generated STL assemblies."""

from pathlib import Path


def render_stl(stl_path: Path, png_path: Path, size: tuple[int, int] = (1200, 900)) -> None:
    import vtk

    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(stl_path))
    reader.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.72, 0.75, 0.80)
    actor.GetProperty().SetSpecular(0.25)
    actor.GetProperty().SetSpecularPower(18.0)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.055, 0.065, 0.085)
    renderer.AddActor(actor)
    renderer.ResetCamera()
    camera = renderer.GetActiveCamera()
    camera.Azimuth(34.0)
    camera.Elevation(24.0)
    camera.Zoom(0.82)
    renderer.ResetCameraClippingRange()

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(*size)
    window.AddRenderer(renderer)
    window.Render()

    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetScale(1)
    capture.SetInputBufferTypeToRGBA()
    capture.ReadFrontBufferOff()
    capture.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(png_path))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
