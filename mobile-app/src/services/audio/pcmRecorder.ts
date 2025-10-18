// src/services/audio/pcmRecorder.ts

import { Audio } from 'expo-av';
import { Platform } from 'react-native';

export class PCMRecorder {
  private recording: Audio.Recording | null = null;
  private isInitialized = false;

  // Request microphone permissions
  async init() {
    console.log('Requesting microphone permissions...');
    const { status } = await Audio.requestPermissionsAsync();
    if (status !== 'granted') {
      alert('Sorry, we need microphone permissions to make this work!');
      this.isInitialized = false;
      return false;
    }
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: true,
      playsInSilentModeIOS: true,
    });
    this.isInitialized = true;
    console.log('Microphone permissions granted and audio mode set.');
    return true;
  }

  // Start a new recording
  async start() {
    if (!this.isInitialized) {
      console.error('Recorder not initialized. Call init() first.');
      const initialized = await this.init();
      if (!initialized) return;
    }

    try {
      console.log('Starting recording...');
      const { recording } = await Audio.Recording.createAsync(
         Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      this.recording = recording;
      console.log('Recording started');
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  }

  // Stop the recording and get the file URI
  async stop(): Promise<string | null> {
    if (!this.recording) {
      console.warn('No active recording to stop.');
      return null;
    }

    console.log('Stopping recording...');
    await this.recording.stopAndUnloadAsync();
    const uri = this.recording.getURI();
    this.recording = null; // Clear the recording object
    console.log('Recording stopped. File saved at:', uri);
    return uri;
  }
}