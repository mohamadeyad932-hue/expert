import sys
import webbrowser
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from experta import *


# =================================================================================
# محرك المعرفة المطور: نظام تشخيص مرن يعتمد على النقاط (Scoring System)
# =================================================================================
class Symptom(Fact):
    pass


class HeadacheExpert(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.diagnosis_result = ""
        self.detailed_reasoning = []
        self.emergency_alert = False
        self.recommendations = []

        # مصفوفات النقاط
        self.scores = {
            'meningitis': 0,
            'migraine': 0,
            'cluster': 0,
            'tension': 0,
            'sinus': 0
        }

        # تسجيل الأعراض التي تم العثور عليها
        self.found_symptoms = {
            'meningitis': [],
            'migraine': [],
            'cluster': [],
            'tension': [],
            'sinus': []
        }

    def add_score(self, diagnosis_type, points, reason):
        """إضافة نقاط لتشخيص معين مع تسجيل السبب"""
        self.scores[diagnosis_type] += points
        self.found_symptoms[diagnosis_type].append(reason)

    def add_detailed_reason(self, title, details):
        self.detailed_reasoning.append({"title": title, "details": details})

    def add_recommendation(self, text):
        self.recommendations.append(text)

    # --- 1. قواعد تحليل الأعراض (توزيع النقاط) ---

    # --- أ. التهاب السحايا (أولوية قصوى) ---
    @Rule(Symptom(fever='yes'))
    def rule_men_fever(self):
        self.add_score('meningitis', 3, "وجود حمى")

    @Rule(Symptom(neck_stiff='yes'))
    def rule_men_neck(self):
        self.add_score('meningitis', 4, "تيبس الرقبة")

    @Rule(Symptom(pain_nature='sharp_diffuse'))
    def rule_men_nature(self):
        self.add_score('meningitis', 2, "ألم حاد منتشر")

    # --- ب. الصداع النصفي (Migraine) ---
    @Rule(OR(Symptom(pain_location='unilateral'), Symptom(pain_location='bilateral')))
    def rule_mig_location(self):
        self.add_score('migraine', 2, "موقع الألم (جانب واحد أو كلاهما)")

    @Rule(Symptom(pain_nature='throbbing'))
    def rule_mig_nature(self):
        self.add_score('migraine', 3, "طبيعة الألم النابض")

    @Rule(Symptom(pain_severity='moderate_to_severe'))
    def rule_mig_severity(self):
        self.add_score('migraine', 2, "شدة الألم المتوسطة إلى الشديدة")

    @Rule(OR(Symptom(duration='4_72_hours'), Symptom(duration='more_than_72_hours')))
    def rule_mig_duration(self):
        self.add_score('migraine', 2, "مدة النوبة (تتناسب مع الشقيقة)")

    @Rule(Symptom(nausea='yes'))
    def rule_mig_nausea(self):
        self.add_score('migraine', 3, "الغثيان (علامة رئيسية للشقيقة)")

    @Rule(Symptom(aura='yes'))
    def rule_mig_aura(self):
        self.add_score('migraine', 3, "وجود هالة بصرية")

    @Rule(Symptom(light_sensitivity='yes'))
    def rule_mig_light(self):
        self.add_score('migraine', 1, "الحساسية للضوء")

    @Rule(Symptom(sound_sensitivity='yes'))
    def rule_mig_sound(self):
        self.add_score('migraine', 1, "الحساسية للصوت")

    # --- ج. الصداع العنقودي (Cluster) ---
    @Rule(Symptom(pain_location='around_eye'))
    def rule_clus_loc(self):
        self.add_score('cluster', 4, "موقع الألم حول العين (علامة مميزة)")

    @Rule(Symptom(pain_nature='burning_stabbing'))
    def rule_clus_nature(self):
        self.add_score('cluster', 3, "طبيعة الألم (حرق/طعن)")

    @Rule(Symptom(pain_severity='very_severe'))
    def rule_clus_sev(self):
        self.add_score('cluster', 2, "الشدة القصوى للألم")

    @Rule(OR(Symptom(duration='15_180_minutes'), Symptom(duration='unknown')))
    def rule_clus_dur(self):
        self.add_score('cluster', 2, "مدة النوبة القصيرة")

    @Rule(Symptom(motor_restlessness='yes'))
    def rule_clus_restless(self):
        self.add_score('cluster', 3, "الهياج الحركي (عدم القدرة على الجلوس)")

    @Rule(OR(Symptom(eye_tearing='yes'), Symptom(nasal_congestion='yes'), Symptom(eye_redness='yes')))
    def rule_clus_autonomic(self):
        self.add_score('cluster', 2, "أعراض عصبية (دموع/احتقان)")

    # --- د. الصداع التوتري (Tension) ---
    @Rule(Symptom(pain_location='bilateral'))
    def rule_ten_loc(self):
        self.add_score('tension', 2, "الألم في الجانبين")

    @Rule(Symptom(pain_nature='pressure'))
    def rule_ten_nature(self):
        self.add_score('tension', 3, "طبيعة الألم (الضغط/الشد)")

    @Rule(OR(Symptom(pain_severity='mild'), Symptom(pain_severity='mild_to_moderate')))
    def rule_ten_sev(self):
        self.add_score('tension', 2, "الشدة الخفيفة إلى المتوسطة")

    @Rule(Symptom(nausea='no'))
    def rule_ten_no_nausea(self):
        self.add_score('tension', 1, "غياب الغثيان")

    @Rule(Symptom(aura='no'))
    def rule_ten_no_aura(self):
        self.add_score('tension', 1, "غياب الهالة")

    @Rule(Symptom(exertion_worsens='no'))
    def rule_ten_no_exertion(self):
        self.add_score('tension', 1, "عدم تأثر الألم بالحركة البدنية العادية")

    # --- هـ. صداع الجيوب الأنفية (Sinus) ---
    @Rule(Symptom(pain_location='face_forehead'))
    def rule_sin_loc(self):
        self.add_score('sinus', 3, "موقع الألم في الوجه/الجبهة")

    @Rule(Symptom(pain_nature='deep_pressure'))
    def rule_sin_nature(self):
        self.add_score('sinus', 2, "الضغط العميق")

    @Rule(Symptom(nasal_discharge='yes'))
    def rule_sin_discharge(self):
        self.add_score('sinus', 2, "إفرازات أنفية")

    @Rule(Symptom(fever='yes'))
    def rule_sin_fever(self):
        self.add_score('sinus', 1, "حمى (تدعم التهاب الجيوب)")

    @Rule(Symptom(bending_worsens='yes'))
    def rule_sin_bend(self):
        self.add_score('sinus', 3, "زيادة الألم عند الانحناء")

    # --- 2. قاعدة اتخاذ القرار النهائية (تحديد الفائز) ---
    @Rule(salience=-1)
    def rule_final_diagnosis(self):
        sorted_scores = sorted(self.scores.items(), key=lambda item: item[1], reverse=True)
        winner = sorted_scores[0]
        max_score = winner[1]
        winner_name = winner[0]

        if winner_name == 'meningitis' and max_score >= 5:
            self.diagnosis_result = "🚨 حالة طوارئ: اشتباه التهاب سحايا (Meningitis)"
            self.emergency_alert = True
            self.add_detailed_reason("تحليل المخاطر:", self.found_symptoms['meningitis'])
            self.add_recommendation("🚑 توجه فوراً لأقرب مستشفى - لا تنتظر!")
        elif max_score < 3:
            self.diagnosis_result = "❓ صداع غير محدد"
            self.add_detailed_reason("التحليل:", ["الأعراض المدخلة غير كافية لتأكيد نوع محدد."])
            self.add_recommendation("راقب الأعراض وكرر التشخيص إذا تغيرت الحالة.")
        else:
            symptoms_found_list = self.found_symptoms[winner_name]

            if winner_name == 'migraine':
                self.diagnosis_result = "🧠 الصداع النصفي (Migraine)"
                self.add_detailed_reason("سبب التشخيص:", symptoms_found_list)
                self.add_recommendation("💊 الراحة في غرفة مظلمة هادئة.")
                self.add_recommendation("💊 تناول مسكنات الشقيقة (Triptans) إن وصفها الطبيب.")

            elif winner_name == 'cluster':
                self.diagnosis_result = "🔥 الصداع العنقودي (Cluster Headache)"
                self.add_detailed_reason("سبب التشخيص:", symptoms_found_list)
                self.add_recommendation("💨 استنشاق الأكسجين النقي (بوصفة طبيب).")
                self.add_recommendation("💊 استشارة الطبيب لوصف أدوية خاصة كالإرغوتامين.")

            elif winner_name == 'tension':
                self.diagnosis_result = "😣 الصداع التوتري (Tension-Type)"
                self.add_detailed_reason("سبب التشخيص:", symptoms_found_list)
                self.add_recommendation("🧘 ممارسة تمارين الاسترخاء وتدليك الرقبة.")
                self.add_recommendation("💊 استخدام المسكنات البسيطة (الباراسيتامول/الإيبوبروفين).")

            elif winner_name == 'sinus':
                self.diagnosis_result = "👃 صداع الجيوب الأنفية (Sinusitis)"
                self.add_detailed_reason("سبب التشخيص:", symptoms_found_list)
                self.add_recommendation("💊 استخدام بخاخات أو قطرات الأنف.")
                self.add_recommendation("💊 شرب السوائل الدافئة واستنشاق البخار.")
                self.add_recommendation("مراجعة طبيب الأنف والأذن والحنجرة إذا استمرت الحمى.")

        self.halt()


# =================================================================================
# واجهة جديدة مع كل عرض في إطار منفصل (نفس الواجهة السابقة بالضبط)
# =================================================================================
class HeadacheDiagnosisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.responses = {}
        self.engine = None
        self.init_ui()
        self.setWindowTitle("🧠 نظام تشخيص الصداع - النظام الخبير المطور")
        self.resize(1200, 850)

    def init_ui(self):
        """تهيئة واجهة المستخدم بالتصميم الأصلي"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_label = QLabel("🧠 نظام تشخيص الصداع - النظام الخبير المطور")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont("Arial", 28, QFont.Weight.Bold)
        header_label.setFont(header_font)
        header_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #2ecc71, stop:1 #9b59b6);
                border-radius: 15px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(header_label)

        description = QLabel("اختر الأعراض التي تشعر بها من القوائم أدناه، ثم اضغط على زر التشخيص")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setFont(QFont("Arial", 12))
        description.setStyleSheet("color: #34495e; margin-bottom: 20px;")
        main_layout.addWidget(description)

        # منطقة الأسئلة
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                border: none;
                background: #ecf0f1;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(25)
        scroll_layout.setContentsMargins(20, 20, 20, 20)

        # ================================
        # مجموعة 1: موقع الألم
        # ================================
        location_group = self.create_symptom_group(
            "📍 موقع الألم",
            "pain_location",
            {
                "عام (في كامل الرأس)": "generalized",
                "أحادي الجانب (على أحد الجانبين)": "unilateral",
                "ثنائي الجانب (على الجانبين)": "bilateral",
                "حول العين مباشرة": "around_eye",
                "الجبهة والوجه": "face_forehead",
                "طوق حول الرأس (من جميع الجوانب)": "band_around_head"
            }
        )
        scroll_layout.addWidget(location_group)

        # ================================
        # مجموعة 2: نوع الألم
        # ================================
        nature_group = self.create_symptom_group(
            "💢 نوع الألم",
            "pain_nature",
            {
                "نابض (يشبه النبض)": "throbbing",
                "ضاغط (كفولّة)": "pressure",
                "حاد منتشر (كطعن في كامل الرأس)": "sharp_diffuse",
                "حرقان وطعن (كشوكة حارة)": "burning_stabbing",
                "ضغط عميق (من داخل الجمجمة)": "deep_pressure"
            }
        )
        scroll_layout.addWidget(nature_group)

        # ================================
        # مجموعة 3: شدة الألم
        # ================================
        severity_group = self.create_symptom_group(
            "📈 شدة الألم",
            "pain_severity",
            {
                "خفيف (لا يؤثر على العمل)": "mild",
                "خفيف إلى متوسط": "mild_to_moderate",
                "متوسط إلى شديد": "moderate_to_severe",
                "شديد جداً (أسوأ ألم في حياتك)": "very_severe"
            }
        )
        scroll_layout.addWidget(severity_group)

        # ================================
        # مجموعة 4: مدة الصداع
        # ================================
        duration_group = self.create_symptom_group(
            "⏱️ مدة الصداع",
            "duration",
            {
                "قصيرة (15-180 دقيقة)": "15_180_minutes",
                "متوسطة (4-72 ساعة)": "4_72_hours",
                "طويلة (أكثر من 72 ساعة)": "more_than_72_hours",
                "غير معروفة": "unknown"
            }
        )
        scroll_layout.addWidget(duration_group)

        # ================================
        # مجموعة 5: أعراض مصاحبة - الجزء 1
        # ================================
        symptoms1_group = QGroupBox("🚨 أعراض مصاحبة (1)")
        symptoms1_group.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        symptoms1_group.setStyleSheet(self.get_group_style("#3498db"))

        symptoms1_layout = QGridLayout(symptoms1_group)
        symptoms1_layout.setSpacing(15)

        symptoms_part1 = [
            ("حمى (ارتفاع حرارة)", "fever", "نعم، لدي حمى", "لا، لا يوجد حمى"),
            ("تيبس في الرقبة", "neck_stiff", "نعم، أشعر بتيبس", "لا، لا أشعر"),
            ("غثيان أو قيء", "nausea", "نعم، أشعر بغثيان", "لا، لا أشعر"),
            ("حساسية من الضوء", "light_sensitivity", "نعم، الضوء يزعجني", "لا، لا يزعجني"),
            ("حساسية من الصوت", "sound_sensitivity", "نعم، الصوت يزعجني", "لا، لا يزعجني"),
            ("دموع في العين", "eye_tearing", "نعم، عيني تدمع", "لا، لا تدمع"),
        ]

        row, col = 0, 0
        max_cols = 3
        for text, key, yes_text, no_text in symptoms_part1:
            symptom_widget = self.create_single_symptom_widget(text, key, yes_text, no_text, "#3498db")
            symptoms1_layout.addWidget(symptom_widget, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        scroll_layout.addWidget(symptoms1_group)

        # ================================
        # مجموعة 6: أعراض مصاحبة - الجزء 2
        # ================================
        symptoms2_group = QGroupBox("🚨 أعراض مصاحبة (2)")
        symptoms2_group.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        symptoms2_group.setStyleSheet(self.get_group_style("#2ecc71"))

        symptoms2_layout = QGridLayout(symptoms2_group)
        symptoms2_layout.setSpacing(15)

        symptoms_part2 = [
            ("إفرازات أنفية ملونة", "nasal_discharge", "نعم، لدي إفرازات", "لا، لا يوجد"),
            ("هالة بصرية (ومضات)", "aura", "نعم، أرى ومضات", "لا، لا أرى"),
            ("احتقان الأنف", "nasal_congestion", "نعم، أنفي محتقن", "لا، ليس محتقن"),
            ("هياج حركي (لا أستطيع الجلوس)", "motor_restlessness", "نعم، لا أستطيع الجلوس", "لا، أستطيع الجلوس"),
            ("احمرار العين", "eye_redness", "نعم، عيني حمراء", "لا، ليست حمراء"),
            ("يزداد عند الانحناء", "bending_worsens", "نعم، يزداد", "لا، لا يزداد"),
        ]

        row, col = 0, 0
        for text, key, yes_text, no_text in symptoms_part2:
            symptom_widget = self.create_single_symptom_widget(text, key, yes_text, no_text, "#2ecc71")
            symptoms2_layout.addWidget(symptom_widget, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        scroll_layout.addWidget(symptoms2_group)

        # ================================
        # مجموعة 7: عوامل مؤثرة
        # ================================
        factors_group = self.create_symptom_group(
            "🔧 عوامل مؤثرة",
            "exertion_worsens",
            {
                "يزداد مع الحركة أو صعود الدرج": "yes",
                "لا يتأثر بالحركة": "no",
                "يزداد مع التوتر والقلق": "stress",
                "يزداد مع الجوع": "hunger"
            }
        )
        scroll_layout.addWidget(factors_group)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, 1)

        # ================================
        # أزرار التحكم
        # ================================
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(30)

        # زر مسح الكل
        self.clear_btn = QPushButton("🗑️ مسح الكل")
        self.clear_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                border: none;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_all)

        # زر معلومات طبية
        self.info_btn = QPushButton("🌐 معلومات طبية")
        self.info_btn.setFont(QFont("Arial", 14))
        self.info_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                border: none;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.info_btn.clicked.connect(self.open_medical_info)

        # زر التشخيص
        self.diagnose_btn = QPushButton("🔍 تشخيص الحالة")
        self.diagnose_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.diagnose_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 20px 40px;
                border-radius: 10px;
                border: none;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #27ae60;
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.diagnose_btn.clicked.connect(self.run_diagnosis)

        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.info_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.diagnose_btn)

        main_layout.addWidget(button_frame)

        # شريط الحالة
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        self.status_bar.showMessage("جاهز - اختر الأعراض وانتقل إلى التشخيص")

    def get_group_style(self, color):
        """إرجاع نمط مجموعة الأعراض"""
        return f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {color};
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
                color: {color};
            }}
        """

    def create_symptom_group(self, title, key, options_dict):
        """إنشاء مجموعة أعراض مع خيارات راديو"""
        group = QGroupBox(title)
        group.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        colors = {
            "📍 موقع الألم": "#9b59b6",
            "💢 نوع الألم": "#e74c3c",
            "📈 شدة الألم": "#f39c12",
            "⏱️ مدة الصداع": "#3498db",
            "🔧 عوامل مؤثرة": "#1abc9c"
        }
        color = colors.get(title, "#3498db")
        group.setStyleSheet(self.get_group_style(color))

        layout = QGridLayout(group)
        layout.setSpacing(12)

        button_group = QButtonGroup(group)
        row, col = 0, 0
        max_cols = 2

        for text, value in options_dict.items():
            radio = QRadioButton(text)
            radio.setFont(QFont("Arial", 12))
            radio.setStyleSheet(f"""
                QRadioButton {{
                    padding: 8px;
                    color: #34495e;
                }}
                QRadioButton::indicator {{
                    width: 20px;
                    height: 20px;
                }}
                QRadioButton::indicator:checked {{
                    background-color: {color};
                    border: 5px solid white;
                    border-radius: 10px;
                }}
                QRadioButton:hover {{
                    background-color: #f8f9fa;
                    border-radius: 5px;
                }}
            """)

            radio.toggled.connect(lambda checked, k=key, v=value:
                                  self.update_response(k, v) if checked else None)

            button_group.addButton(radio)
            layout.addWidget(radio, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        return group

    def create_single_symptom_widget(self, symptom_text, key, yes_text, no_text, color):
        """إنشاء إطار منفصل لكل عرض مع أزرار نعم/لا"""
        # إنشاء الإطار الرئيسي
        frame = QFrame()
        frame.setObjectName("symptomFrame")
        frame.setStyleSheet(f"""
            #symptomFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
            #symptomFrame:hover {{
                background-color: #f8f9fa;
                border: 2px solid {color};
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
        """)

        # تخطيط عمودي للإطار
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        # نص العرض
        symptom_label = QLabel(symptom_text)
        symptom_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        symptom_label.setStyleSheet(f"color: {color}; margin-bottom: 10px;")
        symptom_label.setWordWrap(True)
        symptom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(symptom_label)

        # إطار داخلي لأزرار نعم/لا
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(15)

        # زر نعم
        yes_btn = QPushButton("✅ نعم")
        yes_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        yes_btn.setCheckable(True)
        yes_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #e8f5e9;
                color: #2e7d32;
                padding: 10px 20px;
                border-radius: 6px;
                border: 2px solid #c8e6c9;
            }}
            QPushButton:checked {{
                background-color: #2ecc71;
                color: white;
                border: 2px solid #27ae60;
            }}
            QPushButton:hover {{
                background-color: #c8e6c9;
            }}
        """)

        # زر لا
        no_btn = QPushButton("❌ لا")
        no_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        no_btn.setCheckable(True)
        no_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #ffebee;
                color: #c62828;
                padding: 10px 20px;
                border-radius: 6px;
                border: 2px solid #ffcdd2;
            }}
            QPushButton:checked {{
                background-color: #e74c3c;
                color: white;
                border: 2px solid #c0392b;
            }}
            QPushButton:hover {{
                background-color: #ffcdd2;
            }}
        """)

        # جعل الأزرار حصرية
        button_group = QButtonGroup(frame)
        button_group.addButton(yes_btn, 1)
        button_group.addButton(no_btn, 2)
        button_group.setExclusive(True)

        # ربط الأحداث
        yes_btn.clicked.connect(lambda checked, k=key, yt=yes_text:
                                self.on_symptom_selected(k, yt, yes_btn, no_btn, frame, color,
                                                         True) if checked else None)
        no_btn.clicked.connect(lambda checked, k=key, nt=no_text:
                               self.on_symptom_selected(k, nt, yes_btn, no_btn, frame, color,
                                                        False) if checked else None)

        buttons_layout.addWidget(yes_btn)
        buttons_layout.addWidget(no_btn)
        layout.addWidget(buttons_frame)

        return frame

    def on_symptom_selected(self, key, value, yes_btn, no_btn, frame, color, is_yes):
        """معالجة اختيار عرض"""
        if is_yes:
            self.responses[key] = "yes"
            frame.setStyleSheet(f"""
                #symptomFrame {{
                    background-color: #e8f5e9;
                    border: 3px solid #2ecc71;
                    border-radius: 10px;
                    padding: 15px;
                }}
            """)
        else:
            self.responses[key] = "no"
            frame.setStyleSheet(f"""
                #symptomFrame {{
                    background-color: #ffebee;
                    border: 3px solid #e74c3c;
                    border-radius: 10px;
                    padding: 15px;
                }}
            """)

        answered = len(self.responses)
        self.status_bar.showMessage(f"تم اختيار {answered} عرضاً - استمر في الاختيار أو انتقل للتشخيص")

    def update_response(self, key, value):
        """تحديث الاستجابة للمجموعات الأخرى"""
        self.responses[key] = value
        answered = len(self.responses)
        self.status_bar.showMessage(f"تم اختيار {answered} عرضاً - استمر في الاختيار أو انتقل للتشخيص")

    def clear_all(self):
        """مسح جميع الإجابات لتشخيص حالة جديدة"""
        reply = QMessageBox.question(
            self, "تأكيد المسح",
            "هل أنت متأكد من رغبتك في مسح جميع الإجابات والبدء بتشخيص حالة جديدة؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            # مسح البيانات
            self.responses.clear()

            # إعادة تعيين جميع أزرار الراديو
            for widget in self.findChildren(QRadioButton):
                widget.setAutoExclusive(False)
                widget.setChecked(False)
                widget.setAutoExclusive(True)

            # إعادة تعيين جميع أزرار الأعراض (Yes/No)
            for widget in self.findChildren(QPushButton):
                if widget.isCheckable():
                    widget.setChecked(False)

            # إعادة تعيين أنماط إطارات الأعراض إلى الشكل الأبيض الافتراضي
            for frame in self.findChildren(QFrame):
                if frame.objectName() == "symptomFrame":
                    frame.setStyleSheet("""
                        #symptomFrame {
                            background-color: white;
                            border: 2px solid #3498db;
                            border-radius: 10px;
                            padding: 15px;
                        }
                    """)

            self.status_bar.showMessage("تم مسح جميع الإجابات - ابدأ من جديد")
            QMessageBox.information(self, "تم", "تم مسح كل شيء. جاهز لتشخيص مريض جديد.")

    def run_diagnosis(self):
        """تشغيل عملية التشخيص"""
        required_keys = ['pain_location', 'pain_nature', 'pain_severity', 'duration']
        missing_keys = [key for key in required_keys if key not in self.responses]

        if missing_keys:
            QMessageBox.warning(self, "تنبيه",
                                f"يرجى الإجابة على الأسئلة الأساسية أولاً:\n{', '.join(missing_keys)}")
            return

        self.engine = HeadacheExpert()
        self.engine.reset()

        default_values = {
            'fever': 'no',
            'neck_stiff': 'no',
            'nausea': 'no',
            'light_sensitivity': 'no',
            'sound_sensitivity': 'no',
            'eye_tearing': 'no',
            'bending_worsens': 'no',
            'nasal_congestion': 'no',
            'aura': 'no',
            'motor_restlessness': 'no',
            'nasal_discharge': 'no',
            'eye_redness': 'no',
            'exertion_worsens': 'no'
        }

        all_facts = {**default_values, **self.responses}

        if 'band_around_head' in all_facts.values():
            for key, value in all_facts.items():
                if value == 'band_around_head':
                    all_facts[key] = 'bilateral'

        try:
            self.engine.declare(Symptom(**all_facts))
            self.engine.run()
            self.show_results_popup()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء التشخيص: {str(e)}")

    def show_results_popup(self):
        """عرض النتائج في رسالة منبثقة (MessageBox) بدلاً من الإطار السفلي"""
        if not self.engine:
            return

        result_text = self.engine.diagnosis_result
        icon = QMessageBox.Icon.Information
        title = "نتائج التشخيص"

        if self.engine.emergency_alert:
            icon = QMessageBox.Icon.Critical
            title = "🚨 تحذير هام"
        elif "غير محدد" in result_text:
            icon = QMessageBox.Icon.Warning
            title = "نتائج غير مؤكدة"

        # تجهيز نص الرسالة (HTML)
        detailed_message = f"<h2 style='text-align:center; color:#2c3e50;'>{result_text}</h2>"

        # سبب التشخيص
        if hasattr(self.engine, 'detailed_reasoning') and self.engine.detailed_reasoning:
            detailed_message += "<hr><h3 style='color:#e67e22'>🔍 سبب التشخيص:</h3><ul>"
            for reason_block in self.engine.detailed_reasoning:
                for detail in reason_block['details']:
                    detailed_message += f"<li>{detail}</li>"
            detailed_message += "</ul>"

        # النصائح
        if hasattr(self.engine, 'recommendations') and self.engine.recommendations:
            detailed_message += "<h3 style='color:#27ae60'>💡 النصائح العلاجية:</h3><ul>"
            for rec in self.engine.recommendations:
                detailed_message += f"<li>{rec}</li>"
            detailed_message += "</ul>"

        detailed_message += "<p style='text-align:center; font-size:10px; color:#7f8c8d;'>تنبيه: هذا النظام للأغراض التعليمية ولا يغني عن الطبيب.</p>"

        # إنشاء الرسالة المنبثقة
        msg_box = QMessageBox(icon, title, "", QMessageBox.StandardButton.Ok)
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(detailed_message)

        # إضافة زر مخصص للرابط
        url_btn = msg_box.addButton("🌐 معلومات طبية تفصيلية", QMessageBox.ButtonRole.ActionRole)
        msg_box.exec()

        # فتح الرابط إذا تم الضغط على الزر المخصص
        if msg_box.clickedButton() == url_btn:
            self.open_direct_diagnosis_info()

    def open_direct_diagnosis_info(self):
        """فتح رابط مباشر بناءً على التشخيص"""
        if not self.engine or not self.engine.diagnosis_result:
            return

        urls = {
            "التهاب سحايا": "https://www.mayoclinic.org/ar/diseases-conditions/meningitis/symptoms-causes/syc-20350508",
            "صداع نصفي": "https://www.mayoclinic.org/ar/diseases-conditions/migraine-headache/symptoms-causes/syc-20360201",
            "صداع عنقودي": "https://www.mayoclinic.org/ar/diseases-conditions/cluster-headache/symptoms-causes/syc-20352080",
            "صداع توتري": "https://www.mayoclinic.org/ar/diseases-conditions/tension-headache/symptoms-causes/syc-20353977",
            "صداع جيوب": "https://www.mayoclinic.org/ar/diseases-conditions/acute-sinusitis/symptoms-causes/syc-20351671"
        }

        result_text = self.engine.diagnosis_result
        url_to_open = None
        for key, url in urls.items():
            if key in result_text:
                url_to_open = url
                break

        if url_to_open:
            webbrowser.open(url_to_open)
        else:
            QMessageBox.information(self, "معلومات", "لا يوجد رابط محدد لهذا التشخيص.")

    def open_medical_info(self):
        """فتح نافذة عامة للمعلومات الطبية"""
        urls = {
            "صداع الشقيقة": "https://www.mayoclinic.org/ar/diseases-conditions/migraine-headache/symptoms-causes/syc-20360201",
            "الصداع التوتري": "https://www.mayoclinic.org/ar/diseases-conditions/tension-headache/symptoms-causes/syc-20353977",
            "الصداع العنقودي": "https://www.mayoclinic.org/ar/diseases-conditions/cluster-headache/symptoms-causes/syc-20352080",
            "صداع الجيوب الأنفية": "https://www.mayoclinic.org/ar/diseases-conditions/acute-sinusitis/symptoms-causes/syc-20351671",
            "التهاب السحايا": "https://www.mayoclinic.org/ar/diseases-conditions/meningitis/symptoms-causes/syc-20350508"
        }

        dialog = QDialog(self)
        dialog.setWindowTitle("🌐 معلومات طبية إضافية")
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout(dialog)

        label = QLabel("اختر موضوعًا للبحث عن معلومات طبية موثوقة:")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(label)

        list_widget = QListWidget()
        list_widget.setFont(QFont("Arial", 12))
        list_widget.setStyleSheet("""
            QListWidget {
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #eee;
                color: #34495e;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #f1f2f6;
                border-radius: 5px;
            }
        """)

        for topic in urls.keys():
            list_widget.addItem(topic)
        layout.addWidget(list_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Open | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.open_selected_url(list_widget.currentItem().text(), urls, dialog))
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(button_box)
        dialog.exec()

    def open_selected_url(self, topic, urls, dialog):
        if topic in urls:
            webbrowser.open(urls[topic])
        dialog.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = HeadacheDiagnosisApp()
    window.show()
    sys.exit(app.exec())