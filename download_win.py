# -*- coding:utf-8 -*-  
import os
import requests,time
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
#import multiprocessing
import uuid,json
import base64
import time,random
def parse_har(har_file_name):
    file = open(har_file_name,'r',encoding='utf-8')
    content = file.read()
    my_har_origin = json.loads(content)
    print("[+] Json decoding successfully")
    m3u8 = None
    IV = None
    for req in my_har_origin['log']['entries']:
        #req_json = json.loads(req)
        if 'request' in req:
            if 'url' in req['request']:
                if "src/get?id=" in req['request']['url']:
                    m3u8 = req['response']['content']['text']
                if "authorize?id=" in req['request']['url']:
                    IV = req['response']['content']['text']
                    #print(req['response']['content']['text'])
    file.close()
    print("[+] Get m3u8 and key successfully")
    return m3u8,IV

def read_m3u8(m3u8,key,filename):
    all_content = base64.b64decode(m3u8).decode('utf-8')
    key  = base64.b64decode(key)
    print("[+] Base64 decoder load successfully")
    cryptor = AES.new(key, AES.MODE_CBC, key) 
    if "#EXTM3U" not in all_content:
        print("[-] E: Not found video in " + filename)
        return
    print("[+] Decrypt video successfully")
    file_line = all_content.split("\n")
    #time_str = time.strftime('%d-%H%M%S', time.localtime(time.time()))
    ts_name = "download//{}.ts".format(filename)
    writer = open(ts_name, 'wb')
    print("[*] Downloading ts file...")
    num=1
    max_num=int(int(len(file_line))/2-4)
    for index, line in enumerate(file_line): # 第二层 
        if "EXTINF" in line: # 找ts地址并下载
            pd_url = file_line[index + 1] # 拼出ts片段的URL
            while True:
                try:
                    res = requests.get(pd_url)
                    #print(filename,pd_url)
                    break
                except Exception as e:
                    #print(e)
                    print("[-] E: Rertrying...")
                    time.sleep(random.randint(1,5))
            writer.write(cryptor.decrypt(res.content))
            perc=int((num/(max_num))*50)
            #print(" [",end="")
            #for i in range(0,perc):
                #print("=",end="")
            #for j in range(0,50-perc):
                #print(" ",end="")
            #print("]"+str(num)+" of "+str(max_num),end="\r")
            print("[*] "+str(num)+" of "+str(max_num))
            #print("{} finish download".format(filename))
            num+=1
    writer.close()
    print("[*] Download successful")
    return 0

if __name__ == '__main__': 
    har_list = os.listdir('har')
    os.system("mkdir download")
    print("[*] Download queue:"+str(har_list))
    #pool = multiprocessing.Pool(processes = 1)
    for har in har_list:
        file_without_suffix = har.rsplit('.')[0]
        print("[*] Now processing:"+file_without_suffix)
        try:
            m3u8,key = parse_har('har//'+har)
            read_m3u8(m3u8,key,file_without_suffix)
        except Exception as e:
            print("[-] E: {} ".format(e))
            print("[-] E: {} parse error".format(har))
    #pool.close()
    #pool.join()
            
