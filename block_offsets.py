import numpy as np
from blocks import get_block_name, BID, BX, BY, BZ, BROT
from headers import MapBlock
# Generated via MainaScript:
# #RequireContext CEditorPlugin
# #Include "TextLib" as TL

# main() {
# 		log("-------------  PrintBlocks started -----------------");
# 		foreach(Block in Blocks) {
# 			declare Text bInfo;
# 			bInfo = bInfo ^ "'";
# 			if (!Block.BlockModel.IsTerrain
# 				&& !TL::Find("Clip", Block.BlockModel.Name, False, False)) {
# 				bInfo = bInfo ^ Block.BlockModel.Name;
# 			} else {
# 				continue;
# 			}

# 			bInfo = bInfo ^ "': [";

# 			declare Integer i = 0;
# 			foreach (BlockUnit in Block.BlockUnits) {
# 				declare CBlockUnitModel model <=> BlockUnit.BlockUnitModel;
# 				bInfo = bInfo ^ "[";
# 				bInfo = bInfo ^ model.RelativeOffset.X ^ ", ";
# 				bInfo = bInfo ^ model.RelativeOffset.Y ^ ", ";
# 				bInfo = bInfo ^ model.RelativeOffset.Z ^ "]";
# 				if (i != Block.BlockUnits.count - 1) {
# 					bInfo = bInfo ^ ", ";
# 				}
# 				i = i + 1;
# 			}

# 			bInfo = bInfo ^ "],";
# 			log(bInfo);
# 		}

# 	while(True)
# 	{
# 		yield;
# 	}
# }

BLOCK_OFFSETS = {
    'StadiumRoadMain': [[0, 0, 0]],
    'StadiumRoadMainGTCurve2': [[0, 0, 0], [1, 0, 0], [0, 0, 1], [1, 0, 1]],
    'StadiumRoadMainGTCurve3': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1], [1, 0, 2], [2, 0, 0], [2, 0, 1], [2, 0, 2]],
    'StadiumRoadMainGTCurve4': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 0, 3], [3, 0, 1], [3, 0, 2], [3, 0, 3]],
    'StadiumRoadMainGTCurve5': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1], [2, 0, 0], [2, 0, 1], [2, 0, 2], [3, 0, 1], [3, 0, 2], [3, 0, 3], [3, 0, 4], [4, 0, 2], [4, 0, 3], [4, 0, 4]],
    'StadiumLoopLeft': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 1], [0, 4, 1], [0, 5, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [1, 3, 1], [1, 4, 1], [1, 5, 1], [1, 6, 1], [1, 7, 1], [1, 8, 0], [1, 8, 1], [1, 9, 0], [1, 9, 1], [1, 10, 0], [2, 5, 1], [2, 6, 1], [2, 7, 1], [2, 8, 0], [2, 8, 1], [2, 9, 0], [2, 9, 1], [2, 10, 0]],
    'StadiumLoopRight': [[2, 0, 0], [2, 1, 0], [2, 1, 1], [2, 2, 0], [2, 2, 1], [2, 3, 1], [2, 4, 1], [2, 5, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [1, 3, 1], [1, 4, 1], [1, 5, 1], [1, 6, 1], [1, 7, 1], [1, 8, 0], [1, 8, 1], [1, 9, 0], [1, 9, 1], [1, 10, 0], [0, 5, 1], [0, 6, 1], [0, 7, 1], [0, 8, 0], [0, 8, 1], [0, 9, 0], [0, 9, 1], [0, 10, 0]],
    'StadiumRoadMainStartLine': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainCheckpoint': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainBirds': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainFinishLine': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainStartFinishLine': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainTurbo': [[0, 0, 0]],
    'StadiumRoadMainTurboRoulette': [[0, 0, 0]],
    'StadiumRoadMainFW': [[0, 0, 0]],
    'StadiumGrassCheckpoint': [[0, 0, 0], [0, 1, 0]],
    'StadiumGrassBirds': [[0, 0, 0]],
    'StadiumHolePillar': [[0, 0, 0]],
    'StadiumHolePillar2Front': [[0, 0, 0]],
    'StadiumHolePillar2Line': [[0, 0, 0]],
    'StadiumHolePillar3': [[0, 0, 0]],
    'StadiumHole': [[0, 0, 0]],
    'StadiumRoadStretch': [[0, 0, 0]],
    'StadiumBump1': [[0, 0, 0], [0, 1, 0]],
    'StadiumRamp': [[0, 0, 0]],
    'StadiumRampLow': [[0, 0, 0]],
    'StadiumRoadMainInBeam': [[0, 0, 0]],
    'StadiumRoadMainXBeam': [[0, 0, 0]],
    'StadiumRoadMainGTDiag2x2': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1]],
    'StadiumRoadMainGTDiag2x2Mirror': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1]],
    'StadiumRoadMainGTDiag3x2': [[0, 0, 0], [0, 0, 1], [0, 0, 2], [1, 0, 0], [1, 0, 1], [1, 0, 2]],
    'StadiumRoadMainGTDiag3x2Mirror': [[0, 0, 0], [0, 0, 1], [0, 0, 2], [1, 0, 0], [1, 0, 1], [1, 0, 2]],
    'StadiumRoadMainGTDiag4x3': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 0, 3], [2, 0, 1], [2, 0, 2], [2, 0, 3]],
    'StadiumRoadMainGTDiag4x3Mirror': [[0, 0, 1], [0, 0, 2], [0, 0, 3], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 0, 3], [2, 0, 0], [2, 0, 1]],
    'StadiumRoadMainYShapedDiag2': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1], [2, 0, 0], [2, 0, 1]],
    'StadiumRoadMainYShapedCurve2': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1], [2, 0, 0], [2, 0, 1]],
    'StadiumRoadMainSlopeBase2': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumRoadMainSlopeBase': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainSlopeBase1x2': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1]],
    'StadiumRoadMainSlopeStraight': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainBiSlopeStart': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1]],
    'StadiumRoadMainBiSlopeEnd': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1]],
    'StadiumRoadMainSlopeUTop': [[0, 0, 0]],
    'StadiumRoadMainSlopeUBottom': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainCheckpointUp': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainCheckpointDown': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainTurboUp': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainTurboDown': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainTurboRouletteDown': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainTurboRouletteUp': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainFWSlope': [[0, 0, 0], [0, 1, 0]],
    'StadiumHolePillarSlope': [[0, 0, 0], [0, 1, 0]],
    'StadiumHoleSlope': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadStretchSlope': [[0, 0, 0], [0, 1, 0]],
    'StadiumBump1Slope': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainInBeamSlope': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainXBeamSlope': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainGTDiag2x2Slope': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 2, 1]],
    'StadiumRoadMainGTDiag2x2SlopeMirror': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 2, 1]],
    'StadiumRoadMainGTDiag3x2Slope': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 1], [0, 2, 2], [0, 3, 2], [1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 2, 1], [1, 2, 2], [1, 3, 2]],
    'StadiumRoadMainGTDiag3x2SlopeMirror': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 1], [0, 2, 2], [0, 3, 2], [1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 2, 1], [1, 2, 2], [1, 3, 2]],
    'StadiumRoadMainGTDiag4x3Slope': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 2, 1], [1, 2, 2], [1, 3, 2], [1, 3, 3], [2, 2, 1], [2, 2, 2], [2, 3, 2], [2, 3, 3], [2, 4, 3]],
    'StadiumRoadMainGTDiag4x3SlopeMirror': [[0, 1, 1], [0, 2, 1], [0, 2, 2], [0, 3, 2], [0, 3, 3], [0, 4, 3], [1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 2, 1], [1, 2, 2], [1, 3, 2], [1, 3, 3], [2, 0, 0], [2, 1, 0], [2, 1, 1], [2, 2, 1]],
    'StadiumRoadMainYShapedDiag2SlopeUp': [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [2, 0, 1], [2, 1, 0], [2, 1, 1], [2, 2, 0]],
    'StadiumRoadMainYShapedDiag2SlopeDown': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 2, 1], [2, 0, 0], [2, 1, 0], [2, 1, 1], [2, 2, 1]],
    'StadiumRoadTiltStraight': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadTiltTransition1Left': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadTiltTransition1Right': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadTiltTransition2Left': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1]],
    'StadiumRoadTiltTransition2Right': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1]],
    'StadiumRoadTiltTransition2CurveLeft': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]],
    'StadiumRoadTiltTransition2CurveRight': [[1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1]],
    'StadiumRoadTiltTransition2DiagLeft': [[0, 0, 0], [0, 0, 1], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 1]],
    'StadiumRoadTiltTransition2DiagRight': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 1], [1, 0, 0], [1, 0, 1], [1, 1, 1]],
    'StadiumRoadTiltStraightBirds': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainCheckpointLeft': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumRoadMainCheckpointRight': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumRoadMainTurboLeft': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainTurboRight': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainTurboRouletteLeft': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainTurboRouletteRight': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainFWTilt': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadTiltCorner': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadTiltGTCurve2': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]],
    'StadiumRoadTiltGTCurve3': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 1, 0], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 0], [2, 1, 1], [2, 1, 2]],
    'StadiumRoadTiltGTCurve4': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 0, 3], [2, 1, 0], [2, 1, 1], [3, 0, 1], [3, 0, 2], [3, 0, 3], [3, 1, 1], [3, 1, 2], [3, 1, 3]],
    'StadiumRoadMainGTDiag2x2Tilt': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 1, 0], [1, 1, 1], [1, 2, 1]],
    'StadiumRoadMainGTDiag2x2TiltMirror': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0]],
    'StadiumRoadMainGTDiag3x2TiltMirror': [[0, 1, 0], [0, 1, 1], [0, 1, 2], [0, 2, 1], [0, 2, 2], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 1, 2]],
    'StadiumRoadTiltCornerDownLeft': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadTiltCornerDownRight': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadTiltCornerUpLeft': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadTiltCornerUpRight': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadTiltGTCurve2DownLeft': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 1, 0], [1, 1, 1], [1, 2, 1]],
    'StadiumRoadTiltGTCurve2DownRight': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0]],
    'StadiumRoadTiltGTCurve2UpLeft': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0]],
    'StadiumRoadTiltGTCurve2UpRight': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 1, 0], [1, 1, 1], [1, 2, 1]],
    'StadiumHolePillarTilt': [[0, 0, 0], [0, 1, 0]],
    'StadiumHoleTilt': [[0, 0, 0], [0, 1, 0]],
    'StadiumStretchTilt': [[0, 0, 0], [0, 1, 0]],
    'StadiumBump1Tilt': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainInBeamTilt': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadMainXBeamTilt': [[0, 0, 0], [0, 1, 0]],
    'StadiumPlatformLoopStart': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumPlatformLoopEnd': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumPlatformWallBorder': [[0, 0, 0]],
    'StadiumPlatformWall1': [[0, 0, 0]],
    'StadiumPlatformWall1Screen': [[0, 0, 0]],
    'StadiumPlatformWallCheckpointH': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumPlatformWall2': [[0, 0, 0], [0, 1, 0]],
    'StadiumPlatformWall4': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumPlatformWallCheckpointV': [[0, 0, 0]],
    'StadiumPlatformWallPub2': [[0, 0, 0], [0, 1, 0]],
    'StadiumPlatformWall1Birds': [[0, 0, 0]],
    'StadiumPlatformRoad': [[0, 0, 0]],
    'StadiumPlatformSlope2Straight': [[0, 0, 0], [0, 1, 0]],
    'StadiumPlatformBiSlope2StartSmall': [[0, 0, 0]],
    'StadiumPlatformBiSlope2Start': [[0, 0, 0], [0, 1, 0]],
    'StadiumPlatformBiSlope2End': [[0, 0, 0]],
    'StadiumPlatformTurbo': [[0, 0, 0]],
    'StadiumPlatformTurboDown': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumPlatformTurboLeft': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumPlatformTurboRight': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumPlatformTurboUp': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumPlatformFW': [[0, 0, 0]],
    'StadiumPlatformFWSlope2': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCheckpointRingHRoad': [[0, 0, 0]],
    'StadiumCheckpointRingV': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCheckpointRing2x1V': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 3, 0]],
    'StadiumCheckpointRing2x1H': [[0, 0, 0], [1, 0, 0]],
    'StadiumPlatformMultilap': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumPlatformCheckpoint': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumPlatformCheckpointDown': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumPlatformCheckpointLeft': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumPlatformCheckpointRight': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumPlatformCheckpointUp': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumPlatformGTCurve2Wall1': [[0, 0, 0], [1, 0, 0], [1, 0, 1]],
    'StadiumPlatformGTCurve2Wall2': [[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]],
    'StadiumPlatformGTCurve2Wall4': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [1, 3, 0], [1, 3, 1]],
    'StadiumPlatformGTCurve3Wall1': [[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 0, 1], [2, 0, 2]],
    'StadiumPlatformGTCurve3Wall2': [[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 1, 0], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 0], [2, 1, 1], [2, 1, 2]],
    'StadiumPlatformGTCurve3Wall4': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 3, 0], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 0], [2, 1, 1], [2, 1, 2], [2, 2, 0], [2, 2, 1], [2, 2, 2], [2, 3, 0], [2, 3, 1], [2, 3, 2]],
    'StadiumPlatformToRoad': [[0, 0, 0]],
    'StadiumPlatformToRoad2': [[0, 0, 0], [0, 0, 1]],
    'StadiumPlatformToRoad2Mirror': [[0, 0, 0], [0, 0, 1]],
    'StadiumPlatformToRoadMain': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitToRoadMain': [[0, 0, 0], [0, 1, 0]],
    'StadiumPlatformGridCheckpoint': [[0, 0, 0], [0, 1, 0]],
    'StadiumPlatformGridFW': [[0, 0, 0]],
    'StadiumPlatformGridStraight': [[0, 0, 0]],
    'StadiumPlatformGridTurbo': [[0, 0, 0]],
    'StadiumPlatformGridStraightBirds': [[0, 0, 0]],
    'StadiumCircuitBase': [[0, 0, 0]],
    'StadiumCircuitSlopeStart': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitSlopeStraight': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitSlopeEnd': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitTurbo': [[0, 0, 0]],
    'StadiumCircuitTurboLeft': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitTurboUp': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitTurboRight': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitTurboDown': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitFreeWheeling': [[0, 0, 0]],
    'StadiumCircuitFreeWheelingSlope2Air': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderStraight': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitBorderSlopeStraightLeft': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCircuitBorderSlopeStraightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderSlopeStraightRight': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCircuitBorderSlopeStraightBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderSlopeStartLeft': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderSlopeStartRight': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderSlopeEndRight': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderDiagIn': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitBorderSlopeDiagInLeftBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCircuitBorderSlopeDiagInLeftTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCircuitBorderSlopeDiagInRightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCircuitBorderSlopeDiagInRightBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCircuitBorderDiagOut': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitBorderSlopeDiagOutLeftBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderSlopeDiagOutLeftTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderSlopeDiagOutRightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderSlopeDiagOutRightBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderCornerIn': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitBorderSlopeCornerInLeftBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCircuitBorderSlopeCornerInLeftTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCircuitBorderSlopeCornerInRightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCircuitBorderSlopeCornerInRightBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumCircuitBorderCornerOut': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitSlopeCornerInLeftBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderSlopeCornerOutRightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderSlopeCornerOutRightBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumCircuitBorderGTCurve2In': [[0, 0, 1], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]],
    'StadiumCircuitBorderSlopeGTCurve2InLeftBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 1], [1, 3, 1], [1, 4, 1], [1, 5, 1]],
    'StadiumCircuitBorderSlopeGTCurve2InLeftTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 1], [0, 5, 1], [1, 0, 0], [1, 1, 0], [1, 2, 0]],
    'StadiumCircuitBorderSlopeGTCurve2InRightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 2, 1], [1, 3, 0], [1, 3, 1], [1, 4, 1], [1, 5, 1]],
    'StadiumCircuitBorderSlopeGTCurve2InRightBottom': [[0, 3, 1], [0, 4, 1], [0, 5, 1], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 2, 1], [1, 3, 0], [1, 3, 1], [1, 4, 1]],
    'StadiumCircuitBorderGTCurve2Out': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1]],
    'StadiumCircuitBorderSlopeGTCurve2OutLeftBottom': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 1], [1, 1, 1], [1, 2, 1], [1, 3, 1], [1, 4, 1]],
    'StadiumCircuitBorderSlopeGTCurve2OutLeftTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 1], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 3, 0]],
    'StadiumCircuitBorderSlopeGTCurve2OutRightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 2, 1], [1, 3, 0], [1, 3, 1], [1, 4, 1]],
    'StadiumCircuitBorderSlopeGTCurve2OutRightBottom': [[0, 1, 1], [0, 2, 1], [0, 3, 1], [0, 4, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [1, 3, 1]],
    'StadiumCircuitBorderGTCurve3In': [[0, 0, 2], [0, 1, 2], [1, 0, 1], [1, 0, 2], [1, 1, 1], [1, 1, 2], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 0], [2, 1, 1]],
    'StadiumCircuitBorderSlopeGTCurve3InLeftBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 1], [0, 5, 1], [0, 5, 2], [0, 6, 2], [1, 6, 2], [1, 5, 2], [2, 6, 2], [2, 7, 2], [2, 5, 2], [0, 4, 2], [1, 4, 2], [1, 4, 1], [1, 3, 1], [1, 5, 1]],
    'StadiumCircuitBorderSlopeGTCurve3InLeftTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 1], [0, 5, 1], [1, 0, 0], [1, 1, 0], [1, 2, 0], [2, 0, 0], [2, 1, 0], [2, 2, 0], [1, 2, 1], [1, 3, 1], [1, 3, 0], [0, 5, 2], [0, 6, 2], [0, 7, 2], [0, 4, 2]],
    'StadiumCircuitBorderSlopeGTCurve3InRightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0], [2, 2, 0], [2, 2, 1], [2, 3, 1], [2, 4, 1], [2, 5, 1], [2, 5, 2], [2, 6, 2], [2, 7, 2], [1, 3, 0], [2, 1, 0], [2, 0, 0], [1, 2, 1], [1, 3, 1], [2, 4, 2], [2, 3, 0]],
    'StadiumCircuitBorderGTCurve3Out': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 1, 0], [1, 1, 1], [1, 1, 2], [2, 0, 1], [2, 0, 2], [2, 1, 1], [2, 1, 2]],
    'StadiumCircuitBorderSlopeGTCurve3OutLeftBottom': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 1], [1, 1, 1], [1, 2, 1], [1, 3, 1], [1, 4, 1], [1, 4, 2], [1, 5, 2], [2, 5, 2], [2, 6, 2], [2, 4, 2], [2, 3, 2], [2, 4, 1], [2, 3, 1], [1, 3, 2], [1, 1, 0], [1, 2, 0]],
    'StadiumCircuitBorderSlopeGTCurve3OutLeftTop': [[1, 0, 0], [1, 1, 0], [2, 0, 0], [2, 1, 0], [2, 2, 0], [2, 3, 0], [1, 2, 0], [1, 2, 1], [1, 3, 1], [1, 4, 1], [1, 5, 1], [0, 2, 1], [0, 3, 1], [0, 4, 1], [0, 5, 2], [0, 4, 2], [0, 6, 2], [0, 5, 1], [1, 3, 0], [2, 2, 1], [2, 3, 1], [1, 4, 2], [1, 5, 2]],
    'StadiumCircuitBorderSlopeGTCurve3OutRightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 2, 1], [1, 3, 1], [1, 4, 1], [2, 2, 1], [2, 3, 1], [2, 4, 1], [2, 4, 2], [2, 5, 2], [1, 5, 2], [2, 6, 2], [1, 5, 1], [2, 5, 1], [1, 4, 2], [0, 2, 1], [0, 3, 1], [1, 3, 0]],
    'StadiumCircuitBorderSlopeGTCurve3OutRightBottom': [[0, 3, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [1, 3, 1], [2, 2, 1], [2, 1, 1], [2, 1, 0], [2, 2, 0], [2, 0, 0], [2, 3, 1], [1, 3, 2], [1, 4, 2], [1, 5, 2], [0, 5, 2], [0, 6, 2], [0, 4, 2], [0, 3, 2], [1, 4, 1], [0, 2, 1], [0, 4, 1]],
    'StadiumCircuitBorderGTCurve4In': [[0, 0, 3], [0, 1, 3], [1, 0, 3], [1, 1, 3], [2, 0, 2], [2, 0, 3], [2, 1, 2], [2, 1, 3], [3, 0, 0], [3, 0, 1], [3, 0, 2], [3, 1, 0], [3, 1, 1], [3, 1, 2]],
    'StadiumCircuitBorderSlopeGTCurve4InLeftBottom': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 1], [0, 5, 2], [0, 6, 2], [1, 6, 2], [1, 6, 3], [1, 7, 3], [1, 8, 3], [2, 8, 3], [3, 8, 3], [3, 9, 3], [1, 7, 2], [0, 5, 1], [0, 4, 2], [2, 7, 3], [3, 7, 3], [1, 5, 2], [1, 4, 2], [2, 6, 3]],
    'StadiumCircuitBorderSlopeGTCurve4InLeftTop': [[3, 1, 0], [3, 0, 0], [3, 2, 0], [2, 2, 0], [1, 2, 0], [1, 1, 0], [2, 1, 0], [1, 2, 1], [0, 2, 1], [0, 3, 1], [0, 4, 1], [0, 4, 2], [0, 5, 2], [0, 6, 2], [0, 6, 3], [0, 7, 3], [0, 8, 3], [1, 3, 1], [1, 3, 0], [1, 4, 1], [0, 5, 1], [0, 7, 2], [2, 0, 0], [1, 0, 0], [0, 9, 3], [2, 3, 0], [1, 5, 1]],
    'StadiumCircuitBorderSlopeGTCurve4InRightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 3, 0], [2, 0, 0], [2, 1, 0], [2, 2, 0], [2, 3, 0], [3, 3, 1], [3, 4, 1], [3, 5, 1], [2, 3, 1], [2, 4, 1], [2, 5, 1], [3, 5, 2], [3, 6, 2], [3, 7, 3], [3, 7, 2], [3, 8, 3], [3, 9, 3], [3, 4, 2], [3, 6, 3], [3, 2, 1], [2, 2, 1]],
    'StadiumCircuitBorderSlopeGTCurve4InRightBottom': [[3, 3, 1], [3, 2, 0], [3, 1, 0], [3, 0, 0], [3, 2, 1], [3, 4, 1], [3, 5, 1], [3, 5, 2], [3, 6, 2], [2, 6, 2], [2, 7, 2], [2, 7, 3], [2, 8, 3], [1, 8, 3], [0, 8, 3], [0, 9, 3], [3, 3, 0], [3, 4, 2], [0, 7, 3], [1, 7, 3], [2, 5, 2], [2, 6, 3], [1, 6, 3]],
    'StadiumCircuitBorderGTCurve4Out': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [2, 0, 1], [2, 0, 2], [2, 0, 3], [2, 1, 1], [2, 1, 2], [3, 0, 2], [3, 0, 3], [3, 1, 2], [3, 1, 3]],
    'StadiumCircuitBorderSlopeGTCurve4OutLeftBottom': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [1, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 1], [1, 3, 1], [2, 3, 1], [2, 3, 2], [2, 4, 2], [2, 5, 2], [2, 5, 3], [2, 6, 3], [2, 7, 3], [3, 7, 3], [3, 8, 3], [3, 6, 2], [3, 5, 2], [3, 6, 3], [3, 5, 3], [1, 2, 1], [1, 2, 0], [2, 4, 1], [3, 4, 2], [2, 2, 1], [1, 1, 0]],
    'StadiumCircuitBorderSlopeGTCurve4OutLeftTop': [[2, 3, 1], [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0], [3, 2, 0], [3, 3, 0], [2, 2, 0], [3, 2, 1], [3, 3, 1], [2, 2, 1], [2, 4, 1], [2, 5, 1], [2, 4, 2], [2, 5, 2], [2, 6, 2], [1, 4, 2], [0, 4, 2], [0, 5, 2], [0, 6, 2], [1, 5, 2], [1, 6, 2], [1, 7, 2], [0, 7, 3], [0, 8, 3], [1, 6, 3], [1, 7, 3], [0, 6, 3], [3, 4, 1]],
    'StadiumCircuitBorderSlopeGTCurve4OutRightTop': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 2, 1], [1, 3, 1], [1, 4, 1], [0, 2, 1], [0, 3, 1], [3, 4, 2], [2, 4, 2], [2, 5, 2], [3, 5, 2], [1, 5, 2], [1, 5, 1], [3, 6, 2], [2, 6, 2], [1, 6, 2], [3, 6, 3], [3, 7, 3], [3, 8, 3], [2, 6, 3], [2, 7, 3], [2, 7, 2], [1, 4, 2]],
    'StadiumCircuitBorderSlopeGTCurve4OutRightBottom': [[3, 0, 1], [3, 1, 1], [3, 2, 1], [3, 3, 1], [3, 0, 0], [3, 1, 0], [2, 1, 1], [2, 2, 1], [2, 3, 1], [2, 1, 0], [2, 0, 0], [3, 2, 0], [2, 2, 0], [1, 3, 1], [1, 4, 1], [1, 4, 2], [1, 5, 2], [1, 6, 2], [1, 6, 3], [1, 7, 3], [0, 7, 3], [0, 6, 3], [0, 8, 3], [0, 6, 2], [0, 5, 2], [1, 3, 2], [1, 2, 1], [1, 5, 3], [0, 5, 3]],
    'StadiumCircuitLoopStart': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0]],
    'StadiumCircuitRampBig': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitRampSmall1x05': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitRampSmall1x1': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitHole': [[0, 0, 0]],
    'StadiumCircuitBumpUp': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitBumpUp2': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1]],
    'StadiumCircuitBumpDown': [[0, 0, 0]],
    'StadiumCircuitPillar1': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitPillar2': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitPillar3': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitPillar5': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitPillar6': [[0, 0, 0], [0, 1, 0]],
    'StadiumCircuitPillar7': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadDirtFenceStraight': [[0, 0, 0]],
    'StadiumRoadDirtFenceCorner': [[0, 0, 0]],
    'StadiumRoadDirt': [[0, 0, 0]],
    'StadiumRoadDirtCheckpoint': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadDirtMultiLap': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadDirtTurbo': [[0, 0, 0]],
    'StadiumRoadDirtFreeWheeling': [[0, 0, 0]],
    'StadiumRoadDirtGTCurve2': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0]],
    'StadiumRoadDirtGTCurve3': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 1, 0], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 0], [2, 1, 1]],
    'StadiumRoadDirtGTCurve4': [[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 1], [2, 1, 2], [3, 0, 1], [3, 0, 2], [3, 0, 3], [3, 1, 1], [3, 1, 2], [2, 0, 3], [2, 1, 0]],
    'StadiumRoadDirtStraightBirds': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadDirtHighFenceStraight': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadDirtHighFenceCorner': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadDirtHigh': [[0, 0, 0]],
    'StadiumRoadDirtHighCheckpoint': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumRoadDirtHighMultiLap': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumRoadDirtHighTurbo': [[0, 0, 0]],
    'StadiumRoadDirtHighFreeWheeling': [[0, 0, 0]],
    'StadiumRoadDirtHighGTCurve2': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]],
    'StadiumRoadDirtHighGTCurve3': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 1, 0], [1, 1, 1], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 0], [2, 1, 1], [2, 1, 2]],
    'StadiumRoadDirtHighFenceStraightBirds': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumRoadDirtToRoadDirtHigh': [[0, 0, 0]],
    'StadiumRoadDirtToRoadDirtHigh2': [[0, 0, 0], [0, 0, 1]],
    'StadiumRoadDirtToRoadDirtHighBridge': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadDirtToRoadDirtHighCross': [[0, 0, 0]],
    'StadiumRoadDirtHighToRoad': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadDirtToRoad': [[0, 0, 0]],
    'StadiumRoadDirtToRoadB': [[0, 0, 0]],
    'StadiumBump1InGround': [[0, 0, 0]],
    'StadiumRoadDirtHillWave': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1]],
    'StadiumRoadDirtHillSlope': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumRoadDirtHillSlope2': [[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1]],
    'StadiumRoadMainSlopeUBottomInGround': [[0, 0, 0]],
    'StadiumRoadDirtHillSlopeGT2': [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [1, 3, 0]],
    'StadiumRoadDirtWave_x1': [[0, 0, 0]],
    'StadiumRoadDirtHillSlopeGT2Bis': [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1]],
    'StadiumDirtDeadendDoor': [[0, 0, 0], [0, 1, 0]],
    'StadiumRoadDirtHillTiltStraight': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 0, 1]],
    'StadiumRoadDirtHillTiltCornerIn': [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 2, 0], [1, 3, 0], [0, 0, 0]],
    'StadiumRoadDirtHillTiltGTCurve3In': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 2, 0], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [2, 0, 1], [2, 0, 2], [2, 1, 1], [2, 1, 2], [2, 2, 1], [2, 2, 2], [1, 1, 2], [0, 1, 1]],
    'StadiumRoadDirtHillTiltCornerOut': [[0, 0, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 2, 0]],
    'StadiumRoadDirtHillTiltCheckpointLeft': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0]],
    'StadiumRoadDirtHillTiltCheckpointRight': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0]],
    'StadiumRoadDirtHillTiltToRoadLeft': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 2, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 2, 0]],
    'StadiumRoadDirtHillTiltToRoadRight': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 2, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 2, 0]],
    'StadiumRoadDirtHillTiltCornerLeft': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0]],
    'StadiumRoadDirtHillTiltCornerRight': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0]],
    'StadiumRoadDirtDiagonaleLeft': [[0, 0, 0], [0, 0, 1], [0, 0, 2], [0, 1, 1], [0, 1, 2], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 1, 0], [1, 1, 1]],
    'StadiumRoadDirtDiagonaleRight': [[0, 0, 0], [0, 0, 1], [0, 0, 2], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 1, 1], [1, 1, 2]],
    'StadiumRoadDirtHillTiltToRoadSlope': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1]],
    'StadiumRoadDirtHillTiltToRoadSlopeX2': [[0, 0, 0], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 1, 0], [0, 2, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 2, 1]],
    'StadiumRoadDirtHighGTCurve4': [[0, 0, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 0], [2, 1, 1], [3, 0, 1], [3, 0, 2], [3, 0, 3], [3, 1, 2], [3, 1, 1], [0, 1, 0], [3, 1, 3], [1, 1, 1], [2, 1, 2], [0, 0, 1], [2, 0, 3]],
    'StadiumRoadDirtHillTiltToRoadSlopeMirror': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1]],
    'StadiumRoadDirtHillTiltToRoadSlopeX2Mirror': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 0, 1], [0, 1, 1], [1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 2, 0], [0, 2, 1]],
    'StadiumRoadDirtHillTiltToRoadSlopeX4': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 2, 0], [2, 0, 0], [2, 0, 1], [2, 1, 0], [2, 1, 1], [2, 2, 0], [2, 2, 1], [3, 0, 1], [3, 1, 0], [3, 1, 1], [3, 2, 0], [3, 2, 1]],
    'StadiumRoadDirtHillTiltToRoadSlopeX4Mirror': [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [2, 0, 0], [2, 0, 1], [2, 1, 0], [2, 2, 0], [3, 0, 0], [3, 0, 1], [3, 1, 0], [3, 1, 1], [3, 2, 0]],
    'StadiumTrenchStraight': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchStraightTunnel': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchCorner': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchCross': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchCrossTunnel': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchGTCurve2': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]],
    'StadiumTrenchGTCurve3': [[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 1, 0], [1, 1, 1], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 1], [2, 1, 2], [0, 0, 1]],
    'StadiumTrenchGTCurve3Tunnel': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 0, 2], [2, 0, 1], [2, 0, 2], [2, 1, 2], [2, 0, 0]],
    'StadiumTrenchGTCurve2Tunnel': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 1]],
    'StadiumTrenchCheckpoint': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchMultiLap': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchFreeWheeling': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchTurbo': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchInPillar': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchToRoadMain': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchToRoadMainX2': [[0, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 1]],
    'StadiumTrenchToRoadMainBiSlopeStart': [[0, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 1]],
    'StadiumTrenchXRoadMain': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchToRoadDirt': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchToRoadDirtX2': [[0, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 1]],
    'StadiumTrenchToPlatformBiSlopeStart': [[0, 0, 0], [0, 1, 0]],
    'StadiumTrenchToLoopStart': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumSculptBridgeSuspendSlope2': [[0, 0, 2], [0, 0, 3], [0, 1, 2], [0, 1, 3], [0, 1, 4], [0, 2, 2], [0, 2, 3], [0, 2, 4], [0, 3, 2], [0, 3, 3], [0, 3, 4], [0, 4, 2], [0, 4, 3], [0, 4, 4], [0, 5, 1], [0, 5, 2], [0, 5, 3], [0, 5, 4], [0, 6, 1], [0, 6, 2], [0, 6, 3], [0, 6, 4], [0, 7, 1], [0, 7, 2], [0, 7, 3], [0, 7, 4], [0, 8, 1], [0, 8, 2], [0, 8, 3], [0, 8, 4], [0, 9, 1], [0, 9, 2], [0, 9, 3], [0, 9, 4], [0, 10, 1], [0, 10, 2], [0, 10, 3], [0, 10, 4], [0, 11, 1], [0, 11, 2], [0, 11, 3], [0, 11, 4], [0, 12, 1], [0, 12, 2], [0, 12, 3], [0, 12, 4], [0, 13, 1], [0, 13, 3], [0, 13, 4], [0, 14, 1], [0, 14, 3], [0, 14, 4], [0, 14, 5], [0, 15, 1], [0, 15, 2], [0, 15, 3], [0, 15, 4], [0, 15, 5], [0, 16, 0], [0, 16, 1], [0, 16, 2], [0, 16, 3], [0, 16, 4], [0, 16, 5], [0, 17, 0], [0, 17, 1], [0, 17, 3], [0, 17, 4], [0, 17, 5], [0, 18, 0], [0, 18, 1], [0, 18, 4], [0, 18, 5], [0, 19, 0], [0, 19, 1], [0, 19, 2], [0, 19, 3], [0, 19, 4], [0, 19, 5], [0, 20, 0], [0, 20, 1], [0, 20, 5], [0, 21, 0], [0, 21, 1], [0, 22, 0], [0, 22, 1], [0, 23, 0], [0, 24, 0]],
    'StadiumSculptBridgeSuspendSlope2Mirror': [[0, 0, 2], [0, 0, 3], [0, 1, 2], [0, 1, 3], [0, 1, 4], [0, 2, 2], [0, 2, 3], [0, 2, 4], [0, 3, 2], [0, 3, 3], [0, 3, 4], [0, 4, 2], [0, 4, 3], [0, 4, 4], [0, 5, 1], [0, 5, 2], [0, 5, 3], [0, 5, 4], [0, 6, 1], [0, 6, 2], [0, 6, 3], [0, 6, 4], [0, 7, 1], [0, 7, 2], [0, 7, 3], [0, 7, 4], [0, 8, 1], [0, 8, 2], [0, 8, 3], [0, 8, 4], [0, 9, 1], [0, 9, 2], [0, 9, 3], [0, 9, 4], [0, 10, 1], [0, 10, 2], [0, 10, 3], [0, 10, 4], [0, 11, 1], [0, 11, 2], [0, 11, 3], [0, 11, 4], [0, 12, 1], [0, 12, 3], [0, 12, 4], [0, 13, 1], [0, 13, 3], [0, 13, 4], [0, 14, 1], [0, 14, 3], [0, 14, 4], [0, 15, 1], [0, 15, 2], [0, 15, 4], [0, 15, 5], [0, 16, 0], [0, 16, 1], [0, 16, 2], [0, 16, 3], [0, 16, 4], [0, 16, 5], [0, 17, 0], [0, 17, 1], [0, 17, 3], [0, 17, 4], [0, 17, 5], [0, 18, 0], [0, 18, 1], [0, 18, 4], [0, 18, 5], [0, 19, 0], [0, 19, 1], [0, 19, 2], [0, 19, 3], [0, 19, 4], [0, 19, 5], [0, 20, 0], [0, 20, 1], [0, 20, 5], [0, 21, 0], [0, 21, 1], [0, 22, 0], [0, 22, 1], [0, 23, 0], [0, 24, 0]],
    'StadiumSculptBridgeSuspendSlopeEnd': [[0, 0, 2], [0, 0, 3], [0, 1, 2], [0, 1, 3], [0, 1, 4], [0, 2, 2], [0, 2, 3], [0, 2, 4], [0, 3, 2], [0, 3, 3], [0, 3, 4], [0, 4, 2], [0, 4, 3], [0, 4, 4], [0, 5, 1], [0, 5, 2], [0, 5, 3], [0, 5, 4], [0, 6, 1], [0, 6, 2], [0, 6, 3], [0, 6, 4], [0, 7, 1], [0, 7, 2], [0, 7, 3], [0, 7, 4], [0, 8, 1], [0, 8, 2], [0, 8, 3], [0, 8, 4], [0, 9, 1], [0, 9, 2], [0, 9, 3], [0, 9, 4], [0, 10, 1], [0, 10, 2], [0, 10, 3], [0, 10, 4], [0, 11, 1], [0, 11, 2], [0, 11, 3], [0, 11, 4], [0, 12, 1], [0, 12, 3], [0, 12, 4], [0, 13, 1], [0, 13, 3], [0, 13, 4], [0, 14, 1], [0, 14, 3], [0, 14, 4], [0, 14, 5], [0, 15, 0], [0, 15, 1], [0, 15, 2], [0, 15, 4], [0, 15, 5], [0, 16, 0], [0, 16, 1], [0, 16, 2], [0, 16, 3], [0, 16, 4], [0, 16, 5], [0, 17, 0], [0, 17, 1], [0, 17, 3], [0, 17, 4], [0, 17, 5], [0, 18, 0], [0, 18, 4], [0, 18, 5], [0, 19, 5], [0, 20, 5]],
    'StadiumSculptBridgeSuspendSlopeEndMirror': [[0, 0, 2], [0, 0, 3], [0, 1, 2], [0, 1, 3], [0, 1, 4], [0, 2, 2], [0, 2, 3], [0, 2, 4], [0, 3, 2], [0, 3, 3], [0, 3, 4], [0, 4, 2], [0, 4, 3], [0, 4, 4], [0, 5, 1], [0, 5, 2], [0, 5, 3], [0, 5, 4], [0, 6, 1], [0, 6, 2], [0, 6, 3], [0, 6, 4], [0, 7, 1], [0, 7, 2], [0, 7, 3], [0, 7, 4], [0, 8, 1], [0, 8, 2], [0, 8, 3], [0, 8, 4], [0, 9, 1], [0, 9, 2], [0, 9, 3], [0, 9, 4], [0, 10, 1], [0, 10, 2], [0, 10, 3], [0, 10, 4], [0, 11, 1], [0, 11, 2], [0, 11, 3], [0, 11, 4], [0, 12, 1], [0, 12, 3], [0, 12, 4], [0, 13, 1], [0, 13, 3], [0, 13, 4], [0, 14, 1], [0, 14, 3], [0, 14, 4], [0, 14, 5], [0, 15, 0], [0, 15, 1], [0, 15, 2], [0, 15, 4], [0, 15, 5], [0, 16, 0], [0, 16, 1], [0, 16, 2], [0, 16, 3], [0, 16, 4], [0, 16, 5], [0, 17, 0], [0, 17, 1], [0, 17, 3], [0, 17, 4], [0, 17, 5], [0, 18, 0], [0, 18, 4], [0, 18, 5], [0, 19, 5], [0, 20, 5]],
    'StadiumSculptBridgePillar': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0]],
    'StadiumSculptBridgePillarMirror': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0]],
    'StadiumSculptBridgeSlopeStart': [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 0]],
    'StadiumSculptBridgeSlopeStartMirror': [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 0]],
    'StadiumSculptBridgeSlopeEnd': [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 0]],
    'StadiumSculptBridgeSlopeEndMirror': [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 0]],
    'StadiumSculptBridgeStraight': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1]],
    'StadiumSculptBridgeStraightSmall': [[0, 0, 0], [0, 1, 0]],
    'StadiumTubePillarCap': [[0, 0, 0]],
    'StadiumTubeV1': [[0, 0, 0]],
    'StadiumTubeV4': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]],
    'StadiumTubeV8': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0]],
    'StadiumTube': [[0, 0, 0]],
    'StadiumTubePillar': [[0, 0, 0]],
    'StadiumTubePillarBranch': [[0, 0, 0]],
    'StadiumTubePillarBranch2': [[0, 0, 0]],
    'StadiumTubePillarBranch4': [[0, 0, 0]],
    'StadiumTubeRoad': [[0, 0, 0]],
    'StadiumTubeRoadDown': [[0, 0, 0]],
    'StadiumTubeRoadUp': [[0, 0, 0]],
    'StadiumTubeRoadCross': [[0, 0, 0]],
    'StadiumControlRoadGlass': [[0, 0, 0]],
    'StadiumControlRoadPub': [[0, 0, 0]],
    'StadiumControlRoadCamera': [[0, 0, 0]],
    'StadiumControlCameraPub': [[0, 0, 0]],
    'StadiumControlLight': [[0, 0, 0]],
    'StadiumControlLightBase': [[0, 0, 0]],
    'StadiumTubeRoadLightSystem': [[0, 0, 0]],
    'StadiumTubeRoadSoundSystem': [[0, 0, 0]],
    'StadiumFabricStraight1x1': [[0, 4, 0], [0, 5, 0], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 3, 0], [1, 4, 0]],
    'StadiumFabricPillarAir': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumFabricCornerIn': [[0, 0, 1], [0, 1, 1], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 4, 0], [0, 4, 1], [0, 5, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [1, 3, 0], [1, 4, 0]],
    'StadiumFabricPillarCornerInAir': [[0, 0, 1], [0, 1, 1], [0, 2, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1]],
    'StadiumFabricCornerOut': [[0, 5, 0], [0, 5, 1], [1, 0, 0], [1, 1, 0], [1, 2, 0], [1, 3, 0], [1, 4, 0], [1, 5, 0], [1, 5, 1]],
    'StadiumFabricPillarCornerOut': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumFabricCross1x1': [[0, 0, 0]],
    'StadiumFabricCross3x3': [[2, 0, 0], [2, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, 0], [0, 1, 0], [2, 1, 1], [2, 1, 2], [1, 1, 2], [0, 1, 2], [0, 1, 1], [1, 1, 1], [0, 0, 2], [0, 0, 1], [1, 0, 2], [2, 0, 2], [2, 0, 1]],
    'StadiumFabricCross3x3Screen': [[0, 0, 1], [0, 1, 1], [0, 2, 1], [0, 3, 0], [0, 3, 1], [0, 3, 2], [0, 4, 0], [0, 4, 1], [0, 4, 2], [0, 5, 0], [0, 5, 1], [0, 5, 2], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 1, 0], [1, 1, 1], [1, 1, 2], [1, 2, 0], [1, 2, 1], [1, 2, 2], [1, 3, 0], [1, 3, 1], [1, 3, 2], [1, 4, 0], [1, 4, 1], [1, 4, 2], [1, 5, 0], [1, 5, 1], [1, 5, 2], [2, 0, 1], [2, 1, 1], [2, 2, 1], [2, 3, 0], [2, 3, 1], [2, 3, 2], [2, 4, 0], [2, 4, 1], [2, 4, 2], [2, 5, 0], [2, 5, 1], [2, 5, 2]],
    'StadiumFabricPillarAirScreen': [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 2, 0], [0, 2, 1]],
    'StadiumFabricPillarScreenSmall': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumFabricRamp': [[0, 0, 0]],
    'StadiumFabricRampCornerOut': [[0, 0, 0]],
    'StadiumFabricRampCornerIn': [[0, 0, 1], [1, 0, 0], [1, 0, 1]],
    'StadiumInflatableSupport': [[0, 0, 0]],
    'StadiumInflatablePillar': [[0, 0, 0]],
    'StadiumInflatableTube': [[0, 0, 0]],
    'StadiumInflatableAdvert': [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 2, 0], [1, 2, 0], [0, 3, 0], [1, 3, 0]],
    'StadiumAirship': [[0, 0, 2], [0, 1, 1], [0, 1, 2], [0, 2, 1], [0, 2, 2], [0, 2, 3], [0, 2, 4], [0, 2, 5], [0, 3, 0], [0, 3, 1], [0, 3, 2], [0, 3, 3], [0, 3, 4], [0, 3, 5], [0, 4, 0], [0, 4, 1], [0, 4, 2], [0, 4, 3], [0, 4, 4], [0, 4, 5], [0, 5, 0], [0, 5, 1], [0, 5, 2], [0, 5, 3], [0, 5, 4], [0, 5, 5], [0, 6, 0], [0, 6, 1], [0, 6, 2], [0, 6, 3], [0, 6, 4], [0, 6, 5]],
    'StadiumAirshipDiag': [[0, 4, 0], [2, 0, 2], [2, 1, 2], [2, 2, 2], [2, 3, 2], [2, 4, 2], [2, 5, 2], [2, 6, 2], [2, 6, 1], [2, 5, 1], [2, 4, 1], [2, 3, 1], [2, 2, 1], [1, 2, 2], [1, 3, 2], [1, 4, 2], [1, 5, 2], [1, 6, 2], [1, 6, 1], [1, 5, 1], [1, 4, 1], [1, 3, 1], [0, 5, 1], [0, 4, 1], [0, 3, 1], [1, 5, 0], [1, 4, 0], [1, 3, 0], [2, 2, 3], [2, 3, 3], [2, 4, 3], [2, 5, 3], [2, 6, 3], [3, 6, 2], [3, 5, 2], [3, 4, 2], [3, 3, 2], [3, 2, 2], [3, 2, 3], [3, 3, 3], [3, 4, 3], [3, 5, 3], [3, 6, 3], [4, 6, 4], [4, 5, 4], [4, 4, 4], [4, 3, 4], [4, 2, 4], [4, 3, 3], [4, 4, 3], [4, 5, 3], [3, 5, 4], [3, 4, 4], [3, 3, 4], [1, 2, 1], [0, 3, 0], [0, 5, 0]],
    'StadiumInflatableCastle': [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
    'StadiumInflatableCastleDoor': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [1, 1, 0], [2, 0, 0], [2, 1, 0], [2, 2, 0]],
    'StadiumInflatableCastleBig': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1]],
    'StadiumInflatableCactus': [[0, 0, 0], [0, 1, 0]],
    'StadiumInflatableSnowTree': [[0, 0, 0], [0, 1, 0]],
    'StadiumInflatablePalmTree': [[0, 0, 0], [0, 1, 0]],
    'StadiumSculptA': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0], [0, 10, 0], [0, 11, 0]],
    'StadiumSculptB': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0], [0, 10, 0], [0, 11, 0]],
    'StadiumSculptC': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0], [0, 10, 0], [0, 11, 0]],
    'StadiumSculptArchRingEnd': [[0, 1, 1], [0, 2, 1], [0, 3, 1], [0, 4, 1], [0, 4, 2], [0, 5, 1], [0, 5, 2], [0, 6, 1], [0, 6, 2], [0, 7, 1], [0, 7, 2], [0, 7, 3], [0, 8, 2], [0, 8, 3], [0, 9, 2], [0, 9, 3], [0, 10, 2], [0, 10, 3], [0, 11, 3], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 2, 1], [1, 3, 0], [1, 3, 1], [1, 4, 1], [1, 4, 2], [1, 5, 1], [1, 5, 2], [1, 6, 1], [1, 6, 2], [1, 7, 1], [1, 7, 2], [1, 7, 3], [1, 8, 2], [1, 8, 3], [1, 9, 2], [1, 9, 3], [1, 9, 4], [1, 10, 2], [1, 10, 3], [1, 10, 4], [1, 10, 5], [1, 11, 3], [1, 11, 4], [1, 11, 5], [1, 12, 4], [1, 12, 5], [2, 0, 0], [2, 0, 1], [2, 1, 0], [2, 1, 1], [2, 2, 0], [2, 2, 1], [2, 9, 4], [2, 10, 4], [2, 10, 5], [2, 11, 4], [2, 11, 5], [2, 12, 4], [2, 12, 5], [2, 13, 5], [3, 10, 4], [3, 10, 5], [3, 11, 4], [3, 11, 5], [3, 12, 4], [3, 12, 5], [3, 13, 5]],
    'StadiumSculptArchRingEndMirror': [[0, 10, 4], [0, 10, 5], [0, 11, 4], [0, 11, 5], [0, 12, 4], [0, 12, 5], [0, 13, 5], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 2, 0], [1, 9, 4], [1, 10, 4], [1, 10, 5], [1, 11, 4], [1, 11, 5], [1, 12, 4], [1, 12, 5], [1, 13, 5], [2, 0, 0], [2, 0, 1], [2, 1, 0], [2, 1, 1], [2, 2, 0], [2, 2, 1], [2, 3, 0], [2, 3, 1], [2, 4, 1], [2, 4, 2], [2, 5, 1], [2, 5, 2], [2, 6, 1], [2, 6, 2], [2, 7, 1], [2, 7, 2], [2, 7, 3], [2, 8, 2], [2, 8, 3], [2, 9, 2], [2, 9, 3], [2, 9, 4], [2, 10, 2], [2, 10, 3], [2, 10, 4], [2, 10, 5], [2, 11, 3], [2, 11, 4], [2, 11, 5], [2, 12, 4], [2, 12, 5], [3, 1, 1], [3, 2, 1], [3, 3, 1], [3, 4, 1], [3, 4, 2], [3, 5, 1], [3, 5, 2], [3, 6, 1], [3, 6, 2], [3, 7, 1], [3, 7, 2], [3, 7, 3], [3, 8, 2], [3, 8, 3], [3, 9, 2], [3, 9, 3], [3, 10, 2], [3, 10, 3], [3, 11, 3]],
    'StadiumSculptArchRingStart': [[0, 0, 0], [0, 0, 1], [0, 0, 2], [0, 1, 1], [0, 1, 2], [0, 2, 1], [0, 2, 2], [0, 2, 3], [0, 3, 2], [0, 3, 3], [0, 4, 2], [0, 4, 3], [0, 5, 2], [0, 5, 3], [0, 6, 3], [0, 7, 3], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 1, 1], [1, 1, 2], [1, 2, 1], [1, 2, 2], [1, 2, 3], [1, 3, 2], [1, 3, 3], [1, 4, 2], [1, 4, 3], [1, 5, 2], [1, 5, 3], [1, 5, 4], [1, 6, 3], [1, 6, 4], [1, 7, 3], [1, 7, 4], [1, 8, 3], [1, 8, 4], [1, 9, 3], [1, 9, 4], [1, 10, 4], [2, 0, 0], [2, 6, 4], [2, 7, 3], [2, 7, 4], [2, 8, 3], [2, 8, 4], [2, 9, 3], [2, 9, 4], [2, 10, 4], [2, 10, 5], [2, 11, 4], [2, 11, 5], [2, 12, 4], [3, 8, 4], [3, 9, 4], [3, 10, 4], [3, 10, 5], [3, 11, 4], [3, 11, 5], [3, 12, 4], [3, 12, 5], [3, 13, 4]],
    'StadiumSculptArchRingStartMirror': [[0, 8, 4], [0, 9, 4], [0, 10, 4], [0, 10, 5], [0, 11, 4], [0, 11, 5], [0, 12, 4], [0, 12, 5], [0, 13, 4], [1, 0, 0], [1, 6, 3], [1, 6, 4], [1, 7, 3], [1, 7, 4], [1, 8, 3], [1, 8, 4], [1, 9, 3], [1, 9, 4], [1, 10, 4], [1, 10, 5], [1, 11, 4], [1, 11, 5], [1, 12, 4], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 1, 1], [2, 1, 2], [2, 2, 1], [2, 2, 2], [2, 2, 3], [2, 3, 2], [2, 3, 3], [2, 4, 2], [2, 4, 3], [2, 5, 2], [2, 5, 3], [2, 5, 4], [2, 6, 3], [2, 6, 4], [2, 7, 3], [2, 7, 4], [2, 8, 3], [2, 8, 4], [2, 9, 3], [2, 9, 4], [2, 10, 4], [3, 0, 0], [3, 0, 1], [3, 0, 2], [3, 1, 1], [3, 1, 2], [3, 2, 1], [3, 2, 2], [3, 2, 3], [3, 3, 2], [3, 3, 3], [3, 4, 2], [3, 4, 3], [3, 5, 2], [3, 5, 3], [3, 6, 3], [3, 7, 3]],
    'StadiumPodium': [[0, 0, 0], [0, 1, 0]],
    'StadiumDecoTowerCore6': [[0, 0, 0], [0, 1, 0], [0, 5, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0]],
    'StadiumDecoTowerCore': [[0, 0, 0]],
    'StadiumDecoTowerBeam': [[0, 0, 0]],
    'StadiumDecoTowerA': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0]],
    'StadiumDecoTowerB': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0]],
    'StadiumDecoTowerD': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0]],
    'StadiumDecoTowerC': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0]]
}

def rotate(vec, rot):
    if rot == 1:
        r = np.array([[0, 1], [-1, 0]])
    elif rot == 2:
        r = np.array([[-1, 0], [0, -1]])
    elif rot == 3:
        r = np.array([[0, -1], [1, 0]])
    else:
        return vec

    t = np.array([vec[0], vec[2]])
    x, z = np.dot(t, r)
    return [x, vec[1], z]

def rotate_track(blocks, rotation):
    for block in blocks:
        rotated, _, _ = rotate_block_offsets([block.position, [0, 0, 0], [31, 0, 31]], rotation)
        rotated = rotated[0]

        try:
            offsets = BLOCK_OFFSETS[block.name]
            offsets, _, _ = rotate_block_offsets(offsets, block.rotation)
            _, xoff, zoff = rotate_block_offsets(offsets, rotation)
            block.position = (rotated[0] + xoff, rotated[1], rotated[2] + zoff)
        except KeyError:
            block.position = rotated

        block.rotation = (block.rotation + rotation) % 4
    
    return blocks


def rotate_track_tuples(tblocks, rotation):
    blocks = []
    for tup in tblocks:
        block = MapBlock()
        block.name = get_block_name(tup[BID])
        block.rotation = tup[BROT]
        block.position = [tup[BX], tup[BY], tup[BZ]]
        blocks.append(block)
    
    return [block.to_tup() for block in rotate_track(blocks, rotation)]


def rotate_block_offsets(offsets, rot):
    rotated = [rotate(off, rot) for off in offsets]
    max_x, max_z = 0, 0

    def get_x(vec): return abs(vec[0])
    def get_z(vec): return abs(vec[2])

    if rot == 1:
        max_x = max(rotated, key=get_x)[0]
    elif rot == 2:
        max_x = max(rotated, key=get_x)[0]
        max_z = max(rotated, key=get_z)[2]
    elif rot == 3:
        max_z = max(rotated, key=get_z)[2]
    else:
        return rotated, 0, 0

    return [[off[0] + abs(max_x), off[1], off[2] + abs(max_z)] for off in rotated], max_x, max_z

def occupied_track_positions(track):
    positions = []
    for block in track:
        name = get_block_name(block[BID])
        if not name:
            continue

        try:
            offsets = BLOCK_OFFSETS[name]
        except KeyError:
            continue

        offsets, _, _ = rotate_block_offsets(offsets, block[BROT])
        for offset in offsets:
            positions.append([
                block[BX] + offset[0],
                block[BY] + offset[1],
                block[BZ] + offset[2]
            ])

    return positions


def intersects(track, block):
    track_offsets = occupied_track_positions(track)
    block_offsets = occupied_track_positions([block])

    for block_off in block_offsets:
        for track_off in track_offsets:
            if block_off == track_off:
                return True
    return False
