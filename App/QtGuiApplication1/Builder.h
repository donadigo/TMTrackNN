#pragma once
#include <vector>
#include <string>
#include <functional>
#include "BlockModel.h"
#include "PositionModel.h"
#include "GameMap.h"
#include "PatternData.h"
#include "Types.h"
#include "StadiumBlocks.h"

enum RestMessageType {
	ADD_BLOCK,
	REMOVE_BLOCKS,
	FINISHED,
	SKIP
};

struct BuilderRestMessage {
	RestMessageType type;
	Block block;
	int nRemoved;

	std::string toString() {
		std::string str = "Type=";
		switch (type) {
		case ADD_BLOCK:
			str += "AddBlock\n";
			str += blockToString();
			break;
		case REMOVE_BLOCKS:
			str += "RemoveBlocks\n";
			str += "NRemoved=" + std::to_string(nRemoved);
			break;
		case FINISHED:
			str += "Finished";
			break;
		case SKIP:
			str += "Skip";
			break;
		}

		return str;
	}

	std::string blockToString() {
		std::string str = "Name=";
		str += blocks::getBlockName(block.id) + "\n";
		str += "X=" + std::to_string(block.pos.x) + "\n";
		str += "Y=" + std::to_string(block.pos.y) + "\n";
		str += "Z=" + std::to_string(block.pos.z) + "\n";
		str += "R=" + std::to_string(block.rot);
		return str;
	}
};

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

	int lengthRest;
	std::vector<int> blacklistRest;
	std::vector<float> currentBlockPredsRest;


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

	GameMap& getMap();
	int startRest(const int length);
	BuilderRestMessage step();

	void blacklistPrevRest();

	void stop();
	void setTemperature(const float _temperature);
};