#include "MainWindow.h"

#include <QFileDialog>
#include <QStandardPaths>
#include <iostream>
#include "tf.h"

MainWindow::MainWindow(QWidget *parent)
	: QWidget(parent)
{
	ui.setupUi(this);

	QIcon icon;
	icon.addFile(QString::fromUtf8(ICON_PATH), QSize(), QIcon::Normal, QIcon::Off);

	setWindowIcon(icon);

	nameEdit = new QLineEdit;

	tempSlider = new QSlider(Qt::Horizontal);
	tempSlider->setMinimum(6);
	tempSlider->setMaximum(20);
	tempSlider->setValue(12);
	tempSlider->setToolTip("Higher: more creative, less certain\nLower: more conservative, more certain");;

	moodCombo = new QComboBox();
	moodCombo->addItem("Day");
	moodCombo->addItem("Sunrise");
	moodCombo->addItem("Sunset");
	moodCombo->addItem("Night");

	rdTime = new QRadioButton("Track length");
	rdTime->setChecked(true);
	connect(rdTime, SIGNAL(toggled(bool)), this, SLOT(timeTypeChanged()));

	rdCustom = new QRadioButton("Custom");
	connect(rdCustom, SIGNAL(toggled(bool)), this, SLOT(timeTypeChanged()));

	rd15 = new QRadioButton("15 seconds");
	rd30 = new QRadioButton("30 seconds");
	rd1 = new QRadioButton("1 minute");
	rd1->setChecked(true);

	timeLayout = new QHBoxLayout();
	timeLayout->addWidget(rd15);
	timeLayout->addWidget(rd30);
	timeLayout->addWidget(rd1);
	timeLayout->setContentsMargins(35, 0, 35, 0);

	QFormLayout* form = new QFormLayout;
	form->setVerticalSpacing(12);
	form->setHorizontalSpacing(12);
	form->addRow("Map name:", nameEdit);
	form->addRow("Mood:", moodCombo);
	form->addRow("Variety:", tempSlider);

	QVBoxLayout* mainLayout = new QVBoxLayout;
	mainLayout->addLayout(form);

	timeWidget = new QWidget();
	timeWidget->setLayout(timeLayout);

	lengthSpinBox = new QSpinBox();
	lengthSpinBox->setMaximum(1000);
	lengthSpinBox->setValue(50);

	customLayout = new QFormLayout();
	customLayout->setVerticalSpacing(12);
	customLayout->setHorizontalSpacing(12);
	customLayout->addRow("Number of blocks:", lengthSpinBox);
	customLayout->setContentsMargins(35, 0, 0, 0);

	boxLayout = new QVBoxLayout();
	boxLayout->addWidget(rdTime);
	boxLayout->addWidget(timeWidget);
	boxLayout->addWidget(rdCustom);
	boxLayout->addLayout(customLayout);
	boxLayout->setAlignment(Qt::AlignHCenter);

	generateBtn = new QPushButton("Generate");
	connect(generateBtn, SIGNAL(clicked()), this, SLOT(generateButtonClicked()));

	stopBtn = new QPushButton("Stop");
	stopBtn->setEnabled(false);
	connect(stopBtn, SIGNAL(clicked()), this, SLOT(stopButtonClicked()));

	progressBar = new ProgressBar();
	progressBar->setRange(0, 100);

	buttonLayout = new QHBoxLayout();
	buttonLayout->addWidget(progressBar);
	buttonLayout->addWidget(stopBtn);
	buttonLayout->addWidget(generateBtn);
	buttonLayout->setAlignment(Qt::AlignRight | Qt::AlignBottom);

	mainLayout->addLayout(form);
	mainLayout->addLayout(boxLayout);
	mainLayout->addLayout(buttonLayout);

	this->setLayout(mainLayout);
	timeTypeChanged();

	connect(&thread, SIGNAL(onProgress(int)), this, SLOT(onProgress(int)));
	connect(&thread, SIGNAL(onStatusChanged(QString, bool)), this, SLOT(onStatusChanged(QString, bool)));
	connect(&thread, SIGNAL(finished()), this, SLOT(onThreadFinished()));
}

MainWindow::~MainWindow()
{
}

void MainWindow::stopButtonClicked()
{
	thread.stop();
}

QString MainWindow::getTMMapsDir()
{
	auto p = QStandardPaths::locate(QStandardPaths::StandardLocation::DocumentsLocation, "Maniaplanet/Maps", QStandardPaths::LocateOption::LocateDirectory);
	if (!p.isEmpty()) {
		return p;
	}

	p = QStandardPaths::locate(QStandardPaths::StandardLocation::DocumentsLocation, "TrackMania/Tracks/Challenges", QStandardPaths::LocateOption::LocateDirectory);
	return p;
}

void MainWindow::generate(const QFileInfo* fileInfo)
{
	int length = 0;
	if (rdTime->isChecked()) {
		if (rd15->isChecked()) {
			length = 27;
		} else if (rd30->isChecked()) {
			length = 50;
		} else if (rd1->isChecked()) {
			length = 110;
		}
	} else if (rdCustom->isChecked()) {
		length = lengthSpinBox->value();
	}

	auto mapName = nameEdit->text();
	if (mapName.trimmed().isEmpty()) {
		mapName = fileInfo->baseName().replace(".Challenge.Gbx", "").replace(".Map.Gbx", "");
	}

	thread.fileName = fileInfo->absoluteFilePath();
	thread.mapName = mapName;
	thread.length = length;
	thread.variety = (float)tempSlider->value() / 10.0f;
	thread.mood = moodCombo->currentIndex();
	
	setWindowTitle("TMTrackNN | Generating...");
	thread.start();
}

void MainWindow::generateButtonClicked()
{
	auto fileName = QFileDialog::getSaveFileName(this, "Choose save location", getTMMapsDir());
	if (fileName.isEmpty()) {
		return;
	}

	if (!fileName.endsWith(".Challenge.Gbx") && !fileName.endsWith(".Map.Gbx")) {
		fileName += ".Challenge.Gbx";
	}

	QFileInfo fileInfo(fileName);

	stopBtn->setEnabled(true);
	generateBtn->setEnabled(false);
	timeWidget->setEnabled(false);
	rdTime->setEnabled(false);
	rdCustom->setEnabled(false);
	nameEdit->setEnabled(false);
	tempSlider->setEnabled(false);
	lengthSpinBox->setEnabled(false);
	generate(&fileInfo);
}

void MainWindow::timeTypeChanged()
{
	auto toggled = rdTime->isChecked();
	rd15->setEnabled(toggled);
	rd30->setEnabled(toggled);
	rd1->setEnabled(toggled);
	rdCustom->setChecked(!toggled);
	rdTime->setChecked(toggled);
	lengthSpinBox->setEnabled(!toggled);
}

void MainWindow::onThreadFinished()
{
	generateBtn->setEnabled(true);
	progressBar->setValue(0);
	progressBar->setRange(0, 100);
	stopBtn->setEnabled(false);
	timeWidget->setEnabled(true);
	rdTime->setEnabled(true);
	rdCustom->setEnabled(true);
	nameEdit->setEnabled(true);
	tempSlider->setEnabled(true);
	lengthSpinBox->setEnabled(true);
	setWindowTitle("TMTrackNN");
	timeTypeChanged();
}

void MainWindow::onStatusChanged(QString status, bool initPhase)
{
	if (initPhase) {
		progressBar->setRange(0, 0);
	} else {
		progressBar->setRange(0, 100);
	}

	progressBar->setText(status);
}

void MainWindow::onProgress(int progress)
{
	progressBar->setValue(progress);
}

