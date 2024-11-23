import sys
import vlc
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QSlider
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VLC Video Player")
        self.setGeometry(100, 100, 800, 600)
        self.instance = vlc.Instance('--no-xlib')
        self.player = self.instance.media_player_new()
        self.video_widget = QWidget(self)
        self.player.set_hwnd(self.video_widget.winId())

        self.file_label = QLabel("Выберите файл для воспроизведения")
        self.play_button = QPushButton("Воспроизвести")
        self.pause_button = QPushButton("Пауза")
        self.stop_button = QPushButton("Остановить")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider = QSlider(Qt.Orientation.Horizontal)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(self.file_label)
        layout.addWidget(self.video_widget)
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)

        layout.addWidget(QLabel("Громкость"))
        layout.addWidget(self.volume_slider)

        layout.addWidget(QLabel("Время"))
        layout.addWidget(self.time_slider)

        self.setLayout(layout)

        self.volume_slider.setValue(50)
        self.time_slider.setRange(0, 100)

        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.stop_button.clicked.connect(self.stop_video)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.time_slider.sliderMoved.connect(self.set_position)

        self.set_shortcuts()

        self.open_file()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_slider)
        self.timer.start(100)
        self.updating_slider = False

    def set_shortcuts(self):
        play_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        play_shortcut.activated.connect(self.play_video)

        pause_shortcut = QShortcut(QKeySequence(Qt.Key.Key_P), self)
        pause_shortcut.activated.connect(self.pause_video)

        stop_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        stop_shortcut.activated.connect(self.stop_video)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите видео", "", "Видео файлы (*.mp4 *.avi *.mkv);;Все файлы (*)")
        if file_path:
            self.file_label.setText(f"Файл: {file_path}")
            media = self.instance.media_new(file_path)
            self.player.set_media(media)

    def play_video(self):
        self.player.play()

    def pause_video(self):
        self.player.pause()

    def stop_video(self):
        self.player.stop()

    def set_volume(self):
        volume = self.volume_slider.value()
        self.player.audio_set_volume(volume)

    def set_position(self):
        if not self.updating_slider:
            position = self.time_slider.value()
            self.player.set_time(position * 1000)

    def update_time_slider(self):
        if not self.updating_slider:
            current_time = self.player.get_time() // 1000  
            duration = self.player.get_length() // 1000  

            if duration > 0:
                self.time_slider.setValue(int((current_time / duration) * 100))

            if current_time == duration:
                self.timer.stop()

    def slider_drag_start(self):
        self.updating_slider = True

    def slider_drag_end(self):
        self.updating_slider = False
        self.set_position()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
