#!/usr/bin/env python3
"""
Daily Stock Announcement Tool v1.1.0
Combines stock analysis, Gmail, and Sonos CLI functionality
Sends daily stock portfolio performance reports via email and announces them on Sonos speakers

Changelog 1.1.0:
- Fixed Gmail API credential path resolution
- Added retry mechanism for Sonos speaker commands
- Fixed Sonos text-to-speech argument formatting
- Added proper error logging and fallback handling
- Improved workspace path detection
- Added timeout safeguards for all external calls
"""

import os
import sys
import time
import logging
import datetime
from pathlib import Path
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
import subprocess
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Determine workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()
load_dotenv(WORKSPACE_ROOT / '.env')

# Configuration
PORTFOLIO = {
    'AAPL': 15,
    'MSFT': 8,
    'GOOGL': 5,
    'TSLA': 12,
    'NVDA': 10
}
SONOS_SPEAKER_NAME = os.getenv('SONOS_SPEAKER', 'Living Room')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'user@example.com')

def analyze_portfolio() -> dict:
    """Analyze current portfolio performance"""
    tickers = yf.Tickers(list(PORTFOLIO.keys()))
    prices = tickers.history(period='2d')['Close']
    
    current_prices = prices.iloc[-1]
    previous_prices = prices.iloc[-2]
    
    total_value = 0
    total_change = 0
    performance = []
    
    for ticker, shares in PORTFOLIO.items():
        current = current_prices[ticker]
        prev = previous_prices[ticker]
        value = current * shares
        change = (current - prev) * shares
        pct_change = ((current - prev) / prev) * 100
        
        total_value += value
        total_change += change
        
        performance.append({
            'ticker': ticker,
            'shares': shares,
            'current_price': current,
            'value': value,
            'change_dollars': change,
            'change_percent': pct_change
        })
    
    total_pct_change = (total_change / (total_value - total_change)) * 100 if (total_value - total_change) > 0 else 0
    
    return {
        'date': datetime.date.today().strftime('%Y-%m-%d'),
        'holdings': performance,
        'total_value': total_value,
        'total_change_dollars': total_change,
        'total_change_percent': total_pct_change
    }

def generate_email_report(analysis: dict) -> str:
    """Generate HTML email report from portfolio analysis"""
    html = f"""
    <html>
        <body>
            <h1>Daily Portfolio Performance Report - {analysis['date']}</h1>
            <h2>Total Portfolio Value: ${analysis['total_value']:,.2f}</h2>
            <h3>Today's Change: ${analysis['total_change_dollars']:,.2f} ({analysis['total_change_percent']:+.2f}%)</h3>
            
            <h3>Individual Holdings:</h3>
            <table border="1" cellpadding="8" cellspacing="0">
                <tr>
                    <th>Ticker</th>
                    <th>Shares</th>
                    <th>Current Price</th>
                    <th>Value</th>
                    <th>Change ($)</th>
                    <th>Change (%)</th>
                </tr>
    """
    
    for holding in analysis['holdings']:
        html += f"""
                <tr>
                    <td>{holding['ticker']}</td>
                    <td>{holding['shares']}</td>
                    <td>${holding['current_price']:.2f}</td>
                    <td>${holding['value']:,.2f}</td>
                    <td style="color: {'green' if holding['change_dollars'] >= 0 else 'red'}">
                        ${holding['change_dollars']:,.2f}
                    </td>
                    <td style="color: {'green' if holding['change_percent'] >= 0 else 'red'}">
                        {holding['change_percent']:+.2f}%
                    </td>
                </tr>
        """
    
    html += """
            </table>
            <p>Generated automatically by your stock announcement assistant.</p>
        </body>
    </html>
    """
    return html

def send_gmail(subject: str, body_html: str, max_retries: int = 3) -> bool:
    """Send email via Gmail API with retry mechanism"""
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    
    token_path = WORKSPACE_ROOT / "config" / "token.json"
    
    creds = None
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception as e:
            logger.error(f"Failed to load credentials from {token_path}: {e}")
    else:
        logger.warning(f"Token file not found at {token_path}, checking fallback locations...")
        fallback_paths = [
            Path.cwd() / "config" / "token.json",
            Path.home() / "token.json",
            Path("/config/token.json")
        ]
        for path in fallback_paths:
            if path.exists():
                try:
                    creds = Credentials.from_authorized_user_file(str(path), SCOPES)
                    logger.info(f"Loaded credentials from fallback: {path}")
                    break
                except Exception:
                    continue
    
    if not creds or not creds.valid:
        logger.error("Gmail credentials not found or invalid")
        return False
    
    for attempt in range(max_retries):
        try:
            service = build("gmail", "v1", credentials=creds, cache_discovery=False)
            message = MIMEText(body_html, 'html')
            message['to'] = RECIPIENT_EMAIL
            message['subject'] = subject
            
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            
            send_message = service.users().messages().send(userId="me", body=create_message).execute()
            logger.info(f"Email sent successfully, message ID: {send_message['id']}")
            return True
        except HttpError as error:
            logger.error(f"Attempt {attempt + 1}/{max_retries} - Gmail API error: {error}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
    
    logger.error("Failed to send email after all retries")
    return False

def announce_on_sonos(analysis: dict, max_retries: int = 3) -> bool:
    """Announce portfolio performance on Sonos speaker with retry mechanism"""
    change_dir = "up" if analysis['total_change_dollars'] >= 0 else "down"
    
    announcement = (
        f"Good morning! Here's your daily stock portfolio update for {analysis['date']}. "
        f"Your total portfolio value is ${analysis['total_value']:,.0f}. "
        f"Today it's {change_dir} by ${abs(analysis['total_change_dollars']):,.0f}, which is {analysis['total_change_percent']:.1f} percent. "
    )
    
    # Add top performer and loser
    sorted_holdings = sorted(analysis['holdings'], key=lambda x: x['change_percent'], reverse=True)
    top = sorted_holdings[0]
    bottom = sorted_holdings[-1]
    
    announcement += (
        f"Your top performer is {top['ticker']}, which is {top['change_percent']:.1f} percent {'up' if top['change_percent'] >=0 else 'down'}. "
        f"Your biggest mover is {bottom['ticker']}, which is {bottom['change_percent']:.1f} percent {'up' if bottom['change_percent'] >=0 else 'down'}."
    )
    
    # Clean up whitespace for TTS
    announcement = ' '.join(announcement.split())
    
    for attempt in range(max_retries):
        try:
            # First discover available speakers to verify connectivity
            if attempt == 0:
                try:
                    discover_result = subprocess.run(
                        ["sonos", "discover", "--timeout", "5"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if discover_result.returncode == 0:
                        logger.debug(f"Discovered speakers: {discover_result.stdout}")
                except Exception as e:
                    logger.warning(f"Speaker discovery failed (non-critical): {e}")
            
            # Use sonos cli to speak the announcement - correct argument format
            cmd = [
                "sonos",
                "--name", SONOS_SPEAKER_NAME,
                "say",
                announcement,
                "--voice", "en-US-Neural2-F"
            ]
            
            logger.debug(f"Running Sonos command")
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            logger.info(f"Announcement played successfully on {SONOS_SPEAKER_NAME}")
            if result.stdout:
                logger.debug(f"Sonos output: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} - Sonos error: {e.stderr or e.stdout}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
        except subprocess.TimeoutExpired:
            logger.error(f"Attempt {attempt + 1}/{max_retries} - Sonos command timed out")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} - Unexpected error: {str(e)}")
            logger.debug(traceback.format_exc())
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
    
    logger.error(f"Failed to play announcement after {max_retries} attempts")
    return False

def main():
    logger.info("=" * 60)
    logger.info("Running daily stock announcement workflow v1.1.0")
    logger.info("=" * 60)
    
    try:
        # Step 1: Analyze portfolio
        logger.info("Analyzing portfolio performance...")
        analysis = analyze_portfolio()
        logger.info(f"Portfolio analysis complete - Total value: ${analysis['total_value']:,.2f}")
        
        # Step 2: Generate and send email
        logger.info("Generating email report...")
        email_body = generate_email_report(analysis)
        email_sent = send_gmail(f"Daily Portfolio Report - {analysis['date']}", email_body)
        
        # Step 3: Announce on Sonos
        logger.info("Announcing performance on Sonos...")
        announcement_played = announce_on_sonos(analysis)
        
        logger.info("=" * 60)
        logger.info("Workflow complete!")
        logger.info(f"Email sent: {'✅ Success' if email_sent else '❌ Failed'}")
        logger.info(f"Sonos announcement: {'✅ Success' if announcement_played else '❌ Failed'}")
        logger.info("=" * 60)
        
        # Set exit code based on success/failure
        if not email_sent or not announcement_played:
            logger.warning("One or more components failed - check logs above")
            sys.exit(1)
            
    except Exception as e:
        logger.critical(f"Workflow failed with critical error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
