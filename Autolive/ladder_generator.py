
class Ladder_generator:
    """
    def __init__(self, input_width, input_height, input_bitrate, input_fps):
        self.input_bitrate = input_bitrate
        self.input_width = input_width
        self.input_height = input_height
        self.input_fps = input_fps
    """ 

    def generate(self, input_height, input_bitrate, input_audio_bitrate, input_fps, return_Array, index):
        if input_height < 234 or input_bitrate < 145:
            return return_Array
        
        if input_height < 540 and input_fps > 30:
            input_fps = 30
        
        if input_bitrate > 5000:
            input_bitrate = 5000
            
        if input_height == 320:
            input_height = 360
        
        if round((input_height*16)/9)%2 == 0:
            width = round((input_height*16)/9)
        else:
            width = round((input_height*16)/9) + 1
        
        if index == 1:
            calcBitrate = input_bitrate
        else:
            calcBitrate = round(input_bitrate/(2*int(index)))

        # Audio calibration
        if calcBitrate <= 3000:
            input_audio_bitrate = 96000
        else:
            if input_audio_bitrate > 160000:
                input_audio_bitrate = 192000
            else:
                input_audio_bitrate = 160000


        item = {
            'name': str(width),
            'width': width,
            'height': round(input_height),
            'bitrate': calcBitrate,
            'fps': input_fps,
            'audio_bitrate': input_audio_bitrate
        }
        
        return_Array.append(item)
        
        index += 1

        return self.generate(input_height/1.5, input_bitrate, input_audio_bitrate, input_fps, return_Array, index)


"""
# Tests
test = LadderGenerator()
value = test.generate(1080, 7800, 192000, 60, [])
print(value)
"""
