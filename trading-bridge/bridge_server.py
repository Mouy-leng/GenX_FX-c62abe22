"""
Trading Bridge Server - MT5 to Exness API Bridge
================================================

This server acts as a bridge between MetaTrader 5 Expert Advisor and Exness API.
It receives trading signals from MT5 via socket connection and executes them via Exness API.

Author: @mouyleng / @A6-9V
Device: NUNA 💻
VPS: Singapore 09
"""

import asyncio
import json
import logging
import socket
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Configure logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_filename = LOG_DIR / f"bridge_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class BrokerAPI:
    """Generic broker API interface"""
    
    def __init__(self, broker_name: str, config: Dict):
        self.broker_name = broker_name
        self.config = config
        self.api_url = config.get("api_url", "")
        self.api_key = config.get("api_key", "")
        self.api_secret = config.get("api_secret", "")
        self.account_id = config.get("account_id", "")
        
    async def execute_trade(self, trade_data: Dict) -> Dict:
        """Execute a trade via broker API"""
        logger.info(f"Executing trade on {self.broker_name}: {trade_data}")
        
        # Validate credentials
        if not self.api_key or self.api_key == "YOUR_API_KEY":
            return {
                "success": False,
                "error": "Invalid API credentials. Please configure config/brokers.json"
            }
        
        # Placeholder for actual API implementation
        # In production, this would call the actual Exness API
        logger.warning(f"DEMO MODE: Trade would be executed on {self.broker_name}")
        
        return {
            "success": True,
            "order_id": f"DEMO_{datetime.now().timestamp()}",
            "message": "Trade executed successfully (DEMO MODE)"
        }
    
    async def get_account_info(self) -> Dict:
        """Get account information"""
        return {
            "account_id": self.account_id,
            "broker": self.broker_name,
            "status": "connected"
        }


class TradingBridge:
    """Trading Bridge Server"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5500):
        self.host = host
        self.port = port
        self.brokers: Dict[str, BrokerAPI] = {}
        self.running = False
        
    def load_broker_config(self):
        """Load broker configuration from config file"""
        config_file = Path(__file__).parent / "config" / "brokers.json"
        
        if not config_file.exists():
            logger.error(f"Configuration file not found: {config_file}")
            return
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            for broker_name, broker_config in config.items():
                if broker_config.get("enabled", False):
                    self.brokers[broker_name] = BrokerAPI(broker_name, broker_config)
                    logger.info(f"Loaded broker: {broker_name}")
                else:
                    logger.info(f"Broker {broker_name} is disabled")
        
        except Exception as e:
            logger.error(f"Error loading broker configuration: {e}")
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle client connection"""
        addr = writer.get_extra_info('peername')
        logger.info(f"Client connected from {addr}")
        
        try:
            while True:
                # Read data from client
                data = await reader.read(4096)
                if not data:
                    break
                
                message = data.decode('utf-8').strip()
                logger.info(f"Received: {message}")
                
                # Parse message
                try:
                    request = json.loads(message)
                    response = await self.process_request(request)
                except json.JSONDecodeError:
                    response = {
                        "success": False,
                        "error": "Invalid JSON format"
                    }
                
                # Send response
                response_data = json.dumps(response) + "\n"
                writer.write(response_data.encode('utf-8'))
                await writer.drain()
        
        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")
        
        finally:
            logger.info(f"Client disconnected: {addr}")
            writer.close()
            await writer.wait_closed()
    
    async def process_request(self, request: Dict) -> Dict:
        """Process client request"""
        action = request.get("action", "")
        broker_name = request.get("broker", "EXNESS")
        
        if action == "ping":
            return {"success": True, "message": "pong"}
        
        elif action == "trade":
            if broker_name not in self.brokers:
                return {
                    "success": False,
                    "error": f"Broker {broker_name} not configured or not enabled"
                }
            
            broker = self.brokers[broker_name]
            return await broker.execute_trade(request.get("data", {}))
        
        elif action == "account_info":
            if broker_name not in self.brokers:
                return {
                    "success": False,
                    "error": f"Broker {broker_name} not configured"
                }
            
            broker = self.brokers[broker_name]
            return await broker.get_account_info()
        
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
    
    async def start(self):
        """Start the bridge server"""
        self.load_broker_config()
        
        if not self.brokers:
            logger.warning("No brokers enabled. Please configure config/brokers.json")
        
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f"Trading Bridge Server started on {addr[0]}:{addr[1]}")
        logger.info("Waiting for connections from MT5 Expert Advisor...")
        
        self.running = True
        
        async with server:
            await server.serve_forever()


def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("TRADING BRIDGE SERVER")
    logger.info("Device: NUNA 💻 | User: @mouyleng | Org: @A6-9V")
    logger.info("VPS: Singapore 09 | Trading: 24/7")
    logger.info("=" * 80)
    
    bridge = TradingBridge(host="0.0.0.0", port=5500)
    
    try:
        asyncio.run(bridge.start())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
