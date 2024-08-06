# import os
# import azure.cognitiveservices.speech as speechsdk

# speech_config = speechsdk.SpeechConfig(subscription="6c34a2c3419e4846beb5b5b064df4af6", region='eastus')

# speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

# output_file = "output.mp3"

# audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)

# speech_config.speech_synthesis_voice_name='en-US-SteffanNeural'

# speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

# print("Enter some text that you want to speak >")
# text = input()

# speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

# if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#     print(f"Speech synthesized for text [{text}] and saved to {output_file}")

# elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
#     cancellation_details = speech_synthesis_result.cancellation_details
#     print(f"Speech synthesis canceled: {cancellation_details.reason}")
    
#     if cancellation_details.reason == speechsdk.CancellationReason.Error:
#         if cancellation_details.error_details:
#             print(f"Error details: {cancellation_details.error_details}")
#             print("Did you set the speech resource key and region values?")

# import gpt_imggen_combined as imggen

# imggen.process_prompt('Draw a tree diagram with two branches for the first ball (blue and red) and two branches for the second ball (blue and red) under each of the first branches. Label the outcomes as BB, BR, RB, and RR.').show()

# def get_audio():
#     return 2

import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from pydub.playback import play
import io
import subprocess
from pydub.utils import which

def get_audio(text):

    subscription_key = "c30c3ccd4b8747db997c4c6c08095f5c"
    service_region = "eastus"
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
    speech_config.speech_synthesis_voice_name = 'en-US-SteffanNeural'


    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text [{text}]")

  
        stream = speechsdk.AudioDataStream(speech_synthesis_result)


        audio_data = bytearray()
        buffer_size = 3200  # 3200 bytes = 100 ms of audio at 16kHz, 16-bit mono
        while True:
            buffer = bytes(buffer_size)  
            bytes_read = stream.read_data(buffer)
            if bytes_read == 0:
                break
            audio_data.extend(buffer[:bytes_read]) 

        audio_stream = io.BytesIO(bytes(audio_data))
        audio_segment = AudioSegment.from_file(audio_stream, format="mp3")
        # custom_play(audio_segment)
        
        return bytes(audio_data) 

    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print(f"Error details: {cancellation_details.error_details}")
                print("Did you set the speech resource key and region values?")
        return None

def custom_play(audio_segment):
    output_file = "output.wav"
    audio_segment.export(output_file, format="wav")
    
    PLAYER = which("ffplay") or which("avplay") or which("play")
    subprocess.call([PLAYER, "-nodisp", "-autoexit", "-hide_banner", output_file])

# """ Example Usage """
# text_to_speak = "Hello!"
# print(get_audio(text_to_speak))