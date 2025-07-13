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
        self.root.title("Veritabanı Çeviri Aracı")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Bağlantı nesneleri
        self.connection = None
        self.cursor = None
        self.translator = GoogleTranslator(source='auto', target='tr')
        
        # modu
        self.debug_mode = tk.BooleanVar(value=True)
        
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
        title_label = tk.Label(main_frame, text="🔧 Veritabanı Çeviri Aracı", 
                              font=self.title_font, bg='#f0f0f0', fg="#3c78e7")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sol panel - Bağlantı ayarları
        left_frame = ttk.LabelFrame(main_frame, text="Bağlantı Ayarları", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # modu checkbox
        debug_check = tk.Checkbutton(left_frame, text="🐛 Modu (Detaylı Loglar)", 
                                   variable=self.debug_mode, font=self.label_font)
        debug_check.grid(row=0, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        # Veritabanı tipi seçimi
        ttk.Label(left_frame, text="Veritabanı Tipi:", font=self.label_font).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.db_type = tk.StringVar(value="mysql")
        ttk.Radiobutton(left_frame, text="MySQL", variable=self.db_type, value="mysql", 
                       command=self.update_connection_fields).grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(left_frame, text="MSSQL", variable=self.db_type, value="mssql", 
                       command=self.update_connection_fields).grid(row=1, column=2, sticky=tk.W)
        
        # Bağlantı alanları
        self.create_connection_fields(left_frame)
        
        # Bağlan butonu
        self.connect_btn = tk.Button(left_frame, text="🔗 Bağlan", command=self.connect_database,
                                   font=self.button_font, bg='#3498db', fg='white', 
                                   activebackground='#2980b9', activeforeground='white',
                                   width=15, height=1)
        self.connect_btn.grid(row=8, column=0, columnspan=3, pady=10)

        # Bağlantı durumu
        self.status_label = tk.Label(left_frame, text="Bağlantı Durumu: Bağlı Değil", 
                                   font=self.label_font, fg='red')
        self.status_label.grid(row=9, column=0, columnspan=3, pady=5)
        
        # Test butonu - Yazma yetkisi kontrolü
        self.test_write_btn = tk.Button(left_frame, text="🧪 Yazma Yetkisi Test Et", 
                                      command=self.test_write_permission, state=tk.DISABLED,
                                      font=self.button_font, bg='#9b59b6', fg='white',
                                      activebackground='#8e44ad', activeforeground='white',
                                      width=18, height=1)
        self.test_write_btn.grid(row=10, column=0, columnspan=3, pady=5)
        
        # Tabloları getir butonu
        self.get_tables_btn = tk.Button(left_frame, text="📋 Tabloları Getir", 
                                       command=self.get_tables, state=tk.DISABLED,
                                       font=self.button_font, bg='#27ae60', fg='white',
                                       activebackground='#229954', activeforeground='white',
                                       width=15, height=1)
        self.get_tables_btn.grid(row=11, column=0, columnspan=3, pady=5)
        
        # Tablo seçimi
        ttk.Label(left_frame, text="Tablo Seç:", font=self.label_font).grid(row=12, column=0, sticky=tk.W, pady=5)
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(left_frame, textvariable=self.table_var, state="readonly", width=25)
        self.table_combo.grid(row=12, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.table_combo.bind('<<ComboboxSelected>>', self.on_table_selected)
        
        # Orta panel - Sütun seçimi ve çeviri ayarları
        middle_frame = ttk.LabelFrame(main_frame, text="Çeviri Ayarları", padding="10")
        middle_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Çeviri modunu seç
        ttk.Label(middle_frame, text="Çeviri Modu:", font=self.label_font).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.translate_mode = tk.StringVar(value="save_to_db")  # Default olarak kaydet modu
        ttk.Radiobutton(middle_frame, text="📖 Sadece Göster", variable=self.translate_mode, 
                       value="view_only").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(middle_frame, text="💾 Veritabanına Kaydet", variable=self.translate_mode, 
                       value="save_to_db").grid(row=1, column=1, sticky=tk.W)
        
        # Test modu - Sadece bir kayıt
        self.test_mode = tk.BooleanVar(value=False)
        test_check = tk.Checkbutton(middle_frame, text="🧪 Test Modu (Sadece 1 kayıt işle)", 
                                  variable=self.test_mode, font=self.label_font)
        test_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Sütun seçimi
        ttk.Label(middle_frame, text="Çevrilecek Sütunlar:", font=self.label_font).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Sütun listesi için scroll frame
        self.columns_frame = ttk.Frame(middle_frame)
        self.columns_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Sütun seçim scroll area
        self.columns_canvas = tk.Canvas(self.columns_frame, height=120, bg='white')
        self.columns_scrollbar = ttk.Scrollbar(self.columns_frame, orient="vertical", command=self.columns_canvas.yview)
        self.columns_scrollable_frame = ttk.Frame(self.columns_canvas)
        
        self.columns_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.columns_canvas.configure(scrollregion=self.columns_canvas.bbox("all"))
        )
        
        self.columns_canvas.create_window((0, 0), window=self.columns_scrollable_frame, anchor="nw")
        self.columns_canvas.configure(yscrollcommand=self.columns_scrollbar.set)
        
        self.columns_canvas.pack(side="left", fill="both", expand=True)
        self.columns_scrollbar.pack(side="right", fill="y")
        
        # Kayıt sayısı limiti
        ttk.Label(middle_frame, text="Kayıt Limiti:", font=self.label_font).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.limit_var = tk.StringVar(value="5")
        limit_entry = ttk.Entry(middle_frame, textvariable=self.limit_var, width=10)
        limit_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Hedef dil seçimi
        ttk.Label(middle_frame, text="Hedef Dil:", font=self.label_font).grid(row=6, column=0, sticky=tk.W, pady=5)
        self.target_lang = tk.StringVar(value="tr")
        lang_combo = ttk.Combobox(middle_frame, textvariable=self.target_lang, width=10)
        lang_combo['values'] = ('tr', 'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh')
        lang_combo.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # İşlem butonları
        self.get_data_btn = tk.Button(middle_frame, text="🚀 Verileri Getir ve Çevir", 
                                     command=self.get_and_translate_data, state=tk.DISABLED,
                                     font=self.button_font, bg='#e74c3c', fg='white',
                                     activebackground='#c0392b', activeforeground='white',
                                     width=20, height=2)
        self.get_data_btn.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Manuel UPDATE test butonu
        self.manual_update_btn = tk.Button(middle_frame, text="🔧 Manuel UPDATE Test", 
                                         command=self.test_manual_update, state=tk.DISABLED,
                                         font=self.button_font, bg='#f39c12', fg='white',
                                         activebackground='#e67e22', activeforeground='white',
                                         width=20, height=1)
        self.manual_update_btn.grid(row=8, column=0, columnspan=2, pady=5)
        
        # Sağ panel - Sonuçlar
        right_frame = ttk.LabelFrame(main_frame, text="🔍 Sonuçları", padding="10")
        right_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sonuç alanı
        self.result_text = scrolledtext.ScrolledText(right_frame, width=70, height=40, 
                                                   font=("Courier", 9), wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buton frame
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Temizle butonu
        clear_btn = tk.Button(button_frame, text="🗑️ Temizle", command=self.clear_results,
                             font=self.button_font, bg='#95a5a6', fg='white',
                             activebackground='#7f8c8d', activeforeground='white',
                             width=10, height=1)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Sonuçları dosyaya kaydet butonu
        save_btn = tk.Button(button_frame, text="💾 Sonuçları Kaydet", command=self.save_results,
                            font=self.button_font, bg='#f39c12', fg='white',
                            activebackground='#e67e22', activeforeground='white',
                            width=15, height=1)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=2)
        main_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(1, weight=1)
        middle_frame.columnconfigure(1, weight=1)
        middle_frame.rowconfigure(4, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Program başlangıcında bağlantı bilgilerini yükle
        self.load_connection_info()
        
    def debug_log(self, message):
        """mesajı yazdır"""
        if self.debug_mode.get():
            self.result_text.insert(tk.END, f"🐛 DEBUG: {message}\n")
            self.result_text.see(tk.END)
        
    def create_connection_fields(self, parent):
        # Host/Server
        ttk.Label(parent, text="Host/Server:", font=self.label_font).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.host_entry = ttk.Entry(parent, width=25)
        self.host_entry.grid(row=2, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        self.host_entry.insert(0, "localhost")
        
        # Database
        ttk.Label(parent, text="Veritabanı:", font=self.label_font).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.database_entry = ttk.Entry(parent, width=25)
        self.database_entry.grid(row=3, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Username
        ttk.Label(parent, text="Kullanıcı Adı:", font=self.label_font).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(parent, width=25)
        self.username_entry.grid(row=4, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Password
        ttk.Label(parent, text="Şifre:", font=self.label_font).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(parent, width=25, show="*")
        self.password_entry.grid(row=5, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Port (sadece MySQL için)
        ttk.Label(parent, text="Port:", font=self.label_font).grid(row=6, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(parent, width=10)
        self.port_entry.grid(row=6, column=1, pady=5, sticky=tk.W)
        self.port_entry.insert(0, "3306")
        
        self.remember_check = tk.Checkbutton(parent, text="Bağlantı bilgilerini hatırla", 
                                           variable=self.remember_var, font=self.label_font,
                                           command=self.toggle_remember)
        self.remember_check.grid(row=7, column=0, columnspan=3, pady=5, sticky=tk.W)
        
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
                self.debug_log(f"Bağlantı denenecek: {self.db_type.get()}")
                self.debug_log(f"Host: {self.host_entry.get()}")
                self.debug_log(f"Database: {self.database_entry.get()}")
                self.debug_log(f"User: {self.username_entry.get()}")
                
                if self.db_type.get() == "mysql":
                    self.connection = mysql.connector.connect(
                        host=self.host_entry.get(),
                        user=self.username_entry.get(),
                        password=self.password_entry.get(),
                        database=self.database_entry.get(),
                        port=int(self.port_entry.get()) if self.port_entry.get() else 3306,
                        autocommit=False  # Manuel commit için
                    )
                else:
                    conn_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={self.host_entry.get()};DATABASE={self.database_entry.get()};UID={self.username_entry.get()};PWD={self.password_entry.get()}'
                    self.connection = pyodbc.connect(conn_str)
                    self.connection.autocommit = False
                
                self.cursor = self.connection.cursor()
                self.debug_log("Bağlantı başarılı!")
                self.debug_log(f"Autocommit durumu: {self.connection.autocommit if hasattr(self.connection, 'autocommit') else 'N/A'}")
                
                self.root.after(0, self.connection_success)
                
            except Exception as e:
                self.debug_log(f"Bağlantı hatası: {str(e)}")
                self.root.after(0, lambda: self.connection_error(str(e)))
        
        # Bağlantı işlemini ayrı thread'de çalıştır
        self.connect_btn.config(state=tk.DISABLED, text="Bağlanıyor...")
        thread = threading.Thread(target=connect)
        thread.daemon = True
        thread.start()
        
    def connection_success(self):
        self.status_label.config(text="Bağlantı Durumu: ✅ Bağlı", fg='green')
        self.connect_btn.config(state=tk.NORMAL, text="🔗 Bağlan")
        self.get_tables_btn.config(state=tk.NORMAL)
        self.test_write_btn.config(state=tk.NORMAL)
        self.manual_update_btn.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, "✓ Veritabanı bağlantısı başarılı!\n\n")
        self.save_connection_info()

    def connection_error(self, error_msg):
        self.status_label.config(text="Bağlantı Durumu: ❌ Hata", fg='red')
        self.connect_btn.config(state=tk.NORMAL, text="🔗 Bağlan")
        messagebox.showerror("Bağlantı Hatası", f"Bağlantı kurulamadı:\n{error_msg}")
        
    def test_write_permission(self):
        """Yazma yetkisi test et"""
        try:
            self.debug_log("Yazma yetkisi test ediliyor...")
            
            # Test tablosu oluşturmayı dene
            test_table_name = "test_write_permission"
            
            self.debug_log(f"Test tablosu oluşturuluyor: {test_table_name}")
            self.cursor.execute(f"CREATE TEMPORARY TABLE {test_table_name} (id INT, test_text VARCHAR(100))")
            
            self.debug_log("Test verisi ekleniyor...")
            self.cursor.execute(f"INSERT INTO {test_table_name} (id, test_text) VALUES (1, 'test')")
            
            self.debug_log("Test verisi güncelleniyor...")
            self.cursor.execute(f"UPDATE {test_table_name} SET test_text = 'updated' WHERE id = 1")
            
            self.debug_log("Commit yapılıyor...")
            self.connection.commit()
            
            self.debug_log("Test verisi kontrol ediliyor...")
            self.cursor.execute(f"SELECT * FROM {test_table_name}")
            result = self.cursor.fetchone()
            
            self.debug_log(f"Test sonucu: {result}")
            
            self.result_text.insert(tk.END, "✅ Yazma yetkisi testi BAŞARILI! Veritabanına yazma hakkınız var.\n\n")
            
        except Exception as e:
            self.debug_log(f"Yazma yetkisi test hatası: {str(e)}")
            self.result_text.insert(tk.END, f"❌ Yazma yetkisi testi BAŞARISIZ: {str(e)}\n\n")
            
    def test_manual_update(self):
        """Manuel UPDATE test et"""
        if not self.table_var.get():
            messagebox.showerror("Hata", "Önce bir tablo seçin!")
            return
            
        try:
            table_name = self.table_var.get()
            self.debug_log(f"Manuel UPDATE test başlıyor: {table_name}")
            
            # İlk kaydı al
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            row = self.cursor.fetchone()
            
            if not row:
                self.result_text.insert(tk.END, "❌ Tabloda kayıt bulunamadı!\n\n")
                return
                
            # Sütun isimlerini al
            if self.db_type.get() == "mysql":
                self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns = [col[0] for col in self.cursor.fetchall()]
            else:
                self.cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
                columns = [col[0] for col in self.cursor.fetchall()]
            
            row_dict = dict(zip(columns, row))
            self.debug_log(f"İlk kayıt: {row_dict}")
            
            # Primary key'i bul
            pk_column = columns[0]  # Genelde ilk sütun primary key
            pk_value = row[0]
            
            # Test güncelleme yap (last_update sütunu varsa)
            if 'last_update' in columns:
                update_query = f"UPDATE {table_name} SET last_update = NOW() WHERE {pk_column} = %s"
                self.debug_log(f"Test UPDATE sorgusu: {update_query}")
                self.debug_log(f"Parametre: {pk_value}")
                
                self.cursor.execute(update_query, (pk_value,))
                affected_rows = self.cursor.rowcount
                self.debug_log(f"Etkilenen satır sayısı: {affected_rows}")
                
                self.connection.commit()
                self.debug_log("Commit yapıldı")
                
                self.result_text.insert(tk.END, f"✅ Manuel UPDATE testi başarılı! {affected_rows} satır güncellendi.\n\n")
            else:
                self.result_text.insert(tk.END, "⚠️ Test için uygun sütun bulunamadı (last_update sütunu yok).\n\n")
                
        except Exception as e:
            self.debug_log(f"Manuel UPDATE test hatası: {str(e)}")
            self.result_text.insert(tk.END, f"❌ Manuel UPDATE test hatası: {str(e)}\n\n")
            try:
                self.connection.rollback()
                self.debug_log("Rollback yapıldı")
            except:
                pass
        
    def get_tables(self):
        if not self.connection:
            messagebox.showerror("Hata", "Önce veritabanına bağlanın!")
            return
            
        try:
            self.debug_log("Tablolar getiriliyor...")
            
            if self.db_type.get() == "mysql":
                # Sadece gerçek tabloları getir, view'ları hariç tut
                self.cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_TYPE = 'BASE TABLE'
                """)
                tables = [table[0] for table in self.cursor.fetchall()]
                
                # View'ları da getir ama işaretle
                self.cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_TYPE = 'VIEW'
                """)
                views = [table[0] for table in self.cursor.fetchall()]
                
                self.debug_log(f"Gerçek tablolar: {tables}")
                self.debug_log(f"View'lar (güncellenemez): {views}")
                
            else:
                self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
                tables = [table[0] for table in self.cursor.fetchall()]
                views = []
            
            # Sadece gerçek tabloları combobox'a ekle
            self.table_combo['values'] = tables
            
            self.result_text.insert(tk.END, f"✓ {len(tables)} gerçek tablo bulundu:\n")
            for table in tables:
                self.result_text.insert(tk.END, f"  ✅ {table} (güncellenebilir)\n")
            
            if views:
                self.result_text.insert(tk.END, f"\n⚠️ {len(views)} view bulundu (güncelleme için kullanılamaz):\n")
                for view in views:
                    self.result_text.insert(tk.END, f"  ❌ {view} (view - güncellenemez)\n")
            
            self.result_text.insert(tk.END, "\n")
            
        except Exception as e:
            self.debug_log(f"Tablo getirme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Tablolar alınırken hata oluştu:\n{str(e)}")
    
    def on_table_selected(self, event):
        """Tablo seçildiğinde sütunları göster"""
        table_name = self.table_var.get()
        if not table_name:
            return
            
        try:
            self.debug_log(f"Tablo seçildi: {table_name}")
            
            # Sütun bilgilerini al
            if self.db_type.get() == "mysql":
                self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns_info = self.cursor.fetchall()
                columns = [(col[0], col[1]) for col in columns_info]  # (name, type)
            else:
                self.cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
                columns_info = self.cursor.fetchall()
                columns = [(col[0], col[1]) for col in columns_info]
            
            self.debug_log(f"Sütunlar: {columns}")
            
            # Sütun checkboxlarını temizle
            for widget in self.columns_scrollable_frame.winfo_children():
                widget.destroy()
            
            self.column_vars = {}
            
            # Sadece text türündeki sütunları göster
            text_types = ['varchar', 'text', 'char', 'mediumtext', 'longtext', 'tinytext', 'nvarchar', 'ntext']
            
            for i, (col_name, col_type) in enumerate(columns):
                # Sütun tipini kontrol et
                is_text_column = any(text_type in col_type.lower() for text_type in text_types)
                
                self.column_vars[col_name] = tk.BooleanVar()
                
                # Checkbox oluştur
                checkbox = tk.Checkbutton(
                    self.columns_scrollable_frame,
                    text=f"{col_name} ({col_type})",
                    variable=self.column_vars[col_name],
                    font=self.label_font,
                    state=tk.NORMAL if is_text_column else tk.DISABLED
                )
                checkbox.grid(row=i, column=0, sticky=tk.W, pady=2)
                
                # Text sütunları otomatik seçili olsun
                if is_text_column:
                    self.column_vars[col_name].set(True)
                    self.debug_log(f"Text sütun seçildi: {col_name}")
            
            self.get_data_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.debug_log(f"Sütun bilgisi alma hatası: {str(e)}")
            messagebox.showerror("Hata", f"Sütun bilgileri alınırken hata: {str(e)}")
            
    def get_and_translate_data(self):
        if not self.table_var.get():
            messagebox.showerror("Hata", "Lütfen bir tablo seçin!")
            return
        
        # Seçilen sütunları al
        selected_columns = [col for col, var in self.column_vars.items() if var.get()]
        
        if not selected_columns:
            messagebox.showerror("Hata", "Lütfen çevrilecek en az bir sütun seçin!")
            return
            
        def fetch_and_translate():
            try:
                table_name = self.table_var.get()
                limit = 1 if self.test_mode.get() else (int(self.limit_var.get()) if self.limit_var.get().isdigit() else 5)
                
                self.debug_log(f"İşlem başlıyor - Tablo: {table_name}")
                self.debug_log(f"Seçilen sütunlar: {selected_columns}")
                self.debug_log(f"Limit: {limit}")
                self.debug_log(f"Mod: {self.translate_mode.get()}")
                
                self.root.after(0, lambda: self.result_text.insert(tk.END, f"📊 '{table_name}' tablosundan veriler getiriliyor...\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, f"🔄 Seçilen sütunlar: {', '.join(selected_columns)}\n"))
                self.root.after(0, lambda: self.result_text.insert(tk.END, f"📝 Mod: {'Veritabanına Kaydet' if self.translate_mode.get() == 'save_to_db' else 'Sadece Göster'}\n\n"))
                
                # Translator'ı güncelle
                self.translator = GoogleTranslator(source='auto', target=self.target_lang.get())
                self.debug_log(f"Translator hedef dil: {self.target_lang.get()}")
                
                # Tüm sütunları ve primary key'i al
                if self.db_type.get() == "mysql":
                    self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                    all_columns = [col[0] for col in self.cursor.fetchall()]
                    
                    # Primary key'i bul
                    self.cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
                    pk_info = self.cursor.fetchone()
                    primary_key = pk_info[4] if pk_info else all_columns[0]
                    
                    self.debug_log(f"Primary key: {primary_key}")
                else:
                    self.cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
                    all_columns = [col[0] for col in self.cursor.fetchall()]
                    
                    # Primary key'i bul
                    self.cursor.execute(f"""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                        WHERE TABLE_NAME = '{table_name}' 
                        AND CONSTRAINT_NAME LIKE 'PK_%'
                    """)
                    pk_info = self.cursor.fetchone()
                    primary_key = pk_info[0] if pk_info else all_columns[0]
                    
                    self.debug_log(f"Primary key: {primary_key}")
                
                # Verileri çek
                query = f"SELECT * FROM {table_name} LIMIT {limit}"
                self.debug_log(f"Veri çekme sorgusu: {query}")
                self.cursor.execute(query)
                rows = self.cursor.fetchall()
                
                self.debug_log(f"Çekilen satır sayısı: {len(rows)}")
                
                updated_count = 0
                error_count = 0
                
                for row_index, row in enumerate(rows):
                    row_dict = dict(zip(all_columns, row))
                    pk_value = row_dict[primary_key]
                    
                    self.debug_log(f"İşlenen satır {row_index + 1}, PK: {pk_value}")
                    
                    self.root.after(0, lambda i=row_index, pk=pk_value: 
                                  self.result_text.insert(tk.END, f"🔍 Satır {i + 1} (ID: {pk}):\n"))
                    
                    # Sadece seçilen sütunları çevir
                    updates = {}
                    for col_name in selected_columns:
                        if col_name in row_dict:
                            original_value = row_dict[col_name]
                            
                            self.debug_log(f"  Sütun {col_name}: '{original_value}' ({type(original_value)})")
                            
                            if original_value and isinstance(original_value, str) and original_value.strip():
                                try:
                                    self.debug_log(f"  Çeviri yapılıyor: {original_value[:50]}...")
                                    translated_value = self.translator.translate(original_value)
                                    updates[col_name] = translated_value
                                    
                                    self.debug_log(f"  Çeviri sonucu: {translated_value[:50]}...")
                                    
                                    result_line = f"  {col_name}: {original_value} -> {translated_value}\n"
                                    self.root.after(0, lambda line=result_line: 
                                                  self.result_text.insert(tk.END, line))
                                    
                                except Exception as e:
                                    error_count += 1
                                    self.debug_log(f"  Çeviri hatası: {str(e)}")
                                    error_line = f"  {col_name}: Çeviri hatası: {str(e)}\n"
                                    self.root.after(0, lambda line=error_line: 
                                                  self.result_text.insert(tk.END, line))
                            else:
                                self.debug_log(f"  Sütun atlandı (boş veya string değil)")
                    
                    # Veritabanına kaydet
                    if self.translate_mode.get() == "save_to_db" and updates:
                        try:
                            self.debug_log(f"  Veritabanı güncelleme başlıyor...")
                            
                            # UPDATE sorgusu oluştur
                            if self.db_type.get() == "mysql":
                                set_clause = ", ".join([f"{col} = %s" for col in updates.keys()])
                                update_query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = %s"
                                values = list(updates.values()) + [pk_value]
                            else:
                                set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
                                update_query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?"
                                values = list(updates.values()) + [pk_value]
                            
                            self.debug_log(f"  UPDATE sorgusu: {update_query}")
                            self.debug_log(f"  Parametreler: {values}")
                            
                            # Güncelleme öncesi mevcut değeri kontrol et
                            check_query = f"SELECT {', '.join(updates.keys())} FROM {table_name} WHERE {primary_key} = {'%s' if self.db_type.get() == 'mysql' else '?'}"
                            self.cursor.execute(check_query, (pk_value,))
                            before_values = self.cursor.fetchone()
                            self.debug_log(f"  Güncelleme öncesi değerler: {before_values}")
                            
                            # UPDATE çalıştır
                            self.cursor.execute(update_query, values)
                            affected_rows = self.cursor.rowcount
                            self.debug_log(f"  Etkilenen satır sayısı: {affected_rows}")
                            
                            # Commit yap
                            self.connection.commit()
                            self.debug_log("  Commit yapıldı")
                            
                            # Güncelleme sonrası kontrol et
                            self.cursor.execute(check_query, (pk_value,))
                            after_values = self.cursor.fetchone()
                            self.debug_log(f"  Güncelleme sonrası değerler: {after_values}")
                            
                            # Değişiklik kontrol et
                            if before_values != after_values:
                                updated_count += 1
                                self.root.after(0, lambda: self.result_text.insert(tk.END, "  ✅ Veritabanına kaydedildi ve değişiklik doğrulandı\n"))
                                self.debug_log("  ✅ Değişiklik başarıyla doğrulandı")
                            else:
                                self.root.after(0, lambda: self.result_text.insert(tk.END, "  ⚠️ UPDATE çalıştı ama değişiklik algılanmadı\n"))
                                self.debug_log("  ⚠️ UPDATE çalıştı ama değişiklik algılanmadı")
                            
                        except Exception as e:
                            error_count += 1
                            self.debug_log(f"  Kaydetme hatası: {str(e)}")
                            self.root.after(0, lambda err=str(e): 
                                          self.result_text.insert(tk.END, f"  ❌ Kaydetme hatası: {err}\n"))
                            try:
                                self.connection.rollback()
                                self.debug_log("  Rollback yapıldı")
                            except:
                                pass
                    elif updates:
                        self.debug_log(f"  Sadece görüntüleme modu - veritabanı güncellenmedi")
                    
                    self.root.after(0, lambda: self.result_text.insert(tk.END, "\n"))
                
                # Sonuç mesajı
                if self.translate_mode.get() == "save_to_db":
                    self.root.after(0, lambda: self.result_text.insert(tk.END, 
                                  f"✅ İşlem tamamlandı! {len(rows)} satır işlendi, {updated_count} satır güncellendi, {error_count} hata.\n\n"))
                    self.debug_log(f"İşlem özeti: {len(rows)} işlendi, {updated_count} güncellendi, {error_count} hata")
                else:
                    self.root.after(0, lambda: self.result_text.insert(tk.END, 
                                  f"✅ İşlem tamamlandı! {len(rows)} satır işlendi (sadece görüntüleme).\n\n"))
                    self.debug_log(f"İşlem özeti: {len(rows)} işlendi (sadece görüntüleme)")
                
                self.root.after(0, lambda: self.get_data_btn.config(state=tk.NORMAL, text="🚀 Verileri Getir ve Çevir"))
                
            except Exception as e:
                error_msg = f"Veri işleme hatası:\n{str(e)}"
                self.debug_log(f"Kritik hata: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Hata", error_msg))
                self.root.after(0, lambda: self.get_data_btn.config(state=tk.NORMAL, text="🚀 Verileri Getir ve Çevir"))
                try:
                    self.connection.rollback()
                    self.debug_log("Kritik hata sonrası rollback yapıldı")
                except:
                    pass
        
        # Veri getirme işlemini ayrı thread'de çalıştır
        self.get_data_btn.config(state=tk.DISABLED, text="⏳ İşleniyor...")
        thread = threading.Thread(target=fetch_and_translate)
        thread.daemon = True
        thread.start()
        
    def clear_results(self):
        self.result_text.delete(1.0, tk.END)
    
    def save_results(self):
        """Sonuçları dosyaya kaydet"""
        try:
            content = self.result_text.get(1.0, tk.END)
            if not content.strip():
                messagebox.showwarning("Uyarı", "Kaydedilecek sonuç bulunamadı!")
                return
            
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Başarılı", f"Sonuçlar kaydedildi: {filename}")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi:\n{str(e)}")
        
    def toggle_remember(self):
        """Hatırla checkbox'ı değiştiğinde çalışır"""
        if not self.remember_var.get():
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