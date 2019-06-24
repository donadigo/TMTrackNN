#pragma once
#include <QThread>
#include <QtWidgets/QWidget>
#include <iostream>
#include "Builder.h"
#include "BlockUtils.h"
#include "Windows.h"
#include "Utils.h"

class GenerateThread : public QThread
{
	Q_OBJECT
public:
	GenerateThread(QWidget* parent = Q_NULLPTR) :
		QThread(parent)
	{

	}

	QString mapName;
	QString fileName;
	int length;
	float variety;
	int mood;
	void stop()
	{
		if (builder) {
			builder->stop();
		}

		emit onStatusChanged("Stopped.", false);
	}
signals:
	void onProgress(int progress);
	void onStatusChanged(QString status, bool initPhase);

protected:
	void run()
	{
		if (!builder) {
			emit onStatusChanged("Initializing...", true);
			auto bmodel = std::make_unique<BlockModel>(BLOCK_MODEL_PATH);
			auto pmodel = std::make_unique<PositionModel>(POSITION_MODEL_PATH);

			builder = new Builder(std::move(bmodel), std::move(pmodel));
		}

		emit onStatusChanged("Building...", false);
		using namespace std::placeholders;
		builder->setTemperature(variety);
		auto track = builder->build(length, true, std::bind(&GenerateThread::onBuilderProgress, this, _1, _2));

		std::string s = block_utils::toPythonString(track);
		if (track.size() > 0) {
			utils::saveTrack(track, fileName.toStdString(), mapName.toStdString(), mood);
			emit onStatusChanged("Done.", false);
		}
	}
private:
	Builder* builder = nullptr;

	void onBuilderProgress(int completed, int total)
	{
		emit onProgress((float)completed / (float)total * 100);
	}
};