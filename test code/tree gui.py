from tkinter import *
from tkinter import ttk

class GUI():
    def __init__(self):
        self.root = Tk()
        self.root.title('Sales reporting')
        
        self.frame_main = ttk.Frame(self.root)
        ttk.Label(self.frame_main, text='Sales reporting').grid(row=0, column = 0)
        self.frame_main.pack()
        
    def run(self):
        self.maketree(None)
        self.root.mainloop()
        
    def maketree(self, tree_data):
        self.tree = ttk.Treeview(self.frame_main, columns=('serial', 'active', 'options'))
        self.tree.heading('serial', text = 'DTU serial')
        self.tree.heading('active', text = 'Active during this period?')
        self.tree.heading('options', text = 'Actions')
        
        ## test
        parent1 = self.tree.insert('', 'end', 'test1', text = 'Test tree parent')
        parent1_1 = self.tree.insert(parent1, 'end', 'test2', text = 'Child of first')
        parent1_2 = self.tree.insert(parent1, 'end', 'test3', text = 'Another child of first')
        child1 = self.tree.insert(parent1_1, 'end', 'test4', text = 'Sub child 1')
        child2 = self.tree.insert(parent1_1, 'end', 'test5', text = 'Sub child 2')
        self.tree.set('test5', 'serial', 'test serial')
        parent1 = self.tree.insert('', 'end', 'test6', text = 'Test tree second parent')
        
        self.tree.grid(row=1, column=0)
        self.root.update()
        
ui = GUI()
ui.run()
