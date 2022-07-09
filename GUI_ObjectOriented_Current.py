from tkinter import *
import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import json

class Connect_MongoDB:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.databases = self.client.list_databases()
        self.activedb=""

    def get_database_list(self):
        return self.databases

    def set_current_database(self, value):
        self.activedb = self.client[value]
    
    def get_current_database(self):
        return self.activedb

class Database_Project(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        
        self.stack_frame_container = tk.Frame(self)
        self.stack_frame_container.grid_columnconfigure(0, weight=1)
        self.stack_frame_container.grid_rowconfigure(0, weight=1)
        self.stack_frame_container.pack(side="top", fill="both", expand=True)

        self.frameslist = {}

        for frame in (SelectDatabase, MainPage, CreatePage_Main, CreatePage_InsertOne, CreatePage_InsertMany, DeletePage):
            frame_occurrence = frame.__name__
            active_frame = frame(parent=self.stack_frame_container, controller=self)
            self.frameslist[frame_occurrence] = active_frame
            active_frame.grid(row=0, column=0, sticky="snew")

        self.running_frame = None
        self.reload_frame(SelectDatabase)
            
    def current_frame(self, frame_occurrence):
        active_frame = self.frameslist[frame_occurrence]
        active_frame.tkraise()

    def get_current_frame(self, frame_occurrence):
        active_frame = self.frameslist[frame_occurrence]
        return active_frame

    def reload_frame(self, new_frame_class):
        active_frame = new_frame_class

        if self.running_frame:
            self.running_frame.destroy()
        
        self.running_frame = active_frame(self.stack_frame_container, controller=self)
        self.running_frame.grid(row=0, column=0, sticky="snew")

class Pages:
    coldatabase = ""
    collection = ""
    

class SelectDatabase(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        database_dict = {}
        self.buttons_list = []
        

        self.database_connect = Connect_MongoDB()
        databases = self.database_connect.get_database_list()

        database_list_frame = tk.Frame(self)
        database_list_frame.grid(row=0)

        self.collection_list_frame = tk.Frame(self)
        self.collection_list_frame.grid(row=1)

        label_top = tk.Label(database_list_frame, text="Choose existing database").grid(row=0, column=1, pady=25)
        self.runningdb_label = tk.Label(database_list_frame, text="No active database") 

        for index, db in enumerate(databases):
            database_dict[index] = db

        rowcount= 1
        count= 0
        for key, value in database_dict.items():   
            namedb = value['name']
            tk.Button(database_list_frame, text=str(value['name']), command=lambda namedb=namedb: self.set_activedb(namedb)).grid(row=rowcount, column=(count), padx=50, pady=15)
            count += 1

            if count % 3 == 0:
                rowcount += 1
                count = 0

        self.runningdb_label.grid(row=rowcount + 1, column=0, pady=25)
        create_db_button=tk.Button(database_list_frame, text="+")
        create_db_button.grid(row=rowcount + 1, column=2, pady=25)
        create_db_button.bind("<Button>", lambda e: self.create_database_window())

    def set_activedb(self, name):
        self.database_connect.set_current_database(str(name))
        self.runningdb_label.config(text="Running database:\n" + name)
        self.get_activedb()

    def get_activedb(self):
        runningdb = self.database_connect.get_current_database()
        self.create_collection_list(runningdb)

    def create_collection_list(self, chosendb):
        collection = chosendb.list_collection_names()

        if len(self.buttons_list) != 0:
            for buttons in self.buttons_list:
                buttons.grid_forget()

            self.create_col_button.grid_forget()

        self.buttons_list.clear()

        for collect in collection:
            col = collect
            self.buttons_list.append(tk.Button(self.collection_list_frame, text=str(col), command=lambda col=col: self.set_collection(col, chosendb)))

        rowcount = 0
        count = 0
        for collect in range(len(self.buttons_list)):
            self.buttons_list[collect].grid(row=rowcount, column=count, padx=50, pady=15)
            count += 1

            if count % 3 == 0:
               rowcount += 1
               count = 0

        self.create_col_button=tk.Button(self.collection_list_frame, text="+")
        self.create_col_button.grid(row=rowcount , column=count, pady=25)
        self.create_col_button.bind("<Button>", lambda e: self.create_collection_window())

    def set_collection(self, collection, db):
        Pages.coldatabase = db[collection]
        Pages.collection = collection

        self.controller.reload_frame(MainPage)

    def create_database_window(self):
        self.dbWindow = Toplevel(self)
        self.dbWindow.title("Create New Database")

        self.dbWindow.wait_visibility()
        self.dbWindow.grab_set()

        db_create_label = tk.Label(self.dbWindow, text="Enter valid name \n to create new database")
        db_create_label.grid(row=0, column=0, padx=10, pady=10)
        self.db_entry = tk.Entry(self.dbWindow, borderwidth=5)
        self.db_entry.grid(row=0, column=1, padx=10, pady=10)
        db_submit_button = tk.Button(self.dbWindow, text="ADD DATABASE", command=self.submit_database)
        db_submit_button.grid(row=1, column=2, padx=10, pady=10)

        col_create_label = tk.Label(self.dbWindow, text="Enter valid name\nto create new collection\nDatabases are not\ncreated without content")
        col_create_label.grid(row=1, column=0, padx=10, pady=10)
        self.col_entry = tk.Entry(self.dbWindow, borderwidth=5)
        self.col_entry.grid(row=1, column=1, padx=10, pady=10)

    def submit_database(self):
        newdb_name = self.db_entry.get()
        newcol_name = self.col_entry.get()

        invalid_chars = ['/', '\\', '.', '$', '"', '*', '<', '>', ':', '|', '?']
        valid_status = True

        if len(newdb_name) < 1 or len(newdb_name) > 64 or newdb_name.isspace():
            messagebox.showerror("Error", "Database name too long or too short") 
            valid_status = False 

        if any(i in newdb_name for i in invalid_chars):
            messagebox.showerror("Error", "Database name contains invalid characters")
            valid_status = False 

        if valid_status:
            self.database_connect.set_current_database(str(newdb_name))

            if "system." in newcol_name or newcol_name.isspace() or "$" in newcol_name or len(newcol_name) == 0:
                messagebox.showerror("Error", "Collection contains invalid characters.")
                valid_status = False 

            else:
                runningdb = self.database_connect.get_current_database()
                self.dbWindow.grab_release()
                self.set_collection(newcol_name, runningdb)
                
    def create_collection_window(self):
        self.colWindow = Toplevel(self)
        self.colWindow.title("Create New Collection")

        self.colWindow.wait_visibility()
        self.colWindow.grab_set()

        top_frame = tk.Frame(self.colWindow)
        top_frame.grid(row=0)
        bottom_frame = tk.Frame(self.colWindow)
        bottom_frame.grid(row=1)

        col_create_label = tk.Label(top_frame, text="Enter valid name \n to create new collection")
        col_create_label.grid(row=0, column=0, padx=10, pady=10)

        self.col_entry = tk.Entry(top_frame, borderwidth=5)
        self.col_entry.grid(row=0, column=1, padx=10, pady=10)

        col_submit_button = tk.Button(top_frame, text="ADD COLLECTION", command=self.submit_collection)
        col_submit_button.grid(row=0, column=2, padx=10, pady=10)

        info_label = tk.Label(bottom_frame, text="REMINDER: Databases and collections need to\nbe filled with content to be made permanent.")
        info_label.grid(row=1, column=1)

    def submit_collection(self):
        newcol_name = self.col_entry.get()

        if "system." in newcol_name or newcol_name.isspace() or "$" in newcol_name or len(newcol_name) == 0:
                messagebox.showerror("Error", "Collection contains invalid characters.")

        else:
            runningdb = self.database_connect.get_current_database()
            self.colWindow.grab_release()
            self.set_collection(newcol_name, runningdb)

class MainPage(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        self.controller = controller

        label_collection = tk.Label(self, text="Selected Collection: " + Pages.collection).grid(row=1, column=0, padx=(25,0))

        button3 = tk.Button(self, text="CHANGE DATABASE", command=lambda: controller.reload_frame(SelectDatabase)).grid(row=1, column=2, padx=25, pady=(0,0))

        label_create = tk.Label(self, text="Create and insert data").grid(row=1, column=0, padx=25, pady=(50,0))
        create_button = tk.Button(self, text="CREATE", command=lambda: controller.current_frame("CreatePage_Main")).grid(row=2, column=0)

        label_read = tk.Label(self, text="Query over data").grid(row=1, column=1, padx=25, pady=(50,0))
        read_button = tk.Button(self, text="READ", command=lambda: controller.reload_frame(ReadPage)).grid(row=2, column=1)

        label_update = tk.Label(self, text="Modify existing data").grid(row=3, column=0, padx=25, pady=(50,0))
        update_button = tk.Button(self, text="UPDATE").grid(row=4, column=0, pady=(0,50))

        label_delete = tk.Label(self, text="Remove data").grid(row=3, column=1, padx=25, pady=(50,0))
        delete_button = tk.Button(self, text="DELETE", command=lambda: controller.current_frame("DeletePage")).grid(row=4, column=1, pady=(0,50))   

class CreatePage_Main(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        insert_button = tk.Button(self, text="INSERT ONE", command=lambda: controller.current_frame("CreatePage_InsertOne")).grid(row=0, column=0, padx=(50, 0), pady=(75, 25))
        insertMany_button = tk.Button(self, text="INSERT MANY", command=lambda: controller.current_frame("CreatePage_InsertMany")).grid(row=0, column=1, padx=50, pady=(75, 25))
        import_button = tk.Button(self, text="IMPORT FILE", command=self.import_file).grid(row=0, column=2, padx=(0, 50), pady=(75, 25))
        back_button = tk.Button(self, text="BACK", command=lambda: controller.reload_frame(MainPage)).grid(row=1, column=1, pady=25)

    def import_file(self):
        pass


class CreatePage_InsertOne(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.inputlist = []
        self.newinputlist = []

        frame_self = Frame(self)
        frame_self .pack(fill=BOTH, expand=1)

        self.canvas_insertone = Canvas(frame_self)
        self.canvas_insertone.pack(side=LEFT, fill=BOTH, expand=1)

        scrollbar= tk.Scrollbar(frame_self, orient=VERTICAL, command=self.canvas_insertone.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas_insertone.configure(yscrollcommand=scrollbar.set)
        self.canvas_insertone.bind('<Configure>', lambda e: self.canvas_insertone.configure(scrollregion = self.canvas_insertone.bbox("all")))

        self.frame_two = Frame(self.canvas_insertone)
        self.canvas_insertone.create_window((0,0), window=self.frame_two , anchor="nw")

        labels = [tk.Label(self.frame_two , text="Enter unique field"), tk.Label(self.frame_two , text="Enter corresponding the value/s")]
        self.inputlist.append(labels[:])

        for toplabels in range(1):
            self.inputlist[toplabels][0].grid(row=toplabels, column=0, padx=10, pady=5)
            self.inputlist[toplabels][1].grid(row=toplabels, column=1, padx=10, pady=5)

        first_entries = [tk.Entry(self.frame_two , borderwidth=5), tk.Text(self.frame_two, borderwidth=5, height= 5, width=20)]
        self.newinputlist.append(first_entries[:])
        self.inputlist.append(first_entries[:])

        for x in range(0, len(self.newinputlist) + 1):
            self.newinputlist[0][x].grid(row=1, column=x, padx=10, pady=5)

        button_input_1 = [tk.Button(self.frame_two , text="ADD FIELD/VALUE", command=self.add_insert), tk.Button(self.frame_two, text="BACK", command=lambda: controller.current_frame("CreatePage_Main"))]
        self.inputlist.append(button_input_1[:])
        button_input_2 = [tk.Button(self.frame_two, text="INSERT MANY", command=lambda: controller.current_frame("CreatePage_InsertMany")), tk.Button(self.frame_two, text="SUBMIT DATA", command= self.submit_data)]
        self.inputlist.append(button_input_2[:])
        
        for button in range(len(self.inputlist) - 2, len(self.inputlist)):
            self.inputlist[button][0].grid(row=button, column=0, padx=10, pady=5)
            self.inputlist[button][1].grid(row=button, column=1, padx=10, pady=5)

    def add_insert(self):
        add_input = [tk.Entry(self.frame_two, borderwidth=5), tk.Text(self.frame_two, borderwidth=5, height= 5, width=20)]
        self.inputlist.insert(-2, add_input)
        self.newinputlist.append(add_input)
        
        for widget in self.children.values():
            widget.grid_forget()

        for index, widgets in enumerate(self.inputlist):
            widget_one = widgets[0]
            widget_two = widgets[1]

            widget_one.grid(row=index, column=0, padx=10, pady=5)
            widget_two.grid(row=index, column=1, padx=10)
        
        self.update_idletasks()
        self.canvas_insertone.configure(scrollregion = self.canvas_insertone.bbox('all'))
    
    def submit_data(self):
        current_dict = {}

        for entries in self.newinputlist:
            current_dict[str(entries[0].get())] = str(entries[1].get("1.0", END))[:-1]

        try:
            submit_product = Pages.coldatabase.insert_one( current_dict )

            messagebox.showinfo("MongoDB Document Submission", "Your document has been added to the database.")
            
            self.update_idletasks()
            self.canvas_insertone.configure(scrollregion = self.canvas_insertone.bbox('all'))

            self.controller.reload_frame(CreatePage_InsertOne) 
        except:
            messagebox.showerror("Error", "An Error has occured. Please make sure your inputs are valid.")

class CreatePage_InsertMany(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.inputlist = []
        self.newinputlist = []

        frame_self = Frame(self)
        frame_self.pack(fill=BOTH, expand=1)

        self.canvas_insertmany = Canvas(frame_self)
        self.canvas_insertmany.pack(side=LEFT, fill=BOTH, expand=1)

        scrollbar= tk.Scrollbar(frame_self, orient=VERTICAL, command=self.canvas_insertmany.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas_insertmany.configure(yscrollcommand=scrollbar.set)
        self.canvas_insertmany.bind('<Configure>', lambda e: self.canvas_insertmany.configure(scrollregion = self.canvas_insertmany.bbox("all")))

        self.frame_two = Frame(self.canvas_insertmany)
        self.canvas_insertmany.create_window((0,0), window=self.frame_two , anchor="nw")

        label = tk.Label(self.frame_two, text="Insert valid JSON document")
        first_entry = tk.Text(self.frame_two, borderwidth=5, height= 10, width=20)
        
        self.inputlist.append(label)
        self.inputlist.append(first_entry)
        self.newinputlist.append(first_entry)

        for widgets in range(len(self.inputlist)):
            self.inputlist[widgets].grid(row=widgets, column=0, padx=50, pady=10)

        add_button = tk.Button(self.frame_two, text="ADD INSERT", command=self.add_insert).grid(row=1, column=2, pady=(0,100))
        submit_button = tk.Button(self.frame_two, text="SUBMIT",command=self.submit_data)
        submit_button.grid(row=1, column=2, pady=(0,25))
        insertmany_button = tk.Button(self.frame_two, text="INSERT ONE", command=lambda: controller.current_frame("CreatePage_InsertOne")).grid(row=1, column=2, pady=(50,0))
        back_button = tk.Button(self.frame_two, text="BACK", command=lambda: controller.current_frame("CreatePage_Main")).grid(row=1, column=2, pady=(125,0))

    def add_insert(self):
        newtextbox = tk.Text(self.frame_two, borderwidth=5, height= 10, width=20)
        self.inputlist.append(newtextbox)
        self.newinputlist.append(newtextbox)

        for ndex, widget in enumerate(self.inputlist):
            widget.grid(row=ndex, column=0)

        self.update_idletasks()
        self.canvas_insertmany.configure(scrollregion = self.canvas_insertmany.bbox('all'))

    def submit_data(self):
        try:
            for textbox in self.newinputlist:
                submit_product = Pages.coldatabase.insert_one( json.loads(str(textbox.get("1.0", END) ) ) )

            messagebox.showinfo("MongoDB Document Submission", "Your document has been added to the database.")

            self.update_idletasks()
            self.canvas_insertmany.configure(scrollregion = self.canvas_insertmany.bbox('all'))

            self.controller.reload_frame(CreatePage_InsertMany) 

        except:
            messagebox.showerror("Error", "An Error has occured. Please make sure your inputs are valid.")


class ReadPage(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.searchbox_field = tk.Entry(self, borderwidth=5, width=25)
        self.searchbox_field.insert(0, "<Enter a field>")
        self.searchbox_field.grid(row=0, column=1, padx=(25), pady=(0, 325))

        self.searchbox_query = tk.Entry(self, borderwidth=5, width=25)
        self.searchbox_query.insert(0, "<Enter a query>")
        self.searchbox_query.grid(row=0, column=1, padx=(25), pady=(0, 265))

        searchbutton = tk.Button(self, text="SEARCH", command=self.query)
        searchbutton.grid(row=0, column=1, padx=25, pady=(0, 205))

        advsearchbutton = tk.Button(self, text="ADVANCED\nSEARCH", command=self.advanced_search_window)
        advsearchbutton.grid(row=0, column=1, padx=25, pady=(0, 105))

        back_button = tk.Button(self, text="BACK", command=lambda: controller.reload_frame(MainPage))
        back_button.grid(row=0, column=1, padx=25, pady=(0, 25))

        self.generate_sb()

    def generate_sb(self):
        frame_canvas = tk.Frame(self)
        frame_canvas.grid(row=0, column=0, padx=(10,0), pady=10)

        self.canvas = tk.Canvas(frame_canvas)
        self.canvas.grid(row=0, column=0, sticky="news")

        vertical_sb = tk.Scrollbar(frame_canvas, orient="vertical", command=self.canvas.yview)
        vertical_sb.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=vertical_sb.set)

        self.frame_listbox = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_listbox, anchor="nw")

        self.itemlist = tk.Listbox(self.frame_listbox, width=63)
        self.itemlist.grid(row=0, column=0)

        horizontal_sb = tk.Scrollbar(frame_canvas, orient="horizontal", command=self.canvas.xview)
        horizontal_sb.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=horizontal_sb.set)

    def query(self):
        field_input = self.searchbox_field.get()
        query_input = self.searchbox_query.get()

        if query_input == "<Enter a query>":
            query_input = ""

        if field_input == "<Enter a field>":
            messagebox.showerror("Error", "Select a valid field")

        try:
            self.resetlistbox()

            query_return = Pages.coldatabase.find( { field_input: { "$regex": '.*' + query_input + '.*'} } )

            for document in query_return:
                self.itemlist.insert(END, document)

            self.frame_listbox.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

        except:
            messagebox.showerror("Error", "An error has occurred with the query. Review your input.")

    def advanced_search_window(self):
        self.queryWindow = Toplevel(self)
        self.queryWindow.title("Write Custom Query")

        self.queryWindow.wait_visibility()
        self.queryWindow.grab_set()

        self.custom_query = tk.Text(self.queryWindow, borderwidth=5, height= 10, width=30)
        self.custom_query.grid(row=0, column=0, padx=50, pady=(20, 0))

        submit_query = tk.Button(self.queryWindow, text="SUBMIT", command=self.advanced_search)
        submit_query.grid(row=1, column=0, pady=20)

    def advanced_search(self):
        try:
            self.resetlistbox()

            find_product = Pages.coldatabase.find( json.loads(str(self.custom_query.get("1.0", END) ) ) )
            for document in find_product:
                self.itemlist.insert(END, document)

            self.queryWindow.grab_release()
            self.queryWindow.destroy()

            self.frame_listbox.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

        except:
            messagebox.showerror("Error", "An Error has occured. Please make sure your inputs are valid.")

    def resetlistbox(self):
        if self.itemlist.size() != 0:
            for i in range(self.itemlist.size()):
                self.itemlist.delete(0, END)

class DeletePage(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label_entry1 = tk.Label(self, text="Select Field").grid(row=0, column=0, padx=25, pady=(25,0))
        label_entry2 = tk.Label(self, text="Select Value").grid(row=0, column=1, padx=25, pady=(25,0))

        entry1 = tk.Entry(self, borderwidth=5).grid(row=1, column=0, padx=25, pady=5)
        entry2 = tk.Entry(self, borderwidth=5).grid(row=1, column=1, padx=25, pady=5)

        label_button_one = tk.Label(self, text="Delete first matching document").grid(row=2, column=0, padx=25, pady=5)
        label_button_two = tk.Label(self, text="Delete all matching documents").grid(row=2, column=1, padx=25, pady=5)

        button_delete_one = tk.Button(self, text="DELETE ONE", command=self.delete_one).grid(row=3, column=0, padx=25, pady=5)
        button_delete_two = tk.Button(self, text="DELETE MANY", command=self.delete_many).grid(row=3, column=1, padx=25, pady=5)
        button_delete_collection = tk.Button(self, text="DELETE COLLECTION", command=self.delete_collection).grid(row=4, column=0, padx=25, pady=5)
        back_button = tk.Button(self, text="BACK", command=lambda: controller.reload_frame(MainPage)).grid(row=4, column=1, padx=25, pady=5)

        label_delete_collection = tk.Label(self, text="Note! Pressing this button \n will delete current collection").grid(row=5, column=0, padx=25, pady=(0,25))

    def delete_one(self):
        mycol = Pages.coldatabase
        print(mycol)

    def delete_many(self):
        mycol = Pages.coldatabase
        print(mycol)

    def delete_collection(self):
        mycol = Pages.coldatabase
        print(mycol)
        self.controller.reload_frame(SelectDatabase)



if __name__ == "__main__":
    NoSQL_Project = Database_Project()
    NoSQL_Project.title("NoSQL Database Project")
    NoSQL_Project.maxsize(0, 500)
    NoSQL_Project.mainloop()