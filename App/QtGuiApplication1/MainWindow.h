#pragma once

#include <QWidget>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QFormLayout>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QSlider>
#include <QtWidgets/QRadioButton>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QSpinBox>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QMainWindow>
#include <QCoreApplication>
#include <QFileInfo>
#include <QThread>
#include "ui_MainWindow.h"
#include "ProgressBar.h"
#include "GenerateThread.h"
#include "tf.h"

class MainWindow : public QWidget
{
	Q_OBJECT

public:
	MainWindow(QWidget *parent = Q_NULLPTR);
	~MainWindow();

private:
	Ui::MainWindow ui;
	QLineEdit* nameEdit;
	QSlider* tempSlider;
	QComboBox* moodCombo;
	QRadioButton* rdTime;
	QRadioButton* rdCustom;
	QRadioButton* rd15;
	QRadioButton* rd30;
	QRadioButton* rd1;
	QHBoxLayout* timeLayout;
	QWidget* timeWidget;
	QSpinBox* lengthSpinBox;
	QFormLayout* customLayout;
	QVBoxLayout* boxLayout;
	QPushButton* generateBtn;
	QPushButton* stopBtn;
	QHBoxLayout* buttonLayout;
	ProgressBar* progressBar;

	static QString getTMMapsDir();
	void generate(const QFileInfo* fileInfo);
	Builder* builder = nullptr;
	GenerateThread thread;
public slots:
	void stopButtonClicked();
	void generateButtonClicked();
	void timeTypeChanged();
	void onThreadFinished();
	void onStatusChanged(QString status, bool initPhase);
	void onProgress(int progress);
};
