import cadquery as cq
import numpy as np
import logging

millimeters35 = 35/25.4

baseWidth = 5
baseInnerWidth =3.5
baseHeight = 1.5
baseInnerHeight = 0.95
baseDepth = 1.5

filmGrooveThickness = 0.04
filmGrooveToBase = baseHeight-millimeters35/2
filmGrooveRelief= 0.07
filmGrooveReliefToBase = filmGrooveToBase+.1
baseInnerHeight = filmGrooveReliefToBase

filmPathInletlocation=0.75
filmImageLocation=1
filmPathLinearLength = 3

frontSlotThickness = 0.1
frontSlotLocationFromFront =0.5
frontSlotWidth = 4
frontSlotLocationHeight =0.5 

frontHoleDia = 0.3
frontHoleDist = 3.7
frontHoleCenterToBase = 0.3
frontHoleDepth = 0.5

#locator Pin
locatorPinDia = 0.2
locatorPinDistFromEdgeX = 0.4
locatorPinDistFromEdgeY = 0.3
locatorPinHeight = 0.2

#mountingRailDimensions
railMaterialThickness = 0.1
railEdgeToEdge = 5
blockToRailDist = 0.4
railWidth = 0.4
railHeight = 7
railThickness =  0.1

#                   ┌───────────────────────┐
#                   │    Block              │
#                   │                       │
#      ──┬──────────┴───────────────────────┘
#        │
# Block  │       │                              │
#  to    │       ├──────Edge to Edge────────────┤
# Rail   │       │                              │
# Dist   │   ┌───┴─────┐                  ┌─────┴───┐
#        │   │         │                  │         │
#     ───┴── │   ┌─────┴──┬──             └─────┐   │
#            │   │        │  Rail Thickness     │   │
#            │   └─────┬──┴──         ──┬─┬─────┘   │
#            │         │                │ │         │
#            └───┬─────┤              ──┼─┴─────┬───┤
#                │     │                │       │   │
#                ├─────┤           Material   ──┼───┤
#                │     │             Thickness  │   │
#            Rail Width                             │


baseBlock =(cq.Workplane("XY")
            .box(baseWidth,baseDepth,baseHeight,centered = [True, False,False])
            .faces(">Z")
            .rect(baseInnerWidth,baseDepth)
            .cutBlind(baseInnerHeight-baseHeight))

filmSplinePts = [(-baseWidth/2,filmPathInletlocation),
                 (-filmPathLinearLength/2,filmImageLocation),
                 (filmPathLinearLength/2,filmImageLocation),
                 (baseWidth/2,filmPathInletlocation)]

filmSPts1 = [(x[0],x[1]+filmGrooveThickness/2) for x in filmSplinePts]
filmSPts2 = [(-x[0],x[1]-filmGrooveThickness/2) for x in filmSplinePts]


filmSplinePtstangents = [(1,0),(1,0),(1,0),(1,0)]
reversefilmSplinePtstangents = [(-1,0) for x in range(0,4)]

filmGroove = (cq.Workplane("XY")
              .spline(filmSPts1,tangents=filmSplinePtstangents)
              .lineTo(baseWidth/2,filmPathInletlocation-filmGrooveThickness/2)
              .spline(filmSPts2,tangents=reversefilmSplinePtstangents)
              .close()
              .extrude(baseHeight)
              .translate([0,0,filmGrooveToBase])
              )

dummyFilm = (cq.Workplane("XY")
              .spline(filmSPts1,tangents=filmSplinePtstangents)
              .lineTo(baseWidth/2,filmPathInletlocation-filmGrooveThickness/2)
              .spline(filmSPts2,tangents=reversefilmSplinePtstangents)
              .close()
              .extrude(millimeters35)
              .translate([0,0,filmGrooveToBase])
              )

filmSPts1 = [(x[0],x[1]+filmGrooveRelief) for x in filmSplinePts]
filmSPts2 = [(-x[0],x[1]-filmGrooveRelief) for x in filmSplinePts]

filmGrooveRelief = (cq.Workplane("XY")
              .spline(filmSPts1,tangents=filmSplinePtstangents)
              .lineTo(baseWidth/2,filmPathInletlocation-filmGrooveRelief)
              .spline(filmSPts2,tangents=reversefilmSplinePtstangents)
              .close()
              .extrude(baseHeight)
              .translate([0,0,filmGrooveReliefToBase])
              )

frontSlotCut = (cq.Workplane("XY")
                .box(frontSlotWidth,frontSlotThickness,baseHeight,centered = [True,False,False])
                .translate([0,frontSlotLocationFromFront,frontSlotLocationHeight]))


baseBlock = baseBlock.edges(">Z[1] or <X[1] and (not |X and <Z)").chamfer(0.2)#>Z[1] or >X[1]
# baseBlock = baseBlock.faces(">X or <X or >Z or >Y or <Y").fillet(0.1)
baseBlock = baseBlock.cut(filmGrooveRelief).cut(filmGroove).cut(frontSlotCut)

#cut blind holes
baseBlock = baseBlock.faces("<Y").workplane().pushPoints([(frontHoleDist/2,frontHoleCenterToBase),(-frontHoleDist/2,frontHoleCenterToBase)]).hole(frontHoleDia,depth=frontHoleDepth)

# add locator pins
topPart = (baseBlock.faces(">Z").workplane()
           .rect(baseWidth-2*locatorPinDistFromEdgeX,baseDepth-2*locatorPinDistFromEdgeY,forConstruction=True)
           .translate([0,baseDepth/2,0]).vertices()
           .circle(locatorPinDia/2)
           .extrude(locatorPinHeight)
           )
topPart = topPart.rotate((0,0,baseHeight),(0,1,baseHeight),180)
bottomPart = (baseBlock.faces(">Z").workplane()
              .rect(baseWidth-2*locatorPinDistFromEdgeX,baseDepth-2*locatorPinDistFromEdgeY,forConstruction=True)
              .translate([0,baseDepth/2,0]).vertices()
              .hole(locatorPinDia,depth = locatorPinHeight)
              )

mountingRails = (cq.Workplane("XY")
                .box(railWidth,railThickness,railHeight,centered=[False,False,False])
                .rotate((0,0,0),(0,0,1),180)
                .translate([railEdgeToEdge/2,-blockToRailDist,0])
                .faces("<X or <Z")
                .shell(railMaterialThickness,kind = "intersection")
                )

connectorToBaseWidth = 0.4
connectoHeight = baseHeight
railConnector = (cq.Workplane("XY")
                 .moveTo(railEdgeToEdge/2-railWidth,-blockToRailDist+railMaterialThickness)
                 .lineTo(railEdgeToEdge/2+railMaterialThickness,-blockToRailDist+railMaterialThickness)
                 .lineTo(baseWidth/2,0)
                 .lineTo(baseWidth/2-connectorToBaseWidth,0)
                 .close()
                 .extrude(connectoHeight)
                 )
mountingRails = mountingRails.union(railConnector)

mountingRails = mountingRails.union(mountingRails.mirror("ZY"))
bottomPart = mountingRails.union(bottomPart)
# show_object(mountingRails)
# show_object(railConnector)
show_object(topPart)
show_object(bottomPart)
show_object(dummyFilm)
# filmGrooveCut = cq.Workplane("XY").rect(1,1).rotate((0,0,0),(0,-1,0),90).translate([-baseWidth/2,filmPathInletlocation,0.1])#.sweep(filmPath)
