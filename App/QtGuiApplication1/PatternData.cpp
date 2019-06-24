#include "PatternData.h"
#include <fstream>
#include <sstream>
#include "BlockUtils.h"

PatternData::PatternData(const std::string& path)
{
	std::ifstream is(path);

	std::stringstream ss;
	ss << is.rdbuf();

	j = json::parse(ss.str());

	data.reserve(j["data"].size());
	for (auto obj : j["data"]) {
		PatternEntry entry;
		entry.bid = obj[0].get<int>();
		entry.neighbour.id = obj[1].get<int>();
		entry.neighbour.pos.x = obj[2].get<int>();
		entry.neighbour.pos.y = obj[3].get<int>();
		entry.neighbour.pos.z = obj[4].get<int>();
		entry.neighbour.rot = (Rotation)obj[5].get<int>();
		entry.occurences = obj[6].get<int>();
		data.push_back(entry);
	}
}

PatternData::~PatternData()
{
}

int PatternData::score(Block prevBlock, Block nextBlock)
{
	prevBlock.pos = { 0, 0, 0 };
	auto normalized = block_utils::rotateBlocks({ prevBlock, nextBlock }, (Rotation)((4 - prevBlock.rot) % 4));

	prevBlock = normalized[0];
	nextBlock = normalized[1];
	nextBlock.pos = nextBlock.pos.subtract(prevBlock.pos);

	for (auto entry : data) {
		if (entry.bid == prevBlock.id && entry.neighbour == nextBlock) {
			return entry.occurences;
		}
	}

	return 0;
}
