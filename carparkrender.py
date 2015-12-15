from carpark import *
from openglscene import Scene

import cairo
from drawing2d import ExtendedCairoContext

def placeModelWithinRectangle(model, rect, zPos=0, zScale=1):
    xPos, yPos, angle = rect.trans
    model.pos = np.array([xPos, yPos, zPos])

    model.dir = sphericalToCartesian([1, angle, 0])
    model.up = np.array([0, 0, 1])

    xScale, yScale = rect.size
    model.scale = np.array([xScale, yScale, zScale])


class ParkingLotRender:
    def __init__(self, parkingLot):
        self.openglScene = Scene()
        self.parkingLot = parkingLot

    def release(self):
        self.openglScene.release()

    def openglRenderCamera(self, cam, cubeModel, drawFrustum=True):
        cubeModel.pos = cam.pos
        cubeModel.dir = sphericalToCartesian(cam.sphericalDir)
        cubeModel.up = cam.up
        cubeModel.scale = np.array([0.2, 0.1, 0.1])
        cubeModel.draw(self.openglScene.flatProgram)

        if drawFrustum:
            cubeModel.pos = np.array([0,0,0])
            cubeModel.dir = np.array([1,0,0])
            cubeModel.up = np.array([0,0,1])
            cubeModel.scale = np.array([2,2,1])
            proj = cam.getOpenGlCameraMatrix()
            cubeModel.draw(self.openglScene.flatProgram, np.linalg.inv(proj))

    def renderOpenGL(self, camera):
        self.openglScene.prepareFrame(camera)

        # Carpark config:
        mapSize = self.parkingLot.size
        mapCentre = self.parkingLot.centre

        cubeModel = self.openglScene.models['cube']

        # Draw map outline:
        trans = Transform2D.fromParts(mapSize/2-mapCentre, 0)
        rect = RotatedRectangle(trans, mapSize)
        placeModelWithinRectangle(cubeModel, rect, -0.5)
        cubeModel.draw(self.openglScene.flatProgram)

        # Draw parking spaces:
        for space in self.parkingLot.spaces:
            placeModelWithinRectangle(cubeModel, space, 0, 0.1)
            cubeModel.draw(self.openglScene.flatProgram)

        # Draw cameras:
        self.openglRenderCamera(camera, cubeModel, drawFrustum=False)
        for cam in self.parkingLot.cameras:
            self.openglRenderCamera(cam, cubeModel)

    def renderCairo(self, camera, fname):
        # Carpark config:
        mapSize = self.parkingLot.size
        mapCentre = self.parkingLot.centre

        # Drawing config:
        canvasSize = self.parkingLot.canvasSize

        # Create a canvas of the specified size:
        surface = cairo.PDFSurface(fname, canvasSize[0], canvasSize[1])
        # ctx = cairo.Context(surface)
        ctx = ExtendedCairoContext(surface)
        ctx.transformToRealWorldUnits(canvasSize, mapSize, mapCentre)

        # Draw map outline:
        ctx.set_line_width(0.05)
        ctx.setCol(ctx.getRandCol())
        trans = Transform2D.fromParts(mapSize/2-mapCentre, 0)
        rect = RotatedRectangle(trans, mapSize)
        ctx.rotatedRectangle(rect)
        ctx.stroke()

        # Draw parking spaces:
        ctx.set_line_width(0.05)
        ctx.setCol(ctx.getRandCol())
        for space in self.parkingLot.spaces:
            ctx.rotatedRectangle(space)
            ctx.stroke()
            # ctx.fill()

        # Draw cameras:
        ctx.set_line_width(0.01)
        ctx.setCol(ctx.getRandCol())
        for cam in self.parkingLot.cameras:
            trans2D = Transform2D.fromParts(cam.pos, cam.sphericalDir[1])
            ctx.rotatedRectangle(RotatedRectangle(trans2D, [0.2, 0.1]))
            ctx.stroke()

        # Draw projected detections:


        # Highlight occupied parking spaces:


        ctx.show_page()

        print 'renderCairo:', fname
