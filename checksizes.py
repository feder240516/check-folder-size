import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter import ttk
from collections import deque
#from tqdm import tqdm
import os

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


all_paths = dict()


def check_size(directory=".", is_super_path=False):
    #if directory in all_paths.keys():
    #    return all_paths[directory]
    this_diro = Diro(directory,0)
    total_size = 0
    for thisdir, thissubdirectories, thisfilenames in os.walk(directory):
        
        for d in thissubdirectories:
            if is_super_path: print(d)
            newsubdir = check_size(os.path.join(directory,d))
            total_size += newsubdir.size
            this_diro.subdirectories.append(newsubdir)

        for f in thisfilenames:
            try:
                
                fp = os.path.join(thisdir,f)
                if is_super_path: print(fp)
                filesize = os.path.getsize(fp)
                total_size += filesize
                filediro = Diro(fp,filesize)
                this_diro.subdirectories.append(filediro)
            except:
                pass
        break
    this_diro.size = total_size
    all_paths[directory] = this_diro
    this_diro.subdirectories.sort(key= lambda x: x.size, reverse=True)
    return this_diro

class TreeApp(ttk.Frame):
    def __init__(self, main_window):
        background_style = ttk.Style()
        background_style.configure(style="TFrame")
        ttk.Frame.__init__(self,main_window,style="TFrame")
        main_window.title("Check size")
        main_window.geometry('600x500+100+100')
        self.place(relx=0.05,rely=0.05,relheight=0.9,relwidth=0.9)
        
        self.treeview = ttk.Treeview(self, columns=["Size"])
        self.treeview.heading("#0", text="Archivo")
        self.treeview.heading("#1", text="Tamaño")
        self.treeview.column("Size", anchor=tk.E)
        #self.treeview.grid(row=0,column=0,sticky='NSEW')
        self.treeview.place(relx=0,rely=0,relheight=0.8,relwidth=1)
        #self.treeview.pack(fill="both",expand=True)
        self.parent_node = None
        
        self.select_button = ttk.Button(self, text="Select", command=lambda : self.select_parent_node())
        self.select_button.place(relx=0.8,rely=0.9,relheight=0.1,relwidth=0.2)
        #self.select_button.pack(expand=True,fill='x')
        

        #self.grid(row=0,column=0,sticky='NSEW')
        

        
        #self.pack(fill="both",expand=True)
        

    def set_parent_node(self, diro: Diro):
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
        diro = check_size(directory,True)
        self.set_parent_node(diro)

if __name__ == '__main__':
    root = tk.Tk()
    directory = "."
    app = TreeApp(root)
    app.mainloop()
    """
    print("Bienvenido al programa de segmentación del tamaño de las carpetas")
    print("Aparecerá una ventana para que selecciones la carpeta a analizar")
    root = tk.Tk()
    root.withdraw()
    while True:
        file = filedialog.askdirectory()
        print (file)
        dires = []
        totallysize = 0
        for subdir, dirnames, filings in os.walk(file):
            numelements = len(dirnames) + len(filings)
            numdirs = len(dirnames)
            for i, dirname in enumerate(dirnames):
                dires.append(check_size(os.path.join(subdir,dirname)))
                totallysize += dires[i]
                print(i + 1, "elementos escaneados de", numelements)
            for i, subfile in enumerate(filings):
                try:
                    filesize = os.path.getsize(os.path.join(subdir,subfile))
                    totallysize += filesize
                    dires.append(Diro(os.path.join(subdir,subfile),filesize))
                    print(numdirs + i, "elementos escaneados de", numelements)
                except FileNotFoundError:
                    pass
            break

        dires.sort(key=lambda x: x.size, reverse=True)
        for i in dires:
            print(i)

        print("Tamaño total de este directorio:\n" + str(Diro(file, totallysize)))
        input("Presione enter para intentar otro directorio\n")
        all_paths.clear()
    """
