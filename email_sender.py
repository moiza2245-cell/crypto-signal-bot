"""
==============================================
  EMAIL SIGNAL SENDER (Gmail - FREE)
==============================================
Gmail se FREE mein signals bhejta hai.
Koi paid service nahi chahiye!
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD


def send_email_signal(symbol, signal):
    """Gmail se signal bhejo"""
    try:
        is_long = "LONG" in signal['direction']
        direction_emoji = "🟢📈 LONG (BUY)" if is_long else "🔴📉 SHORT (SELL)"
        bg_color = "#00c853" if is_long else "#ff1744"
        text_color = "#1b5e20" if is_long else "#b71c1c"

        def fmt(price):
            if price >= 1000:
                return f"${price:,.2f}"
            elif price >= 1:
                return f"${price:.4f}"
            else:
                return f"${price:.8f}"

        # ── Beautiful HTML Email ──
        indicators_html = ""
        for name, detail in signal['details'].items():
            indicators_html += f"<tr><td style='padding:6px 12px;font-weight:bold;'>{name}</td><td style='padding:6px 12px;'>{detail}</td></tr>"

        html = f"""
        <html>
        <body style="font-family:Arial,sans-serif;background:#0d1117;color:#ffffff;padding:20px;">
            
            <div style="max-width:500px;margin:auto;background:#161b22;border-radius:12px;overflow:hidden;border:1px solid #30363d;">
                
                <!-- Header -->
                <div style="background:{bg_color};padding:20px;text-align:center;">
                    <h1 style="margin:0;color:#fff;font-size:20px;">🚀 CRYPTO SIGNAL ALERT</h1>
                    <h2 style="margin:5px 0 0;color:#fff;font-size:28px;">{symbol}</h2>
                </div>

                <!-- Direction -->
                <div style="padding:20px;text-align:center;">
                    <span style="font-size:24px;font-weight:bold;color:{bg_color};">{direction_emoji}</span>
                    <br>
                    <span style="font-size:16px;color:#ffd600;">{signal['strength']}</span>
                    <br>
                    <span style="font-size:14px;color:#90caf9;">Confidence: {signal['confidence']}</span>
                </div>

                <!-- Prices -->
                <table style="width:100%;border-collapse:collapse;">
                    <tr style="background:#1e2430;">
                        <td style="padding:12px;color:#90caf9;font-weight:bold;">💰 Entry</td>
                        <td style="padding:12px;color:#fff;font-size:18px;text-align:right;">{fmt(signal['entry'])}</td>
                    </tr>
                    <tr style="background:#1a1e28;">
                        <td style="padding:12px;color:#ff5252;font-weight:bold;">✋ Stop Loss</td>
                        <td style="padding:12px;color:#ff5252;font-size:18px;text-align:right;">{fmt(signal['stop_loss'])}</td>
                    </tr>
                    <tr style="background:#1e2430;">
                        <td style="padding:12px;color:#69f0ae;font-weight:bold;">🎯 TP 1</td>
                        <td style="padding:12px;color:#69f0ae;font-size:18px;text-align:right;">{fmt(signal['take_profit_1'])}</td>
                    </tr>
                    <tr style="background:#1a1e28;">
                        <td style="padding:12px;color:#69f0ae;font-weight:bold;">🎯 TP 2</td>
                        <td style="padding:12px;color:#69f0ae;font-size:18px;text-align:right;">{fmt(signal['take_profit_2'])}</td>
                    </tr>
                    <tr style="background:#1e2430;">
                        <td style="padding:12px;color:#69f0ae;font-weight:bold;">🎯 TP 3</td>
                        <td style="padding:12px;color:#69f0ae;font-size:18px;text-align:right;">{fmt(signal['take_profit_3'])}</td>
                    </tr>
                    <tr style="background:#1a1e28;">
                        <td style="padding:12px;color:#ffd600;font-weight:bold;">⚖️ R:R Ratio</td>
                        <td style="padding:12px;color:#ffd600;font-size:18px;text-align:right;">{signal['risk_reward']}</td>
                    </tr>
                </table>

                <!-- Indicators -->
                <div style="padding:15px;">
                    <h3 style="color:#90caf9;margin:0 0 10px;">📊 Indicator Details:</h3>
                    <table style="width:100%;border-collapse:collapse;font-size:13px;">
                        {indicators_html}
                    </table>
                </div>

                <!-- Disclaimer -->
                <div style="padding:15px;background:#1a1e28;text-align:center;border-top:1px solid #30363d;">
                    <p style="color:#ff9800;font-size:11px;margin:0;">
                        ⚠️ Ye sirf signal hai, guarantee nahi! Stop Loss zaroor lagao!
                    </p>
                </div>
            </div>

        </body>
        </html>
        """

        # ── Plain text version ──
        plain_text = f"""
🚀 CRYPTO SIGNAL ALERT
━━━━━━━━━━━━━━━━━━━━
🪙 Coin: {symbol}
📊 Direction: {direction_emoji}
💪 Strength: {signal['strength']}
🎯 Confidence: {signal['confidence']}

💰 Entry: {fmt(signal['entry'])}
✋ Stop Loss: {fmt(signal['stop_loss'])}
🎯 TP 1: {fmt(signal['take_profit_1'])}
🎯 TP 2: {fmt(signal['take_profit_2'])}
🎯 TP 3: {fmt(signal['take_profit_3'])}
⚖️ R:R Ratio: {signal['risk_reward']}

📊 Indicators:
"""
        for name, detail in signal['details'].items():
            plain_text += f"• {name}: {detail}\n"

        plain_text += "\n⚠️ Ye sirf signal hai, guarantee nahi!\n⚠️ Stop Loss zaroor lagao!"

        # ── Send Email ──
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚀 {symbol} — {direction_emoji} | {signal['strength']}"
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = GMAIL_ADDRESS  # Khud ko bhejo

        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, GMAIL_ADDRESS, msg.as_string())

        print(f"  ✅ Email sent to {GMAIL_ADDRESS}!")
        return True

    except Exception as e:
        print(f"  ❌ Email send failed: {e}")
        return False
