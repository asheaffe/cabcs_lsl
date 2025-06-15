# run ngrok http 8080 and then python3 qualtrics.py to get the server up and running
# change http address to forwarding address from ngrok (e.g. https://f38f-130-64-22-2.ngrok-free.app)

import asyncio
import json
import sys
from aiohttp import web
from datetime import datetime
import win32gui

class Qualtrics():
    def __init__(self):
        self.app, self.data = self.create_app()
        self.json_data = None
        self.runner = None
        self.site = None
        self.data_received_event = asyncio.Event()
    
    async def _async_init(self):
        # Start the server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, 'localhost', 8080)
        await self.site.start()
        
        print("Server started on http://localhost:8080")

    @classmethod
    async def create(cls):
        """Main function to run the server"""
        instance = cls()
        await instance._async_init()
        return instance
    
    async def cleanup(self):
        """Cleans up the server. I hate python multithreading :)"""
        if self.runner:
            await self.runner.cleanup()

    def create_app(self):
        """Create the web application"""
        app = web.Application()
        
        # Routes
        post = self.handle_post
        app.router.add_post('/data', post)  # Main endpoint for your data
        app.router.add_get('/', self.handle_get)        # Status check
        app.router.add_options('/data', self.handle_options)  # CORS preflight
        app.router.add_options('/', self.handle_options)      # CORS preflight for root
        
        return app, post

    def minimize_browser(self):
        """Used to automatically minimize windows after each block"""
        def enum_windows_callback(hwnd, results):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd).lower()
                    browser_keywords = ['Qualtrics']
                    if any(keyword in window_title for keyword in browser_keywords):
                        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                        print(f"Minimized window: {win32gui.GetWindowText(hwnd)}")
            except Exception as e:
                print(f"Error with window {hwnd}: {e}")
        
        win32gui.EnumWindows(enum_windows_callback, [])
            

    async def handle_post(self, request):
        """Handle POST requests and print out the data"""
        try:
            # Get the content type
            content_type = request.headers.get('Content-Type', '')
            
            # print(f"\n--- New POST Request at {datetime.now()} ---")
            # print(f"Headers: {dict(request.headers)}")
            # print(f"Content-Type: {content_type}")
            
            # Handle JSON data
            if 'application/json' in content_type:
                data = await request.json()
                self.json_data = data

                # signal that data has been received 
                if hasattr(self, 'data_received_event'):
                    self.data_received_event.set()

                #print(f"JSON Data: {json.dumps(data, indent=2)}")
            
            # Handle form data
            elif 'application/x-www-form-urlencoded' in content_type:
                data = await request.post()
                #print(f"Form Data: {dict(data)}")
            
            # Handle text data
            else:
                data = await request.text()
                #print(f"Raw Data: {data}")
            
            #print("--- End Request ---\n")

            # minimize qualtrics window
            #self.minimize_browser()
            
            # Return a success response with CORS headers
            response = web.json_response({
                'status': 'success', 
                'message': 'Data received',
                'timestamp': datetime.now().isoformat()
            })
            
            # Add CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            
            return response
            
        except Exception as e:
            print(f"Error processing request: {e}")
            response = web.json_response({
                'status': 'error', 
                'message': str(e)
            }, status=400)
            
            # Add CORS headers even for errors
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            
            return response

    async def handle_get(self, request):
        """Handle GET requests - just a simple status check"""
        response = web.json_response({
            'status': 'Server is running!',
            'endpoints': ['/data (POST)', '/ (GET)']
        })
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response

    async def handle_options(self, request):
        """Handle OPTIONS requests for CORS"""
        #print("OPTIONS request received")
        
        response = web.Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response





# if __name__ == '__main__':
#     # check that platform is Windows for window minimization
#     try:
#         if sys.platform == "win32":
#             import win32gui
#             import win32con
#             asyncio.run(main())
#     except ImportError:
#         print(f"Warning: Platform specific libraries not available for {sys.platform}")

    