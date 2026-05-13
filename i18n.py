"""
Alterfy — i18n / translations
"""
import json, os

_DATA_DIR = os.path.join(os.path.expanduser("~"), ".alterfy")
_PREF_FILE = os.path.join(_DATA_DIR, "prefs.json")

LANGUAGES = {
    "en":    "English",
    "en_gb": "English (UK)",
    "tr":    "Türkçe",
    "de":    "Deutsch",
    "fr":    "Français",
    "zh":    "简体中文",
    "hi":    "हिन्दी",
    "it":    "Italiano",
    "pt":    "Português",
}

_STRINGS: dict[str, dict[str, str]] = {
    # ── nav ──────────────────────────────────────
    "nav_home": {
        "en":"Home","en_gb":"Home","tr":"Ana Sayfa","de":"Startseite",
        "fr":"Accueil","zh":"主页","hi":"होम","it":"Home","pt":"Início",
    },
    "nav_search": {
        "en":"Search","en_gb":"Search","tr":"Ara","de":"Suche",
        "fr":"Rechercher","zh":"搜索","hi":"खोज","it":"Cerca","pt":"Pesquisar",
    },
    "nav_library": {
        "en":"Your Library","en_gb":"Your Library","tr":"Kitaplığın","de":"Deine Bibliothek",
        "fr":"Votre bibliothèque","zh":"你的音乐库","hi":"आपकी लाइब्रेरी","it":"La tua libreria","pt":"Sua Biblioteca",
    },
    # ── home ─────────────────────────────────────
    "greeting_morning": {
        "en":"Good morning","en_gb":"Good morning","tr":"Günaydın","de":"Guten Morgen",
        "fr":"Bonjour","zh":"早上好","hi":"शुभ प्रभात","it":"Buongiorno","pt":"Bom dia",
    },
    "greeting_afternoon": {
        "en":"Good afternoon","en_gb":"Good afternoon","tr":"İyi öğleden sonralar","de":"Guten Nachmittag",
        "fr":"Bon après-midi","zh":"下午好","hi":"नमस्ते","it":"Buon pomeriggio","pt":"Boa tarde",
    },
    "greeting_evening": {
        "en":"Good evening","en_gb":"Good evening","tr":"İyi akşamlar","de":"Guten Abend",
        "fr":"Bonsoir","zh":"晚上好","hi":"शुभ संध्या","it":"Buona sera","pt":"Boa noite",
    },
    "home_empty": {
        "en":"Start listening to get personalized recommendations",
        "en_gb":"Start listening to get personalised recommendations",
        "tr":"Kişiselleştirilmiş öneriler için müzik dinlemeye başla",
        "de":"Höre Musik, um personalisierte Empfehlungen zu erhalten",
        "fr":"Commencez à écouter pour obtenir des recommandations personnalisées",
        "zh":"开始收听以获取个性化推荐","hi":"व्यक्तिगत अनुशंसाओं के लिए सुनना शुरू करें",
        "it":"Inizia ad ascoltare per ottenere consigli personalizzati",
        "pt":"Comece a ouvir para obter recomendações personalizadas",
    },
    "home_empty_sub": {
        "en":"Search for music to begin","en_gb":"Search for music to begin",
        "tr":"Başlamak için müzik ara","de":"Suche nach Musik, um zu beginnen",
        "fr":"Recherchez de la musique pour commencer","zh":"搜索音乐开始",
        "hi":"शुरू करने के लिए संगीत खोजें","it":"Cerca musica per iniziare",
        "pt":"Pesquise música para começar",
    },
    "recently_played": {
        "en":"Recently played","en_gb":"Recently played","tr":"Son çalınanlar","de":"Zuletzt gespielt",
        "fr":"Récemment joués","zh":"最近播放","hi":"हाल में बजाया","it":"Riprodotti di recente","pt":"Reproduzidos recentemente",
    },
    "top_tracks": {
        "en":"Your top tracks","en_gb":"Your top tracks","tr":"En çok dinlediklerin","de":"Deine Top-Tracks",
        "fr":"Vos meilleures pistes","zh":"你的热门曲目","hi":"आपके शीर्ष ट्रैक","it":"Le tue canzoni top","pt":"Suas melhores músicas",
    },
    "more_from": {
        "en":"More from","en_gb":"More from","tr":"Şundan daha fazlası:","de":"Mehr von",
        "fr":"Plus de","zh":"更多来自","hi":"और अधिक","it":"Altro da","pt":"Mais de",
    },
    # ── search ───────────────────────────────────
    "search_placeholder": {
        "en":"Search songs, artists…","en_gb":"Search songs, artists…",
        "tr":"Şarkı, sanatçı ara…","de":"Songs, Künstler suchen…",
        "fr":"Rechercher des chansons, artistes…","zh":"搜索歌曲、艺术家…",
        "hi":"गाने, कलाकार खोजें…","it":"Cerca canzoni, artisti…","pt":"Buscar músicas, artistas…",
    },
    "search_results": {
        "en":"Search Results","en_gb":"Search Results","tr":"Arama Sonuçları","de":"Suchergebnisse",
        "fr":"Résultats de recherche","zh":"搜索结果","hi":"खोज परिणाम","it":"Risultati di ricerca","pt":"Resultados da pesquisa",
    },
    "recent_searches": {
        "en":"Recent searches","en_gb":"Recent searches","tr":"Son aramalar","de":"Letzte Suchanfragen",
        "fr":"Recherches récentes","zh":"最近的搜索","hi":"हाल की खोजें","it":"Ricerche recenti","pt":"Pesquisas recentes",
    },
    "clear_all": {
        "en":"Clear all","en_gb":"Clear all","tr":"Tümünü temizle","de":"Alles löschen",
        "fr":"Tout effacer","zh":"全部清除","hi":"सब हटाएं","it":"Cancella tutto","pt":"Limpar tudo",
    },
    "no_results": {
        "en":"No results","en_gb":"No results","tr":"Sonuç bulunamadı","de":"Keine Ergebnisse",
        "fr":"Aucun résultat","zh":"没有结果","hi":"कोई परिणाम नहीं","it":"Nessun risultato","pt":"Sem resultados",
    },
    "searching": {
        "en":"Searching…","en_gb":"Searching…","tr":"Aranıyor…","de":"Suche läuft…",
        "fr":"Recherche…","zh":"搜索中…","hi":"खोज रहा है…","it":"Ricerca in corso…","pt":"Pesquisando…",
    },
    # ── library ──────────────────────────────────
    "your_library": {
        "en":"Your Library","en_gb":"Your Library","tr":"Kitaplığın","de":"Deine Bibliothek",
        "fr":"Votre bibliothèque","zh":"你的音乐库","hi":"आपकी लाइब्रेरी","it":"La tua libreria","pt":"Sua Biblioteca",
    },
    "new_playlist": {
        "en":"New playlist","en_gb":"New playlist","tr":"Yeni çalma listesi","de":"Neue Playlist",
        "fr":"Nouvelle playlist","zh":"新建播放列表","hi":"नई प्लेलिस्ट","it":"Nuova playlist","pt":"Nova playlist",
    },
    "no_playlists": {
        "en":"No playlists yet.\nClick 'New playlist' to create one.",
        "en_gb":"No playlists yet.\nClick 'New playlist' to create one.",
        "tr":"Henüz çalma listesi yok.\nOluşturmak için 'Yeni çalma listesi'ne tıkla.",
        "de":"Noch keine Playlists.\nKlicke auf 'Neue Playlist', um eine zu erstellen.",
        "fr":"Pas encore de playlists.\nCliquez sur 'Nouvelle playlist' pour en créer une.",
        "zh":"还没有播放列表。\n点击\u300e新建播放列表\u300f创建一个。",
        "hi":"अभी तक कोई प्लेलिस्ट नहीं।\n'नई प्लेलिस्ट' पर क्लिक करें।",
        "it":"Nessuna playlist ancora.\nClicca 'Nuova playlist' per crearne una.",
        "pt":"Nenhuma playlist ainda.\nClique em 'Nova playlist' para criar uma.",
    },
    "playlist_name_prompt": {
        "en":"Playlist name:","en_gb":"Playlist name:","tr":"Çalma listesi adı:","de":"Playlist-Name:",
        "fr":"Nom de la playlist :","zh":"播放列表名称：","hi":"प्लेलिस्ट का नाम:","it":"Nome playlist:","pt":"Nome da playlist:",
    },
    "rename_playlist": {
        "en":"Rename Playlist","en_gb":"Rename Playlist","tr":"Çalma Listesini Yeniden Adlandır",
        "de":"Playlist umbenennen","fr":"Renommer la playlist","zh":"重命名播放列表",
        "hi":"प्लेलिस्ट का नाम बदलें","it":"Rinomina playlist","pt":"Renomear playlist",
    },
    "delete_playlist": {
        "en":"Delete playlist","en_gb":"Delete playlist","tr":"Çalma listesini sil","de":"Playlist löschen",
        "fr":"Supprimer la playlist","zh":"删除播放列表","hi":"प्लेलिस्ट हटाएं","it":"Elimina playlist","pt":"Excluir playlist",
    },
    "confirm_delete": {
        "en":"Delete","en_gb":"Delete","tr":"Sil","de":"Löschen",
        "fr":"Supprimer","zh":"删除","hi":"हटाएं","it":"Elimina","pt":"Excluir",
    },
    "songs": {
        "en":"songs","en_gb":"songs","tr":"şarkı","de":"Songs","fr":"chansons",
        "zh":"首歌","hi":"गाने","it":"canzoni","pt":"músicas",
    },
    "playlist_empty": {
        "en":"This playlist is empty.\nRight-click any song and choose 'Add to playlist'.",
        "en_gb":"This playlist is empty.\nRight-click any song and choose 'Add to playlist'.",
        "tr":"Bu çalma listesi boş.\nHerhangi bir şarkıya sağ tıklayıp 'Çalma listesine ekle'yi seç.",
        "de":"Diese Playlist ist leer.\nRechtsklick auf einen Song und 'Zur Playlist hinzufügen' wählen.",
        "fr":"Cette playlist est vide.\nFaites un clic droit sur une chanson et choisissez 'Ajouter à la playlist'.",
        "zh":"此播放列表为空。\n右键单击任意歌曲并选择\u300e添加到播放列表\u300f。",
        "hi":"यह प्लेलिस्ट खाली है।\nकिसी भी गाने पर राइट-क्लिक करें और 'प्लेलिस्ट में जोड़ें' चुनें।",
        "it":"Questa playlist è vuota.\nFai clic destro su qualsiasi canzone e scegli 'Aggiungi alla playlist'.",
        "pt":"Esta playlist está vazia.\nClique com o botão direito em qualquer música e escolha 'Adicionar à playlist'.",
    },
    # ── context menus ─────────────────────────────
    "play_now": {
        "en":"Play now","en_gb":"Play now","tr":"Şimdi çal","de":"Jetzt abspielen",
        "fr":"Jouer maintenant","zh":"立即播放","hi":"अभी चलाएं","it":"Riproduci ora","pt":"Tocar agora",
    },
    "add_to_playlist_menu": {
        "en":"Add to playlist","en_gb":"Add to playlist","tr":"Çalma listesine ekle","de":"Zur Playlist hinzufügen",
        "fr":"Ajouter à la playlist","zh":"添加到播放列表","hi":"प्लेलिस्ट में जोड़ें","it":"Aggiungi alla playlist","pt":"Adicionar à playlist",
    },
    "remove_from_playlist": {
        "en":"Remove from playlist","en_gb":"Remove from playlist","tr":"Çalma listesinden kaldır",
        "de":"Aus Playlist entfernen","fr":"Retirer de la playlist","zh":"从播放列表中删除",
        "hi":"प्लेलिस्ट से हटाएं","it":"Rimuovi dalla playlist","pt":"Remover da playlist",
    },
    "open_playlist_menu": {
        "en":"Open","en_gb":"Open","tr":"Aç","de":"Öffnen","fr":"Ouvrir","zh":"打开","hi":"खोलें","it":"Apri","pt":"Abrir",
    },
    "rename_menu": {
        "en":"Rename","en_gb":"Rename","tr":"Yeniden adlandır","de":"Umbenennen","fr":"Renommer",
        "zh":"重命名","hi":"नाम बदलें","it":"Rinomina","pt":"Renomear",
    },
    # ── lyrics ───────────────────────────────────
    "lyrics_title": {
        "en":"Lyrics","en_gb":"Lyrics","tr":"Şarkı Sözleri","de":"Songtext",
        "fr":"Paroles","zh":"歌词","hi":"गीत के बोल","it":"Testo","pt":"Letra",
    },
    "lyrics_not_found": {
        "en":"No lyrics found for this track.","en_gb":"No lyrics found for this track.",
        "tr":"Bu şarkı için söz bulunamadı.","de":"Für diesen Track wurden keine Texte gefunden.",
        "fr":"Aucune parole trouvée pour cette piste.","zh":"未找到此曲目的歌词。",
        "hi":"इस ट्रैक के लिए कोई गीत नहीं मिला।","it":"Nessun testo trovato per questo brano.",
        "pt":"Nenhuma letra encontrada para esta faixa.",
    },
    "lyrics_loading": {
        "en":"Loading lyrics…","en_gb":"Loading lyrics…","tr":"Sözler yükleniyor…","de":"Texte werden geladen…",
        "fr":"Chargement des paroles…","zh":"加载歌词中…","hi":"गीत लोड हो रहे हैं…","it":"Caricamento testo…","pt":"Carregando letra…",
    },
    "lyrics_instrumental": {
        "en":"This is an instrumental track.","en_gb":"This is an instrumental track.",
        "tr":"Bu enstrümantal bir parça.","de":"Dies ist ein Instrumentalstück.",
        "fr":"C'est un morceau instrumental.","zh":"这是一首纯音乐。",
        "hi":"यह एक वाद्य रचना है।","it":"Questo è un brano strumentale.","pt":"Esta é uma faixa instrumental.",
    },
    # ── add-to-playlist dialog ────────────────────
    "atp_title": {
        "en":"Add to playlist","en_gb":"Add to playlist","tr":"Çalma listesine ekle","de":"Zur Playlist hinzufügen",
        "fr":"Ajouter à la playlist","zh":"添加到播放列表","hi":"प्लेलिस्ट में जोड़ें","it":"Aggiungi alla playlist","pt":"Adicionar à playlist",
    },
    "atp_create_new": {
        "en":"+ Create new playlist","en_gb":"+ Create new playlist","tr":"+ Yeni çalma listesi oluştur","de":"+ Neue Playlist erstellen",
        "fr":"+ Créer une nouvelle playlist","zh":"+ 创建新播放列表","hi":"+ नई प्लेलिस्ट बनाएं","it":"+ Crea nuova playlist","pt":"+ Criar nova playlist",
    },
    "cancel": {
        "en":"Cancel","en_gb":"Cancel","tr":"İptal","de":"Abbrechen","fr":"Annuler",
        "zh":"取消","hi":"रद्द करें","it":"Annulla","pt":"Cancelar",
    },
    # ── settings ─────────────────────────────────
    "nav_settings": {
        "en":"Settings","en_gb":"Settings","tr":"Ayarlar","de":"Einstellungen","fr":"Paramètres",
        "zh":"设置","hi":"सेटिंग्स","it":"Impostazioni","pt":"Configurações",
    },
    "nav_about": {
        "en":"About","en_gb":"About","tr":"Hakkında","de":"Über","fr":"À propos",
        "zh":"关于","hi":"बारे में","it":"Info","pt":"Sobre",
    },
    "settings_language": {
        "en":"Language","en_gb":"Language","tr":"Dil","de":"Sprache","fr":"Langue",
        "zh":"语言","hi":"भाषा","it":"Lingua","pt":"Idioma",
    },
    "settings_language_sub": {
        "en":"Choose the display language for Alterfy",
        "en_gb":"Choose the display language for Alterfy",
        "tr":"Alterfy için görüntüleme dilini seçin",
        "de":"Wähle die Anzeigesprache für Alterfy",
        "fr":"Choisissez la langue d'affichage pour Alterfy",
        "zh":"选择 Alterfy 的显示语言",
        "hi":"Alterfy के लिए प्रदर्शन भाषा चुनें",
        "it":"Scegli la lingua di visualizzazione per Alterfy",
        "pt":"Escolha o idioma de exibição do Alterfy",
    },
    "settings_restart_note": {
        "en":"Language change takes effect immediately.",
        "en_gb":"Language change takes effect immediately.",
        "tr":"Dil değişikliği hemen geçerli olur.",
        "de":"Die Sprachänderung wird sofort wirksam.",
        "fr":"Le changement de langue prend effet immédiatement.",
        "zh":"语言更改立即生效。",
        "hi":"भाषा परिवर्तन तुरंत प्रभावी होता है।",
        "it":"Il cambio di lingua ha effetto immediato.",
        "pt":"A mudança de idioma entra em vigor imediatamente.",
    },
}

_current_lang = "en"


def load_lang() -> str:
    global _current_lang
    os.makedirs(_DATA_DIR, exist_ok=True)
    try:
        with open(_PREF_FILE, "r", encoding="utf-8") as f:
            prefs = json.load(f)
        _current_lang = prefs.get("language", "en")
    except Exception:
        _current_lang = "en"
    return _current_lang


def save_lang(lang: str):
    global _current_lang
    _current_lang = lang
    os.makedirs(_DATA_DIR, exist_ok=True)
    try:
        prefs = {}
        if os.path.exists(_PREF_FILE):
            with open(_PREF_FILE, "r", encoding="utf-8") as f:
                prefs = json.load(f)
        prefs["language"] = lang
        with open(_PREF_FILE, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
    except Exception as ex:
        print(f"[i18n] save error: {ex}")


def t(key: str, lang: str = None) -> str:
    """Translate key to current (or specified) language."""
    lng = lang or _current_lang
    bucket = _STRINGS.get(key, {})
    return bucket.get(lng) or bucket.get("en") or key


load_lang()
