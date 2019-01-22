from tkinter import *
from tkinter import messagebox, filedialog
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter.constants import CENTER, LEFT, N, E, W, S

class GUI():
    def __init__(self):
        self.root = Tk()
        self.root.title('UI test')
        self.root.geometry('800x500')
        
        self.frame_main = ttk.Frame(self.root)
        self.frame_main.pack(fill = BOTH, expand = 1)
        
    def run(self):
        ## fees list: widget, button, name, amount, unit, type
        self.fees = []
        self.fees_row_index = 0
        self.frame_fees = ttk.Frame(self.frame_main)
        
        ## new fee widgets
        self.frame_fees_new = ttk.Labelframe(self.frame_fees, text = 'New fee')
        
        self.fee_name_value = StringVar()
        self.fee_amount_value = StringVar()
        self.fee_type_value = StringVar()        
        
        ttk.Label(self.frame_fees_new, text = 'Fee name').grid(row = 0, column = 0)
        ttk.Label(self.frame_fees_new, text = 'Amount').grid(row = 0, column = 1)
        ttk.Label(self.frame_fees_new, text = 'Rate').grid(row = 0, column = 2)
        
        self.fee_name = ttk.Entry(self.frame_fees_new, textvariable = self.fee_name_value, width = 25)
        self.fee_amount = ttk.Spinbox(self.frame_fees_new, format = '%.2f', increment = 0.01, textvariable = self.fee_amount_value)
        self.fee_type = ttk.Combobox(self.frame_fees_new, values = ['% of total sales value', 'dollars per transaction', '% of CC sales value', 'dollars per CC sale', '% of cash sales value', 'dollars per cash sale', 'dollars per active DTU'], textvariable = self.fee_type_value)        
        
        self.fee_name.grid(row = 1, column = 0)
        self.fee_amount.grid(row = 1, column = 1)
        self.fee_type.grid(row = 1, column = 2)
        ttk.Button(self.frame_fees_new, text = 'Add fee', command = self.add_fee).grid(row = 1, column = 4)
        
        self.frame_fees_new.grid(row = 0, column = 0, sticky = 'ew')
        
        ## current fee container
        self.frame_fees_current = ttk.LabelFrame(self.frame_fees, text = 'Current fees')
        self.frame_fees_current.grid(row = 1, column = 0, sticky = 'ew')        
        
        self.frame_fees.grid(row = 0, column = 0)
        
    def add_fee(self):
        fee_name = str(self.fee_name_value.get())
        fee_amount = float(self.fee_amount_value.get())
        fee_type = self.fee_type_value.get()
       
        fee_print = fee_name + ': ' + ('%.2f' % fee_amount) + ' ' + fee_type
        
        widget_text = ttk.Label(self.frame_fees_current, text = fee_print)
        widget_button = ttk.Button(self.frame_fees_current, text = 'Remove', command = lambda: self.remove_fee(widget_text))
        
        widget_text.grid(row = self.fees_row_index, column = 1)
        widget_button.grid(row = self.fees_row_index, column = 0)
        self.fees_row_index += 1
        
        self.fees.append([widget_text, widget_button, fee_name, fee_amount, fee_type])
        
    def remove_fee(self, widget_text):
        remove_entry = None
        for entry in self.fees:
            if entry[0] == widget_text:
                remove_entry = entry
                break
                
        if remove_entry == None:
            return
                
        remove_entry[0].grid_forget()
        remove_entry[1].grid_forget()
        self.fees.remove(entry)
        self.root.update()                
        
        
ui = GUI()
ui.run()