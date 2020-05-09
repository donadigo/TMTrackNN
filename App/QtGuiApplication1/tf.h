#pragma once
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <Windows.h>
#include <tensorflow/c_api.h>
#include <fstream>
#include <iostream>
#include <stdio.h>
#define GET_ADDRESS(hModule, name) (decltype(name)*)GetProcAddress(hModule, #name)

#define TFL tf::TFLib::GetDefault()

namespace tf {
	class TFLib {
	public:
		decltype(TF_AbortWhile)* AbortWhile;
		decltype(TF_AddControlInput)* AddControlInput;
		decltype(TF_AddGradients)* AddGradients;
		decltype(TF_AddInput)* AddInput;
		decltype(TF_AddInputList)* AddInputList;
		decltype(TF_AllocateTensor)* AllocateTensor;
		decltype(TF_CloseDeprecatedSession)* CloseDeprecatedSession;
		decltype(TF_CloseSession)* CloseSession;
		decltype(TF_ColocateWith)* ColocateWith;
		decltype(TF_DataTypeSize)* DataTypeSize;
		decltype(TF_DeleteBuffer)* DeleteBuffer;
		decltype(TF_DeleteDeprecatedSession)* DeleteDeprecatedSession;
		decltype(TF_DeleteDeviceList)* DeleteDeviceList;
		decltype(TF_DeleteFunction)* DeleteFunction;
		decltype(TF_DeleteGraph)* DeleteGraph;
		decltype(TF_DeleteImportGraphDefOptions)* DeleteImportGraphDefOptions;
		decltype(TF_DeleteLibraryHandle)* DeleteLibraryHandle;
		decltype(TF_DeletePRunHandle)* DeletePRunHandle;
		decltype(TF_DeleteSession)* DeleteSession;
		decltype(TF_DeleteSessionOptions)* DeleteSessionOptions;
		decltype(TF_DeleteStatus)* DeleteStatus;
		decltype(TF_DeleteTensor)* DeleteTensor;
		decltype(TF_DeprecatedSessionListDevices)* DeprecatedSessionListDevices;
		decltype(TF_DeviceListCount)* DeviceListCount;
		decltype(TF_DeviceListMemoryBytes)* DeviceListMemoryBytes;
		decltype(TF_DeviceListName)* DeviceListName;
		decltype(TF_DeviceListType)* DeviceListType;
		decltype(TF_Dim)* Dim;
		decltype(TF_ExtendGraph)* ExtendGraph;
		decltype(TF_FinishOperation)* FinishOperation;
		decltype(TF_FinishWhile)* FinishWhile;
		decltype(TF_FunctionGetAttrValueProto)* FunctionGetAttrValueProto;
		decltype(TF_FunctionImportFunctionDef)* FunctionImportFunctionDef;
		decltype(TF_FunctionSetAttrValueProto)* FunctionSetAttrValueProto;
		decltype(TF_FunctionToFunctionDef)* FunctionToFunctionDef;
		decltype(TF_GetAllOpList)* GetAllOpList;
		decltype(TF_GetBuffer)* GetBuffer;
		decltype(TF_GetCode)* GetCode;
		decltype(TF_GetOpList)* GetOpList;
		decltype(TF_GraphCopyFunction)* GraphCopyFunction;
		decltype(TF_GraphGetTensorNumDims)* GraphGetTensorNumDims;
		decltype(TF_GraphGetTensorShape)* GraphGetTensorShape;
		decltype(TF_GraphImportGraphDef)* GraphImportGraphDef;
		decltype(TF_GraphImportGraphDefWithReturnOutputs)* GraphImportGraphDefWithReturnOutputs;
		decltype(TF_GraphNextOperation)* GraphNextOperation;
		decltype(TF_GraphOperationByName)* GraphOperationByName;
		decltype(TF_GraphSetTensorShape)* GraphSetTensorShape;
		decltype(TF_GraphToFunction)* GraphToFunction;
		decltype(TF_GraphToGraphDef)* GraphToGraphDef;
		decltype(TF_ImportGraphDefOptionsAddControlDependency)* ImportGraphDefOptionsAddControlDependency;
		decltype(TF_ImportGraphDefOptionsAddInputMapping)* ImportGraphDefOptionsAddInputMapping;
		decltype(TF_ImportGraphDefOptionsAddReturnOutput)* ImportGraphDefOptionsAddReturnOutput;
		decltype(TF_ImportGraphDefOptionsNumReturnOutputs)* ImportGraphDefOptionsNumReturnOutputs;
		decltype(TF_ImportGraphDefOptionsRemapControlDependency)* ImportGraphDefOptionsRemapControlDependency;
		decltype(TF_ImportGraphDefOptionsSetPrefix)* ImportGraphDefOptionsSetPrefix;
		decltype(TF_LoadLibrary)* LoadLibrary;
		decltype(TF_LoadSessionFromSavedModel)* LoadSessionFromSavedModel;
		decltype(TF_Message)* Message;
		decltype(TF_NewBuffer)* NewBuffer;
		decltype(TF_NewBufferFromString)* NewBufferFromString;
		decltype(TF_NewDeprecatedSession)* NewDeprecatedSession;
		decltype(TF_NewGraph)* NewGraph;
		decltype(TF_NewImportGraphDefOptions)* NewImportGraphDefOptions;
		decltype(TF_NewOperation)* NewOperation;
		decltype(TF_NewSession)* NewSession;
		decltype(TF_NewSessionOptions)* NewSessionOptions;
		decltype(TF_NewStatus)* NewStatus;
		decltype(TF_NewTensor)* NewTensor;
		decltype(TF_NewWhile)* NewWhile;
		decltype(TF_NumDims)* NumDims;
		decltype(TF_OperationDevice)* OperationDevice;
		decltype(TF_OperationGetAttrBool)* OperationGetAttrBool;
		decltype(TF_OperationGetAttrBoolList)* OperationGetAttrBoolList;
		decltype(TF_OperationGetAttrFloat)* OperationGetAttrFloat;
		decltype(TF_OperationGetAttrFloatList)* OperationGetAttrFloatList;
		decltype(TF_OperationGetAttrInt)* OperationGetAttrInt;
		decltype(TF_OperationGetAttrIntList)* OperationGetAttrIntList;
		decltype(TF_OperationGetAttrMetadata)* OperationGetAttrMetadata;
		decltype(TF_OperationGetAttrShape)* OperationGetAttrShape;
		decltype(TF_OperationGetAttrShapeList)* OperationGetAttrShapeList;
		decltype(TF_OperationGetAttrString)* OperationGetAttrString;
		decltype(TF_OperationGetAttrStringList)* OperationGetAttrStringList;
		decltype(TF_OperationGetAttrTensor)* OperationGetAttrTensor;
		decltype(TF_OperationGetAttrTensorList)* OperationGetAttrTensorList;
		decltype(TF_OperationGetAttrTensorShapeProto)* OperationGetAttrTensorShapeProto;
		decltype(TF_OperationGetAttrTensorShapeProtoList)* OperationGetAttrTensorShapeProtoList;
		decltype(TF_OperationGetAttrType)* OperationGetAttrType;
		decltype(TF_OperationGetAttrTypeList)* OperationGetAttrTypeList;
		decltype(TF_OperationGetAttrValueProto)* OperationGetAttrValueProto;
		decltype(TF_OperationGetControlInputs)* OperationGetControlInputs;
		decltype(TF_OperationGetControlOutputs)* OperationGetControlOutputs;
		decltype(TF_OperationInput)* OperationInput;
		decltype(TF_OperationInputListLength)* OperationInputListLength;
		decltype(TF_OperationInputType)* OperationInputType;
		decltype(TF_OperationName)* OperationName;
		decltype(TF_OperationNumControlInputs)* OperationNumControlInputs;
		decltype(TF_OperationNumControlOutputs)* OperationNumControlOutputs;
		decltype(TF_OperationNumInputs)* OperationNumInputs;
		decltype(TF_OperationNumOutputs)* OperationNumOutputs;
		decltype(TF_OperationOpType)* OperationOpType;
		decltype(TF_OperationOutputConsumers)* OperationOutputConsumers;
		decltype(TF_OperationOutputListLength)* OperationOutputListLength;
		decltype(TF_OperationOutputNumConsumers)* OperationOutputNumConsumers;
		decltype(TF_OperationOutputType)* OperationOutputType;
		decltype(TF_OperationToNodeDef)* OperationToNodeDef;
		decltype(TF_PRun)* PRun;
		decltype(TF_PRunSetup)* PRunSetup;
		decltype(TF_Reset)* Reset;
		decltype(TF_Run)* Run;
		decltype(TF_SessionListDevices)* SessionListDevices;
		decltype(TF_SessionPRun)* SessionPRun;
		decltype(TF_SessionPRunSetup)* SessionPRunSetup;
		decltype(TF_SessionRun)* SessionRun;
		decltype(TF_SetAttrBool)* SetAttrBool;
		decltype(TF_SetAttrBoolList)* SetAttrBoolList;
		decltype(TF_SetAttrFloat)* SetAttrFloat;
		decltype(TF_SetAttrFloatList)* SetAttrFloatList;
		decltype(TF_SetAttrInt)* SetAttrInt;
		decltype(TF_SetAttrIntList)* SetAttrIntList;
		decltype(TF_SetAttrShape)* SetAttrShape;
		decltype(TF_SetAttrShapeList)* SetAttrShapeList;
		decltype(TF_SetAttrString)* SetAttrString;
		decltype(TF_SetAttrStringList)* SetAttrStringList;
		decltype(TF_SetAttrTensor)* SetAttrTensor;
		decltype(TF_SetAttrTensorList)* SetAttrTensorList;
		decltype(TF_SetAttrTensorShapeProto)* SetAttrTensorShapeProto;
		decltype(TF_SetAttrTensorShapeProtoList)* SetAttrTensorShapeProtoList;
		decltype(TF_SetAttrType)* SetAttrType;
		decltype(TF_SetAttrTypeList)* SetAttrTypeList;
		decltype(TF_SetAttrValueProto)* SetAttrValueProto;
		decltype(TF_SetConfig)* SetConfig;
		decltype(TF_SetDevice)* SetDevice;
		decltype(TF_SetStatus)* SetStatus;
		decltype(TF_SetTarget)* SetTarget;
		decltype(TF_StringDecode)* StringDecode;
		decltype(TF_StringEncode)* StringEncode;
		decltype(TF_StringEncodedSize)* StringEncodedSize;
		decltype(TF_TensorByteSize)* TensorByteSize;
		decltype(TF_TensorData)* TensorData;
		decltype(TF_TensorMaybeMove)* TensorMaybeMove;
		decltype(TF_TensorType)* TensorType;
		decltype(TF_Version)* Version;

		void Init(const char* dllPath);

		static TFLib& GetDefault()
		{
			static TFLib instance;
			return instance;
		}
	};

	static void Init(const char* dllPath)
	{
		TFL.Init(dllPath);
	}

	static void DeallocateBuffer(void* data, size_t) {
		std::free(data);
	}

	static TF_Buffer* ReadBufferFromFile(const char* file) {
		const auto f = std::fopen(file, "rb");
		if (f == nullptr) {
			std::cout << "Failed to open file: " << file << "\n";
			return nullptr;
		}

		std::fseek(f, 0, SEEK_END);
		const auto fsize = ftell(f);
		std::fseek(f, 0, SEEK_SET);

		if (fsize < 1) {
			std::fclose(f);
			return nullptr;
		}

		const auto data = std::malloc(fsize);
		std::fread(data, fsize, 1, f);
		std::fclose(f);

		TF_Buffer* buf = TFL.NewBuffer();
		buf->data = data;
		buf->length = fsize;
		buf->data_deallocator = DeallocateBuffer;

		return buf;
	}

	static TF_Graph* LoadGraph(const char* graphPath)
	{
		auto buff = ReadBufferFromFile(graphPath);
		if (!buff) {
			return nullptr;
		}

		auto opts = TFL.NewImportGraphDefOptions();

		auto status = TFL.NewStatus();
		auto graph = TFL.NewGraph();

		TFL.GraphImportGraphDef(graph, buff, opts, status);

		TFL.DeleteBuffer(buff);
		TFL.DeleteImportGraphDefOptions(opts);

		if (TFL.GetCode(status) != TF_OK) {
			std::cout << TFL.Message(status) << "\n";
			TFL.DeleteGraph(graph);
			TFL.DeleteStatus(status);
			return nullptr;
		}

		TFL.DeleteStatus(status);
		return graph;
	}
}