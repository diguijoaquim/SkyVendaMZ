import socket
import threading
import os
import json
from tkinter import *
from tkinter import ttk, filedialog, simpledialog, scrolledtext
from tkinter.font import Font

# Configurações globais
PORT = 5000
UPLOAD_FOLDER = 'upload'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Cores e estilos
COLORS = {
    'primary': '#2196F3',
    'secondary': '#E3F2FD',
    'background': '#FFFFFF',
    'text': '#333333',
    'success': '#4CAF50',
    'accent': '#FFC107',
    'selected': '#90CAF9'
}

class MessagingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat & File Sharing")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS['background'])
        
        # Configurar estilos
        self.configure_styles()
        
        # Inicializar variáveis
        self.connected_devices = {}
        self.client = None
        self.selected_device = None
        self.username = self.get_username()
        
        # Criar interface
        self.create_interface()
        
    def configure_styles(self):
        # Configurar fonte
        self.default_font = Font(family="Helvetica", size=10)
        self.title_font = Font(family="Helvetica", size=12, weight="bold")
        
        # Configurar estilos do ttk
        style = ttk.Style()
        style.configure("Primary.TButton",
                       background=COLORS['primary'],
                       foreground="white",
                       padding=10,
                       font=self.default_font)
        
        style.configure("Secondary.TButton",
                       background=COLORS['secondary'],
                       padding=8,
                       font=self.default_font)
                       
    def get_username(self):
        username = simpledialog.askstring(
            "Bem-vindo!",
            "Digite seu nome de usuário:",
            parent=self.root
        )
        return username if username else f"Usuário-{socket.gethostbyname(socket.gethostname())}"
        
    def create_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Área de mensagens
        messages_frame = ttk.LabelFrame(main_frame, text="Mensagens", padding="5")
        messages_frame.grid(row=0, column=0, columnspan=2, sticky=(N, W, E, S), pady=5)
        
        self.chat_area = scrolledtext.ScrolledText(
            messages_frame,
            wrap=WORD,
            width=50,
            height=20,
            font=self.default_font,
            bg=COLORS['background']
        )
        self.chat_area.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Frame para lista de dispositivos
        devices_frame = ttk.LabelFrame(main_frame, text="Dispositivos Conectados", padding="5")
        devices_frame.grid(row=0, column=2, sticky=(N, W, E, S), pady=5, padx=5)
        
        # Lista de dispositivos com barra de rolagem
        devices_list_frame = ttk.Frame(devices_frame)
        devices_list_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.device_list = Listbox(
            devices_list_frame,
            font=self.default_font,
            selectmode=SINGLE,
            bg=COLORS['background'],
            highlightthickness=1,
            activestyle='dotbox',
            selectbackground=COLORS['selected']
        )
        self.device_list.pack(fill=BOTH, expand=True, side=LEFT)
        
        # Barra de rolagem para lista de dispositivos
        devices_scrollbar = ttk.Scrollbar(devices_list_frame, orient=VERTICAL, command=self.device_list.yview)
        devices_scrollbar.pack(side=RIGHT, fill=Y)
        self.device_list.config(yscrollcommand=devices_scrollbar.set)
        
        # Botão de atualizar lista
        ttk.Button(
            devices_frame,
            text="Atualizar Lista",
            style="Secondary.TButton",
            command=self.refresh_device_list
        ).pack(fill=X, padx=5, pady=5)
        
        # Label para mostrar dispositivo selecionado
        self.selected_device_label = ttk.Label(
            devices_frame,
            text="Nenhum dispositivo selecionado",
            font=self.default_font,
            wraplength=200
        )
        self.selected_device_label.pack(fill=X, padx=5, pady=5)
        
        # Frame para entrada de mensagem
        input_frame = ttk.Frame(main_frame, padding="5")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(W, E), pady=5)
        
        self.message_entry = ttk.Entry(
            input_frame,
            font=self.default_font
        )
        self.message_entry.insert(0, "Digite sua mensagem...")
        self.message_entry.bind('<FocusIn>', lambda e: self.on_entry_click(e, "Digite sua mensagem..."))
        self.message_entry.bind('<FocusOut>', lambda e: self.on_focus_out(e, "Digite sua mensagem..."))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        self.message_entry.pack(fill=X, expand=True, side=LEFT, padx=(0, 5))
        
        # Frame para botões
        buttons_frame = ttk.Frame(main_frame, padding="5")
        buttons_frame.grid(row=2, column=0, columnspan=3, sticky=(W, E), pady=5)
        
        # Botões
        ttk.Button(
            buttons_frame,
            text="Iniciar Servidor",
            style="Primary.TButton",
            command=lambda: threading.Thread(target=self.start_server).start()
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Conectar",
            style="Primary.TButton",
            command=self.connect_to_selected
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Enviar Mensagem",
            style="Secondary.TButton",
            command=self.send_message
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Enviar Arquivo",
            style="Secondary.TButton",
            command=lambda: self.send_file()
        ).pack(side=LEFT, padx=5)
        
        # Configurar evento de seleção da lista
        self.device_list.bind('<<ListboxSelect>>', self.on_device_select)
        
    def on_device_select(self, event):
        selection = self.device_list.curselection()
        if selection:
            self.selected_device = self.device_list.get(selection[0])
            self.selected_device_label.config(
                text=f"Selecionado: {self.selected_device}",
                foreground=COLORS['success']
            )
        else:
            self.selected_device = None
            self.selected_device_label.config(
                text="Nenhum dispositivo selecionado",
                foreground=COLORS['text']
            )

    def refresh_device_list(self):
        """Atualiza a lista de dispositivos conectados"""
        self.chat_area.insert(END, "Atualizando lista de dispositivos...\n")
        self.update_device_list()
        self.chat_area.insert(END, f"Lista atualizada. {len(self.connected_devices)} dispositivos encontrados.\n")
        self.chat_area.see(END)

    def on_entry_click(self, event, placeholder):
        """Função para limpar o placeholder quando o usuário clica no campo"""
        if self.message_entry.get() == placeholder:
            self.message_entry.delete(0, END)
            self.message_entry.config(foreground=COLORS['text'])

    def on_focus_out(self, event, placeholder):
        """Função para restaurar o placeholder quando o campo perde o foco"""
        if not self.message_entry.get():
            self.message_entry.insert(0, placeholder)
            self.message_entry.config(foreground='gray')

    def update_device_list(self):
        self.device_list.delete(0, END)
        for addr, name in self.connected_devices.items():
            self.device_list.insert(END, f"{name} ({addr[0]})")

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', PORT))
        server.listen(5)
        self.chat_area.insert(END, f"Servidor iniciado na porta {PORT}\n")
        
        def accept_connections():
            while True:
                conn, addr = server.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()
                
        threading.Thread(target=accept_connections).start()

    def handle_client(self, conn, addr):
        try:
            device_name = conn.recv(1024).decode()
            self.connected_devices[addr] = device_name
            self.update_device_list()
            
            self.chat_area.insert(END, f"{device_name} ({addr}) conectado.\n")
            self.chat_area.see(END)

            while True:
                data = conn.recv(1024).decode()
                if data.startswith('MSG:'):
                    message = data[4:]
                    self.chat_area.insert(END, f"{device_name}: {message}\n", 'message')
                    self.chat_area.see(END)
                elif data.startswith('FILE:'):
                    self.handle_file_receive(conn, device_name)
        except:
            self.chat_area.insert(END, f"{self.connected_devices.get(addr, addr)} desconectado.\n")
            self.connected_devices.pop(addr, None)
            self.update_device_list()
        finally:
            conn.close()

    def handle_file_receive(self, conn, device_name):
        filename = conn.recv(1024).decode()
        filesize = int(conn.recv(1024).decode())
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            received = 0
            while received < filesize:
                chunk = conn.recv(1024)
                f.write(chunk)
                received += len(chunk)
                
        self.chat_area.insert(END, f"Arquivo recebido: {filename} de {device_name}\n")
        self.chat_area.see(END)

    def connect_to_selected(self):
        if not self.selected_device:
            self.chat_area.insert(END, "Por favor, selecione um dispositivo primeiro.\n")
            return
            
        peer_ip = self.selected_device.split('(')[1][:-1]
        self.client = self.connect_to_peer(peer_ip)

    def connect_to_peer(self, host):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, PORT))
            client.send(self.username.encode())
            self.chat_area.insert(END, f"Conectado ao peer: {host}:{PORT}\n")
            return client
        except Exception as e:
            self.chat_area.insert(END, f"Erro ao conectar: {str(e)}\n")
            return None

    def send_message(self):
        if not self.client:
            self.chat_area.insert(END, "Por favor, conecte-se a um dispositivo primeiro.\n")
            return
            
        if not self.selected_device:
            self.chat_area.insert(END, "Por favor, selecione um dispositivo primeiro.\n")
            return
            
        if self.message_entry.get() != "Digite sua mensagem...":
            message = self.message_entry.get()
            if message:
                try:
                    self.client.send(f'MSG:{message}'.encode())
                    self.chat_area.insert(END, f"Você para {self.selected_device}: {message}\n")
                    self.chat_area.see(END)
                    self.message_entry.delete(0, END)
                    self.message_entry.insert(0, "Digite sua mensagem...")
                except:
                    self.chat_area.insert(END, "Erro ao enviar mensagem. Verifique a conexão.\n")

    def send_file(self):
        if not self.client:
            self.chat_area.insert(END, "Por favor, conecte-se a um dispositivo primeiro.\n")
            return
            
        if not self.selected_device:
            self.chat_area.insert(END, "Por favor, selecione um dispositivo primeiro.\n")
            return
            
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                filename = os.path.basename(file_path)
                filesize = os.path.getsize(file_path)

                self.client.send('FILE:'.encode())
                self.client.send(filename.encode())
                self.client.send(str(filesize).encode())

                with open(file_path, 'rb') as f:
                    while chunk := f.read(1024):
                        self.client.send(chunk)
                self.chat_area.insert(END, f"Arquivo enviado: {filename} para {self.selected_device}\n")
                self.chat_area.see(END)
            except:
                self.chat_area.insert(END, "Erro ao enviar arquivo. Verifique a conexão.\n")

if __name__ == "__main__":
    root = Tk()
    app = MessagingApp(root)
    root.mainloop()