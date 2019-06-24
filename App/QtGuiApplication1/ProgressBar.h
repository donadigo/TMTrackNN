#pragma once
#include <QtWidgets/QProgressBar>

class ProgressBar : public QProgressBar
{
	Q_OBJECT
public:
	ProgressBar(QWidget* parent = Q_NULLPTR) :
		QProgressBar(parent)
	{
		setAlignment(Qt::AlignCenter);
	}

	void setText(const QString text)
	{
		_text = text;
	}

	QString text() const
	{
		return _text;
	}
private:
	QString _text;
};