#pragma once
#include <array>
#include "StadiumBlocks.h"

static std::vector<float> getTechWeights()
{
	std::vector<float> weights(blocks::BLOCKS.size(), 1.0f);
	// StadiumRoadMain
	weights[6 - 1] = 0.5;

		// StadiumPlatformTo*
	weights[127 - 1] = 0.8f;
	weights[128 - 1] = 0.8f;
	weights[129 - 1] = 0.8f;

	// Circuit blocks
	for (int i = 131; i < 195+1; i++) {
		weights[i - 1] = 4;
	}

	// StadiumPlatformToRoadMain
	weights[130 - 1] = 4;

	// StadiumCircuitBase
	weights[136 - 1] = 2;

	// Dirt blocks
	for (int i = 196; i < 233 + 1; i++) {
		weights[i - 1] = 120;
	}

	// Decoration blocks that can be used to build
	for (int i = 264; i < 279 + 1 + 1; i++) {
		weights[i - 1] = 3;
	}

	return weights;
}
