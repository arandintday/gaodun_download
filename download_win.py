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
    #file = open(har_file_name,'rb')
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
                    if "application" in req['response']['content']['mimeType']:
                        print("[+] Base64 code detected")
                    else:
                        print("[-] E: Not support bin type key for now")
                        return
                    IV = req['response']['content']['text']
                    print("[*] The key is {}, {} byte".format(IV,len(IV)))
    file.close()
    print("[+] Get m3u8 and key successfully")
    return m3u8,IV

def read_m3u8(m3u8,key,filename):
    all_content = base64.b64decode(m3u8).decode('utf-8')
    key  = base64.b64decode(key)
    print("[+] Base64 decoder load successfully")
    print("[*] The decoded key is {},{} byte".format(key,len(key)))
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
                    print("[-] E: {} ".format(e))
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
            print("[*] "+str(num)+" of "+str(max_num),end="\r")
            #print("{} finish download".format(filename))
            num+=1
    writer.close()
    print("[*] {} download successful".format(filename))
    return 0

if __name__ == '__main__':
    fin=0
    err=0
    folder = os.path.exists("download")
    folder2 = os.path.exists("har")
    if not folder:
        os.makedirs("download")
    else:
        print("[*] Download folder already exists")
    if not folder2:
        os.makedirs("har")
    else:
        print("[*] Har folder already exists")
    har_list = os.listdir('har')
    print("[*] Download queue:"+str(har_list))
    #pool = multiprocessing.Pool(processes = 1)
    for har in har_list:
        file_without_suffix = har.rsplit('.')[0]
        print("[*] Now processing:"+file_without_suffix)
        try:
            m3u8,key = parse_har('har//'+har)
            read_m3u8(m3u8,key,file_without_suffix)
            fin+=1
        except Exception as e:
            print("[-] E: {} ".format(e))
            print("[-] E: Can't download {}, not a supported file or it contains non base64 key".format(har))
            err+=1
    #pool.close()
    #pool.join()
    print("{} files download successful，{} files download failed".format(fin,err))
    os.system("pause")
