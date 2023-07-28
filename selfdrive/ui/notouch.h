#pragma once

#include <QVBoxLayout>
#include <QWidget>
#include <QProcess>
#include <QMouseEvent>

#include "selfdrive/ui/qt/onroad.h"
#include "selfdrive/ui/qt/offroad/settings.h"
#include "tools/replay/replay.h"

class MainWindowNoTouch : public QWidget {
  Q_OBJECT

public:
  explicit MainWindowNoTouch(QWidget *parent = 0);

private:
  void mousePressEvent(QMouseEvent *event) override;
  QVBoxLayout *main_layout;
  QProcess *process;

  OnroadWindow *onroad;
  std::unique_ptr<Replay> replay;
};
