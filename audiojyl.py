import wave
from pyaudio import PyAudio,paInt16  
from aip import AipSpeech


def get_audio(flag=0,filepath = 'test.wav',APP_ID = '36058518',API_KEY = 'TRcLPD92i4WnvgZ7XkcIN3wO',SECRET_KEY = 'BXnx0E78fhGzwfVlZF8zLBUe66vnSsCI',CHUNK=1024,FORMAT=paInt16,CHANNEL=1,RATE=16000,RECORD_SECONDS=10):
    print("*" * 10, "结印 释放技能")
    if True:
        
        pa = PyAudio()
        stream = pa.open(format=FORMAT,
                         channels=CHANNEL,
                         rate=RATE,
                         input=True,
                         frames_per_buffer=CHUNK)
       

        frames = []  
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):  
            # 读取chunk个字节 保存到data中
            data = stream.read(CHUNK)  
            # 向列表frames中添加数据data
            frames.append(data)  
            # 判断开始结束标志
            if(flag==0):  break
            # 判断是否超时 暂定10s
            if(i == int(RATE / CHUNK * RECORD_SECONDS)-1): return -1
        print("*" * 10, "录音结束\n")
        stream.stop_stream()
        # 停止数据流
        stream.close()  
        # 关闭PyAudio
        pa.terminate()  

        #写入录音文件
        save_wave_file(pa, filepath, frames,CHANNEL,RATE,FORMAT)
        
        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        result = client.asr(get_file_content('test.wav'), 'wav',16000,{'dev_pid': 1537,})
        return result['result']
        
# 保存为wav文件
def save_wave_file(pa, filepath, data,CHANNEL,RATE,FORMAT=paInt16):
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(CHANNEL)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(data))
    wf.close()

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()



if __name__ == '__main__':
    # 10s后判定为超时
    RECORD_SECONDS=10
    # 获取语音识别结果
    # result = get_audio(1)
    result = get_audio(1)
    print("result:",result,"type：",type(result))
    # result: ['你好你好你好你好，忙的是主要做。'] type： <class 'list'>
    print('释放技能结束！')
  