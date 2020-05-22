import struct
import time
import wave

import numpy as np
import pygame


class MusicUtils:
    music_file_path = None
    music_is_playing = False
    music_is_paused = False

    channels_number = None
    samp_width = None
    frame_rate = None
    frames_number = None
    comp_type = None
    comp_name = None

    channel_frames = []
    channels_original = []
    specter = None
    specter_original = None
    new_specter = []
    each_frequency_elements = []
    maximum_frequency = 0
    minimum_frequency = 0
    buffer_size = None

    sound = None
    sound_start_time = 0

    def __init__(self):
        self.types = {
            1: np.int8,
            2: np.int16,
            4: np.int32
        }

    @staticmethod
    def init_bandwidth(bandwidth_count, min_freq, max_freq):
        bands = [0] * bandwidth_count
        step = round(max_freq / 2 ** bandwidth_count)
        for i in range(bandwidth_count):
            bands[i] = bands[i-1] + step * 2 ** i if i > 0 else min_freq + step * 2 ** i
        return bands

    def load_music(self):
        song = wave.open(self.music_file_path, mode='rb')

        (self.channels_number, self.samp_width,
         self.frame_rate, self.frames_number,
         self.comp_type, self.comp_name) = song.getparams()

        song_frames = song.readframes(self.frames_number)
        frames_converted = np.fromstring(song_frames, dtype=self.types[self.samp_width])

        for i in range(self.channels_number):
            self.channel_frames.append(frames_converted[i::self.channels_number])

        self.channel_frames = np.array(self.channel_frames)
        self.channels_original = self.channel_frames.copy()

        self.specter = np.fft.rfft(self.channels_original)
        self.specter_original = self.specter.copy()

        self.maximum_frequency = self.frame_rate // 2
        self.each_frequency_elements = self.specter.shape[1] // (self.maximum_frequency - self.minimum_frequency)
        self.buffer_size = self.frame_rate

        pygame.mixer.pre_init(frequency=self.frame_rate,
                              size=-self.samp_width * 8,
                              channels=self.channels_number)

        pygame.init()

    def play_music(self):
        tmp_channels = [self.channel_frames[0], self.channel_frames[1]]
        tmp_channels = np.array(tmp_channels)
        tmp_channels = np.ascontiguousarray(tmp_channels.T)
        tmp_sound = pygame.sndarray.make_sound(tmp_channels)

        self.sound = tmp_sound
        pygame.mixer.Sound.play(self.sound)
        self.sound_start_time = int(time.time())

    def pause_music(self):
        self.music_is_playing = False
        self.music_is_paused = True

    def unpause_music(self):
        self.music_is_playing = True
        self.music_is_paused = False

    def stop_music(self):
        self.music_is_playing = False
        self.music_is_paused = False
        pygame.mixer.Sound.stop(self.sound)

    def update_music(self):
        current_time = int(time.time())
        starts_at = current_time - self.sound_start_time

        tmp_channels = [self.channel_frames[0][self.buffer_size * starts_at:],
                        self.channel_frames[1][self.buffer_size * starts_at:]]

        tmp_channels = np.array(tmp_channels)
        tmp_channels = np.ascontiguousarray(tmp_channels.T)
        tmp_sound = pygame.sndarray.make_sound(tmp_channels)

        pygame.mixer.Sound.stop(self.sound)
        self.sound = tmp_sound
        pygame.mixer.Sound.play(self.sound)

    def equaliser_music_edit(self, low_frequency, high_frequency, strength):
        """
        Function to edit sound frequencies
        :param high_frequency: Frequency level at which stop cutting
        :param low_frequency: Frequency level at which start cutting
        :param strength: Cutting strength, where 0 means "no effect", positive numbers equals "Higher bandwidth"
                        and negatives means "Lower bandwidth"
        :type strength: int
        """

        new_specter = self.specter.copy()
        for i in range(self.channels_number):
            new_specter[i][self.each_frequency_elements * low_frequency
                           : self.each_frequency_elements * high_frequency + 1] *= 10 ** (strength / 20)

        self.channel_frames = (np.fft.irfft(new_specter)).astype(self.types[self.samp_width])
        self.new_specter = new_specter
