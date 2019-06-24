#pragma once
#include <vector>
#include <string>
#include <algorithm>
#include <tuple>
#include <climits>
#include "Types.h"
#include "StadiumBlocks.h"

namespace block_utils {

static Vector3i rotate(const Vector3i vec, const Rotation rot)
{
	std::vector<std::vector<int>> mat;
	switch (rot) {
	case Rotation::EAST:
		mat = { {0, 1}, {-1, 0} };
		break;
	case Rotation::SOUTH:
		mat = { {-1, 0}, {0, -1} };
		break;
	case Rotation::WEST:
		mat = { {0, -1}, {1, 0} };
		break;
	default:
		return vec;
	}

	Vector3i rotated = vec;
	rotated.x = vec.x * mat[0][0] + vec.z * mat[1][0];
	rotated.z = vec.x * mat[0][1] + vec.z * mat[1][1];
	return rotated;
}

static std::tuple<std::vector<Vector3i>, int, int> rotateBlockOffsets(const std::vector<Vector3i>& offsets, const Rotation rot)
{
	std::vector<Vector3i> rotated;

	int maxX = 0, maxZ = 0;
	switch (rot) {
	case Rotation::EAST:
		for (auto off : offsets) {
			rotated.push_back(rotate(off, rot));
			maxX = (std::max)(maxX, std::abs(rotated.back().x));
		}

		break;
	case Rotation::SOUTH:
		for (auto off : offsets) {
			rotated.push_back(rotate(off, rot));
			maxX = (std::max)(maxX, std::abs(rotated.back().x));
			maxZ = (std::max)(maxZ, std::abs(rotated.back().z));
		}

		break;
	case Rotation::WEST:
		for (auto off : offsets) {
			rotated.push_back(rotate(off, rot));
			maxZ = (std::max)(maxZ, std::abs(rotated.back().z));
		}

		break;
	default:
		return std::make_tuple(offsets, 0, 0);
	}

	for (int i = 0; i < rotated.size(); i++) {
		auto vec = rotated[i];
		rotated[i] = { vec.x + std::abs(maxX), vec.y, vec.z + std::abs(maxZ) };
	}

	return std::make_tuple(rotated, maxX, maxZ);
}

static std::vector<Block> rotateBlocks(const std::vector<Block>& blocks, const Rotation rot)
{
	std::vector<Block> result;
	result.reserve(blocks.size());
	for (auto block : blocks) {
		auto rotated = std::get<0>(rotateBlockOffsets({ block.pos,{ 0, 0, 0 },{ 31, 0, 31 } }, rot));
		auto pivot = rotated[0];

		Rotation resultRot = static_cast<Rotation>(((int)block.rot + (int)rot) % 4);

		if (block.id > blocks::BLOCKS.size()) {
			result.push_back({ block.id, pivot, resultRot });
			continue;
		}

		auto name = blocks::BLOCKS[block.id - 1];
		auto offsets = blocks::getBlockOffsets(name);
		offsets = std::get<0>(rotateBlockOffsets(offsets, block.rot));

		auto tup = rotateBlockOffsets(offsets, rot);
		auto maxX = std::get<1>(tup);
		auto maxZ = std::get<2>(tup);
		Vector3i pos = { pivot.x + maxX, pivot.y, pivot.z + maxZ };

		result.push_back({ block.id, pos, resultRot });
	}

	return result;
}

static std::vector<Vector3i> getOccupiedBlockVectors(const std::vector<Block>& blocks)
{
	std::vector<Vector3i> occ;
	for (auto block : blocks) {
		if (block.id > blocks::BLOCKS.size()) {
			occ.push_back(block.pos);
			continue;
		}

		auto name = blocks::BLOCKS[block.id - 1];
		auto offsets = blocks::getBlockOffsets(name);
		offsets = std::get<0>(rotateBlockOffsets(offsets, block.rot));
		for (int i = 0; i < offsets.size(); i++) {
			offsets[i] = offsets[i].add(block.pos);
		}

		occ.reserve(occ.size() + offsets.size());
		occ.insert(occ.end(), offsets.begin(), offsets.end());
	}

	return occ;
}

static bool intersects(const std::vector<Block>& blocks, const Block& block)
{
	auto trackOffsets = getOccupiedBlockVectors(blocks);
	auto blockOffsets = getOccupiedBlockVectors({ block });

	for (auto blockOff : blockOffsets) {
		for (auto trackOff : trackOffsets) {
			if (blockOff == trackOff) {
				return true;
			}
		}
	}

	return false;
}

static std::string toPythonString(const std::vector<Block>& blocks)
{
	std::string str = "[";
	for (int i = 0; i < blocks.size(); i++) {
		str += "(";
		auto block = blocks[i];
		str += std::to_string(block.id);
		str += ",";
		str += std::to_string(block.pos.x);
		str += ",";
		str += std::to_string(block.pos.y);
		str += ",";
		str += std::to_string(block.pos.z);
		str += ",";
		str += std::to_string((int)block.rot);

		str += ")";
		if (i < blocks.size() - 1) {
			str += ",";
		}
	}

	str += "]";
	return str;
}

}