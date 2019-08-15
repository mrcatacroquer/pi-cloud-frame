import glob
import logging
import sys
from abc import abstractmethod, ABC

from PyQt5 import QtWidgets, QtGui, QtCore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# delay between slide transitions (ms)
SLIDESHOW_DELAY = 30000


class AbstractMediaPlayer(ABC):
    """
    Abstract base class for all media players
    """

    def __init__(self, name, folder):
        """
        Create a default abstract media player.
        All sub-classes should call this parent constructor.

        :param name: string used to refer to the media player
        :param folder: folder containing the media (images, video...)
        """
        self._name = name
        self._media_folder = folder
        self._media_list = None
        self._current_media_index = None

        self.refresh_media_list()

    @abstractmethod
    def get_main_widget(self):
        """
        Get the top-level widget of the media player

        :return: the top-level widget
        """
        pass

    def refresh_media_list(self):
        """
        Re-load the media list from the filesystem

        :return: a list of filenames
        """
        logger.debug("Refreshing media list for %s in folder %s", self.get_name(), self.get_folder())
        self._media_list = glob.glob(self.get_folder() + "/*")
        self._current_media_index = 0
        logger.debug("Loaded photo list: %s", self._media_list)

    def get_name(self):
        """
        Get the name of the media player

        :return: textual name of the media player
        """
        return self._name

    def get_folder(self):
        """"
        Get the location of the folder containing the media

        :return: the folder name
        """
        return self._media_folder

    def get_playlist(self):
        """
        Get a list of media to be played by this media player

        :return: list of filenames
        """
        return self._media_list

    @abstractmethod
    def show_current_media(self):
        """
        Display the current media
        """
        pass

    def next(self):
        """
        Display the next media. If at the end of the playlist, jump to the start
        """
        logger.debug("_current_media_index = %d", self._current_media_index)
        logger.debug("length _media_list = %d", len(self._media_list))
        if self._current_media_index >= len(self._media_list) - 1:
            logger.debug("Starting at beginning of media")
            self._current_media_index = 0
        else:
            self._current_media_index += 1
            logger.debug("Setting _current_media_index to %d", self._current_media_index)
        self.show_current_media()

    def prev(self):
        """
        Display the previous media. If at the start of the playlist, jump to the end
        """
        if self._current_media_index <= 0:
            logger.debug("Starting at end of media")
            self._current_media_index = len(self._media_list) - 1
        else:
            self._current_media_index -= 1
        self.show_current_media()

    def _set_main_widget(self, widget):
        self._main_window = widget


class VideoPlayer(AbstractMediaPlayer):
    def __init__(self, name, folder):
        super().__init__(name, folder)

    def get_main_widget(self):
        # TODO implement video player
        pass

    def show_current_media(self):
        # TODO implement video player
        pass


class PhotoPlayer(AbstractMediaPlayer):

    def __init__(self, name, folder):
        super().__init__(name, folder)
        self.main_window = QtWidgets.QLabel()
        self.main_window.setAlignment(QtCore.Qt.AlignCenter)

    def get_main_widget(self):
        return self.main_window

    def show_current_media(self):
        if not self._media_list:
            self.main_window.setText("Media Player %s: No media to show" % self.get_name())
            return

        image_filename = self._media_list[self._current_media_index]
        logger.debug("Showing image %s", image_filename)
        image = QtGui.QImage(image_filename)
        if image:
            pmap = QtGui.QPixmap.fromImage(image)
            self.main_window.setPixmap(pmap.scaled(
                self.get_main_widget().size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation))
        else:
            logger.info("Could not load image: %s", image_filename)


class PhotoFrame(QtWidgets.QMainWindow):
    def __init__(self, delay):
        super(PhotoFrame, self).__init__()

        # setup media players
        self.players = self.init_players()
        self.current_player_index = 0

        self._build_UI()
        self.showFullScreen()

        # start timer
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self._timer_callback)
        timer.start(delay)

        # go...
        self.get_current_player().show_current_media()

    @staticmethod
    def init_players():
        """
        Factory method to create the set of media players

        :return: a list of AbstractMediaPlayer instances
        """
        players = [PhotoPlayer("Photo Player", "photos"), PhotoPlayer("Photo Player 2", "photos2"), VideoPlayer("Video Player", "video")]
        logger.info("Initialising players: %s", players)
        return players

    def next_player(self):
        """
        Switch to the next media player. If at the end of the player list, jump to the start
        """
        logger.debug("current_player_index = %d", self.current_player_index)
        logger.debug("length player_list = %d", len(self.players))
        if self.current_player_index >= len(self.players) - 1:
            logger.debug("Starting at beginning of media")
            new_index = 0
        else:
            new_index = self.current_player_index + 1

        self._set_player_by_index(new_index)

    def prev_player(self):
        """
        Switch to the previous media player. If at the end of the player list, jump to the start
        """
        logger.debug("current_player_index = %d", self.current_player_index)
        logger.debug("length player_list = %d", len(self.players))
        if self.current_player_index <= 0:
            logger.debug("Starting at end of players")
            new_index = len(self.players) - 1
        else:
            new_index = self.current_player_index - 1

        self._set_player_by_index(new_index)

    def get_current_player(self):
        """
        Get a reference to the current media player

        :return: the current media player
        """
        return self.players[self.current_player_index]

    def refresh_all_playlists(self):
        """
        Re-load media playlists for all players
        """
        for p in self.players:
            p.refresh_media_list()

    def _timer_callback(self):
        self.get_current_player().next()

    def _build_UI(self):
        # setup UI - use a QStackedWidget to avoid widgets being destroyed
        self.stack = QtWidgets.QStackedWidget()
        for p in self.players:
            player_widget = p.get_main_widget()
            if player_widget:
                self.stack.addWidget(player_widget)
            else:
                not_implemented = QtWidgets.QLabel("Media Player %s: Not yet implemented" % p.get_name())
                not_implemented.setAlignment(QtCore.Qt.AlignCenter)
                self.stack.addWidget(not_implemented)
        self.setCentralWidget(self.stack)

    def _set_player_by_index(self, index):
        new_player = self.players[index]
        logger.debug("Changing to player index %d (%s)", index, new_player.get_name())
        self.stack.setCurrentIndex(index)
        self.current_player_index = index
        new_player.show_current_media()

    def mousePressEvent(self, mouse):
        """
        Handle mouse clicks

        :param mouse: the mouse event
        """
        width, height = self.size().width(), self.size().height()
        x, y = mouse.pos().x(), mouse.pos().y()

        if x >= width * 0.8:
            self.get_current_player().next()
        if x <= width * 0.2:
            self.get_current_player().prev()
        if y >= height * 0.8:
            self.next_player()
        if y <= height * 0.2:
            self.prev_player()

    def keyPressEvent(self, key):
        """
        Handle key-presses

        :param key: the pressed key
        """
        key_press = key.key()
        if key_press == QtCore.Qt.Key_Escape:
            self.close()
        if key_press == QtCore.Qt.Key_Left:
            self.get_current_player().prev()
        if key_press == QtCore.Qt.Key_Right:
            self.get_current_player().next()
        if key_press == QtCore.Qt.Key_Up:
            self.prev_player()
        if key_press == 32:
            self.refresh_all_playlists()
        if key_press == QtCore.Qt.Key_Down:
            self.next_player()


def exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


def main():
    sys._excepthook = sys.excepthook
    sys.excepthook = exception_hook

    app = QtWidgets.QApplication(sys.argv)

    window = PhotoFrame(SLIDESHOW_DELAY)
    window.raise_()

    app.exec_()


if __name__ == '__main__':
    main()