import tkinter as tk
from  tkinter  import ttk,filedialog
import os 
from convert import Convert
import threading
import math
from multiprocessing import Pool
from tqdm import tqdm

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.convert = Convert()

        self.source_root = tk.StringVar()
        self.target_root = tk.StringVar()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")
        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

        #源目录
        self.get_folder = tk.Button(self)
        self.get_folder["text"] = "打开源文件目录"
        self.get_folder["command"] = self.open_source_dir
        self.get_folder.pack(side="top")

        #存放目录
        self.get_folder = tk.Button(self)
        self.get_folder["text"] = "打开存放目录"
        self.get_folder["command"] = self.open_target_dir
        self.get_folder.pack(side="top")

        self.bt_run = tk.Button(self)
        self.bt_run["text"] = "确定"
        self.bt_run["command"] = self.converting
        self.bt_run.pack(side="top")

    def say_hi(self):
        print("hi there, everyone!")

    #打开文件夹
    def open_source_dir(self):
        folder_path = filedialog.askdirectory()
        print("选择的文件夹路径是:", folder_path)
        self.source_root.set(folder_path)

    def open_target_dir(self):
        folder_path = filedialog.askdirectory()
        print("选择的文件夹路径是:", folder_path)
        self.target_root.set(folder_path)

    def converting(self):
        #遍历source_root
        #将source_root的文件夹分组,采用多线程并发操作
        source_name = os.listdir(self.source_root.get())
        print(f'source name :{self.source_root.get()}')
        #获取当前电脑的核数
        cpu_count = os.cpu_count()
        #打印
        print(f"当前电脑的核数是{cpu_count}")
        #根据cpu核数， 完成并发线程
        source_len = len(source_name)
        #每个线程处理的文件数
        part = math.ceil(source_len / cpu_count)
        source_name = [source_name[i:i+part] for i in range(0,source_len,part)]
            
        for part_audio in source_name:
            thred = threading.Thread(target=self.toMp4,args=[part_audio,self.target_root.get()])
            thred.start()
        # thred.join()
        # self.btnClick()
        

    def toMp4(self,source,target):
        #如果source 以.ncm 结尾
        print(f'### Now is :{source} ###')
        for s in source:
            if os.path.splitext(s)[1] == '.ncm':
                self.convert.ncm2mp3(self.source_root.get(),s,target)
            else:
                s = os.path.join(self.source_root.get(),s)
                self.convert.flac2mp3(s,target)
    def btnClick():
        tk.messagebox.showinfo("消息", "转换已完成~")

windows = tk.Tk()
windows.geometry('400x300')
app = Application(master=windows)
app.mainloop()
