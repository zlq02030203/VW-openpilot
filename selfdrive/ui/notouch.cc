#include <sys/resource.h>

#include <QApplication>
#include <QtWidgets>
#include <QGraphicsScene>
#include <QtMultimedia>
#include <QtMultimediaWidgets>
#include <QVideoWidget>
#include <QGraphicsVideoItem>
#include <QDebug>

#include "system/hardware/hw.h"
#include "cereal/messaging/messaging.h"
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/notouch.h"
#include "selfdrive/ui/qt/qt_window.h"

const QString VIDEOS_PATH = "../assets/videos/out";
const QString GST_VIDEO_CMD = QString("gst-launch-1.0 -v multifilesrc location=\"%1\" ! decodebin ! videorate ! queue2 ! video/x-raw,framerate=20/1 ! queue2 ! videoconvert ! queue2 ! videoflip method=clockwise ! queue2 ! autovideosink");


MainWindowNoTouch::MainWindowNoTouch(QWidget *parent) : QMainWindow(parent) {
  setpriority(PRIO_PROCESS, 0, -5);
  Hardware::set_brightness(80);

  // WORKS:
  QMediaPlayer *player = new QMediaPlayer;
  QMediaPlaylist *playlist = new QMediaPlaylist(player);
  playlist->addMedia(QUrl::fromLocalFile("/home/batman/Downloads/adeeb-dm-2.mp4"));
  playlist->setPlaybackMode(QMediaPlaylist::Loop);

  QVideoWidget *videoWidget = new QVideoWidget(this);
  player->setVideoOutput(videoWidget);
  player->setPlaylist(playlist);

  videoWidget->show();
  setCentralWidget(videoWidget);
  player->play();

//  playlist->addMedia(QUrl("http://example.com/myclip2.mp4"));

//  main_layout = new QVBoxLayout(this);
//  main_layout->setMargin(0);
//
//  QStringList filters;
//  filters << "*.mp4" << "*.mkv";
//  QDir videos_path = QDir(VIDEOS_PATH);
//  videos_path.setNameFilters(filters);
//  QString content_name;
//  while ((content_name = MultiOptionDialog::getSelection(tr("Select content"), videos_path.entryList(), "", this)).isEmpty()) {
//    qDebug() << "No content selected!";
//  }
//
//  content_name = VIDEOS_PATH + "/" + content_name;
//  qDebug() << "Selected:" << content_name;
//
//  // play video
//  QTimer::singleShot(0, [=]() {
//    std::system(QString("while true; do %1; done").arg(GST_VIDEO_CMD.arg(content_name)).toStdString().c_str());
//  });
//
//  // no outline to prevent the focus rectangle
//  setStyleSheet(R"(
//    * {
//      font-family: Inter;
//      outline: none;
//    }
//  )");
//  setAttribute(Qt::WA_NoSystemBackground);
}

//MainWindowNoTouch::MainWindowNoTouch(QWidget *parent) : QMainWindow(parent) {
//  QMediaPlayer *player = new QMediaPlayer(this);
//  QVideoWidget *videoWidget = new QVideoWidget(this);
//  QMediaPlaylist *playlist = new QMediaPlaylist(player);
//
//  playlist->addMedia(QUrl::fromLocalFile("./video.mp4"));
//  playlist->setPlaybackMode(QMediaPlaylist::Loop);
//
//  player->setVideoOutput(videoWidget);
//  player->setPlaylist(playlist);
//
//  setCentralWidget(videoWidget);
//  player->play();
//}


int main(int argc, char *argv[]) {
  initApp(argc, argv);
  QApplication a(argc, argv);
  MainWindowNoTouch w;
  setMainWindow(&w);

  return a.exec();
}
