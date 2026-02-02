//+------------------------------------------------------------------+
//|                                              PythonBridgeEA.mq5 |
//|                                  Trading Bridge Expert Advisor  |
//|                              Device: NUNA 💻 | User: @mouyleng  |
//|                        Organization: @A6-9V | VPS: Singapore 09 |
//+------------------------------------------------------------------+
#property copyright "A6-9V Trading Systems"
#property link      "https://github.com/A6-9V"
#property version   "1.00"
#property description "Expert Advisor that bridges MetaTrader 5 with Python trading bridge"

//--- Input parameters
input int      BridgePort = 5500;        // Python bridge port
input string   BrokerName = "EXNESS";    // Broker name
input bool     AutoExecute = true;       // Auto-execute trades
input double   DefaultLotSize = 0.01;    // Default lot size
input int      Slippage = 10;            // Maximum slippage in points
input bool     EnableLogging = true;     // Enable detailed logging

//--- Global variables
int socket_handle = INVALID_HANDLE;
datetime last_connection_attempt = 0;
bool is_connected = false;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("================================================================================");
    Print("PYTHON BRIDGE EA - INITIALIZATION");
    Print("================================================================================");
    Print("Bridge Port: ", BridgePort);
    Print("Broker Name: ", BrokerName);
    Print("Auto Execute: ", AutoExecute ? "Enabled" : "Disabled");
    Print("Default Lot Size: ", DefaultLotSize);
    Print("================================================================================");
    
    //--- Initialize bridge connection
    if(!ConnectToBridge())
    {
        Print("WARNING: Failed to connect to Python bridge on initialization");
        Print("Will retry connection periodically...");
    }
    else
    {
        Print("✓ Successfully connected to Python bridge");
        
        //--- Send initialization message
        string init_message = "{\"action\":\"ping\",\"broker\":\"" + BrokerName + "\"}";
        SendToBridge(init_message);
    }
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    Print("================================================================================");
    Print("PYTHON BRIDGE EA - SHUTDOWN");
    Print("Reason code: ", reason);
    Print("================================================================================");
    
    //--- Close socket connection
    if(socket_handle != INVALID_HANDLE)
    {
        SocketClose(socket_handle);
        socket_handle = INVALID_HANDLE;
        is_connected = false;
        Print("✓ Bridge connection closed");
    }
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    //--- Check connection status periodically
    if(!is_connected)
    {
        //--- Try to reconnect every 30 seconds
        if(TimeCurrent() - last_connection_attempt > 30)
        {
            if(EnableLogging)
                Print("Attempting to reconnect to Python bridge...");
            
            ConnectToBridge();
            last_connection_attempt = TimeCurrent();
        }
        return;
    }
    
    //--- Process any incoming messages from bridge
    ProcessBridgeMessages();
}

//+------------------------------------------------------------------+
//| Connect to Python bridge                                         |
//+------------------------------------------------------------------+
bool ConnectToBridge()
{
    //--- Close existing connection if any
    if(socket_handle != INVALID_HANDLE)
    {
        SocketClose(socket_handle);
        socket_handle = INVALID_HANDLE;
    }
    
    //--- Create new socket connection
    socket_handle = SocketCreate();
    if(socket_handle == INVALID_HANDLE)
    {
        Print("ERROR: Failed to create socket. Error code: ", GetLastError());
        return false;
    }
    
    //--- Connect to localhost on specified port
    if(!SocketConnect(socket_handle, "127.0.0.1", BridgePort, 1000))
    {
        Print("ERROR: Failed to connect to bridge on port ", BridgePort);
        Print("Error code: ", GetLastError());
        Print("Make sure the Python bridge is running (start-bridge.ps1)");
        SocketClose(socket_handle);
        socket_handle = INVALID_HANDLE;
        is_connected = false;
        return false;
    }
    
    is_connected = true;
    Print("Bridge connection initialized on port ", BridgePort);
    last_connection_attempt = TimeCurrent();
    
    return true;
}

//+------------------------------------------------------------------+
//| Send message to Python bridge                                    |
//+------------------------------------------------------------------+
bool SendToBridge(string message)
{
    if(socket_handle == INVALID_HANDLE || !is_connected)
    {
        if(EnableLogging)
            Print("ERROR: Cannot send message - bridge not connected");
        return false;
    }
    
    //--- Send message
    int sent = SocketSend(socket_handle, message + "\n");
    if(sent <= 0)
    {
        Print("ERROR: Failed to send message to bridge");
        is_connected = false;
        return false;
    }
    
    if(EnableLogging)
        Print("Sent to bridge: ", message);
    
    return true;
}

//+------------------------------------------------------------------+
//| Process incoming messages from bridge                            |
//+------------------------------------------------------------------+
void ProcessBridgeMessages()
{
    if(socket_handle == INVALID_HANDLE || !is_connected)
        return;
    
    //--- Check for incoming data
    uint len = SocketIsReadable(socket_handle);
    if(len > 0)
    {
        //--- Read data
        string response = "";
        char buffer[];
        ArrayResize(buffer, len);
        
        int received = SocketRead(socket_handle, buffer, len, 100);
        if(received > 0)
        {
            response = CharArrayToString(buffer, 0, received);
            
            if(EnableLogging)
                Print("Received from bridge: ", response);
            
            //--- Process response (parse JSON and take action)
            ProcessBridgeResponse(response);
        }
    }
}

//+------------------------------------------------------------------+
//| Process bridge response                                          |
//+------------------------------------------------------------------+
void ProcessBridgeResponse(string response)
{
    //--- Simple response processing
    //--- In production, this would parse JSON and handle different response types
    
    if(StringFind(response, "error") >= 0)
    {
        Print("Bridge reported error: ", response);
    }
    else if(StringFind(response, "success") >= 0)
    {
        if(EnableLogging)
            Print("Bridge operation successful: ", response);
    }
}

//+------------------------------------------------------------------+
//| Trade execution example                                          |
//+------------------------------------------------------------------+
bool ExecuteTradeViaBridge(string symbol, int order_type, double lots, double price)
{
    if(!AutoExecute)
    {
        Print("Auto-execute disabled - trade skipped");
        return false;
    }
    
    //--- Prepare trade request message
    string message = StringFormat(
        "{\"action\":\"trade\",\"broker\":\"%s\",\"data\":{\"symbol\":\"%s\",\"type\":%d,\"lots\":%.2f,\"price\":%.5f}}",
        BrokerName,
        symbol,
        order_type,
        lots,
        price
    );
    
    //--- Send to bridge
    return SendToBridge(message);
}

//+------------------------------------------------------------------+
//| Expert timer function (optional - for periodic tasks)            |
//+------------------------------------------------------------------+
void OnTimer()
{
    //--- Periodic tasks can be added here
    //--- For example: send heartbeat to bridge
    
    if(is_connected)
    {
        string heartbeat = "{\"action\":\"ping\",\"broker\":\"" + BrokerName + "\"}";
        SendToBridge(heartbeat);
    }
}

//+------------------------------------------------------------------+
