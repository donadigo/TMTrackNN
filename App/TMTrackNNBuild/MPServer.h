#pragma once
#include <memory>
#include "Builder.h"
#include <httplib.h>

class MPServer
{
public:
	MPServer(std::unique_ptr<Builder> builder);
	~MPServer();
	void run();
	int readInt32(int& bytesRecv);
private:
	void waitForClient();
	void readBuild();
	void writeString(const std::string& str);
	std::string readString(int & bytesRecv);
	std::unique_ptr<Builder> builder;
	httplib::Server server;
};

