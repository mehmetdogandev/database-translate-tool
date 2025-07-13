import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
import pyodbc
from deep_translator import GoogleTranslator
import threading
from tkinter import font
import os

class DatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Veritabanı Bağlantı ve Çeviri Aracı")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Bağlantı nesneleri
        self.connection = None
        self.cursor = None
        self.translator = GoogleTranslator(source='auto', target='tr')
        # Bağlantı bilgilerini hatırla özelliği
        self.remember_var = tk.BooleanVar()
        self.connection_file = "baglanti-bilgileri.txt"
        # Font ayarları
        self.title_font = font.Font(family="Arial", size=16, weight="bold")
        self.label_font = font.Font(family="Arial", size=10)
        self.button_font = font.Font(family="Arial", size=10, weight="bold")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık
        title_label = tk.Label(main_frame, text="Veritabanı Bağlantı ve Çeviri Aracı", 
                              font=self.title_font, bg='#f0f0f0', fg='#2c3e50')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Sol panel - Bağlantı ayarları
        left_frame = ttk.LabelFrame(main_frame, text="Bağlantı Ayarları", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Veritabanı tipi seçimi
        ttk.Label(left_frame, text="Veritabanı Tipi:", font=self.label_font).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.db_type = tk.StringVar(value="mysql")
        ttk.Radiobutton(left_frame, text="MySQL", variable=self.db_type, value="mysql", 
                       command=self.update_connection_fields).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(left_frame, text="MSSQL", variable=self.db_type, value="mssql", 
                       command=self.update_connection_fields).grid(row=0, column=2, sticky=tk.W)
        
        # Bağlantı alanları
        self.create_connection_fields(left_frame)
        
        # Bağlan butonu
        self.connect_btn = tk.Button(left_frame, text="Bağlan", command=self.connect_database,
                                   font=self.button_font, bg='#3498db', fg='white', 
                                   activebackground='#2980b9', activeforeground='white',
                                   width=15, height=1)
        self.connect_btn.grid(row=7, column=0, columnspan=3, pady=10)

        # Bağlantı durumu
        self.status_label = tk.Label(left_frame, text="Bağlantı Durumu: Bağlı Değil", 
                                   font=self.label_font, fg='red')
        self.status_label.grid(row=8, column=0, columnspan=3, pady=5)
        
        # Tabloları getir butonu
        self.get_tables_btn = tk.Button(left_frame, text="Tabloları Getir", 
                                       command=self.get_tables, state=tk.DISABLED,
                                       font=self.button_font, bg='#27ae60', fg='white',
                                       activebackground='#229954', activeforeground='white',
                                       width=15, height=1)
        self.get_tables_btn.grid(row=9, column=0, columnspan=3, pady=5)
        
        # Tablo seçimi
        ttk.Label(left_frame, text="Tablo Seç:", font=self.label_font).grid(row=10, column=0, sticky=tk.W, pady=5)
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(left_frame, textvariable=self.table_var, state="readonly", width=25)
        self.table_combo.grid(row=10, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Verileri getir butonu
        self.get_data_btn = tk.Button(left_frame, text="Verileri Getir ve Çevir", 
                                     command=self.get_and_translate_data, state=tk.DISABLED,
                                     font=self.button_font, bg='#e74c3c', fg='white',
                                     activebackground='#c0392b', activeforeground='white',
                                     width=18, height=1)
        self.get_data_btn.grid(row=11, column=0, columnspan=3, pady=10)
        
        # Sağ panel - Sonuçlar
        right_frame = ttk.LabelFrame(main_frame, text="Sonuçlar", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sonuç alanı
        self.result_text = scrolledtext.ScrolledText(right_frame, width=60, height=35, 
                                                   font=("Courier", 9), wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Temizle butonu
        clear_btn = tk.Button(right_frame, text="Temizle", command=self.clear_results,
                             font=self.button_font, bg='#95a5a6', fg='white',
                             activebackground='#7f8c8d', activeforeground='white',
                             width=10, height=1)
        clear_btn.grid(row=1, column=0, pady=5)
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        # Program başlangıcında bağlantı bilgilerini yükle
        self.load_connection_info()
        
    def create_connection_fields(self, parent):
        # Host/Server
        ttk.Label(parent, text="Host/Server:", font=self.label_font).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.host_entry = ttk.Entry(parent, width=25)
        self.host_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.host_entry.insert(0, "localhost")
        
        # Database
        ttk.Label(parent, text="Veritabanı:", font=self.label_font).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.database_entry = ttk.Entry(parent, width=25)
        self.database_entry.grid(row=2, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Username
        ttk.Label(parent, text="Kullanıcı Adı:", font=self.label_font).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(parent, width=25)
        self.username_entry.grid(row=3, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Password
        ttk.Label(parent, text="Şifre:", font=self.label_font).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(parent, width=25, show="*")
        self.password_entry.grid(row=4, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Port (sadece MySQL için)
        ttk.Label(parent, text="Port:", font=self.label_font).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(parent, width=10)
        self.port_entry.grid(row=5, column=1, pady=5, sticky=tk.W)
        self.port_entry.insert(0, "3306")
        self.remember_check = tk.Checkbutton(parent, text="Bağlantı bilgilerini hatırla", 
        variable=self.remember_var, font=self.label_font,
        command=self.toggle_remember)
        self.remember_check.grid(row=6, column=0, columnspan=3, pady=5, sticky=tk.W)

        
    def update_connection_fields(self):
        if self.db_type.get() == "mysql":
            self.port_entry.config(state='normal')
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, "3306")
       
           
        else:
            self.port_entry.config(state='disabled')
            
    def connect_database(self):
        def connect():
            try:
                if self.db_type.get() == "mysql":
                    self.connection = mysql.connector.connect(
                        host=self.host_entry.get(),
                        user=self.username_entry.get(),
                        password=self.password_entry.get(),
                        database=self.database_entry.get(),
                        port=int(self.port_entry.get()) if self.port_entry.get() else 3306
                    )
                else:
                    conn_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={self.host_entry.get()};DATABASE={self.database_entry.get()};UID={self.username_entry.get()};PWD={self.password_entry.get()}'
                    self.connection = pyodbc.connect(conn_str)
                
                self.cursor = self.connection.cursor()
                self.root.after(0, self.connection_success)
                
            except Exception as e:
                self.root.after(0, lambda: self.connection_error(str(e)))
        
        # Bağlantı işlemini ayrı thread'de çalıştır
        self.connect_btn.config(state=tk.DISABLED, text="Bağlanıyor...")
        thread = threading.Thread(target=connect)
        thread.daemon = True
        thread.start()
        
    def connection_success(self):
        self.status_label.config(text="Bağlantı Durumu: Bağlı", fg='green')
        self.connect_btn.config(state=tk.NORMAL, text="Bağlan")
        self.get_tables_btn.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, "✓ Veritabanı bağlantısı başarılı!\n\n")
        # Başarılı bağlantı sonrası bilgileri kaydet
        self.save_connection_info()

    def connection_error(self, error_msg):
        self.status_label.config(text="Bağlantı Durumu: Hata", fg='red')
        self.connect_btn.config(state=tk.NORMAL, text="Bağlan")
        messagebox.showerror("Bağlantı Hatası", f"Bağlantı kurulamadı:\n{error_msg}")
        
    def get_tables(self):
        if not self.connection:
            messagebox.showerror("Hata", "Önce veritabanına bağlanın!")
            return
            
        try:
            if self.db_type.get() == "mysql":
                self.cursor.execute("SHOW TABLES")
            else:
                self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            
            tables = [table[0] for table in self.cursor.fetchall()]
            self.table_combo['values'] = tables
            self.get_data_btn.config(state=tk.NORMAL)
            
            self.result_text.insert(tk.END, f"✓ {len(tables)} tablo bulundu:\n")
            for table in tables:
                self.result_text.insert(tk.END, f"  - {table}\n")
            self.result_text.insert(tk.END, "\n")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Tablolar alınırken hata oluştu:\n{str(e)}")
            
    def get_and_translate_data(self):
        if not self.table_var.get():
            messagebox.showerror("Hata", "Lütfen bir tablo seçin!")
            return
            
        def fetch_and_translate():
            try:
                table_name = self.table_var.get()
                self.root.after(0, lambda: self.result_text.insert(tk.END, f"📊 '{table_name}' tablosundan veriler getiriliyor...\n\n"))
                
                # Sütun isimlerini al
                if self.db_type.get() == "mysql":
                    self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                    columns = [col[0] for col in self.cursor.fetchall()]
                    self.cursor.execute(f"SELECT * FROM {table_name}")
                else:
                    self.cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
                    columns = [col[0] for col in self.cursor.fetchall()]
                    self.cursor.execute(f"SELECT * FROM {table_name}")
                
                rows = self.cursor.fetchall()
                
                # Verileri işle ve çevir
                for row_index, row in enumerate(rows):
                    self.root.after(0, lambda i=row_index: self.result_text.insert(tk.END, f"🔍 Satır {i + 1}:\n"))
                    
                    for col_index, value in enumerate(row):
                        original_value = value
                        translated_value = "NULL" if value is None else value
                        
                        if value and isinstance(value, str):
                            try:
                                translated_value = self.translator.translate(value)
                            except Exception as e:
                                translated_value = f"Çeviri hatası: {str(e)}"
                        
                        result_line = f"  {columns[col_index]}: {original_value} -> {translated_value}\n"
                        self.root.after(0, lambda line=result_line: self.result_text.insert(tk.END, line))
                    
                    self.root.after(0, lambda: self.result_text.insert(tk.END, "\n"))
                
                self.root.after(0, lambda: self.result_text.insert(tk.END, f"✅ İşlem tamamlandı! {len(rows)} satır işlendi.\n\n"))
                self.root.after(0, lambda: self.get_data_btn.config(state=tk.NORMAL, text="Verileri Getir ve Çevir"))
                
            except Exception as e:
                error_msg = f"Veri işleme hatası:\n{str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Hata", error_msg))
                self.root.after(0, lambda: self.get_data_btn.config(state=tk.NORMAL, text="Verileri Getir ve Çevir"))
        
        # Veri getirme işlemini ayrı thread'de çalıştır
        self.get_data_btn.config(state=tk.DISABLED, text="İşleniyor...")
        thread = threading.Thread(target=fetch_and_translate)
        thread.daemon = True
        thread.start()
        
    def clear_results(self):
        self.result_text.delete(1.0, tk.END)
    def toggle_remember(self):
        """Hatırla checkbox'ı değiştiğinde çalışır"""
        if not self.remember_var.get():
            # Tik kaldırıldıysa dosyayı temizle
            self.clear_connection_file()
    
    def save_connection_info(self):
        """Bağlantı bilgilerini dosyaya kaydet"""
        if self.remember_var.get():
            try:
                with open(self.connection_file, 'w', encoding='utf-8') as f:
                    f.write(f"db_type={self.db_type.get()}\n")
                    f.write(f"host={self.host_entry.get()}\n")
                    f.write(f"database={self.database_entry.get()}\n")
                    f.write(f"username={self.username_entry.get()}\n")
                    f.write(f"password={self.password_entry.get()}\n")
                    f.write(f"port={self.port_entry.get()}\n")
            except Exception as e:
                print(f"Bağlantı bilgileri kaydedilirken hata: {e}")
        else:
            self.clear_connection_file()
    
    def load_connection_info(self):
        """Program başlangıcında bağlantı bilgilerini yükle"""
        if os.path.exists(self.connection_file):
            try:
                with open(self.connection_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:  # Dosya boş değilse
                        self.remember_var.set(True)
                        for line in lines:
                            line = line.strip()
                            if '=' in line:
                                key, value = line.split('=', 1)
                                if key == 'db_type':
                                    self.db_type.set(value)
                                elif key == 'host':
                                    self.host_entry.delete(0, tk.END)
                                    self.host_entry.insert(0, value)
                                elif key == 'database':
                                    self.database_entry.delete(0, tk.END)
                                    self.database_entry.insert(0, value)
                                elif key == 'username':
                                    self.username_entry.delete(0, tk.END)
                                    self.username_entry.insert(0, value)
                                elif key == 'password':
                                    self.password_entry.delete(0, tk.END)
                                    self.password_entry.insert(0, value)
                                elif key == 'port':
                                    self.port_entry.delete(0, tk.END)
                                    self.port_entry.insert(0, value)
                        self.update_connection_fields()
                        # Checkbox'ı da tikle
                        if hasattr(self, 'remember_check'):
                            self.remember_check.select()
            except Exception as e:
                print(f"Bağlantı bilgileri yüklenirken hata: {e}")
    
    def clear_connection_file(self):
        """Bağlantı bilgileri dosyasını temizle"""
        try:
            with open(self.connection_file, 'w', encoding='utf-8') as f:
                f.write("")  # Dosyayı boş yap
        except Exception as e:
            print(f"Dosya temizlenirken hata: {e}")
        
    def on_closing(self):
        if self.connection:
            try:
                self.cursor.close()
                self.connection.close()
            except:
                pass
        self.root.destroy()

def main():
    root = tk.Tk()
    app = DatabaseGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()