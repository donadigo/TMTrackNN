#define NOMINMAX
#pragma once
#include <vector>
#include <sstream>
#include <iostream>

typedef std::vector<std::vector<float>> Float2D;

#define Vector3i Vector3<int>
#define Vector3f Vector3<float>
enum Rotation
{
	NORTH = 0,
	EAST = 1,
	SOUTH = 2,
	WEST = 3
};

template <typename T>
struct Vector3
{
	T x;
	T y;
	T z;

	Vector3<T> add(const Vector3<T> other) {
		return { x + other.x, y + other.y, z + other.z };
	}

	Vector3<T> subtract(const Vector3<T> other) {
		return { x - other.x, y - other.y, z - other.z };
	}
};


struct Block
{
	int id;
	Vector3i pos;
	Rotation rot;
};

template <typename T>
inline std::ostream& operator<<(std::ostream& os, const Vector3<T>& vec) {
	return os << vec.x << " " << vec.y << " " << vec.z << " ";
}

template <typename T>
inline bool operator==(const Vector3<T>& a, const Vector3<T>& b) {
	return a.x == b.x && a.y == b.y && a.z == b.z;
}

inline bool operator==(const Block& a, const Block& b) {
	return a.id == b.id && a.pos == b.pos && a.rot == b.rot;
}

inline std::ostream& operator<<(std::ostream& os, const Block& block) {
	return os << block.id << " " << block.pos.x << " " << block.pos.y << " " << block.pos.z << " " << block.rot;
}