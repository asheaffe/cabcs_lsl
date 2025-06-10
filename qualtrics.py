# run ngrok http 8080 and then python3 server.py to get the server up and running
# change http address to forwarding address from ngrok (e.g. https://f38f-130-64-22-2.ngrok-free.app)

import asyncio
import json
from aiohttp import web
from datetime import datetime

async def handle_post(request):
    """Handle POST requests and print out the data"""
    try:
        # Get the content type
        content_type = request.headers.get('Content-Type', '')
        
        print(f"\n--- New POST Request at {datetime.now()} ---")
        print(f"Headers: {dict(request.headers)}")
        print(f"Content-Type: {content_type}")
        
        # Handle JSON data
        if 'application/json' in content_type:
            data = await request.json()
            print(f"JSON Data: {json.dumps(data, indent=2)}")
        
        # Handle form data
        elif 'application/x-www-form-urlencoded' in content_type:
            data = await request.post()
            print(f"Form Data: {dict(data)}")
        
        # Handle text data
        else:
            data = await request.text()
            print(f"Raw Data: {data}")
        
        print("--- End Request ---\n")
        
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

async def handle_get(request):
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

async def handle_options(request):
    """Handle OPTIONS requests for CORS"""
    print("OPTIONS request received")
    
    response = web.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    return response

def create_app():
    """Create the web application"""
    app = web.Application()
    
    # Routes
    app.router.add_post('/data', handle_post)  # Main endpoint for your data
    app.router.add_get('/', handle_get)        # Status check
    app.router.add_options('/data', handle_options)  # CORS preflight
    app.router.add_options('/', handle_options)      # CORS preflight for root
    
    return app

async def main():
    """Main function to run the server"""
    app = create_app()
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    
    print("🚀 Server started on http://localhost:8080")
    print("📡 POST endpoint: http://localhost:8080/data")
    print("📊 Status check: http://localhost:8080/")
    print("Press Ctrl+C to stop the server")
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        print("\n👋 Server shutting down...")
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())