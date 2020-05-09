#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <iostream>
#include <tensorflow/c_api.h>
#include <Windows.h>
#include <chrono>
#include <array>
#include <sstream>
#include <time.h>
#include "tf.h"
#include "Builder.h"
#include "BlockModel.h"
#include "PositionModel.h"
#include "Config.h"
#include "Utils.h"
#include "MPServer.h"

static void progressCallback(int completed, int total) {
	std::cout << completed << std::endl;
}

int main(int argc, char *argv[])
{
	srand(time(NULL));
	if (!std::ifstream(TF_PATH).good()) {
		std::cerr << "Fatal: could not find tensorflow.dll" << std::endl;
		return 1;
	}

	tf::Init(TF_PATH);

	bool failSafe = true;
	int length = 100;
	double temperature = 1.2;
	int mood = 0;
	std::string outputPath;
	std::string mapName = "TMTrackNN Output";

	for (int i = 1; i < argc; i++) {
		std::string opt = argv[i];
		if (opt == "--help" || opt == "-h") {
			std::cout << "Available options:" << std::endl
				<< "-o [--output] REQUIRED the output path to the saved .Challenge.Gbx file" << std::endl
				<< "-l [--length] the length of the track (in blocks)" << std::endl
				<< "-t [--temperature] the variety used (1.2 is the default)" << std::endl
				<< "-d [--disable-failsafe] do not perform any integrity checks when building the track" << std::endl
				<< "-n [--name] the name of the map (TMTrackNN Output is the default)" << std::endl
				<< "-m [--mood] the mood of the map (0 = day; 1 = sunrise; 2 = sunset; 3 = night), default is 0" << std::endl;
			return true;
		}

#define HAS_NEXT_ARG i + 1 < argc
		if ((opt == "--length" || opt == "-l") && HAS_NEXT_ARG) {
			length = std::atoi(argv[i + 1]);
			i++;
		}
		else if ((opt == "--temperature" || opt == "-t") && HAS_NEXT_ARG) {
			temperature = std::atof(argv[i + 1]);
			i++;
		}
		else if ((opt == "--output" || opt == "-o") && HAS_NEXT_ARG) {
			outputPath = argv[i + 1];
			i++;
		}
		else if (opt == "--disable-failsafe" || opt == "-d") {
			failSafe = false;
		}
		else if ((opt == "--name" || opt == "-n") && HAS_NEXT_ARG) {
			mapName = argv[i + 1];
			i++;
		}
		else if ((opt == "--mood" || opt == "-m") && HAS_NEXT_ARG) {
			mood = std::atoi(argv[i + 1]);
			i++;
		}
	}

	using namespace std::placeholders;
	auto bmodel = std::make_unique<BlockModel>(BLOCK_MODEL_PATH);
	auto pmodel = std::make_unique<PositionModel>(POSITION_MODEL_PATH);

	auto builder = std::make_unique<Builder>(std::move(bmodel), std::move(pmodel));

	if (argc < 2) {
		MPServer server(std::move(builder));
		server.run();
		return 0;
	}

	if (outputPath.empty()) {
		std::cerr << "You must provide the output path: --output path/to/file.Challenge.Gbx" << std::endl;
		return false;
	}


	builder->setTemperature(temperature);

	auto track = builder->build(length, failSafe, std::bind(progressCallback, _1, _2));
	utils::saveTrack(track, outputPath, mapName, mood);

	return 0;
}
