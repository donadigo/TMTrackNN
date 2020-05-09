#pragma once
#include "MPServer.h"
#include "Builder.h"
#include "Utils.h"

#define START "start"

#define TMTRACKNN_PORT 60050
#define MESSAGE_TYPE_BUFSIZE 4
#define BUFSIZE 32

enum MessageType {
	BUILD = 0,
	CANCEL_BUILD = 1
};

MPServer::MPServer(std::unique_ptr<Builder> builder):
	builder(std::move(builder))
{
	server.Get("/builder/start", [&](const httplib::Request& req, httplib::Response& res) {
		auto lenStr = req.get_param_value("length");
		if (!lenStr.empty()) {
			std::cout << "Start builder.\n";
			int fixedY = this->builder->startRest(std::atoi(lenStr.c_str()));
			res.set_content("FixedY=" + std::to_string(fixedY), "text/plain");

			//while (this->builder->step().type != FINISHED);

			//std::string outputPath = "F:\\ManiaplanetData\\Maps\\TMTrackNN\\Step.Challenge.Gbx";
			//std::string mapName = "Step";
			//auto map = this->builder->getMap();
			//map.update();
			//auto track = map.filterBlocks(map.center(), { GRASS_BLOCK });
			//utils::saveTrack(track, outputPath, mapName, 1);
		}
	});

	server.Get("/builder/next", [&](const httplib::Request& req, httplib::Response& res) {
		BuilderRestMessage msg = this->builder->step();
		res.set_content(msg.toString(), "text/plain");
	});

	server.Post("/builder/place_block_failed", [&](const httplib::Request& req, httplib::Response& res) {
		this->builder->blacklistPrevRest();
	});

	server.Get("/builder/status", [&](const httplib::Request& req, httplib::Response& res) {
		res.set_content("Status=Running", "text/plain");
	});
}


MPServer::~MPServer()
{
}

void MPServer::waitForClient()
{
	//clientSocket = SOCKET_ERROR;
	//while (clientSocket == SOCKET_ERROR) {
	//	clientSocket = accept(mainSocket, NULL, NULL);
	//}
}

void MPServer::readBuild()
{
	//std::cout << "Read build\n";
	char buf[4] = { 0, 0, 0, 0 };
	//writeString("StadiumRoadMain\n");
	//while (true) {
		//send(clientSocket, buf, 4, 0);
	//}
	//writeString("StadiumRoadMain");
}

std::string MPServer::readString(int& bytesRecv)
{
	//char buf[64];
	//bytesRecv = recv(clientSocket, buf, 64, 0);
	//if (bytesRecv <= 0) {
	//	return "";
	//}

	// TODO
	return "";
}


int MPServer::readInt32(int& bytesRecv)
{
	/*char buf[4];
	bytesRecv = recv(clientSocket, buf, 4, 0);
	if (bytesRecv != 4) {
		return -1;
	}

	return (int)*buf;*/
	return 0;
}

void MPServer::writeString(const std::string& str)
{
	//int size = str.size();
	//char* buf = static_cast<char*>(static_cast<void*>(&size));
	////send(clientSocket, buf, 4, 0);
	////for (auto c : str) {
	////	char b[1] = { c };
	////	send(clientSocket, b, 1, 0);
	////}
	//send(clientSocket, str.data(), size, 0);
}

void MPServer::run()
{
	std::cout << "Server run\n";
	server.listen ("127.0.0.1", TMTRACKNN_PORT);
	/*WSADATA wsaData;
	int res = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (res != NO_ERROR) {
		std::cerr << "Failed to startup!\n";
		return;
	}

	mainSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (mainSocket == INVALID_SOCKET) {
		std::cerr << "Error creating socket: " << WSAGetLastError() << "\n";
		WSACleanup();
		return;
	}

	IN_ADDR addr;
	inet_pton(AF_INET, "127.0.0.1", &addr);

	sockaddr_in service;
	memset(&service, 0, sizeof(service));
	service.sin_family = AF_INET;
	service.sin_addr = addr;
	service.sin_port = htons(TMTRACKNN_PORT);

	if (bind(mainSocket, (SOCKADDR*)&service, sizeof(service)) == SOCKET_ERROR) {
		std::cout << "Binding to socket failed.\n";
		closesocket(mainSocket);
		WSACleanup();
		return;
	}

	if (listen(mainSocket, 1) == SOCKET_ERROR) {
		std::cout << "Error listening on socket.\n";
		WSACleanup();
		return;
	}

	std::cout << "Server ready!\n";
	waitForClient();

	while (true) {
		int bytesRecv;
		int message = readInt32(bytesRecv);
		if (bytesRecv == 0 || bytesRecv == WSAECONNRESET) {
			waitForClient();
			continue;
		}
	
		if (bytesRecv < 0) {
			waitForClient();
			continue;
		}

		switch (message) {
		case BUILD:
			readBuild();
			break;
		case CANCEL_BUILD:
			builder->stop();
			break;
		}*/

		//for (int i = 0; i < bytesRecv; i++) {
		//	std::cout << buf[i];
		//}

		//send(clientSocket, buf, bytesRecv, 0);

		//std::cout << "\n";
	//}
}

