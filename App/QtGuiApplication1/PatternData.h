#pragma once
#include <string>
#include <nlohmann\json.hpp>
#include "Types.h"

using json = nlohmann::json;

struct PatternEntry
{
	int bid;
	Block neighbour;
	int occurences;
};

class PatternData
{
public:
	PatternData(const std::string& path);
	~PatternData();
	int score(Block prevBlock, Block nextBlock);
private:
	json j;
	std::vector<PatternEntry> data;
};

