import sqlite3
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import os
import datetime

class TicketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CR TICKETS")

        # Crear un objeto de estilo temático
        self.style = ThemedStyle(root)
        # Establecer el tema (puedes cambiar 'clam' a otros temas disponibles)
        self.style.set_theme("clam")

        # Determina el entorno (producción o desarrollo)
        environment = os.environ.get("TICKET_APP_ENVIRONMENT", "production")

        if environment == "production":
            # PATH para entorno de producción
            db_path = os.path.abspath("TICKETS/ittickets.db")
        else:
            # PATH para entorno de desarrollo
            shared_folder = r"\\Provicionalserv\tickets"  # Reemplaza con la ruta real de tu carpeta compartida
            db_filename = "ittickets.db"
            db_path = os.path.join(shared_folder, db_filename)

        # Imprime la ruta para verificar que sea la correcta
        print("Ruta de la base de datos:", db_path)

        try:
            # Intenta abrir la conexión a la base de datos
            self.conn = sqlite3.connect(db_path)
            print("Conexión a la base de datos exitosa.")
        except sqlite3.Error as e:
            # Captura y muestra cualquier error que ocurra al intentar abrir la conexión
            print("Error al abrir la base de datos:", e)

        # Variables para Entry y ID del ticket seleccionado
        self.ticket_id_var = tk.StringVar()
        self.fecha_var = tk.StringVar()
        self.categoria_var = tk.StringVar()
        self.posicion_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        self.impacto_var = tk.StringVar()

        self.impacto_combobox_var = tk.StringVar()

        # Variable para filtro de prioridad
        self.prioridad_var = tk.StringVar()
        self.prioridad_var.set("Todas")  # Inicializar la variable con "Todas"

        # Crear formulario
        self.create_form()

        # Treeview para mostrar tickets
        self.create_treeview()

        # Actualizar la aplicación cada minuto
        self.root.after(60000, self.update_tickets)

    def create_form(self):
        form_frame = ttk.LabelFrame(self.root, text="Nuevo Ticket")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Obtener la fecha actual (sin horas, minutos ni segundos)
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")

        # Variable de control para el Combobox de categoría
        self.categoria_combobox_var = tk.StringVar()

        entries = [
            ("Fecha:", tk.Entry(form_frame, textvariable=self.fecha_var)),
            ("Categoría:", ttk.Combobox(form_frame, textvariable=self.categoria_combobox_var, values=["Hardware", "Software", "Network"])),
            ("Posición:", tk.Entry(form_frame, textvariable=self.posicion_var)),
            ("Descripción:", tk.Entry(form_frame, textvariable=self.descripcion_var)),
            ("Prioridad:", ttk.Combobox(form_frame, textvariable=self.impacto_combobox_var, values=["Baja", "Media", "Alta", "Urgente"])),
        ]

        # Establecer la fecha actual en el Entry de fecha
        entries[0][1].insert(0, fecha_actual)

        for row, (label, entry) in enumerate(entries):
            ttk.Label(form_frame, text=label).grid(
                row=row, column=0, padx=5, pady=5, sticky="e"
            )
            entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(form_frame, text="Agregar Ticket", command=self.add_ticket).grid(
            row=len(entries), column=0, columnspan=2, pady=10
        )

        # Botón para actualizar ticket seleccionado
        ttk.Button(
            form_frame, text="Actualizar Ticket", command=self.update_ticket
        ).grid(row=len(entries) + 1, column=0, columnspan=2, pady=10)

        # Menú desplegable para filtrar por prioridad
        prioridades = ["Todas", "Baja", "Media", "Alta", "Urgente"]
        ttk.Label(form_frame, text="Filtrar por Prioridad:").grid(
            row=len(entries) + 2, column=0, padx=5, pady=5, sticky="e"
        )
        ttk.Combobox(
            form_frame, textvariable=self.prioridad_var, values=prioridades
        ).grid(row=len(entries) + 2, column=1, padx=5, pady=5, sticky="ew")

    def create_treeview(self):
        tree_frame = ttk.LabelFrame(self.root, text="Tickets")
        tree_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        columns = ("ID", "Fecha", "Categoría", "Posición", "Descripción", "Impacto")
        self.treeview = ttk.Treeview(
            tree_frame, columns=columns, show="headings", selectmode="browse"
        )

        for col in columns:
            self.treeview.heading(col, text=col)
            self.treeview.column(col, width=100, anchor="center")

        self.treeview.grid(row=0, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        ttk.Button(tree_frame, text="Eliminar Ticket", command=self.delete_ticket).grid(
            row=1, column=0, pady=10
        )

        # Configurar evento de clic en el Treeview
        self.treeview.bind("<ButtonRelease-1>", self.select_ticket)

        self.update_tickets()

    def add_ticket(self):
        # Obtener los valores de las variables
        fecha = self.fecha_var.get()
        categoria = self.categoria_combobox_var.get()  # Corregir aquí
        posicion = self.posicion_var.get()
        descripcion = self.descripcion_var.get()
        impacto = self.impacto_combobox_var.get()  # Corregir aquí

        # Insertar el ticket en la base de datos
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO tickets (fecha, categoria, posicion, descripcion, impacto)
            VALUES (?, ?, ?, ?, ?)
        """,
            (fecha, categoria, posicion, descripcion, impacto),
        )
        self.conn.commit()
        self.update_tickets()

        # Limpiar campos después de agregar un ticket
        self.clear_fields()

    def update_ticket(self):
        # Obtener los valores de las variables
        ticket_id = self.ticket_id_var.get()
        fecha = self.fecha_var.get()
        categoria = self.categoria_combobox_var.get()  # Corregir aquí
        posicion = self.posicion_var.get()
        descripcion = self.descripcion_var.get()
        impacto = self.impacto_combobox_var.get()  # Corregir aquí

        # Actualizar el ticket en la base de datos
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE tickets
            SET fecha=?, categoria=?, posicion=?, descripcion=?, impacto=?
            WHERE id=?
        """,
            (fecha, categoria, posicion, descripcion, impacto, ticket_id),
        )
        self.conn.commit()
        self.update_tickets()

        # Limpiar campos después de actualizar un ticket
        self.clear_fields()

    def delete_ticket(self):
        selected_item = self.treeview.selection()
        if selected_item:
            ticket_id = self.treeview.item(selected_item, "values")[0]
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
            self.conn.commit()
            self.update_tickets()

    def select_ticket(self, event):
        selected_item = self.treeview.selection()
        if selected_item:
            ticket_values = self.treeview.item(selected_item, "values")
            self.ticket_id_var.set(ticket_values[0])
            self.fecha_var.set(ticket_values[1])
            self.categoria_combobox_var.set(ticket_values[2])  # Corregir aquí
            self.posicion_var.set(ticket_values[3])
            self.descripcion_var.set(ticket_values[4])
            self.impacto_combobox_var.set(ticket_values[5])  # Corregir aquí

    def clear_fields(self):
        self.ticket_id_var.set("")
        self.fecha_var.set("")
        self.categoria_combobox_var.set("")  # Corregir aquí
        self.posicion_var.set("")
        self.descripcion_var.set("")
        self.impacto_combobox_var.set("")  # Corregir aquí

    def update_tickets(self):
        cursor = self.conn.cursor()

        # Obtener la prioridad seleccionada
        prioridad = self.prioridad_var.get()

        if prioridad == "Todas":
            cursor.execute("SELECT * FROM tickets ORDER BY impacto DESC")
        else:
            cursor.execute(
                "SELECT * FROM tickets WHERE impacto = ? ORDER BY impacto DESC",
                (prioridad,),
            )

        tickets = cursor.fetchall()

        # Limpiar Treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Actualizar Treeview
        for ticket in tickets:
            self.treeview.insert("", "end", values=ticket)

        # Programar la próxima actualización después de 1 minuto
        self.root.after(60000, self.update_tickets)

if __name__ == "__main__":
    root = tk.Tk()
    app = TicketApp(root)
    root.mainloop()
