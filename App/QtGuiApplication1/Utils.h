#pragma once
#include <vector>
#include "tf.h"
#include "BlockUtils.h"
#include "Config.h"

namespace utils {
template<class T>
inline std::vector<float> FlattenVector(std::vector<std::vector<float>> m)
{
	std::vector<T> a;
	for (auto vec : m) {
		for (auto element : m) {
			a.push_back(element);
		}
	}

	return a;
}

template <typename T>
static inline int argmax(std::vector<T> vec)
{
	int max = 0;
	if (vec.size() == 1) {
		return max;
	}

	for (int i = 1; i < vec.size(); i++) {
		if (vec[i] > vec[max]) {
			max = i;
		}
	}

	return max;
}

static void saveTrack(const std::vector<Block>& track, const std::string& path, const std::string& mapName, int mood) {
	std::string s = block_utils::toPythonString(track);
	std::ostringstream ss;
	ss << SAVEGBX_PATH << " -o " << "\"" << path << "\"";
	ss << " -t " << TEMPLATE_PATH;
	ss << " -d \"" << s << "\"";
	ss << " -n " << "\"" << mapName << "\"";
	ss << " -m " << std::to_string(mood);

	WinExec(ss.str().c_str(), SW_HIDE);
}

static inline void FreeTensors(TF_Tensor** tensors, int size)
{
	for (int i = 0; i < size; i++)
		TFL.DeleteTensor(tensors[i]);
}
}

