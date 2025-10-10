#!/usr/bin/env python3
"""
Master Translation Script - Handles all translation batches
Usage: python3 translate_batch_1.py [batch_number]
"""
import json
import sys
from pathlib import Path

LANGS_DIR = Path("languages")

# Comprehensive translations for the first 10 languages: ar, de, es, fr, it, ja, ko, pt, ru, zh
TRANSLATIONS_BATCH_1 = {
    # Actions
    "actions.close": {
        "ar": "إغلاق", "de": "Schließen", "es": "Cerrar", "fr": "Fermer", "it": "Chiudi",
        "ja": "閉じる", "ko": "닫기", "pt": "Fechar", "ru": "Закрыть", "zh": "关闭"
    },
    "actions.copy": {
        "ar": "نسخ الكلمة المفتاحية", "de": "Keyword kopieren", "es": "Copiar palabra clave", 
        "fr": "Copier le mot-clé", "it": "Copia parola chiave", "ja": "キーワードをコピー", 
        "ko": "키워드 복사", "pt": "Copiar palavra-chave", "ru": "Копировать ключевое слово", "zh": "复制关键词"
    },
    "actions.copied": {
        "ar": "تم النسخ إلى الحافظة!", "de": "In Zwischenablage kopiert!", "es": "¡Copiado al portapapeles!", 
        "fr": "Copié dans le presse-papiers !", "it": "Copiato negli appunti!", "ja": "クリップボードにコピーしました！", 
        "ko": "클립보드에 복사됨!", "pt": "Copiado para a área de transferência!", "ru": "Скопировано в буфер обмена!", "zh": "已复制到剪贴板！"
    },
    "actions.export": {
        "ar": "تصدير CSV", "de": "CSV exportieren", "es": "Exportar CSV", 
        "fr": "Exporter CSV", "it": "Esporta CSV", "ja": "CSVエクスポート", 
        "ko": "CSV 내보내기", "pt": "Exportar CSV", "ru": "Экспорт CSV", "zh": "导出CSV"
    },
    
    # Entitlements
    "entitlements.sidebar.plan_label": {
        "ar": "خطتك", "de": "Dein Tarif", "es": "Tu plan", "fr": "Votre forfait", "it": "Il tuo piano",
        "ja": "あなたのプラン", "ko": "요금제", "pt": "Seu plano", "ru": "Ваш план", "zh": "您的计划"
    },
    "entitlements.tier.free": {
        "ar": "مجاني", "de": "Kostenlos", "es": "Gratis", "fr": "Gratuit", "it": "Gratuito",
        "ja": "無料", "ko": "무료", "pt": "Grátis", "ru": "Бесплатно", "zh": "免费"
    },
    "entitlements.tier.pro": {
        "ar": "احترافي", "de": "Pro", "es": "Pro", "fr": "Pro", "it": "Pro",
        "ja": "プロ", "ko": "프로", "pt": "Pro", "ru": "Про", "zh": "专业版"
    },
    "entitlements.tier.enterprise": {
        "ar": "مؤسسة", "de": "Unternehmen", "es": "Empresa", "fr": "Entreprise", "it": "Aziendale",
        "ja": "エンタープライズ", "ko": "엔터프라이즈", "pt": "Empresa", "ru": "Корпоративный", "zh": "企业版"
    },
    "entitlements.sidebar.ai_credits": {
        "ar": "أرصدة الذكاء الاصطناعي", "de": "KI-Guthaben", "es": "Créditos de IA", 
        "fr": "Crédits IA", "it": "Crediti IA", "ja": "AIクレジット", "ko": "AI 크레딧",
        "pt": "Créditos de IA", "ru": "Кредиты ИИ", "zh": "AI积分"
    },
    "entitlements.actions.upgrade": {
        "ar": "ترقية الخطة", "de": "Plan upgraden", "es": "Actualizar plan", 
        "fr": "Mettre à niveau", "it": "Aggiorna piano", "ja": "プランをアップグレード", "ko": "플랜 업그레이드",
        "pt": "Atualizar plano", "ru": "Обновить план", "zh": "升级计划"
    },
    "entitlements.actions.buy_credits": {
        "ar": "شراء أرصدة الذكاء الاصطناعي", "de": "KI-Guthaben kaufen", "es": "Comprar créditos de IA", 
        "fr": "Acheter des crédits IA", "it": "Acquista crediti IA", "ja": "AIクレジットを購入", "ko": "AI 크레딧 구매",
        "pt": "Comprar créditos de IA", "ru": "Купить кредиты ИИ", "zh": "购买AI积分"
    },
    "entitlements.actions.upgrade_now": {
        "ar": "الترقية الآن", "de": "Jetzt upgraden", "es": "Actualizar ahora", 
        "fr": "Mettre à niveau maintenant", "it": "Aggiorna ora", "ja": "今すぐアップグレード", "ko": "지금 업그레이드",
        "pt": "Atualizar agora", "ru": "Обновить сейчас", "zh": "立即升级"
    },
    "entitlements.sidebar.ai_unlocked": {
        "ar": "مساحة عمل الذكاء الاصطناعي مفتوحة", "de": "KI-Arbeitsbereich freigeschaltet", "es": "Espacio de trabajo IA desbloqueado", 
        "fr": "Espace de travail IA déverrouillé", "it": "Area di lavoro IA sbloccata", "ja": "AIワークスペースがアンロックされました", "ko": "AI 작업 공간 잠금 해제됨",
        "pt": "Espaço de trabalho IA desbloqueado", "ru": "Рабочее пространство ИИ разблокировано", "zh": "AI工作区已解锁"
    },
    "entitlements.sidebar.ai_locked": {
        "ar": "افتح مساحة عمل الذكاء الاصطناعي بالأرصدة", "de": "KI-Arbeitsbereich mit Guthaben freischalten", "es": "Desbloquear espacio de trabajo IA con créditos", 
        "fr": "Déverrouiller l'espace de travail IA avec des crédits", "it": "Sblocca area di lavoro IA con crediti", "ja": "クレジットでAIワークスペースをアンロック", "ko": "크레딧으로 AI 작업 공간 잠금 해제",
        "pt": "Desbloquear espaço de trabalho IA com créditos", "ru": "Разблокировать рабочее пространство ИИ кредитами", "zh": "使用积分解锁AI工作区"
    },
    "entitlements.status.loading": {
        "ar": "جاري تحميل الخطة...", "de": "Plan wird geladen…", "es": "Cargando plan...", 
        "fr": "Chargement du forfait...", "it": "Caricamento piano...", "ja": "プランを読み込み中…", "ko": "플랜 로딩 중...",
        "pt": "Carregando plano...", "ru": "Загрузка плана…", "zh": "加载计划中..."
    },
    "entitlements.status.error": {
        "ar": "تعذر تحميل الخطة", "de": "Plan konnte nicht geladen werden", "es": "No se pudo cargar el plan", 
        "fr": "Impossible de charger le forfait", "it": "Impossibile caricare il piano", "ja": "プランを読み込めません", "ko": "플랜을 로드할 수 없음",
        "pt": "Não foi possível carregar o plano", "ru": "Не удалось загрузить план", "zh": "无法加载计划"
    },
    "entitlements.locked.module": {
        "ar": "قم بترقية خطتك للوصول إلى هذه الوحدة.", "de": "Upgraden Sie Ihren Plan, um auf dieses Modul zuzugreifen.", "es": "Actualiza tu plan para acceder a este módulo.", 
        "fr": "Mettez à niveau votre forfait pour accéder à ce module.", "it": "Aggiorna il tuo piano per accedere a questo modulo.", "ja": "このモジュールにアクセスするにはプランをアップグレードしてください。", "ko": "이 모듈에 액세스하려면 플랜을 업그레이드하세요.",
        "pt": "Atualize seu plano para acessar este módulo.", "ru": "Обновите свой план для доступа к этому модулю.", "zh": "升级计划以访问此模块。"
    },
    "entitlements.sidebar.expires": {
        "ar": "يتجدد في {{formatted}}", "de": "Verlängert sich am {{formatted}}", "es": "Se renueva el {{formatted}}", 
        "fr": "Renouvellement le {{formatted}}", "it": "Rinnovo il {{formatted}}", "ja": "{{formatted}}に更新", "ko": "{{formatted}}에 갱신",
        "pt": "Renova em {{formatted}}", "ru": "Продлевается {{formatted}}", "zh": "{{formatted}}续订"
    },
    
    # Billing
    "billing.error.checkout_failed": {
        "ar": "تعذر فتح الدفع. حاول مرة أخرى.", "de": "Checkout konnte nicht geöffnet werden. Bitte versuchen Sie es erneut.", "es": "No se pudo abrir el pago. Inténtalo de nuevo.", 
        "fr": "Impossible d'ouvrir le paiement. Veuillez réessayer.", "it": "Impossibile aprire il checkout. Riprova.", "ja": "チェックアウトを開けません。もう一度お試しください。", "ko": "결제를 열 수 없습니다. 다시 시도하세요.",
        "pt": "Não foi possível abrir o checkout. Tente novamente.", "ru": "Не удалось открыть оформление заказа. Попробуйте снова.", "zh": "无法打开结账。请重试。"
    },
    "billing.error.signin_required": {
        "ar": "يرجى تسجيل الدخول للترقية.", "de": "Bitte melden Sie sich an, um zu upgraden.", "es": "Inicia sesión para actualizar.", 
        "fr": "Veuillez vous connecter pour mettre à niveau.", "it": "Accedi per aggiornare.", "ja": "アップグレードするにはサインインしてください。", "ko": "업그레이드하려면 로그인하세요.",
        "pt": "Faça login para atualizar.", "ru": "Войдите, чтобы обновить.", "zh": "请登录以升级。"
    },
    "billing.error.upgrade_unavailable": {
        "ar": "الترقية غير متاحة حاليًا. يرجى الاتصال بالدعم.", "de": "Upgrade ist derzeit nicht verfügbar. Bitte kontaktieren Sie den Support.", "es": "La actualización no está disponible actualmente. Contacta con soporte.", 
        "fr": "La mise à niveau n'est pas disponible actuellement. Veuillez contacter le support.", "it": "L'aggiornamento non è attualmente disponibile. Contatta il supporto.", "ja": "アップグレードは現在利用できません。サポートにお問い合わせください。", "ko": "업그레이드를 현재 사용할 수 없습니다. 지원팀에 문의하세요.",
        "pt": "A atualização não está disponível no momento. Entre em contato com o suporte.", "ru": "Обновление в настоящее время недоступно. Свяжитесь со службой поддержки.", "zh": "升级目前不可用。请联系支持。"
    },
    "billing.error.buy_credits_signin": {
        "ar": "قم بتسجيل الدخول لشراء أرصدة الذكاء الاصطناعي.", "de": "Melden Sie sich an, um KI-Guthaben zu kaufen.", "es": "Inicia sesión para comprar créditos de IA.", 
        "fr": "Connectez-vous pour acheter des crédits IA.", "it": "Accedi per acquistare crediti IA.", "ja": "AIクレジットを購入するにはサインインしてください。", "ko": "AI 크레딧을 구매하려면 로그인하세요.",
        "pt": "Faça login para comprar créditos de IA.", "ru": "Войдите, чтобы купить кредиты ИИ.", "zh": "登录以购买AI积分。"
    },
    "billing.error.buy_credits_unavailable": {
        "ar": "شراء أرصدة الذكاء الاصطناعي غير متاح حاليًا. يرجى الاتصال بالدعم.", "de": "KI-Guthaben-Kauf ist derzeit nicht verfügbar. Bitte kontaktieren Sie den Support.", "es": "La compra de créditos de IA no está disponible ahora. Contacta con soporte.", 
        "fr": "L'achat de crédits IA n'est pas disponible actuellement. Veuillez contacter le support.", "it": "L'acquisto di crediti IA non è attualmente disponibile. Contatta il supporto.", "ja": "AIクレジットの購入は現在利用できません。サポートにお問い合わせください。", "ko": "AI 크레딧 구매를 현재 사용할 수 없습니다. 지원팀에 문의하세요.",
        "pt": "A compra de créditos de IA não está disponível no momento. Entre em contato com o suporte.", "ru": "Покупка кредитов ИИ в настоящее время недоступна. Свяжитесь со службой поддержки.", "zh": "AI积分购买目前不可用。请联系支持。"
    },
    "billing.status.launching_checkout": {
        "ar": "جاري فتح الدفع...", "de": "Checkout wird geöffnet…", "es": "Abriendo pago...", 
        "fr": "Ouverture du paiement...", "it": "Apertura checkout...", "ja": "チェックアウトを開いています…", "ko": "결제 열기 중...",
        "pt": "Abrindo checkout...", "ru": "Открытие оформления заказа…", "zh": "打开结账中..."
    },
    "billing.status.loading_credit_packs": {
        "ar": "جاري تحميل حزم الأرصدة...", "de": "Guthaben-Pakete werden geladen…", "es": "Cargando paquetes de créditos...", 
        "fr": "Chargement des packs de crédits...", "it": "Caricamento pacchetti crediti...", "ja": "クレジットパックを読み込み中…", "ko": "크레딧 팩 로딩 중...",
        "pt": "Carregando pacotes de créditos...", "ru": "Загрузка пакетов кредитов…", "zh": "加载积分包中..."
    },
    
    # Search
    "search.status.loading": {
        "ar": "تشغيل تحليل الكلمات المفتاحية...", "de": "Keyword-Analyse läuft…", "es": "Ejecutando análisis de palabras clave...", 
        "fr": "Analyse des mots-clés en cours...", "it": "Esecuzione analisi parole chiave...", "ja": "キーワード分析実行中…", "ko": "키워드 분석 실행 중...",
        "pt": "Executando análise de palavras-chave...", "ru": "Выполняется анализ ключевых слов…", "zh": "运行关键词分析中..."
    },
    
    # CTA & Hero
    "cta.upgrade_title": {
        "ar": "افتح القوة الكاملة", "de": "Volle Power freischalten", "es": "Desbloquea todo el poder", 
        "fr": "Débloquez toute la puissance", "it": "Sblocca tutta la potenza", "ja": "フルパワーをアンロック", "ko": "전체 파워 잠금 해제",
        "pt": "Desbloqueie todo o poder", "ru": "Разблокируйте полную мощь", "zh": "解锁全部功能"
    },
    "cta.upgrade_description": {
        "ar": "احصل على عمليات بحث غير محدودة ورؤى الذكاء الاصطناعي", "de": "Unbegrenzte Suchen und KI-Einblicke erhalten", "es": "Obtén búsquedas ilimitadas e insights de IA", 
        "fr": "Obtenez des recherches illimitées et des insights IA", "it": "Ottieni ricerche illimitate e insights IA", "ja": "無制限の検索とAIインサイトを取得", "ko": "무제한 검색 및 AI 인사이트 받기",
        "pt": "Obtenha buscas ilimitadas e insights de IA", "ru": "Получите неограниченные поиски и инсайты ИИ", "zh": "获取无限搜索和AI洞察"
    },
    "cta.upgrade_button": {
        "ar": "الترقية الآن", "de": "Jetzt upgraden", "es": "Actualizar ahora", 
        "fr": "Mettre à niveau maintenant", "it": "Aggiorna ora", "ja": "今すぐアップグレード", "ko": "지금 업그레이드",
        "pt": "Atualizar agora", "ru": "Обновить сейчас", "zh": "立即升级"
    },
    "hero.title": {
        "ar": "ذكاء الكلمات المفتاحية متعدد الأسواق", "de": "Multi-Markt-Keyword-Intelligence", "es": "Inteligencia de palabras clave multi-mercado", 
        "fr": "Intelligence de mots-clés multi-marchés", "it": "Intelligence di parole chiave multi-mercato", "ja": "マルチマーケットキーワードインテリジェンス", "ko": "다중 시장 키워드 인텔리전스",
        "pt": "Inteligência de palavras-chave multi-mercado", "ru": "Мультирыночная аналитика ключевых слов", "zh": "多市场关键词智能"
    },
    "hero.subtitle": {
        "ar": "ابحث عن الكلمات المفتاحية في أكثر من 100 دولة ومنصة. احصل على بيانات بحث فورية من Google وYouTube وAmazon والمزيد.", 
        "de": "Recherchieren Sie Keywords in über 100 Ländern und Plattformen. Erhalten Sie Echtzeit-Suchdaten von Google, YouTube, Amazon und mehr.", 
        "es": "Investiga palabras clave en más de 100 países y plataformas. Obtén datos de búsqueda en tiempo real de Google, YouTube, Amazon y más.", 
        "fr": "Recherchez des mots-clés dans plus de 100 pays et plateformes. Obtenez des données de recherche en temps réel de Google, YouTube, Amazon et plus.", 
        "it": "Ricerca parole chiave in oltre 100 paesi e piattaforme. Ottieni dati di ricerca in tempo reale da Google, YouTube, Amazon e altro.", 
        "ja": "100か国以上のプラットフォームでキーワードをリサーチ。Google、YouTube、Amazonなどからリアルタイムの検索データを取得。", 
        "ko": "100개 이상의 국가 및 플랫폼에서 키워드를 조사하세요. Google, YouTube, Amazon 등에서 실시간 검색 데이터를 확인하세요.", 
        "pt": "Pesquise palavras-chave em mais de 100 países e plataformas. Obtenha dados de pesquisa em tempo real do Google, YouTube, Amazon e mais.", 
        "ru": "Исследуйте ключевые слова в более чем 100 странах и платформах. Получайте данные поиска в реальном времени от Google, YouTube, Amazon и других.", 
        "zh": "在100多个国家和平台上研究关键词。获取来自Google、YouTube、Amazon等的实时搜索数据。"
    },
    "hero.cta_primary": {
        "ar": "ابدأ استكشاف الكلمات المفتاحية", "de": "Beginnen Sie mit der Keyword-Erkundung", "es": "Empezar a explorar palabras clave", 
        "fr": "Commencer à explorer les mots-clés", "it": "Inizia a esplorare le parole chiave", "ja": "キーワードの探索を開始", "ko": "키워드 탐색 시작",
        "pt": "Começar a explorar palavras-chave", "ru": "Начать исследование ключевых слов", "zh": "开始探索关键词"
    },
    "hero.cta_secondary": {
        "ar": "اطلع على الأسعار والخطط", "de": "Preise & Pläne ansehen", "es": "Ver precios y planes", 
        "fr": "Voir les tarifs et forfaits", "it": "Vedi prezzi e piani", "ja": "料金とプランを見る", "ko": "가격 및 플랜 보기",
        "pt": "Ver preços e planos", "ru": "Посмотреть цены и планы", "zh": "查看价格和计划"
    },
    "hero.trust_markets": {
        "ar": "{{count}}+ سوق", "de": "{{count}}+ Märkte", "es": "{{count}}+ mercados", 
        "fr": "{{count}}+ marchés", "it": "{{count}}+ mercati", "ja": "{{count}}以上の市場", "ko": "{{count}}개 이상의 시장",
        "pt": "{{count}}+ mercados", "ru": "{{count}}+ рынков", "zh": "{{count}}+个市场"
    },
    "hero.trust_refresh": {
        "ar": "بيانات فورية", "de": "Echtzeit-Daten", "es": "Datos en tiempo real", 
        "fr": "Données en temps réel", "it": "Dati in tempo reale", "ja": "リアルタイムデータ", "ko": "실시간 데이터",
        "pt": "Dados em tempo real", "ru": "Данные в реальном времени", "zh": "实时数据"
    },
    "hero.trust_teams": {
        "ar": "فرق تشحن أسبوعيًا", "de": "Teams, die wöchentlich liefern", "es": "Equipos que lanzan semanalmente", 
        "fr": "Équipes qui livrent chaque semaine", "it": "Team che lanciano settimanalmente", "ja": "毎週リリースするチーム", "ko": "매주 배송하는 팀",
        "pt": "Equipes que lançam semanalmente", "ru": "Команды, выпускающие еженедельно", "zh": "每周发布的团队"
    },
    
    # Features
    "features.semantic.title": {
        "ar": "التجميع الدلالي", "de": "Semantische Clusterung", "es": "Agrupación semántica", 
        "fr": "Regroupement sémantique", "it": "Clustering semantico", "ja": "セマンティッククラスタリング", "ko": "의미론적 클러스터링",
        "pt": "Agrupamento semântico", "ru": "Семантическая кластеризация", "zh": "语义聚类"
    },
    "features.semantic.description": {
        "ar": "تجميع الكلمات المفتاحية المدعوم بالذكاء الاصطناعي يفهم نية البحث وأنماط سلوك المستخدم", 
        "de": "KI-gestützte Keyword-Gruppierung, die Suchabsichten und Nutzerverhaltensmuster versteht", 
        "es": "Agrupación de palabras clave impulsada por IA que comprende la intención de búsqueda y los patrones de comportamiento del usuario", 
        "fr": "Regroupement de mots-clés alimenté par l'IA qui comprend l'intention de recherche et les modèles de comportement des utilisateurs", 
        "it": "Raggruppamento di parole chiave basato su IA che comprende l'intento di ricerca e i modelli di comportamento degli utenti", 
        "ja": "検索意図とユーザー行動パターンを理解するAI駆動のキーワードグルーピング", 
        "ko": "검색 의도와 사용자 행동 패턴을 이해하는 AI 기반 키워드 그룹화", 
        "pt": "Agrupamento de palavras-chave orientado por IA que entende a intenção de pesquisa e os padrões de comportamento do usuário", 
        "ru": "Группировка ключевых слов на базе ИИ, которая понимает намерения поиска и модели поведения пользователей", 
        "zh": "AI驱动的关键词分组，理解搜索意图和用户行为模式"
    },
    "features.localization.title": {
        "ar": "التوطين العالمي", "de": "Globale Lokalisierung", "es": "Localización global", 
        "fr": "Localisation mondiale", "it": "Localizzazione globale", "ja": "グローバルローカライゼーション", "ko": "글로벌 현지화",
        "pt": "Localização global", "ru": "Глобальная локализация", "zh": "全球本地化"
    },
    "features.localization.description": {
        "ar": "ابحث عن الكلمات المفتاحية في أكثر من 100 دولة مع دعم اللغة الأصلية والرؤى الإقليمية", 
        "de": "Recherchieren Sie Keywords in über 100 Ländern mit muttersprachlicher Unterstützung und regionalen Einblicken", 
        "es": "Investiga palabras clave en más de 100 países con soporte de idioma nativo e insights regionales", 
        "fr": "Recherchez des mots-clés dans plus de 100 pays avec support linguistique natif et insights régionaux", 
        "it": "Ricerca parole chiave in oltre 100 paesi con supporto linguistico nativo e insights regionali", 
        "ja": "100か国以上でネイティブ言語サポートと地域別インサイトを使ってキーワードをリサーチ", 
        "ko": "100개 이상의 국가에서 모국어 지원 및 지역 인사이트로 키워드 조사", 
        "pt": "Pesquise palavras-chave em mais de 100 países com suporte de idioma nativo e insights regionais", 
        "ru": "Исследуйте ключевые слова в более чем 100 странах с поддержкой родного языка и региональными инсайтами", 
        "zh": "在100多个国家研究关键词，提供母语支持和区域洞察"
    },
    "features.ai_briefs.title": {
        "ar": "ملخصات المحتوى بالذكاء الاصطناعي", "de": "KI-Content-Briefings", "es": "Resúmenes de contenido IA", 
        "fr": "Briefs de contenu IA", "it": "Brief di contenuto IA", "ja": "AIコンテンツブリーフ", "ko": "AI 콘텐츠 브리프",
        "pt": "Briefings de conteúdo IA", "ru": "ИИ брифы контента", "zh": "AI内容简报"
    },
    "features.ai_briefs.description": {
        "ar": "احصل على توصيات محتوى مبنية على البيانات بناءً على تحليل SERP المباشر وأبحاث المنافسين", 
        "de": "Erhalten Sie datengestützte Content-Empfehlungen basierend auf Live-SERP-Analyse und Konkurrenzforschung", 
        "es": "Obtén recomendaciones de contenido basadas en datos según el análisis SERP en vivo e investigación de competidores", 
        "fr": "Obtenez des recommandations de contenu basées sur les données selon l'analyse SERP en direct et la recherche de concurrents", 
        "it": "Ottieni raccomandazioni di contenuto basate su dati secondo l'analisi SERP dal vivo e la ricerca sui concorrenti", 
        "ja": "ライブSERP分析と競合調査に基づくデータ駆動型コンテンツ推奨を取得", 
        "ko": "실시간 SERP 분석 및 경쟁사 조사를 기반으로 데이터 기반 콘텐츠 권장 사항 받기", 
        "pt": "Obtenha recomendações de conteúdo baseadas em dados com base na análise SERP ao vivo e pesquisa de concorrentes", 
        "ru": "Получайте рекомендации по контенту на основе данных с учетом live-анализа SERP и исследования конкурентов", 
        "zh": "根据实时SERP分析和竞争对手研究获取数据驱动的内容建议"
    },
}

def apply_translations(lang_codes):
    for lang_code in lang_codes:
        locale_file = LANGS_DIR / lang_code / "locale.json"
        if not locale_file.exists():
            continue
        
        with open(locale_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        strings = data.get('strings', {})
        updated = 0
        
        for key, translations in TRANSLATIONS_BATCH_1.items():
            if key in strings and lang_code in translations:
                # Update if it's currently in English (placeholder)
                if key in strings:
                    strings[key] = translations[lang_code]
                    updated += 1
        
        if updated > 0:
            data['strings'] = dict(sorted(strings.items()))
            with open(locale_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write('\n')
            print(f"✅ Updated {updated} keys in {lang_code}")

# Apply to first 10 languages
batch_1_langs = ['ar', 'de', 'es', 'fr', 'it', 'ja', 'ko', 'pt', 'ru', 'zh']
apply_translations(batch_1_langs)
print(f"\n🎉 Batch 1 complete! Translated keys for: {', '.join(batch_1_langs)}")
