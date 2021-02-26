#!/usr/bin/python3

#author: Jhon Rayo
import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter import ttk
from collections import deque
from multiprocessing import Process, Queue, freeze_support
from threading import Thread
#from tqdm import tqdm
import os
import signal

multi_queue = Queue()

DELAY_PROGRESS = 50
DELAY_CHECK_END_PROCESS = 100
class Diro:
    def __init__(self,name,size):
        self.name = os.path.normpath(name)
        self.size = size
        self.subdirectories = list()

    def __str__(self):
        return "..." + self.name.ljust(50)[-50:] + " " + self.norm_size

    def __radd__(self, other):
        if type(other) == int:
            return other + self.size
        elif type(other) is Diro:
            return other.size + self.size
        else:
            raise TypeError()

    def __eq__(self, other):
        return type(other) == Diro and other.name == self.name

    @property
    def last_path(self):
        return os.path.basename(os.path.normpath(self.name))

    @property
    def norm_size(self):
        shownsize = ""
        if self.size > 1024 * 1024 * 1024:
            shownsize = f'{self.size / (1024*1024*1024):.2f}' + " Gb"
        elif self.size > 1024 * 1024:
            shownsize = f'{self.size / (1024*1024):.2f}' + " Mb"
        elif self.size > 1024:
            shownsize = f'{self.size / 1024:.2f}' + " Kb"
        else:
            shownsize = f'{self.size:.2f}' + " b"
        return shownsize



def normalize_directory(directory: str):
    return os.path.expanduser(directory)

def check_size(queue, directory=".", is_super_path=False):
    directory = normalize_directory(directory)
    all_paths = dict()
    root_diro = None
    
    for thisdir, thissubdirectories, thisfilenames in os.walk(directory,topdown=False):
        total_size = 0
        this_diro = Diro(thisdir,0)
        
        for d in thissubdirectories:
            subdir_fullpath = str(os.path.join(thisdir,d))
            if subdir_fullpath in all_paths:
                newsubdir = all_paths[subdir_fullpath]
                total_size += newsubdir.size
                this_diro.subdirectories.append(newsubdir)
            else:
                print(subdir_fullpath + ' is either a symlink or you don\'t have read permissions for this directory. Skipped.')

        for f in thisfilenames:
            try:
                
                fp = os.path.join(thisdir,f)
                filesize = os.path.getsize(fp)
                total_size += filesize
                filediro = Diro(fp,filesize)
                this_diro.subdirectories.append(filediro)
            except:
                print(f"Couldn't open file {fp}")
                pass
        
        this_diro.size = total_size
        all_paths[thisdir] = this_diro
        this_diro.subdirectories.sort(key= lambda x: x.size, reverse=True)
        root_diro = this_diro
    queue.put(root_diro)
    return

class TreeApp(ttk.Frame):
    def __init__(self, main_window):
        background_style = ttk.Style()
        background_style.configure(style="TFrame")
        ttk.Frame.__init__(self,main_window,style="TFrame")
        main_window.title("Check size")
        main_window.geometry('600x500+100+100')
        self.place(relx=0.05,rely=0.05,relheight=0.9,relwidth=0.9)
        
        self.treeview = ttk.Treeview(self, columns=["Size"])
        self.treeview.heading("#0", text="File")
        self.treeview.heading("#1", text="Size")
        self.treeview.column("Size", anchor=tk.E)
        self.treeview.place(relx=0,rely=0,relheight=0.8,relwidth=1)
        self.parent_node = None
        
        self.select_button = ttk.Button(self, text="Select directory", command=lambda : self.select_parent_node())
        self.select_button.place(relx=0.8,rely=0.9,relheight=0.1,relwidth=0.2)
        
        self.progress = ttk.Progressbar(self,mode='indeterminate')
        self.progress.place(relx=0,rely=0.9,relheight=0.1,relwidth=0.6)

    def set_parent_node(self, diro: Diro):
        if diro is None:
            print('ERROR: Required argument diro is None. Ensure you have enough permissions for reading selected directory')
            if self.parent_node != None:
                self.treeview.delete(self.parent_node)
            return
        if self.parent_node != None:
            self.treeview.delete(self.parent_node)
        self.parent_node = self.treeview.insert("", tk.END, text=diro.last_path, values=[diro.norm_size])
        
        nodes_to_add = deque([(diro,self.parent_node)])
        while len(nodes_to_add) > 0:
            selected_diro, selected_node = nodes_to_add.pop()
            for subdiro in selected_diro.subdirectories:
                try:
                    subnode = self.treeview.insert(selected_node,tk.END,text=subdiro.last_path,values=[subdiro.norm_size])
                    nodes_to_add.append((subdiro,subnode))    
                except Exception as e:
                    print(e)

    def select_parent_node(self):
        directory = filedialog.askdirectory()
        if directory == '': return
        self.after(DELAY_CHECK_END_PROCESS,self.checkProcessFinish)
        self.select_button.config(state=tk.DISABLED)
        self.p1 = Process(target=check_size, args=(multi_queue, directory, True))
        self.progress.start(DELAY_PROGRESS)
        self.p1.start()
        
        
    def checkProcessFinish(self):
        if multi_queue.empty():
            self.after(DELAY_CHECK_END_PROCESS,self.checkProcessFinish)
        else:
            diro = multi_queue.get(0)
            self.set_parent_node(diro)
            self.progress.stop()
            self.select_button.config(state=tk.NORMAL)

if __name__ == '__main__':
    freeze_support()
    root = tk.Tk()
    directory = "."
    app = TreeApp(root)
    app.mainloop()
