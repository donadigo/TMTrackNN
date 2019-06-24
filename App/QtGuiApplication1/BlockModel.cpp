#include <random>
#include <array>
#include "BlockModel.h"
#include "Utils.h"
#include "tf.h"

BlockModel::BlockModel(std::string path):
	session(path, "lstm_1_input", { "dense_1/Softmax" })
{
}


BlockModel::~BlockModel()
{

}

int BlockModel::sample(std::vector<float> preds, const float temperature)
{
	float sum = 0;
	for (int i = 0; i < preds.size(); i++) {
		preds[i] = std::exp(std::log(preds[i]) / temperature);
		sum += preds[i];
	}

	std::vector<int> weights(preds.size());
	for (int i = 0; i < preds.size(); i++) {
		weights[i] = (int)(preds[i] / sum * 100);
	}

	std::discrete_distribution<> d(weights.begin(), weights.end());
	std::random_device rd;
	std::mt19937 gen(rd());

	return d(gen);
}


std::vector<float> BlockModel::predict(const Float2D& input)
{
	const int length = LOOKBACK * NUM_BLOCKS * sizeof(float);
	const int64_t dims[] = { 1, LOOKBACK, NUM_BLOCKS };
	auto tensor = TFL.AllocateTensor(TF_DataType::TF_FLOAT, dims, 3, length);

	auto tensorData = TFL.TensorData(tensor);

	std::vector<float> inputVector;
	for (auto vec : input) {
		inputVector.insert(inputVector.end(), vec.begin(), vec.end());
	}

	std::memcpy(tensorData, inputVector.data(), length);

	auto out = session.predict(tensor);
	if (!out) {
		return {};
	}

	auto arr = static_cast<float*>(TFL.TensorData(out[0]));

	std::vector<float> vec(NUM_BLOCKS);
	vec.assign(arr, arr + NUM_BLOCKS);
	utils::FreeTensors(out, 1);
	return vec;
}
