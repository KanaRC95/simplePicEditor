import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Imagenes")
        
        self.original_image = None
        self.modified_image = None
        self.history = []
        self.redo_stack = []
        self.path = ''
        
        self.create_widgets()
        self.isBg = False
        self.load_background_image('bg.png')
        
    def create_widgets(self):
        frame = Frame(self.root)
        frame.pack(fill=X, side=TOP)
	
	
	
        self.canvas_frame = Frame(self.root)
        self.canvas_frame.pack(fill=BOTH, expand=YES)
        
        self.canvas = Canvas(self.canvas_frame, bg='white',width=540, height=540, scrollregion=(0, 0, 530, 530))
        self.hbar = Scrollbar(self.canvas_frame, orient=HORIZONTAL, command=self.canvas.xview)
        self.hbar.pack(side=BOTTOM, fill=X)
        self.vbar = Scrollbar(self.canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        self.vbar.pack(side=RIGHT, fill=Y)
        
        
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        
        
        
        btn_open = Button(frame, text="Abrir", command=self.open_image)
        btn_open.pack(side=LEFT)
        
        btn_save = Button(frame, text="Guardar", command=self.save_image)
        btn_save.pack(side=LEFT)
        
        edit_menu = Menubutton(frame, text="Editar", relief=RAISED)
        self.edit_menu = Menu(edit_menu, tearoff=0)
        edit_menu.config(menu=self.edit_menu)
        self.edit_menu.add_command(label="Mover", command=self.show_input_dialog('move'))
        self.edit_menu.add_command(label="Rotar", command=self.show_input_dialog('rotate'))
        self.edit_menu.add_command(label="Redimensionar", command=self.show_input_dialog('resize'))
        self.edit_menu.add_command(label="Espejo", command=self.mirror_image)
        self.edit_menu.add_command(label="Recortar", command=self.show_input_dialog('crop'))
        edit_menu.pack(side=LEFT)
        
        btn_undo = Button(frame, text="Deshacer", command=self.undo)
        btn_undo.pack(side=LEFT)
        
        btn_redo = Button(frame, text="Rehacer", command=self.redo)
        btn_redo.pack(side=LEFT)
        
        btn_view_original = Button(frame, text="Ver Original", command=self.view_original)
        btn_view_original.pack(side=LEFT)
        
       	btn_details = Button(frame, text="Detalles", command=self.show_details)
        btn_details.pack(side=LEFT)
        
        
    def load_background_image(self, file_path):
        if file_path:
            self.original_image = cv2.imread(file_path)
            self.modified_image = self.original_image.copy()
            self.history = [self.modified_image.copy()]
            self.redo_stack = []
            self.show_image()
    
    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_image = cv2.imread(file_path)
            self.modified_image = self.original_image.copy()
            self.history = [self.modified_image.copy()]
            self.redo_stack = []
            self.isBg = False
            self.path = file_path
            self.show_image()
    
    def save_image(self):
        if self.modified_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                     filetypes=[("JPEG files", "*.jpg"),
                                                                ("PNG files", "*.png"),
                                                                ("All files", "*.*")])
            if file_path:
                cv2.imwrite(file_path, self.modified_image)
        else:
            messagebox.showerror("Error", "Ninguna imagen para guardar")
    
    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.modified_image = self.history[-1].copy()
            self.show_image()
        else:
            messagebox.showwarning("Advertencia", "No hay mas acciones para deshacer")
    
    def redo(self):
        if self.redo_stack:
            self.history.append(self.redo_stack.pop())
            self.modified_image = self.history[-1].copy()
            self.show_image()
        else:
            messagebox.showwarning("Advertencia", "No hay mas accionar para rehacer")
    
    def show_input_dialog(self, action):
        def handler():
            self.dialog_window = Toplevel(self.root)
            self.dialog_window.title("Ingrese los parametros")

            if action == 'move':
                Label(self.dialog_window, text="Coordenadas (x):").grid(row=0, column=0)
                self.dx_entry = Entry(self.dialog_window)
                self.dx_entry.grid(row=0, column=1)
                
                Label(self.dialog_window, text="Coordenadas (y):").grid(row=1, column=0)
                self.dy_entry = Entry(self.dialog_window)
                self.dy_entry.grid(row=1, column=1)
                
                Button(self.dialog_window, text="Aplicar", command=self.apply_move).grid(row=2, columnspan=2)
            
            elif action == 'rotate':
                Label(self.dialog_window, text="Angulo:").grid(row=0, column=0)
                self.angle_entry = Entry(self.dialog_window)
                self.angle_entry.grid(row=0, column=1)
                
                Button(self.dialog_window, text="Aplicar", command=self.apply_rotate).grid(row=1, columnspan=2)
            
            elif action == 'resize':
                Label(self.dialog_window, text="Anchura:").grid(row=0, column=0)
                self.width_entry = Entry(self.dialog_window)
                self.width_entry.grid(row=0, column=1)
                
                Label(self.dialog_window, text="Altura:").grid(row=1, column=0)
                self.height_entry = Entry(self.dialog_window)
                self.height_entry.grid(row=1, column=1)

                self.aspect_var = IntVar()
                Checkbutton(self.dialog_window, text="Mantener Rel. Aspecto", variable=self.aspect_var).grid(row=2, columnspan=2)
                
                Button(self.dialog_window, text="Apply", command=self.apply_resize).grid(row=3, columnspan=2)
            
            
            elif action == 'crop':
                Label(self.dialog_window, text="Punto 1 (x):").grid(row=0, column=0)
                self.x1_entry = Entry(self.dialog_window)
                self.x1_entry.grid(row=0, column=1)
                
                Label(self.dialog_window, text="Punto 1 (y):").grid(row=1, column=0)
                self.y1_entry = Entry(self.dialog_window)
                self.y1_entry.grid(row=1, column=1)
                
                Label(self.dialog_window, text="Punto 2 (x):").grid(row=2, column=0)
                self.x2_entry = Entry(self.dialog_window)
                self.x2_entry.grid(row=2, column=1)
                
                Label(self.dialog_window, text="Punto 2 (y):").grid(row=3, column=0)
                self.y2_entry = Entry(self.dialog_window)
                self.y2_entry.grid(row=3, column=1)
                
                Button(self.dialog_window, text="Aplicar", command=self.apply_crop).grid(row=4, columnspan=2)
            
            self.dialog_window.transient(self.root)
            self.dialog_window.grab_set()
            self.root.wait_window(self.dialog_window)
        return handler
    
    def apply_move(self):
        dx = int(self.dx_entry.get())
        dy = int(self.dy_entry.get())
        rows, cols, _ = self.modified_image.shape
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        self.modified_image = cv2.warpAffine(self.modified_image, M, (cols, rows))
        self.update_history()
        self.show_image()
        self.dialog_window.destroy()
    
    def apply_rotate(self):
        angle = float(self.angle_entry.get())
        rows, cols, _ = self.modified_image.shape
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
        self.modified_image = cv2.warpAffine(self.modified_image, M, (cols, rows))
        self.update_history()
        self.show_image()
        self.dialog_window.destroy()
    
    """
    def apply_resize(self):
        scale = float(self.scale_entry.get())
        new_size = (int(self.modified_image.shape[1] * scale), int(self.modified_image.shape[0] * scale))
        self.modified_image = cv2.resize(self.modified_image, new_size)
        self.update_history()
        self.show_image()
        self.dialog_window.destroy()
    """
    def apply_resize(self):
        width = int(self.width_entry.get())
        height = int(self.height_entry.get())
        if self.aspect_var.get() == 1:  # Maintain aspect ratio
            aspect_ratio = self.modified_image.shape[1] / self.modified_image.shape[0]
            if width / height > aspect_ratio:
                width = int(height * aspect_ratio)
            else:
                height = int(width / aspect_ratio)
        self.modified_image = cv2.resize(self.modified_image, (width, height))
        self.update_history()
        self.show_image()
        self.dialog_window.destroy()

    def apply_crop(self):
        x1 = int(self.x1_entry.get())
        y1 = int(self.y1_entry.get())
        x2 = int(self.x2_entry.get())
        y2 = int(self.y2_entry.get())
        self.modified_image = self.modified_image[y1:y2, x1:x2]
        self.update_history()
        self.show_image()
        self.dialog_window.destroy()
    
    def mirror_image(self):
        if self.modified_image is not None:
            self.modified_image = cv2.flip(self.modified_image, 1)
            self.update_history()
            self.show_image()
    
    def update_history(self):
        self.history.append(self.modified_image.copy())
        self.redo_stack = []
    
    def show_image(self):
        if self.modified_image is not None:
            img = cv2.cvtColor(self.modified_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            #self.canvas.create_image(0, 0, anchor=NW, image=imgtk)
            #self.canvas.image = imgtk
            if self.isBg == True:
                self.canvas.config(scrollregion=(0, 0, imgtk.width(), imgtk.height()))
                self.canvas.create_image(365, 270, anchor=CENTER, image=imgtk)
                self.canvas.image = imgtk
                
            else:
                self.canvas.config(scrollregion=(0, 0, imgtk.width(), imgtk.height()))
                self.canvas.create_image(0, 0, anchor=NW, image=imgtk)
                self.canvas.image = imgtk
                
    def view_original(self):
       if self.original_image is not None and self.path != '':
           new_window = Toplevel(self.root)
           new_window.title("Original Image")
           
           canvas = Canvas(new_window, bg='gray')
           hbar = Scrollbar(new_window, orient=HORIZONTAL, command=canvas.xview)
           hbar.pack(side=BOTTOM, fill=X)
           vbar = Scrollbar(new_window, orient=VERTICAL, command=canvas.yview)
           vbar.pack(side=RIGHT, fill=Y)

           canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
           canvas.pack(fill=BOTH, expand=YES)

           b, g, r = cv2.split(self.original_image)
           img = cv2.merge((r, g, b))
           im = Image.fromarray(img)
           imgtk = ImageTk.PhotoImage(image=im)
           canvas.config(scrollregion=(0, 0, imgtk.width(), imgtk.height()))
           canvas.create_image(0, 0, anchor=NW, image=imgtk)
           canvas.image = imgtk
       else:
            messagebox.showwarning("Advertencia", "No hay ninguna imagen cargada")

    def show_details(self):
        if self.modified_image is not None and self.path != '':
            height, width, channels = self.modified_image.shape
            size_in_bytes = os.path.getsize(self.path)
            size_in_mb = size_in_bytes / (1024 * 1024)
            details = (
                f"Anchura: {width} pixels\n"
                f"Altura: {height} pixels\n"
                f"Canales: {channels}\n"
                f"Tamaño: {size_in_mb:.2f} MB"
            )
            messagebox.showinfo("Detalles de la imagen", details)
        else:
            messagebox.showwarning("Advertencia", "No hay ninguna imagen cargada")
if __name__ == "__main__":
    root = Tk()
    editor = ImageEditor(root)
    root.mainloop()
