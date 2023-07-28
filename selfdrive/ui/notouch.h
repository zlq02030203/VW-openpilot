#pragma once

#include <QVBoxLayout>
#include <QWidget>
#include <QMainWindow>

#include "selfdrive/ui/qt/onroad.h"
#include "selfdrive/ui/qt/offroad/settings.h"
#include "tools/replay/replay.h"

//class MainWindowNoTouch : public QMainWindow {
//  Q_OBJECT
//
//public:
//  explicit MainWindowNoTouch();
//
//private:
//  QVBoxLayout *main_layout;
//
//  OnroadWindow *onroad;
//  std::unique_ptr<Replay> replay;
//};

class MainWindowNoTouch : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindowNoTouch(QWidget *parent = nullptr);
private:
  QVBoxLayout *main_layout;

  OnroadWindow *onroad;
  std::unique_ptr<Replay> replay;
};
