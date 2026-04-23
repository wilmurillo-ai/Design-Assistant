"""App name to package name mapping for supported applications."""

APP_PACKAGES: dict[str, str] = {
    # Social & Messaging
    "WeChat": "com.tencent.mm",
    "QQ": "com.tencent.mobileqq",
    "Weibo": "com.sina.weibo",
    # E-commerce
    "Taobao": "com.taobao.taobao",
    "JD": "com.jingdong.app.mall",
    "Pinduoduo": "com.xunmeng.pinduoduo",
    "Taobao Flash": "com.taobao.taobao",
    "JD Express": "com.jingdong.app.mall",
    # Lifestyle & Social
    "REDnote": "com.xingin.xhs",
    "Douban": "com.douban.frodo",
    "Zhihu": "com.zhihu.android",
    # Maps & Navigation
    "Amap": "com.autonavi.minimap",
    "Baidu Maps": "com.baidu.BaiduMap",
    # Food & Services
    "Meituan": "com.sankuai.meituan",
    "Dianping": "com.dianping.v1",
    "Eleme": "me.ele",
    "KFC": "com.yek.android.kfc.activitys",
    # Travel
    "Trip.com": "ctrip.android.view",
    "Railway12306": "com.MobileTicket",
    "12306": "com.MobileTicket",
    "Qunar": "com.Qunar",
    "Qunar Travel": "com.Qunar",
    "Didi": "com.sdu.didi.psnger",
    # Video & Entertainment
    "bilibili": "tv.danmaku.bili",
    "Douyin": "com.ss.android.ugc.aweme",
    "Kuaishou": "com.smile.gifmaker",
    "Tencent Video": "com.tencent.qqlive",
    "iQIYI": "com.qiyi.video",
    "Youku": "com.youku.phone",
    "Mango TV": "com.hunantv.imgo.activity",
    "Hongguo Drama": "com.phoenix.read",
    # Music & Audio
    "NetEase Cloud Music": "com.netease.cloudmusic",
    "QQ Music": "com.tencent.qqmusic",
    "Soda Music": "com.luna.music",
    "Ximalaya": "com.ximalaya.ting.android",
    # Reading
    "Tomato Novel": "com.dragon.read",
    "Tomato Free Novel": "com.dragon.read",
    "Qimao Free Novel": "com.kmxs.reader",
    # Productivity
    "Feishu": "com.ss.android.lark",
    "QQ Mail": "com.tencent.androidqqmail",
    # AI & Tools
    "Doubao": "com.larus.nova",
    # Health & Fitness
    "keep": "com.gotokeep.keep",
    "Meiyou": "com.lingan.seeyou",
    # News & Information
    "Tencent News": "com.tencent.news",
    "Toutiao": "com.ss.android.article.news",
    # Real Estate
    "Beike": "com.lianjia.beike",
    "Anjuke": "com.anjuke.android.app",
    # Finance
    "Tonghuashun": "com.hexin.plat.android",
    # Games
    "Honkai Star Rail": "com.miHoYo.hkrpg",
    "Honkai: Star Rail": "com.miHoYo.hkrpg",
    "Love and Deepspace": "com.papegames.lysk.cn",
    # Indian Apps - Entertainment & Tickets
    "BookMyShow": "com.bt.bms",
    "bookmyshow": "com.bt.bms",
    "Book My Show": "com.bt.bms",
    "book my show": "com.bt.bms",
    # Indian Apps - Food & Grocery
    "Swiggy": "in.swiggy.android",
    "swiggy": "in.swiggy.android",
    "Zomato": "com.application.zomato",
    "zomato": "com.application.zomato",
    "Blinkit": "com.grofers.customerapp",
    "blinkit": "com.grofers.customerapp",
    "BigBasket": "com.bigbasket.mobileapp",
    "bigbasket": "com.bigbasket.mobileapp",
    "Zepto": "com.zeptoconsumerapp",
    "zepto": "com.zeptoconsumerapp",
    # Indian Apps - E-commerce
    "Flipkart": "com.flipkart.android",
    "flipkart": "com.flipkart.android",
    "Amazon": "in.amazon.mShop.android.shopping",
    "amazon": "in.amazon.mShop.android.shopping",
    "Amazon India": "in.amazon.mShop.android.shopping",
    "Myntra": "com.myntra.android",
    "myntra": "com.myntra.android",
    "Meesho": "com.meesho.supply",
    "meesho": "com.meesho.supply",
    "Nykaa": "com.fsn.nykaa",
    "nykaa": "com.fsn.nykaa",
    "Ajio": "com.ril.ajio",
    "ajio": "com.ril.ajio",
    # Indian Apps - Ride & Transport
    "Uber": "com.ubercab",
    "uber": "com.ubercab",
    "Ola": "com.olacabs.customer",
    "ola": "com.olacabs.customer",
    "Rapido": "com.rapido.passenger",
    "rapido": "com.rapido.passenger",
    # Indian Apps - Payments
    "Paytm": "net.one97.paytm",
    "paytm": "net.one97.paytm",
    "PayTM": "net.one97.paytm",
    "PhonePe": "com.phonepe.app",
    "phonepe": "com.phonepe.app",
    "GPay": "com.google.android.apps.nbu.paisa.user",
    "Google Pay": "com.google.android.apps.nbu.paisa.user",
    "gpay": "com.google.android.apps.nbu.paisa.user",
    "Cred": "com.dreamplug.androidapp",
    "cred": "com.dreamplug.androidapp",
    # Indian Apps - Travel
    "MakeMyTrip": "com.makemytrip",
    "makemytrip": "com.makemytrip",
    "Make My Trip": "com.makemytrip",
    "IRCTC": "cris.mmtd.rail",
    "irctc": "cris.mmtd.rail",
    "IRCTC Rail Connect": "cris.mmtd.rail",
    "Cleartrip": "com.cleartrip.android",
    "cleartrip": "com.cleartrip.android",
    "Goibibo": "com.goibibo",
    "goibibo": "com.goibibo",
    "redBus": "in.redbus.android",
    "Redbus": "in.redbus.android",
    "redbus": "in.redbus.android",
    # Indian Apps - Entertainment & Streaming
    "Hotstar": "in.startv.hotstar",
    "hotstar": "in.startv.hotstar",
    "Disney+ Hotstar": "in.startv.hotstar",
    "JioCinema": "com.jio.media.ondemand",
    "jiocinema": "com.jio.media.ondemand",
    # Indian Apps - Finance
    "Zerodha": "com.zerodha.kite3",
    "Zerodha Kite": "com.zerodha.kite3",
    "zerodha": "com.zerodha.kite3",
    "Groww": "com.nextbillion.groww",
    "groww": "com.nextbillion.groww",
    # System
    "AndroidSystemSettings": "com.android.settings",
    "Android System Settings": "com.android.settings",
    "Android  System Settings": "com.android.settings",
    "Android-System-Settings": "com.android.settings",
    "Settings": "com.android.settings",
    "AudioRecorder": "com.android.soundrecorder",
    "audiorecorder": "com.android.soundrecorder",
    "Bluecoins": "com.rammigsoftware.bluecoins",
    "bluecoins": "com.rammigsoftware.bluecoins",
    "Broccoli": "com.flauschcode.broccoli",
    "broccoli": "com.flauschcode.broccoli",
    "Booking.com": "com.booking",
    "Booking": "com.booking",
    "booking.com": "com.booking",
    "booking": "com.booking",
    "BOOKING.COM": "com.booking",
    "Chrome": "com.android.chrome",
    "chrome": "com.android.chrome",
    "Google Chrome": "com.android.chrome",
    "Clock": "com.android.deskclock",
    "clock": "com.android.deskclock",
    "Contacts": "com.android.contacts",
    "contacts": "com.android.contacts",
    "Duolingo": "com.duolingo",
    "duolingo": "com.duolingo",
    "Expedia": "com.expedia.bookings",
    "expedia": "com.expedia.bookings",
    "Files": "com.android.fileexplorer",
    "files": "com.android.fileexplorer",
    "File Manager": "com.android.fileexplorer",
    "file manager": "com.android.fileexplorer",
    "gmail": "com.google.android.gm",
    "Gmail": "com.google.android.gm",
    "GoogleMail": "com.google.android.gm",
    "Google Mail": "com.google.android.gm",
    "GoogleFiles": "com.google.android.apps.nbu.files",
    "googlefiles": "com.google.android.apps.nbu.files",
    "FilesbyGoogle": "com.google.android.apps.nbu.files",
    "GoogleCalendar": "com.google.android.calendar",
    "Google-Calendar": "com.google.android.calendar",
    "Google Calendar": "com.google.android.calendar",
    "google-calendar": "com.google.android.calendar",
    "google calendar": "com.google.android.calendar",
    "GoogleChat": "com.google.android.apps.dynamite",
    "Google Chat": "com.google.android.apps.dynamite",
    "Google-Chat": "com.google.android.apps.dynamite",
    "GoogleClock": "com.google.android.deskclock",
    "Google Clock": "com.google.android.deskclock",
    "Google-Clock": "com.google.android.deskclock",
    "GoogleContacts": "com.google.android.contacts",
    "Google-Contacts": "com.google.android.contacts",
    "Google Contacts": "com.google.android.contacts",
    "google-contacts": "com.google.android.contacts",
    "google contacts": "com.google.android.contacts",
    "GoogleDocs": "com.google.android.apps.docs.editors.docs",
    "Google Docs": "com.google.android.apps.docs.editors.docs",
    "googledocs": "com.google.android.apps.docs.editors.docs",
    "google docs": "com.google.android.apps.docs.editors.docs",
    "Google Drive": "com.google.android.apps.docs",
    "Google-Drive": "com.google.android.apps.docs",
    "google drive": "com.google.android.apps.docs",
    "google-drive": "com.google.android.apps.docs",
    "GoogleDrive": "com.google.android.apps.docs",
    "Googledrive": "com.google.android.apps.docs",
    "googledrive": "com.google.android.apps.docs",
    "GoogleFit": "com.google.android.apps.fitness",
    "googlefit": "com.google.android.apps.fitness",
    "GoogleKeep": "com.google.android.keep",
    "googlekeep": "com.google.android.keep",
    "GoogleMaps": "com.google.android.apps.maps",
    "Google Maps": "com.google.android.apps.maps",
    "googlemaps": "com.google.android.apps.maps",
    "google maps": "com.google.android.apps.maps",
    "Google Play Books": "com.google.android.apps.books",
    "Google-Play-Books": "com.google.android.apps.books",
    "google play books": "com.google.android.apps.books",
    "google-play-books": "com.google.android.apps.books",
    "GooglePlayBooks": "com.google.android.apps.books",
    "googleplaybooks": "com.google.android.apps.books",
    "GooglePlayStore": "com.android.vending",
    "Google Play Store": "com.android.vending",
    "Google-Play-Store": "com.android.vending",
    "GoogleSlides": "com.google.android.apps.docs.editors.slides",
    "Google Slides": "com.google.android.apps.docs.editors.slides",
    "Google-Slides": "com.google.android.apps.docs.editors.slides",
    "GoogleTasks": "com.google.android.apps.tasks",
    "Google Tasks": "com.google.android.apps.tasks",
    "Google-Tasks": "com.google.android.apps.tasks",
    "Joplin": "net.cozic.joplin",
    "joplin": "net.cozic.joplin",
    "McDonald": "com.mcdonalds.app",
    "mcdonald": "com.mcdonalds.app",
    "Osmand": "net.osmand",
    "osmand": "net.osmand",
    "PiMusicPlayer": "com.Project100Pi.themusicplayer",
    "pimusicplayer": "com.Project100Pi.themusicplayer",
    "Quora": "com.quora.android",
    "quora": "com.quora.android",
    "Reddit": "com.reddit.frontpage",
    "reddit": "com.reddit.frontpage",
    "RetroMusic": "code.name.monkey.retromusic",
    "retromusic": "code.name.monkey.retromusic",
    "SimpleCalendarPro": "com.scientificcalculatorplus.simplecalculator.basiccalculator.mathcalc",
    "SimpleSMSMessenger": "com.simplemobiletools.smsmessenger",
    "Telegram": "org.telegram.messenger",
    "temu": "com.einnovation.temu",
    "Temu": "com.einnovation.temu",
    "Tiktok": "com.zhiliaoapp.musically",
    "tiktok": "com.zhiliaoapp.musically",
    "Twitter": "com.twitter.android",
    "twitter": "com.twitter.android",
    "X": "com.twitter.android",
    "VLC": "org.videolan.vlc",
    "WeChat": "com.tencent.mm",
    "wechat": "com.tencent.mm",
    "Whatsapp": "com.whatsapp",
    "WhatsApp": "com.whatsapp",
}

APP_PACKAGES_CASEFOLDED = {
    name.casefold(): package for name, package in APP_PACKAGES.items()
}


def get_package_name(app_name: str) -> str | None:
    """
    Get the package name for an app.

    Args:
        app_name: The display name of the app.

    Returns:
        The Android package name, or None if not found.
    """
    return APP_PACKAGES.get(app_name) or APP_PACKAGES_CASEFOLDED.get(app_name.casefold())


def get_app_name(package_name: str) -> str | None:
    """
    Get the app name from a package name.

    Args:
        package_name: The Android package name.

    Returns:
        The display name of the app, or None if not found.
    """
    for name, package in APP_PACKAGES.items():
        if package == package_name:
            return name
    return None


def list_supported_apps() -> list[str]:
    """
    Get a list of all supported app names.

    Returns:
        List of app names.
    """
    return list(APP_PACKAGES.keys())
