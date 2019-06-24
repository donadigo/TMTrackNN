#pragma once
#include <vector>
#include <string>
#include <functional>
#include "BlockModel.h"
#include "PositionModel.h"
#include "GameMap.h"
#include "PatternData.h"
#include "Types.h"


class Builder
{
private:
	std::unique_ptr<BlockModel> blockModel;
	std::unique_ptr<PositionModel> positionModel;
	GameMap map;
	PatternData pdata;
	uint16_t lookback;
	float temperature;
	bool running = false;
	std::vector<float> blockWeights;

	void prepareInputs(Float2D& XBlock, Float2D& XPosition);
	std::pair<Block, std::vector<float>> predictNextBlock(const Float2D& XBlock,
														Float2D XPosition,
														const std::vector<float>& prevBlockPreds,
														std::vector<int> blacklist,
														int blockOverride);

public:
	Builder(std::unique_ptr<BlockModel> blockModel, std::unique_ptr<PositionModel> positionModel);
	~Builder();
	std::vector<Block> build(const int length, const bool failSafe, std::function<void(int, int)> progressCallback);
	void stop();
	void setTemperature(const float _temperature);
};