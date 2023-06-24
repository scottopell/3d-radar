from direct.filter.FilterManager import FilterManager
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import GraphicsWindow, Shader, Texture, TransparencyAttrib

from lib.camera.camera_control import CameraControl
from lib.util.util import defaultLight


class App(DirectObject):
    def __init__(self, showbase: ShowBase) -> None:
        self.base = showbase

        self.base.setBackgroundColor(0, 0, 0, 1)
        # self.wireframeOn()

        defaultLight(self.base)
        self.cameraControl = CameraControl(self.base)
        self.cameraControl.pitch = 0

        cube = self.base.loader.loadModel("../assets/cube.glb")
        if cube:
            self.cube = cube

        self.cube.reparentTo(self.base.render)

        shader = Shader.load(
            Shader.SL_GLSL,
            vertex="shaders/volume-vert.glsl",
            fragment="shaders/volume-frag.glsl",
        )

        manager = FilterManager(self.base.win, self.base.cam)  # type: ignore
        tex = Texture()
        depth = Texture()
        plane = manager.renderSceneInto(colortex=tex, depthtex=depth)
        if plane:
            self.plane = plane

        self.plane.setShader(shader)
        self.plane.setShaderInput("tex", tex)
        self.plane.setShaderInput("dtex", depth)

        # plane = self.base.loader.loadModel("../assets/plane.glb")
        # if plane:
        #     self.plane = plane

        # self.plane.reparentTo(self.base.render)
        # self.plane.setP(90)
        # self.plane.setScale(100)
        # self.plane.reparentTo(self.base.camera)
        # self.plane.setY(10)
        # self.plane.setShader(shader)
        # self.plane.setTransparency(TransparencyAttrib.MAlpha)
        # self.plane.setBin("fixed", 0)
        # self.plane.setDepthTest(False)
        # self.plane.setDepthWrite(False)

        self.plane.setShaderInput("bounds_start", (0, -2, -2))
        self.plane.setShaderInput("bounds_end", (2, 2, 2))

        self.plane.setShaderInput("myCamera", self.base.camera)
        self.plane.setShaderInput("myCameraNode", self.base.camera)

        self.plane.setShaderInput(
            "proj", self.base.cam.node().getLens().getProjectionMatInv()
        )

        # For some reason this seems to be typed incorrectly; override the type
        window: GraphicsWindow = self.base.win  # type: ignore
        self.windowSize = (window.getXSize(), window.getYSize())

        self.plane.setShaderInput("resolution", self.windowSize)

        self.accept("window-event", self.handleWindowEvent)

        base.taskMgr.add(self.updateCameraPosition, "update-camera-position")

    def handleWindowEvent(self, win: GraphicsWindow) -> None:
        newSize = (win.getXSize(), win.getYSize())
        if newSize[0] == self.windowSize[0] and newSize[1] == self.windowSize[1]:
            return

        self.windowSize = newSize
        self.plane.setShaderInput("resolution", self.windowSize)

    def updateCameraPosition(self, task: Task.Task) -> int:
        self.plane.setShaderInput(
            "camera_position",
            self.base.camera.getPos(self.base.render),
        )

        self.plane.setShaderInput(
            "proj", self.base.cam.node().getLens().getProjectionMatInv()
        )

        return task.cont


base = ShowBase()
app = App(base)
base.run()
