#pragma once
#include <vector>
#include "Types.h"
class GameMap
{
public:
	GameMap(Vector3i size);
	~GameMap();
	std::vector<Block>& operator()();
	const Block& operator[](int index);
	const std::vector<Block>& getDecoded();
	const std::vector<Vector3i>& getOccupied();
	std::vector<Block> center();
	std::vector<Block> filterBlocks(const std::vector<Block>& blocks, const std::vector<int>& blacklist);
	bool exceedsSize();
	Vector3i getSize() const;
	int length();
	void clear();
	void add(Block block);
	void pop();
	void setStartVector(Vector3i vec);
	void update();
private:
	std::vector<Block> track;
	std::vector<Vector3i> occupied;
	std::vector<Block> decoded;
	Vector3i size;
	Vector3i startVector;

	std::pair<Vector3i, Vector3i> getBounds();
};

