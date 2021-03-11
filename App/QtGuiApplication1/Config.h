#pragma once
#define LOOKBACK 20
#define NUM_BLOCKS 363
#define INPUT_LEN NUM_BLOCKS + 7

const float SCALE_VECTOR[3] = { 0.03703704, 0.03030303, 0.04347826 };
const float MIN_VECTOR[3] = { 0.48148148, 0.57575758, 0.43478261 };

#ifdef _DEBUG
#define BLOCK_MODEL_PATH "F:/Python/tmtools/models/tech/tmp/block_model.pb"
#define POSITION_MODEL_PATH "F:/Python/tmtools/models/tech/tmp/position_model.pb"
#define PATTERN_DATA_PATH "F:/Python/tmtools/pattern_data.json"
#define TF_PATH "C:/tensorflow/tensorflow.dll"
#define SAVEGBX_PATH "F:/Python/SaveGBX/dist/savegbx/savegbx.exe"
#define TEMPLATE_PATH "F:/Python/tmtools/data/Template.Map.Gbx"
#define ICON_PATH "F:/Python/TMTrackNN2/icon/icon.ico"

#else
#define BLOCK_MODEL_PATH "data/block_model.pb"
#define POSITION_MODEL_PATH "data/position_model.pb"
#define PATTERN_DATA_PATH "data/pattern_data.json"
#define TF_PATH "tensorflow.dll"
#define SAVEGBX_PATH "savegbx/savegbx.exe"
#define TEMPLATE_PATH "data/Template.Map.Gbx"
#define ICON_PATH "data/icon.ico"
#endif