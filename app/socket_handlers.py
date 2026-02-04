"""
WTTG2 Organizer - SocketIO Event Handlers
Handles real-time WebSocket communication with clients.
"""
from flask_socketio import emit
from app.data_manager import DataManager
from app.config import Config

# Initialize data manager
data_manager = DataManager(Config.DATA_FILE)


def register_handlers(socketio):
    """
    Register all SocketIO event handlers.
    
    Args:
        socketio: SocketIO instance to register handlers with
    """
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection - send initial data"""
        print("Client connected")
        
        # Get Local IP for mobile sync
        import socket
        try:
            # Connect to a public DNS to get the real local IP (doesn't send data)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "127.0.0.1"

        # Send data + IP
        data = data_manager.get_data()
        data['server_ip'] = local_ip
        emit('init_data', data)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print("Client disconnected")
    
    @socketio.on('update_key')
    def handle_update_key(payload):
        """
        Handle key value update.
        payload: { index: int, value: str }
        """
        try:
            idx = payload.get('index')
            val = payload.get('value', '')
            
            if data_manager.set_key(idx, val):
                socketio.emit('data_update', data_manager.get_data())
        except Exception as e:
            print(f"Error in update_key: {e}")
    
    @socketio.on('update_key_marker')
    def handle_key_marker(payload):
        """
        Handle wiki marker toggle.
        payload: { key_index: int, marker_index: int (0-2) }
        """
        try:
            k_idx = payload.get('key_index')
            m_idx = payload.get('marker_index')
            
            if data_manager.toggle_key_marker(k_idx, m_idx):
                socketio.emit('data_update', data_manager.get_data())
        except Exception as e:
            print(f"Error in update_key_marker: {e}")
    
    @socketio.on('update_notes')
    def handle_update_notes(payload):
        """
        Handle notes update.
        payload: { text: str }
        """
        try:
            text = payload.get('text', '')
            
            if data_manager.set_notes(text):
                socketio.emit('data_update', data_manager.get_data())
        except Exception as e:
            print(f"Error in update_notes: {e}")
    
    @socketio.on('update_site_marker')
    def handle_site_marker(payload):
        """
        Handle site marker toggle.
        payload: { site_name: str, color: 'green'|'red' }
        """
        try:
            site = payload.get('site_name')
            color = payload.get('color')
            
            if data_manager.toggle_site_marker(site, color):
                socketio.emit('data_update', data_manager.get_data())
        except Exception as e:
            print(f"Error in update_site_marker: {e}")
    
    @socketio.on('toggle_1337')
    def handle_toggle_1337(payload):
        """
        Handle 1337 mode toggle.
        payload: { enabled: bool }
        """
        try:
            enabled = payload.get('enabled', False)
            
            if data_manager.set_mode_1337(enabled):
                socketio.emit('data_update', data_manager.get_data())
        except Exception as e:
            print(f"Error in toggle_1337: {e}")
    
    @socketio.on('add_wifi')
    def handle_add_wifi(payload):
        """
        Handle wifi entry addition.
        payload: { ssid: str, pass: str, loc: str }
        """
        try:
            ssid = payload.get('ssid', '')
            password = payload.get('pass', '')
            location = payload.get('loc', '')
            
            if ssid and password:
                if data_manager.add_wifi(ssid, password, location):
                    socketio.emit('data_update', data_manager.get_data())
        except Exception as e:
            print(f"Error in add_wifi: {e}")
    
    @socketio.on('delete_wifi')
    def handle_delete_wifi(payload):
        """
        Handle wifi entry deletion.
        payload: { index: int }
        """
        try:
            idx = payload.get('index')
            
            if data_manager.delete_wifi(idx):
                socketio.emit('data_update', data_manager.get_data())
        except Exception as e:
            print(f"Error in delete_wifi: {e}")

    @socketio.on('reset_data')
    def handle_reset_data():
        """Handle full data reset"""
        try:
            if data_manager.reset_data():
                print("System reset performed")
                socketio.emit('init_data', data_manager.get_data())
        except Exception as e:
            print(f"Error in reset_data: {e}")
