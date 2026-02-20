from http.server import BaseHTTPRequestHandler
import json
import statistics

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Read the request
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data)
        
        # Get what the user asked for
        regions_to_check = request_data.get('regions', [])
        threshold = request_data.get('threshold_ms', 180)
        
        # Load our sample data
        with open('q-vercel-latency.json', 'r') as file:
            all_data = json.load(file)
        
        # Calculate results
        results = {}
        for region in regions_to_check:
            region_records = [item for item in all_data if item['region'] == region]
            
            if region_records:
                latencies = [r['latency_ms'] for r in region_records]
                uptimes = [r['uptime_pct'] for r in region_records]
                
                # Calculate statistics
                avg_latency = sum(latencies) / len(latencies)
                
                # 95th percentile
                sorted_latencies = sorted(latencies)
                p95_index = int(len(sorted_latencies) * 0.95)
                p95_latency = sorted_latencies[p95_index]
                
                avg_uptime = sum(uptimes) / len(uptimes)
                breaches = sum(1 for l in latencies if l > threshold)
                
                results[region] = {
                    'avg_latency': round(avg_latency, 2),
                    'p95_latency': round(p95_latency, 2),
                    'avg_uptime': round(avg_uptime, 2),
                    'breaches': breaches
                }
        
        self.wfile.write(json.dumps(results).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
