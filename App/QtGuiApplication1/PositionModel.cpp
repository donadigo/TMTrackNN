#include "PositionModel.h"
#include "Config.h"
#include "Utils.h"
#include "tf.h"

PositionModel::PositionModel(const std::string& path):
	session(path, "input_1", {"pos/BiasAdd", "rot/Softmax"})
{
}


PositionModel::~PositionModel()
{
}

void PositionModel::predict(const Float2D& input,
	std::vector<float>& position, std::vector<float>& rotation)
{
	const int featureLength = NUM_BLOCKS + 7;
	const int length = LOOKBACK * featureLength * sizeof(float);
	const int64_t dims[] = { 1, LOOKBACK, featureLength };
	auto tensor = TFL.AllocateTensor(TF_DataType::TF_FLOAT, dims, 3, length);

	auto tensorData = TFL.TensorData(tensor);

	std::vector<float> inputVector;
	for (auto vec : input) {
		inputVector.insert(inputVector.end(), vec.begin(), vec.end());
	}

	std::memcpy(tensorData, inputVector.data(), length);

	auto out = session.predict(tensor);
	if (!out) {
		return;
	}

	auto positionArr = static_cast<float*>(TFL.TensorData(out[0]));
	auto rotationArr = static_cast<float*>(TFL.TensorData(out[1]));

	position.assign(positionArr, positionArr + 3);
	rotation.assign(rotationArr, rotationArr + 4);
	utils::FreeTensors(out, 2);
}
