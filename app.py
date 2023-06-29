from tkinter import *
from tkinter import ttk
import sqlite3

class Producto:
    db = "database/productos.db"  # Ruta BBDD

    def __init__(self, root):
        self.ventana = root
        self.ventana.title("App Gestor de Productos")
        self.ventana.resizable(1, 1)  # Atributo que permite redimensionar el tamaño de la interfaz

        # Creación del contenedor Frame Principal
        # Creamos la variable frame. Le indicamos que debe ejecutarse en la ventana principal
        frame = LabelFrame(self.ventana, text="Registrar un nuevo Producto")
        frame.grid(row=0, column=0, columnspan=4, pady=20)

        # Label + Entry Nombre
        self.etiqueta_nombre = Label(frame, text="Nombre:")
        self.etiqueta_nombre.grid(row=0, column=0, sticky=W)
        self.nombre = Entry(frame)
        self.nombre.focus()
        self.nombre.grid(row=0, column=1)

        # Label + Entry Precio
        self.etiqueta_precio = Label(frame, text="Precio:")
        self.etiqueta_precio.grid(row=1, column=0, sticky=W)
        self.precio = Entry(frame)
        self.precio.grid(row=1, column=1)

        # Label + Entry Categoria
        self.etiqueta_categoria = Label(frame, text="Categoría:")
        self.etiqueta_categoria.grid(row=0, column=2, sticky=W)
        self.categoria = Entry(frame)
        self.categoria.grid(row=0, column=3)

        # Label + Entry Stock
        self.etiqueta_stock = Label(frame, text="Stock:")
        self.etiqueta_stock.grid(row=1, column=2, sticky=W)
        self.stock = Entry(frame)
        self.stock.grid(row=1, column=3)

        # Boton de Agregar un Producto
        self.boton_agregar = ttk.Button(frame, text="Guardar Producto", command=self.add_producto)
        self.boton_agregar.grid(row=2, columnspan=4, pady=10)

        # Mensaje informativo para el usuario. fr pone el texto en rojo
        self.mensaje = Label(text="", fg="red")
        self.mensaje.grid(row=3, column=0, columnspan=4)

        # Tabla Treeview
        # Se modifica la fuente de las cabeceras y se eliminan los bordes
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=("Calibri", 11))
        style.configure("mystyle.Treeview.Heading", font=("Calibri", 13, "bold"))
        style.layout("mystyle.Treeview", [("mystyle.Treeview.treearea", {"sticky": "nswe"})])

        # Estructura de la tabla
        self.tabla = ttk.Treeview(self.ventana, height=20, columns=("Nombre", "Precio", "Categoría", "Stock"), style="mystyle.Treeview")
        self.tabla.grid(row=4, column=0, columnspan=4, pady=10)

        # Creamos la cabecera de la Tabla
        self.tabla.heading("#0", text="ID", anchor=CENTER)
        self.tabla.column("#0", width=50, anchor=CENTER)
        self.tabla.heading("Nombre", text="Nombre", anchor=CENTER)
        self.tabla.heading("Precio", text="Precio", anchor=CENTER)
        self.tabla.heading("Categoría", text="Categoría", anchor=CENTER)
        self.tabla.heading("Stock", text="Stock", anchor=CENTER)

        # Creamos Botón para eliminar
        self.boton_eliminar = ttk.Button(text="Eliminar", command=self.eliminar_producto)
        self.boton_eliminar.grid(row=5, column=0, pady=10)

        # Creamos Botón para editar
        self.boton_editar = ttk.Button(text="Editar", command=self.editar_producto)
        self.boton_editar.grid(row=5, column=1, pady=10)

        # llamada al Método get_productos() para obtener el listado de productos al iniciar la app
        self.get_productos()

    def db_consulta(self, query, parametros=()):
        # Método que conecta con la BBDD mediante SQLlite3
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            resultado = cursor.execute(query, parametros)
            conn.commit()
        return resultado

    def get_productos(self):
        # Método que retorna un listado de los productos dentro de BBDD
        registros_db = self.db_consulta("SELECT * FROM producto ORDER BY nombre DESC")
        self.tabla.delete(*self.tabla.get_children())
        for fila in registros_db:
            self.tabla.insert("", 0, text=fila[0], values=(fila[1], fila[2], fila[3], fila[4]))

    def add_producto(self):
        # Método que permite añadir nuevos valores a la BD. Indexado con el botón Guardar Producto de la app gráfica
        # Cada campo hace referencia a una de las 4 columnas que compone la BD.

        # Obtenemos los valores que componen estas 4 variables
        nombre = self.nombre.get()
        precio = self.precio.get()
        categoria = self.categoria.get()
        stock = self.stock.get()

        # Verificamos que ningún campo esté vacío ya que en la BD los valores son notnull
        if nombre == '' or precio == '' or categoria == '' or stock == '':
            self.mensaje["text"] = "Todos los campos son requeridos"
            return

        # Generamos la consulta a BD para insertar los nuevos datos
        # self.nombre.delete, borramos el valor en la etiqueta para dejarla limpia y poder introducid más datos
        query = "INSERT INTO producto (nombre, precio, categoria, stock) VALUES (?, ?, ?, ?)"
        self.db_consulta(query, (nombre, precio, categoria, stock))
        self.mensaje["text"] = "Producto agregado correctamente"
        self.nombre.delete(0, END)
        self.precio.delete(0, END)
        self.categoria.delete(0, END)
        self.stock.delete(0, END)
        self.get_productos()

    def eliminar_producto(self):
        # Método que permite Eliminar un producto - Indexado con el botón Eliminar de la app gráfica
        seleccionado = self.tabla.focus()
        datos = self.tabla.item(seleccionado)
        producto_id = datos["text"]

        # Generamos la consulta a BD para eliminar los datos
        query = "DELETE FROM producto WHERE id = ?"
        self.db_consulta(query, (producto_id,))
        self.mensaje["text"] = "Producto eliminado correctamente"
        self.get_productos()

    def editar_producto(self):
        # Método que permite modificar los valores de un producto
        seleccionado = self.tabla.focus()
        datos = self.tabla.item(seleccionado)
        producto_id = datos["text"]

        # Creamos una nueva ventana en la interfaz gráfica
        self.ventana_editar = Toplevel()
        self.ventana_editar.title("Editar Producto")

        # Generamos la consulta a BD para recoger los datos
        query = "SELECT * FROM producto WHERE id = ?"
        resultado = self.db_consulta(query, (producto_id,))
        producto = resultado.fetchone()

        # Creamos Label y Entry de Nombre dentro de ventana_editar
        self.etiqueta_nombre = Label(self.ventana_editar, text="Nombre:")
        self.etiqueta_nombre.grid(row=0, column=0, sticky=W)
        self.nombre_editar = Entry(self.ventana_editar)
        self.nombre_editar.insert(0, producto[1])
        self.nombre_editar.focus()
        self.nombre_editar.grid(row=0, column=1)

        # Creamos Label y Entry de Nombre dentro de ventana_editar
        self.etiqueta_precio = Label(self.ventana_editar, text="Precio:")
        self.etiqueta_precio.grid(row=1, column=0, sticky=W)
        self.precio_editar = Entry(self.ventana_editar)
        self.precio_editar.insert(0, producto[2])
        self.precio_editar.grid(row=1, column=1)

        # Creamos Label y Entry de Nombre dentro de ventana_editar
        self.etiqueta_categoria = Label(self.ventana_editar, text="Categoría:")
        self.etiqueta_categoria.grid(row=2, column=0, sticky=W)
        self.categoria_editar = Entry(self.ventana_editar)
        self.categoria_editar.insert(0, producto[3])
        self.categoria_editar.grid(row=2, column=1)

        # Creamos Label y Entry de Nombre dentro de ventana_editar
        self.etiqueta_stock = Label(self.ventana_editar, text="Stock:")
        self.etiqueta_stock.grid(row=3, column=0, sticky=W)
        self.stock_editar = Entry(self.ventana_editar)
        self.stock_editar.insert(0, producto[4])
        self.stock_editar.grid(row=3, column=1)

        # Creamos el boton guardar dentro de la ventana_editar
        self.boton_guardar = ttk.Button(self.ventana_editar, text="Guardar Cambios", command=lambda: self.guardar_cambios(producto_id))
        self.boton_guardar.grid(row=4, columnspan=2, pady=10)

    def guardar_cambios(self, producto_id):
        # Método que guarda los cambios - indexado con el botón guardar de ventana_editar
        nombre = self.nombre_editar.get()
        precio = self.precio_editar.get()
        categoria = self.categoria_editar.get()
        stock = self.stock_editar.get()

        # Generamos la consulta a BD para recoger los datos
        query = "UPDATE producto SET nombre = ?, precio = ?, categoria = ?, stock = ? WHERE id = ?"
        self.db_consulta(query, (nombre, precio, categoria, stock, producto_id))
        self.mensaje["text"] = "Cambios guardados correctamente"
        self.ventana_editar.destroy()
        self.get_productos() # Ejecutamos este método para que la lista de elementos de la app gráfica se actualice

if __name__ == "__main__":
    root = Tk()  # Crea una instancia de la ventana principal de la app
    app = Producto(root)  # Creo el objeto de la clase Producto y le paso la ventana gráfica
    root.iconphoto(False, PhotoImage(
        file="/Users/carlos/Documents/PyCharm/M6_Tkinter/recursos/terminal.png"))  # Añade un icono a la ventana gráfica
    root.mainloop()  # Mantiene la ventana gráfica de la app abierta
