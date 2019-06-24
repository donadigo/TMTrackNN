#include <QtWidgets/QApplication>
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
#include "MainWindow.h"

using namespace std;

int main(int argc, char *argv[])
{
	srand(time(NULL));
	if (!std::ifstream(TF_PATH).good()) {
		MessageBoxW(NULL, L"Could not find tensorflow.dll.", L"Error", MB_ICONERROR);
		return 1;
	}

	tf::Init(TF_PATH);
#ifdef DEBUG
	AllocConsole();
	freopen("CONOUT$", "w", stdout);
#endif
	QApplication app(argc, argv);
	MainWindow window;

	window.show();
	return app.exec();
}
