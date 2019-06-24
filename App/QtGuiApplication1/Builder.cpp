#include <random>
#include <tuple>
#include "Builder.h"
#include "PositionModel.h"
#include "Utils.h"
#include "Config.h"
#include "StadiumBlocks.h"
#include "BlockUtils.h"
#include "TechWeights.h"
#include <math.h>
#include <iostream>

#define MAX_BLACKLIST_SIZE 10

using namespace blocks;

template<typename T>
static inline int randomRange(T low, T high)
{
	return rand() % (high - low) + low;
}

static inline Block getRandomStartBlock()
{
	return { START_LINE_BLOCK, { 0, 0, 0 }, (Rotation)randomRange<int>(0, 4) };
}

static std::vector<float> blockToVector(const int inputLen, const Block& block, const bool encodePos)
{
	std::vector<float> vec(inputLen);
	vec[block.id - 1] = 1.0f;
	if (encodePos) {
		vec[NUM_BLOCKS] = block.pos.x * SCALE_VECTOR[0] + MIN_VECTOR[0];
		vec[NUM_BLOCKS + 1] = block.pos.y * SCALE_VECTOR[1] + MIN_VECTOR[1];
		vec[NUM_BLOCKS + 2] = block.pos.z * SCALE_VECTOR[2] + MIN_VECTOR[2];
		vec[NUM_BLOCKS + 3 + block.rot] = 1.0f;
	}
	else {
		std::fill(vec.begin() + NUM_BLOCKS, vec.end(), -1.0f);
	}

	return vec;
}

void Builder::prepareInputs(Float2D& XBlock, Float2D& XPosition)
{
	XBlock.resize(lookback, std::vector<float>(NUM_BLOCKS));
	XPosition.resize(lookback, std::vector<float>(INPUT_LEN));

	int length = map.length();
	int end = length > lookback ? length - lookback : 0;

	int step = lookback - 1;
	for (int i = length - 1; i >= end; i--) {
		auto block = map[i];
		XBlock[step][block.id - 1] = 1.0f;
		
		auto encoding = blockToVector(INPUT_LEN, block, true);
		XPosition[step] = encoding;
		step--;
	}
}

std::pair<Block, std::vector<float>> Builder::predictNextBlock(const Float2D& XBlock,
	Float2D XPosition,
	const std::vector<float>& prevBlockPreds, 
	std::vector<int> blacklist, int blockOverride)
{
	Block block;

	std::vector<float> predsVector;
	if (blockOverride == -1) {
		if (!prevBlockPreds.empty()) {
			predsVector = prevBlockPreds;
		} else {
			predsVector = blockModel->predict(XBlock);
			for (int i = 0; i < blockWeights.size(); i++) {
				predsVector[i] *= blockWeights[i];
			}
		}

		for (int id : blacklist) {
			predsVector[id - 1] = 0;
		}

		block.id = BlockModel::sample(predsVector, temperature) + 1;
	} else {
		block.id = blockOverride;
	}

	for (int i = 1; i < lookback; i++) {
		XPosition[i - 1] = XPosition[i];
	}

	auto last = blockToVector(INPUT_LEN, block, false);
	XPosition[lookback - 1] = last;
	
	std::vector<float> position, rotation;
	positionModel->predict(XPosition, position, rotation);

	block.pos = { (int)std::round(position[0]), (int)std::round(position[1]), (int)std::round(position[2]) };
	block.rot = (Rotation)utils::argmax(rotation);

	return std::make_pair(block, predsVector);
}

Builder::Builder(std::unique_ptr<BlockModel> blockModel, std::unique_ptr<PositionModel> positionModel):
	blockModel(std::move(blockModel)),
	positionModel(std::move(positionModel)),
	pdata(PATTERN_DATA_PATH),
	blockWeights(getTechWeights()),
	map({ 20, 8, 20 }),
	lookback(LOOKBACK),
	temperature(1.2)
{
}

Builder::~Builder()
{
}

std::vector<Block> Builder::build(const int length, const bool failSafe,
	std::function<void(int, int)> progressCallback)
{
	running = true;
	map.clear();
	map.add(getRandomStartBlock());

	std::vector<int> blacklist;
	const int fixedY = randomRange(1, 5);
	const Vector3i startVector = { 0, fixedY, 0 };
	map.setStartVector(startVector);

	std::vector<float> currentBlockPreds;
	while (map.length() < length) {
		if (!running) {
			return {};
		}

		int mapLength = map.length();

		bool end = mapLength == length - 1;

		int bSize = blacklist.size();
		if (bSize >= MAX_BLACKLIST_SIZE || (bSize == 1 && end)) {
			int back;
			if (mapLength > length - 5) {
				back = 5;
			} else if (end) {
				back = 10;
			}
			else {
				back = randomRange<int>(2, 6);
			}

			int endIdx = (std::min)(mapLength - 1, back);
			if (endIdx > 0) {
				map().erase(map().end() - endIdx - 1, map().end());
			}

			end = false;
			blacklist.clear();
			currentBlockPreds = {};
		}

		int overrideBlock = end ? FINISH_LINE_BLOCK : -1;

		Float2D XBlock, XPosition;
		prepareInputs(XBlock, XPosition);

		auto pair = predictNextBlock(XBlock, XPosition, currentBlockPreds, blacklist, overrideBlock);
		auto block = pair.first;
		currentBlockPreds = pair.second;

		map.add(block);
		map.update();
		auto decoded = map.getDecoded();

		if (failSafe) {
#define BACKTRACK() {\
	blacklist.push_back(block.id); \
	map.pop(); \
	continue; \
}
			if (map.exceedsSize()) {
				BACKTRACK();
			}

			int minY = decoded.back().pos.y;
			auto occ = block_utils::getOccupiedBlockVectors({ decoded.back() });
			if (!occ.empty()) {
				for (auto off : occ) {
					minY = (std::min)(minY, off.y);
				}
			}

			if (minY > 1 &&
				(block.id == GRASS_BLOCK ||
					std::find(blocks::GROUND_BLOCKS.begin(), blocks::GROUND_BLOCKS.end(), block.id) != blocks::GROUND_BLOCKS.end())) {
				BACKTRACK();
			}

			std::vector<Block> current(decoded.begin(), decoded.end() - 1);
			if (block_utils::intersects(current, decoded.back()) ||
				(block.id == FINISH_LINE_BLOCK && !end)) {
				BACKTRACK();
			}

			if (map.length() >= 2) {
				auto prev = map[map.length() - 2];
				if (pdata.score(prev, block) < 5) {
					BACKTRACK();
				}
			}
#undef BACKTRACK
		}

		blacklist.clear();
		currentBlockPreds = {};
		progressCallback(map.length(), length);
	}

	map.update();
	return map.filterBlocks(map.center(), { GRASS_BLOCK });
}

void Builder::stop()
{
	running = false;
}

void Builder::setTemperature(const float _temperature)
{
	temperature = _temperature;
}
