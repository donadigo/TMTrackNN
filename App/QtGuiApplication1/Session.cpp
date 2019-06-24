#include "Session.h"
#include <tensorflow/c_api.h>
#include <Windows.h>
#include <chrono>
#include <array>
#include "tf.h"
#include <iostream>
#include "Utils.h"


Session::Session(const std::string& path, const std::string& inputName, const std::vector<std::string>& outputs)
{
	graph = tf::LoadGraph(path.c_str());
	if (!graph) {
		return;
	}

	inputOp = { TFL.GraphOperationByName(graph, inputName.c_str()), 0 };
	for (auto output : outputs)
		outputOps.push_back({ TFL.GraphOperationByName(graph, output.c_str()), 0 });

	status = TFL.NewStatus();

	auto opts = TFL.NewSessionOptions();
	sess = TFL.NewSession(graph, opts, status);

	TFL.DeleteSessionOptions(opts);
}

Session::~Session()
{
	if (sess) TFL.DeleteSession(sess, status);
	if (graph) TFL.DeleteGraph(graph);
	if (status) TFL.DeleteStatus(status);
}

TF_Tensor** Session::predict(TF_Tensor* inputs)
{
	TF_Tensor** outputs = new TF_Tensor*[outputOps.size()];
	TFL.SessionRun(sess, nullptr, &inputOp, &inputs, 1, outputOps.data(), outputs, outputOps.size(), nullptr, 0, nullptr, status);
	if (!CHECK_STATUS(status)) {
		utils::FreeTensors(outputs, outputOps.size());
		return nullptr;
	}

	return outputs;
}
