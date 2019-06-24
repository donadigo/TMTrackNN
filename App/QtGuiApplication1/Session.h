#pragma once
#include <tensorflow/c_api.h>
#include <string>
#include <vector>
#define CHECK_STATUS(status) TFL.GetCode(status) == TF_OK
class Session
{
public:
	Session(const std::string& path, const std::string& inputName, const std::vector<std::string>& outputs);
	~Session();
	TF_Tensor** predict(TF_Tensor* inputs);
private:
	TF_Graph* graph;
	TF_Session* sess;
	TF_Status* status;
	TF_Output inputOp;
	std::vector<TF_Output> outputOps;
};

