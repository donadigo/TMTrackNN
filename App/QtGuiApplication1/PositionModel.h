#pragma once
#include "Session.h"
#include "Types.h"

class PositionModel
{
public:
	PositionModel(const std::string& path);
	~PositionModel();
	void predict(const Float2D& input, std::vector<float>& position, std::vector<float>& rotation);
private:
	Session session;
};

