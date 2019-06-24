#pragma once
#include <string>
#include <vector>
#include "Session.h"
#include "Types.h"
#include "Config.h"

class BlockModel
{
public:
	BlockModel(std::string path);
	~BlockModel();
	static int sample(std::vector<float> preds, const float temperature);
	std::vector<float> predict(const Float2D& input);
private:
	Session session;
};

