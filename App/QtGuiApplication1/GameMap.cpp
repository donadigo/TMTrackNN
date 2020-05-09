#include "GameMap.h"
#include "BlockUtils.h"

GameMap::GameMap(Vector3i size) :
	size(size)
{
}

GameMap::~GameMap()
{
}

std::vector<Block>& GameMap::operator()()
{
	return track;
}

const Block & GameMap::operator[](int index)
{
	return track[index];
}

const std::vector<Block>& GameMap::getDecoded()
{
	return decoded;
}

const std::vector<Vector3i>& GameMap::getOccupied()
{
	return occupied;
}

void GameMap::clear()
{
	track.clear();
}

void GameMap::add(Block block)
{
	track.push_back(block);
}

void GameMap::pop()
{
	track.pop_back();
}

void GameMap::setStartVector(Vector3i vec)
{
	startVector = vec;
}

std::pair<Vector3i, Vector3i> GameMap::getBounds()
{
	Vector3i minVector = occupied[0];
	Vector3i maxVector = occupied[0];
	for (int i = 1; i < occupied.size(); i++) {
		auto off = occupied[i];
		minVector.x = (std::min)(minVector.x, off.x);
		minVector.y = (std::min)(minVector.y, off.y);
		minVector.z = (std::min)(minVector.z, off.z);
		maxVector.x = (std::max)(maxVector.x, off.x);
		maxVector.y = (std::max)(maxVector.y, off.y);
		maxVector.z = (std::max)(maxVector.z, off.z);
	}

	return std::make_pair(minVector, maxVector);
}

void GameMap::update()
{
	decoded.clear();
	decoded.reserve(length());

	decoded.push_back({ track[0].id, startVector, track[0].rot });
	for (int i = 1; i < track.size(); i++) {
		auto block = track[i];
		auto prev = decoded[i - 1];
		decoded.push_back({
			block.id,
			block.pos.add(prev.pos),
			block.rot
		});
	}

	occupied = block_utils::getOccupiedBlockVectors(decoded);
}

std::vector<Block> GameMap::center()
{
	auto bounds = getBounds();
	auto minVector = bounds.first;
	auto maxVector = bounds.second;

	minVector.y -= 1;
	maxVector.y -= 1;

	int cx = 32 - (maxVector.x - minVector.x + 1);
	if (cx > 0) {
		cx = cx / 2;
	}

	int cz = 32 - (maxVector.z - minVector.z + 1);
	if (cz > 0) {
		cz = cz / 2;
	}

	minVector.x = minVector.x >= 0 ? 0 : minVector.x;
	minVector.y = minVector.y >= 0 ? 0 : minVector.y;
	minVector.z = minVector.z >= 0 ? 0 : minVector.z;

	maxVector.x = maxVector.x < 32 ? 0 : maxVector.x - 31;
	maxVector.y = maxVector.y < 32 ? 0 : maxVector.y - 31;
	maxVector.z = maxVector.z < 32 ? 0 : maxVector.z - 31;

	Vector3i anchorOffset = { minVector.x - maxVector.x, 0, minVector.z - maxVector.z };
	Vector3i centerOffset = { cx, 0, cz };

	std::vector<Block> centered;
	for (auto block : decoded) {
		centered.push_back({
			block.id,
			block.pos.subtract(anchorOffset).add(centerOffset),
			block.rot
		});
	}

	return centered;
}

std::vector<Block> GameMap::filterBlocks(const std::vector<Block>& blocks, const std::vector<int>& blacklist)
{
	std::vector<Block> filtered;
	for (auto block : blocks) {
		if (std::find(blacklist.begin(), blacklist.end(), block.id) != blacklist.end()) {
			continue;
		}

		filtered.push_back(block);
	}

	return filtered;
}

bool GameMap::exceedsSize()
{
	auto bounds = getBounds();
	auto minVector = bounds.first;
	auto maxVector = bounds.second;

	return maxVector.x - minVector.x + 1 > size.x ||
		maxVector.y - minVector.y + 1 > size.y ||
		maxVector.z - minVector.z + 1 > size.z ||
		minVector.y < 1;
}

Vector3i GameMap::getSize() const
{
	return size;
}

int GameMap::length()
{
	return track.size();
}
